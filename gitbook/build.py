#!/usr/bin/env python3
"""Build the GitBook source folder (gitbook/) from content/, public/images/ and sidebars/.

Run from the repo root:   python gitbook/build.py

content/ is never edited. gitbook/ is a generated copy. GitBook's Git Sync has no
plugin/hook system (unlike Docusaurus remark plugins or MkDocs hooks), so the copy gets
the same build-time conversions the other two builds do, and nothing else:
  1. '## Title {/*id*/}'  ->  '## Title'   (GitBook would show the marker as heading text)
  2. '/reference/react/memo#x' links  ->  relative '.md' links GitBook can resolve
  3. '#id' anchors  ->  '#<anchor GitBook generates from the heading text>'
  4. '<img src="/images/...">'  ->  relative path
Text, code, tags and everything else are left exactly as written.
Use  python gitbook/build.py --no-rewrite  to get the plain byte-identical copy instead.
"""
import hashlib
import json
import posixpath
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
IMAGES = ROOT / "public" / "images"
SIDEBARS = ROOT / "sidebars"
OUT = ROOT / "gitbook"
VERSION = "19.3"  # react.dev fills {{version}} in sidebar headers
REWRITE = "--no-rewrite" not in sys.argv

AREAS = ["Learn", "Reference", "Community", "Blog"]
COPY_DIRS = ["blog", "community", "errors", "learn", "reference", "warnings"]


# ------------------------------------------------------------------ SUMMARY.md
def md_for(path):
    p = path.strip("/")
    for cand in (p + ".md", p + "/index.md"):
        if (CONTENT / cand).is_file():
            return cand
    return None


def label(title):
    for ch in "\\<>[]":
        title = title.replace(ch, "\\" + ch)
    return title


lines = ["# Summary", "", "* [React](README.md)", ""]
used = set()
skipped = []


def emit(routes, depth):
    for r in routes:
        if r.get("hasSectionHeader"):
            lines.append("")
            lines.append("## " + r["sectionHeader"].replace("{{version}}", VERSION))
            lines.append("")
            continue
        f = md_for(r["path"]) if r.get("path", "").startswith("/") else None
        if f is None:
            skipped.append((r["title"], r.get("path")))
            emit(r.get("routes", []), depth)
            continue
        if f in used:
            skipped.append((r["title"] + " (duplicate)", r["path"]))
            emit(r.get("routes", []), depth)
            continue
        used.add(f)
        lines.append("  " * depth + "* [" + label(r["title"]) + "](" + f + ")")
        emit(r.get("routes", []), depth + 1)


for area in AREAS:
    data = json.loads((SIDEBARS / f"sidebar{area}.json").read_text(encoding="utf-8"))
    emit(data["routes"], 0)

extra = sorted(
    str(p.relative_to(CONTENT)).replace("\\", "/")
    for p in CONTENT.rglob("*.md")
    if str(p.relative_to(CONTENT)).replace("\\", "/") not in used
    and str(p.relative_to(CONTENT)).replace("\\", "/") != "index.md"
)
lines += ["", "## Not in the react.dev sidebar", ""]
for f in extra:
    head = (CONTENT / f).read_text(encoding="utf-8")
    title = None
    if head.startswith("---"):
        for ln in head.split("---")[1].splitlines():
            if ln.startswith("title:"):
                title = ln[6:].strip().strip("'\"")
    if not title:
        title = "Errors: " + Path(f).stem
    lines.append("* [" + label(title) + "](" + f + ")")
    used.add(f)

# ------------------------------------------------------------------ copy
for d in COPY_DIRS + ["images", "assets"]:
    shutil.rmtree(OUT / d, ignore_errors=True)
for d in COPY_DIRS:
    shutil.copytree(CONTENT / d, OUT / d)
shutil.copy2(CONTENT / "versions.md", OUT / "versions.md")
shutil.copytree(IMAGES, OUT / "images")


# ------------------------------------------------------------------ rewrite
FENCE = re.compile(r"\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6}) (.*?)(?: \{/\*([^*]+)\*/\})?\s*$")
LINK = re.compile(r"(\]\()([^)\s]*)((?:\s+\"[^\"]*\")?\))")
REFDEF = re.compile(r"^(\s*\[[^\]]+\]:\s*)(\S+)(.*)$")
IMGSRC = re.compile(r"(src=\")(/[^\"]*)(\")")
CODESPAN = re.compile(r"(`+[^`]*`+)")


def gb_slug(text):
    """Anchor GitBook builds from heading text (GitHub-style: lowercase, drop punctuation, spaces to '-')."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.replace("`", "").lower().strip()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def md_files():
    return sorted(p for p in OUT.rglob("*.md") if p.parent != OUT or p.name == "versions.md")


def body_lines(text):
    """Yield (index, line_without_CR, in_fence) for every line."""
    infence = False
    for i, ln in enumerate(text.split("\n")):
        b = ln[:-1] if ln.endswith("\r") else ln
        if FENCE.match(b):
            infence = not infence
            yield i, b, True
            continue
        yield i, b, infence


# Pass 1: anchors per file
all_files = {str(p.relative_to(OUT)).replace("\\", "/") for p in OUT.rglob("*") if p.is_file()}
ids = {}  # rel -> {explicit id: slug}
slugs = {}  # rel -> set of slugs
for p in md_files():
    rel = str(p.relative_to(OUT)).replace("\\", "/")
    seen = Counter()
    idmap, sl = {}, set()
    for _, b, fenced in body_lines((CONTENT / rel).read_text(encoding="utf-8")):
        if fenced:
            continue
        m = HEADING.match(b)
        if not m:
            continue
        s = gb_slug(m.group(2))
        final = s if seen[s] == 0 else f"{s}-{seen[s]}"
        seen[s] += 1
        sl.add(final)
        if m.group(3):
            idmap[m.group(3)] = final
    ids[rel], slugs[rel] = idmap, sl


def resolve(cur, path):
    """Find the gitbook/ file a link path points to, or None."""
    cands = []
    if path.startswith("/"):
        cands.append(path.lstrip("/"))
    elif path.startswith("."):
        cands.append(posixpath.normpath(posixpath.join(posixpath.dirname(cur), path)))
    else:  # bare 'learn/foo': react.dev's browser tolerates it; try root-relative first
        cands += [path, posixpath.normpath(posixpath.join(posixpath.dirname(cur), path))]
    for c in cands:
        c = c.rstrip("/")
        for t in (c, c + ".md", c + "/index.md"):
            if t in all_files:
                return t
    return None


stats = Counter()
unresolved = []


def fix_target(cur, url):
    if re.match(r"(https?:|mailto:|//)", url) or url == "":
        return url
    path, _, anchor = url.partition("#")
    if path == "":  # same-page anchor
        if anchor in ids[cur]:
            stats["anchor_remapped"] += ids[cur][anchor] != anchor
            return "#" + ids[cur][anchor]
        return url
    if path.startswith("."):  # '../images/x.png' already works in GitBook
        return url
    target = resolve(cur, path)
    if target is None:
        stats["link_unresolved"] += 1
        unresolved.append((cur, url))
        return url
    rel = posixpath.relpath(target, posixpath.dirname(cur))
    stats["link_rewritten"] += 1
    if anchor:
        a = ids.get(target, {}).get(anchor, anchor)
        stats["anchor_remapped"] += a != anchor
        return rel + "#" + a
    return rel


def rewrite_text(cur, text):
    out = []
    for _, b, fenced in body_lines(text):
        cr = "\r" if text.split("\n")[len(out)].endswith("\r") else ""
        if not fenced:
            m = HEADING.match(b)
            if m and m.group(3):
                b = m.group(1) + " " + m.group(2)
                stats["heading_id_stripped"] += 1
            r = REFDEF.match(b)
            if r:
                b = r.group(1) + fix_target(cur, r.group(2)) + r.group(3)
            parts = CODESPAN.split(b)
            for i in range(0, len(parts), 2):
                s = LINK.sub(lambda mm: mm.group(1) + fix_target(cur, mm.group(2)) + mm.group(3), parts[i])
                def img(mm):
                    t = resolve(cur, mm.group(2))
                    if t is None:
                        return mm.group(0)
                    stats["img_src_rewritten"] += 1
                    return mm.group(1) + posixpath.relpath(t, posixpath.dirname(cur)) + mm.group(3)
                parts[i] = IMGSRC.sub(img, s)
            b = "".join(parts)
        out.append(b + cr)
    return "\n".join(out)


changed_files = 0
if REWRITE:
    for p in md_files():
        rel = str(p.relative_to(OUT)).replace("\\", "/")
        src = (CONTENT / rel).read_bytes().decode("utf-8")
        new = rewrite_text(rel, src)
        if new != src:
            changed_files += 1
            p.write_bytes(new.encode("utf-8"))

# ------------------------------------------------------------------ config files
(OUT / "SUMMARY.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
# ------------------------------------------------------------------ homepage (README.md)
# react.dev's homepage is code (src/components/Layout/HomeContent.js), not content, so there
# is no page to copy. This rebuilds it from the same text and code examples, using only
# GitBook blocks: page layout front matter, buttons, columns, cards, images.
from html import escape as _esc

LOGO = ROOT / "docusaurus" / "static" / "img" / "logo.svg"
(OUT / "assets").mkdir(exist_ok=True)
shutil.copy2(LOGO, OUT / "assets" / "react-logo.svg")


def _button(label, href, kind="primary"):
    return f'<a href="{href}" class="button {kind}">{label}</a>'


def _section(title, before, code, after, cta=None):
    s = [f"## {title}", "", "{% columns %}", '{% column width="50%" %}', before, ""]
    if after:
        s += [after, ""]
    if cta:
        s += [_button(*cta, kind="secondary"), ""]
    s += ["{% endcolumn %}", "", "{% column %}", "```jsx", code.strip("\n"), "```", "{% endcolumn %}", "{% endcolumns %}", "", "***", ""]
    return "\n".join(s)


EX1 = """function Video({ video }) {
  return (
    <div>
      <Thumbnail video={video} />
      <a href={video.url}>
        <h3>{video.title}</h3>
        <p>{video.description}</p>
      </a>
      <LikeButton video={video} />
    </div>
  );
}"""
EX2 = """function VideoList({ videos, emptyHeading }) {
  const count = videos.length;
  let heading = emptyHeading;
  if (count > 0) {
    const noun = count > 1 ? 'Videos' : 'Video';
    heading = count + ' ' + noun;
  }
  return (
    <section>
      <h2>{heading}</h2>
      {videos.map(video =>
        <Video key={video.id} video={video} />
      )}
    </section>
  );
}"""
EX3 = """import { useState } from 'react';

function SearchableVideoList({ videos }) {
  const [searchText, setSearchText] = useState('');
  const foundVideos = filterVideos(videos, searchText);
  return (
    <>
      <SearchInput
        value={searchText}
        onChange={newText => setSearchText(newText)} />
      <VideoList
        videos={foundVideos}
        emptyHeading={`No matches for “${searchText}”`} />
    </>
  );
}"""
EX4 = """import { db } from './database.js';
import { Suspense } from 'react';

async function ConferencePage({ slug }) {
  const conf = await db.Confs.find({ slug });
  return (
    <ConferenceLayout conf={conf}>
      <Suspense fallback={<TalksLoading />}>
        <Talks confId={conf.id} />
      </Suspense>
    </ConferenceLayout>
  );
}

async function Talks({ confId }) {
  const talks = await db.Talks.findAll({ confId });
  const videos = talks.map(talk => talk.video);
  return <SearchableVideoList videos={videos} />;
}"""

COMMUNITY = [
    ("react_conf_fun.webp", "People singing karaoke at React Conf"),
    ("react_india_sunil.webp", "Sunil Pai speaking at React India"),
    ("react_conf_hallway.webp", "A hallway conversation between two people at React Conf"),
    ("react_india_hallway.webp", "A hallway conversation at React India"),
    ("react_conf_elizabet.webp", "Elizabet Oliveira speaking at React Conf"),
    ("react_india_selfie.webp", "People taking a group selfie at React India"),
    ("react_conf_nat.webp", "Nat Alison speaking at React Conf"),
    ("react_india_team.webp", "Organizers greeting attendees at React India"),
]

# Latest four posts, the same list react.dev's homepage takes from the blog sidebar
_blog = json.loads((SIDEBARS / "sidebarBlog.json").read_text(encoding="utf-8"))
_posts = []
for r in _blog["routes"]:
    for p in r.get("routes", []):
        f = md_for(p.get("path", ""))
        if f and len(_posts) < 4:
            _posts.append((p.get("titleForHomepage") or p["title"], p.get("date", ""), f))

news_rows = "\n".join(
    f"    <tr><td><strong>{_esc(t)}</strong></td><td>{_esc(d)}</td>"
    f'<td><a href="{f}">{f}</a></td></tr>'
    for t, d, f in _posts
)
gallery_rows = "\n".join(
    f'    <tr><td>{_esc(alt)}</td><td><a href="images/home/community/{img}">{img}</a></td></tr>'
    for img, alt in COMMUNITY
)

HOME = f"""---
description: The library for web and native user interfaces
layout:
  width: wide
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: false
  pagination:
    visible: true
---

# React

<div align="center"><figure><img src="assets/react-logo.svg" alt="React logo" width="160"><figcaption></figcaption></figure></div>

<p align="center">{_button("Learn React", "learn/index.md")} {_button("API Reference", "reference/react/index.md", "secondary")}</p>

***

{_section("Create user interfaces from components",
 "React lets you build user interfaces out of individual pieces called components. Create your own React components like `Thumbnail`, `LikeButton`, and `Video`. Then combine them into entire screens, pages, and apps.",
 EX1,
 "Whether you work on your own or with thousands of other developers, using React feels the same. It is designed to let you seamlessly combine components written by independent people, teams, and organizations.")}
{_section("Write components with code and markup",
 "React components are JavaScript functions. Want to show some content conditionally? Use an `if` statement. Displaying a list? Try array `map()`. Learning React is learning programming.",
 EX2,
 "This markup syntax is called JSX. It is a JavaScript syntax extension popularized by React. Putting JSX markup close to related rendering logic makes React components easy to create, maintain, and delete.")}
{_section("Add interactivity wherever you need it",
 "React components receive data and return what should appear on the screen. You can pass them new data in response to an interaction, like when the user types into an input. React will then update the screen to match the new data.",
 EX3,
 "You don’t have to build your whole page in React. Add React to your existing HTML page, and render interactive React components anywhere on it.",
 ("Add React to your page", "learn/add-react-to-an-existing-project.md"))}
{_section("Go full-stack with a framework",
 "React is a library. It lets you put components together, but it doesn’t prescribe how to do routing and data fetching. To build an entire app with React, we recommend a full-stack React framework like [Next.js](https://nextjs.org) or [React Router](https://reactrouter.com).",
 EX4,
 "React is also an architecture. Frameworks that implement it let you fetch data in asynchronous components that run on the server or even during the build. Read data from a file or a database, and pass it down to your interactive components.",
 ("Get started with a framework", "learn/creating-a-react-app.md"))}
## Use the best from every platform

People love web and native apps for different reasons. React lets you build both web apps and native apps using the same skills. It leans upon each platform’s unique strengths to let your interfaces feel just right on every platform.

{{% columns %}}
{{% column %}}
### Stay true to the web

People expect web app pages to load fast. On the server, React lets you start streaming HTML while you’re still fetching data, progressively filling in the remaining content before any JavaScript code loads. On the client, React can use standard web APIs to keep your UI responsive even in the middle of rendering.
{{% endcolumn %}}

{{% column %}}
### Go truly native

People expect native apps to look and feel like their platform. [React Native](https://reactnative.dev) and [Expo](https://github.com/expo/expo) let you build apps in React for Android, iOS, and more. They look and feel native because their UIs _are_ truly native. It’s not a web view—your React components render real Android and iOS views provided by the platform.
{{% endcolumn %}}
{{% endcolumns %}}

With React, you can be a web _and_ a native developer. Your team can ship to many platforms without sacrificing the user experience. Your organization can bridge the platform silos, and form teams that own entire features end-to-end.

{_button("Build for native platforms", "https://reactnative.dev/", "secondary")}

***

## Upgrade when the future is ready

React approaches changes with care. Every React commit is tested on business-critical surfaces with over a billion users. Over 100,000 React components at Meta help validate every migration strategy.

The React team is always researching how to improve React. Some research takes years to pay off. React has a high bar for taking a research idea into production. Only proven approaches become a part of React.

#### Latest React news

<table data-view="cards">
  <thead>
    <tr><th></th><th></th><th data-hidden data-card-target data-type="content-ref"></th></tr>
  </thead>
  <tbody>
{news_rows}
  </tbody>
</table>

{_button("Read more React news", "blog/index.md", "secondary")}

***

## Join a community of millions

You’re not alone. Two million developers from all over the world visit the React docs every month. React is something that people and teams can agree on.

<table data-view="cards">
  <thead>
    <tr><th></th><th data-hidden data-card-cover data-type="files"></th></tr>
  </thead>
  <tbody>
{gallery_rows}
  </tbody>
</table>

This is why React is more than a library, an architecture, or even an ecosystem. React is a community. It’s a place where you can ask for help, find opportunities, and meet new friends. You will meet both developers and designers, beginners and experts, researchers and artists, teachers and students. Our backgrounds may be very different, but React lets us all create user interfaces together.

***

<h2 align="center">Welcome to the React community</h2>

<p align="center">{_button("Get Started", "learn/index.md")}</p>
"""
(OUT / "README.md").write_bytes(HOME.encode("utf-8"))

# GitBook owns this file once synced (it commits title edits back to GitHub), so only create it if missing.
if not (ROOT / "gitbook-docs.yaml").exists():
    (ROOT / "gitbook-docs.yaml").write_bytes(
        (
            "$schema: https://api.gitbook.com/gitbook-docs.yaml\n"
            "site:\n"
            "  title: React Docs\n"
            "  structure:\n"
            "    - type: section\n"
            "      key: react-docs\n"
            "      title: React Docs\n"
            "      path: react-docs\n"
            "      default: true\n"
            "      children:\n"
            "        - type: space\n"
            "          key: react\n"
            "          title: React\n"
            "          path: react\n"
            "          default: true\n"
            "          content:\n"
            "            directory: ./gitbook\n"
            "            language: en\n"
        ).encode("utf-8")
    )
(ROOT / ".gitbook.yaml").unlink(missing_ok=True)

ga = ROOT / ".gitattributes"
text = ga.read_text(encoding="utf-8") if ga.exists() else ""
if "gitbook/** -text" not in text:
    if text and not text.endswith("\n"):
        text += "\n"
    ga.write_bytes((text + "gitbook/** -text\n").encode("utf-8"))


# ------------------------------------------------------------------ verification
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


bad = 0
for f in used:
    if not (OUT / f).is_file():
        print("MISSING in gitbook/:", f)
        bad += 1
for p in IMAGES.rglob("*"):
    if p.is_file() and sha(p) != sha(OUT / "images" / p.relative_to(IMAGES)):
        print("IMAGE DIFFERS:", p)
        bad += 1

# every internal link / anchor in the generated files
broken_links, broken_anchors = [], []
heading_markers_left = 0
for p in md_files():
    rel = str(p.relative_to(OUT)).replace("\\", "/")
    for _, b, fenced in body_lines(p.read_text(encoding="utf-8")):
        if fenced:
            continue
        if REWRITE and HEADING.match(b) and "{/*" in b:
            heading_markers_left += 1
        for part in CODESPAN.split(b)[::2]:
            for m in LINK.finditer(part):
                url = m.group(2)
                if re.match(r"(https?:|mailto:|//)", url) or not url:
                    continue
                path, _, anchor = url.partition("#")
                if path == "":
                    tgt = rel
                else:
                    tgt = posixpath.normpath(posixpath.join(posixpath.dirname(rel), path))
                if tgt not in all_files:
                    broken_links.append((rel, url))
                elif anchor and tgt.endswith(".md") and anchor not in slugs.get(tgt, set()):
                    broken_anchors.append((rel, url))

content_md = sum(1 for _ in CONTENT.rglob("*.md")) - 1
print(f"SUMMARY entries: {len(used)} | md pages in gitbook/: {len(md_files())} (content has {content_md}) | images: {sum(1 for _ in (OUT / 'images').rglob('*') if _.is_file())}")
if REWRITE:
    print(f"Rewrite: {changed_files} files changed | headings cleaned: {stats['heading_id_stripped']} | links rewritten: {stats['link_rewritten']} | anchors remapped: {stats['anchor_remapped']} | img src rewritten: {stats['img_src_rewritten']}")
    print(f"Links that point at nothing in content/ (left as written): {stats['link_unresolved']}")
    print(f"After rewrite: broken links {len(broken_links)} on {len({r for r, _ in broken_links})} pages | broken anchors {len(broken_anchors)} on {len({r for r, _ in broken_anchors})} pages | heading markers left {heading_markers_left}")
else:
    print("Plain byte-identical copy (no rewrite).")
print("Left out of SUMMARY (no file / duplicate):")
for s in skipped:
    print("  ", s)
if "--details" in sys.argv:
    for name, lst in (("UNRESOLVED", unresolved), ("BROKEN LINK", broken_links), ("BROKEN ANCHOR", broken_anchors)):
        for r, u in sorted(set(lst)):
            print(f"  {name}: {r} -> {u}")
print("Skipped content/index.md (stub: 'See HomeContent.js'); README.md is the landing page.")
print("OK" if not bad else f"{bad} PROBLEMS")
sys.exit(1 if bad else 0)
