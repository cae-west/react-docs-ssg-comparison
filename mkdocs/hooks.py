"""
MkDocs hooks that let MkDocs Material display the UNMODIFIED react.dev content.

The content files are never edited. Everything here runs in memory while MkDocs
builds, the same way Docusaurus's theme components and remark plugin do.

Why this is needed: react.dev's pages are MDX (Markdown + React components),
but MkDocs reads plain Markdown (Python-Markdown). Without this file:
  - tags like <Sandpack> and <Note> are treated as raw HTML, so the code blocks
    inside them are not rendered and JSX in the code is swallowed by the browser
  - heading ids written as {/*usage*/} show up as text
  - images and fonts outside ../content are never copied into the site
  - the navigation is alphabetical instead of following React's sidebars
"""
import html
import json
import os
import posixpath
import re
import shutil

from mkdocs.structure.files import File

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
CONTENT = os.path.join(ROOT, "content")
SIDEBARS = os.path.join(ROOT, "sidebars")
IMAGES = os.path.join(ROOT, "public", "images")
VERSION = "19.3"  # react.dev fills {{version}} in sidebar headers from siteConfig.version


# ---------------------------------------------------------------- navigation
def _doc_for(route):
    """Map a react.dev URL like /learn/state to a file in content/."""
    rel = route.strip("/")
    if rel == "":
        return "index.md"
    for cand in (rel + ".md", rel + "/index.md"):
        if os.path.isfile(os.path.join(CONTENT, cand)):
            return cand.replace("\\", "/")
    return None


def _convert(routes, used):
    """Turn react.dev sidebar JSON into an MkDocs nav list."""
    out, section = [], None
    for node in routes:
        if node.get("hasSectionHeader"):
            # A section header ("GET STARTED") groups the items that follow it.
            section = []
            out.append({node["sectionHeader"].replace("{{version}}", VERSION): section})
            continue
        target = section if section is not None else out
        path = node.get("path", "")
        # Titles like "<textarea>" must be escaped: MkDocs inserts nav titles as raw HTML,
        # and an unescaped <textarea> swallows the rest of the page.
        title = html.escape(node["title"], quote=False)
        if path.startswith("http"):
            target.append({title: path})
            continue
        doc = _doc_for(path) if path else None
        children = node.get("routes") or []
        if children:
            items = []
            if doc and doc not in used:
                used.add(doc)
                items.append({"Overview" if not doc.endswith("index.md") else title: doc})
            items.extend(_convert(children, used))
            if items:
                target.append({title: items})
        elif doc and doc not in used:
            used.add(doc)
            target.append({title: doc})
    return out


def on_config(config):
    used = {"index.md"}
    nav = [{"Home": "index.md"}]
    for name, label in (("Learn", "Learn"), ("Reference", "Reference"),
                        ("Community", "Community"), ("Blog", "Blog")):
        with open(os.path.join(SIDEBARS, f"sidebar{name}.json"), encoding="utf-8") as f:
            data = json.load(f)
        nav.append({label: _convert(data["routes"], used)})
    config["nav"] = nav
    return config


# ------------------------------------------------- images live in ../public
def on_files(files, config):
    """Add ../public/images to the build so images are copied and links validate."""
    for dirpath, _, names in os.walk(IMAGES):
        for name in names:
            src = os.path.relpath(os.path.join(dirpath, name), os.path.join(ROOT, "public"))
            files.append(File(src.replace("\\", "/"), os.path.join(ROOT, "public"),
                              config["site_dir"], config["use_directory_urls"]))
    return files


# ------------------------------------------------------- page conversion
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
HEADING_ID = re.compile(r"^(#{1,6}\s.*?)\s*\{/\*\s*([^*]+?)\s*\*/\}\s*$")
JSX_COMMENT = re.compile(r"\{/\*.*?\*/\}", re.S)
ATTR = re.compile(r'(\w+)=(?:"([^"]*)"|\{([^}]*)\})')

CALLOUTS = {
    "Note": ("rd-note", "Note"), "Pitfall": ("rd-pitfall", "Pitfall"),
    "Deprecated": ("rd-deprecated", "Deprecated"), "Wip": ("rd-pitfall", "Under Construction"),
    "Experimental": ("rd-note", "Experimental Feature"), "RSC": ("rd-blue", "React Server Components"),
}
CARDS = {"YouWillLearn": "You will learn", "Recap": "Recap", "LearnMore": "Learn more"}
WRAPPERS = {  # tag -> css class of a plain wrapper whose inside stays Markdown
    "Intro": "rd-intro", "Sandpack": "rd-sandpack", "SandpackRSC": "rd-sandpack",
    "SandpackWithHTMLOutput": "rd-sandpack", "Challenges": "rd-challenges",
    "Recipes": "rd-recipes", "DiagramGroup": "rd-diagrams", "IllustrationBlock": "rd-diagrams",
    "ConsoleBlock": "rd-console", "ConsoleBlockMulti": "rd-console", "ConsoleLogLine": "rd-console-line",
    "TeamMember": "rd-team", "BlogCard": "rd-blogcard", "FullWidth": "rd-plain", "CodeDiagram": "rd-plain",
    "TerminalBlock": "rd-terminal",
}
DROP = {"InlineToc", "YouTubeIframe", "ErrorDecoder", "LanguageList"}


def _attrs(tag_line):
    return {k: (v1 if v1 is not None and v1 != "" else v2) for k, v1, v2 in ATTR.findall(tag_line)}


def _site_prefix(page):
    """Relative path from this page's URL back to the site root."""
    depth = page.url.count("/") if page.url else 0
    return "../" * depth


def _md_prefix(page):
    """Relative path from this page's .md file back to the docs root."""
    depth = page.file.src_uri.count("/")
    return "../" * depth


def _fence(info):
    """`js src/App.js active {2}` -> `js title="src/App.js"` (MkDocs can't read MDX meta)."""
    tokens = re.sub(r"\{[^}]*\}", " ", info).split()
    if not tokens:
        return ""
    lang = tokens[0]
    title = next((t for t in tokens[1:] if re.search(r"[./]\w", t)), None)
    return f'{lang} title="{title}"' if title else lang


def _open_tag(name, line, page):
    a = _attrs(line)
    if name in CALLOUTS:
        cls, title = CALLOUTS[name]
        return f'<div class="rd-callout {cls}" markdown="1">\n<p class="rd-callout-title">{title}</p>\n'
    if name in CARDS:
        title = CARDS[name]
        return f'<div class="rd-card" markdown="1">\n<p class="rd-card-title">{title}</p>\n'
    if name == "DeepDive":
        return '<details class="rd-deepdive" markdown="1">\n<summary>Deep Dive</summary>\n'
    if name in ("Hint", "Solution"):
        label = "Show hint" if name == "Hint" else "Show solution"
        return f'<details class="rd-hint" markdown="1">\n<summary>{label}</summary>\n'
    if name in ("Diagram", "Illustration"):
        src = a.get("src") or f'/images/docs/diagrams/{a.get("name", "")}.png'
        alt = html.escape(a.get("alt", ""), quote=True)
        img = f'<img src="{_site_prefix(page)}{src.lstrip("/")}" alt="{alt}">'
        if line.rstrip().endswith("/>"):
            return f'<figure class="rd-figure">{img}</figure>\n'
        return f'<figure class="rd-figure" markdown="1">{img}\n<figcaption markdown="1">\n'
    if name in WRAPPERS:
        extra = ""
        if name == "Recipes" and a.get("titleText"):
            extra = f'\n<p class="rd-card-title">{html.escape(a["titleText"])}</p>\n'
        if name == "TeamMember" and a.get("name"):
            photo = a.get("photo", "")
            img = (f'<img class="rd-team-photo" src="{_site_prefix(page)}{photo.lstrip("/")}" alt="">'
                   if photo else "")
            extra = (f'\n{img}<p class="rd-card-title" id="{a.get("permalink", "")}">'
                     f'{html.escape(a["name"])}</p>\n<p>{html.escape(a.get("title", ""))}</p>\n')
        if name == "BlogCard" and a.get("title"):
            url = a.get("url", "")
            target = _md_link(url, page) or url
            extra = f'\n### [{a["title"]}]({target})\n\n*{a.get("date", "")}*\n'
        return f'<div class="{WRAPPERS[name]}" markdown="1">{extra}\n'
    return None


def _close_tag(name):
    if name in ("DeepDive", "Hint", "Solution"):
        return "</details>\n"
    if name == "Diagram":
        return "</figcaption>\n</figure>\n"
    return "</div>\n"


def _md_link(url, page):
    """/learn/state#x -> relative link to learn/state.md#x, so MkDocs can resolve it."""
    m = re.match(r"^(/[^)#\s]*)(#[^)\s]*)?$", url)
    if not m:
        return None
    doc = _doc_for(m.group(1))
    if not doc:
        return None
    rel = posixpath.relpath(doc, posixpath.dirname(page.file.src_uri) or ".")
    return rel + (m.group(2) or "")


def on_page_markdown(markdown, page, config, files):
    # Page titles such as "<textarea>" (front matter) are inserted as raw HTML by the
    # theme, and an unescaped <textarea> swallows the rest of the page.
    if page.file.src_uri == "index.md":
        # react.dev's homepage is code, not content (index.md only says "See HomeContent.js"),
        # so the homepage uses its own template. Must be set here: MkDocs picks the
        # template before on_page_context runs.
        page.meta["template"] = "home.html"
    meta_title = page.meta.get("title")
    if isinstance(meta_title, str) and "<" in meta_title:
        page.meta["title"] = html.escape(meta_title, quote=False)
    out, fence = [], None
    for line in markdown.splitlines():
        m = FENCE.match(line)
        if fence:
            if m and m.group(2).startswith(fence) and not m.group(3).strip():
                fence = None
            out.append(line)
            continue
        if m:  # opening code fence: keep the language and file name only
            fence = m.group(2)
            out.append(f"{m.group(1)}{fence}{_fence(m.group(3))}")
            continue

        stripped = line.strip()
        # Heading ids: ## Usage {/*usage*/}  ->  ## Usage { #usage }
        h = HEADING_ID.match(line)
        if h:
            out.append(f"{h.group(1)} {{ #{h.group(2)} }}")
            continue

        # A plain <div className="..."> that only opens on this line (e.g. the card list on
        # blog/index.md) wraps Markdown. Python-Markdown leaves everything inside a plain
        # HTML block unprocessed unless the block is marked markdown="1".
        if re.match(r'^<div className="[^"]*">$', stripped):
            out.append("\n" + stripped.replace("className=", 'markdown="1" class=') + "\n")
            continue

        tag = re.match(r"^<(/?)([A-Z]\w*)\b", stripped)
        if tag:
            closing, name = tag.group(1) == "/", tag.group(2)
            if name in DROP:
                continue
            if name == "Solution" and stripped.endswith("/>"):
                out.append('\n<hr class="rd-divider">\n')  # separator between recipes
                continue
            if name == "CodeStep":
                pass  # inline; handled below
            elif closing:
                out.append("\n" + _close_tag(name))
                continue
            else:
                opened = _open_tag(name, stripped, page)
                if opened is not None:
                    out.append("\n" + opened)
                    # a tag can carry its content on the same line, e.g. <Diagram ...>caption</Diagram>
                    rest = re.sub(r"^<[^>]*>", "", stripped, count=1) if not stripped.endswith("/>") else ""
                    close = re.search(rf"</{name}>\s*$", rest)
                    if rest.strip():
                        out.append(re.sub(rf"</{name}>\s*$", "", rest))
                    if close:
                        out.append("\n" + _close_tag(name))
                    continue

        # Inline pieces
        line = re.sub(r"<CodeStep[^>]*>(.*?)</CodeStep>", r'<mark class="rd-codestep">\1</mark>', line)
        line = JSX_COMMENT.sub("", line)
        # Raw HTML written for React: className -> class, /images/ -> relative to the page URL
        line = line.replace("className=", "class=")
        line = re.sub(r'src="/images/', f'src="{_site_prefix(page)}images/', line)
        # Images: /images/x and ../images/x -> relative to this file
        line = re.sub(r"\]\((?:\.\./)?/?images/", f"]({_md_prefix(page)}images/", line)
        # Site-absolute links -> relative .md links (works on any base URL)
        line = re.sub(r"\]\((/[^)\s]*)\)",
                      lambda mm: f"]({_md_link(mm.group(1), page) or mm.group(1)})", line)
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------- homepage stub title
def on_page_context(context, page, config, nav):
    if page.file.src_uri == "index.md":
        page.meta.setdefault("hide", ["navigation", "toc"])
    return context
