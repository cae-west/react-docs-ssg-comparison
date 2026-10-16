#!/usr/bin/env python3
"""Build the GitBook source folder (gitbook/) from content/, public/images/ and sidebars/.

Run from the repo root:   python gitbook/build.py

Nothing in content/ is edited. Files are copied byte-for-byte into gitbook/ using
the same folder layout as react.dev URLs, so '../images/...' links resolve.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
IMAGES = ROOT / "public" / "images"
SIDEBARS = ROOT / "sidebars"
OUT = ROOT / "gitbook"
VERSION = "19.3"  # react.dev fills {{version}} in sidebar headers

# Sidebars in reading order. Home is a shortcut list of the others, so it is skipped.
AREAS = ["Learn", "Reference", "Community", "Blog"]
COPY_DIRS = ["blog", "community", "errors", "learn", "reference", "warnings"]


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
            emit(r.get("routes", []), depth)  # keep any children, one level up
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

# Pages that exist in content/ but are not in any sidebar (react.dev reaches them by link only).
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
    if not title:  # no front matter (the three errors/ pages)
        title = "Errors: " + Path(f).stem
    lines.append("* [" + label(title) + "](" + f + ")")
    used.add(f)

# Clean only the folders this script creates, then copy.
for d in COPY_DIRS + ["images"]:
    shutil.rmtree(OUT / d, ignore_errors=True)
for d in COPY_DIRS:
    shutil.copytree(CONTENT / d, OUT / d)
shutil.copy2(CONTENT / "versions.md", OUT / "versions.md")
shutil.copytree(IMAGES, OUT / "images")

(OUT / "SUMMARY.md").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
(OUT / "README.md").write_bytes(
    (
        "# React\n\n"
        "The React documentation, rebuilt in GitBook from the unmodified react.dev content.\n"
        "Use the sidebar to browse Learn, Reference, Community and Blog.\n"
    ).encode("utf-8")
)
# GitBook site-level Git Sync config: one space whose content is the gitbook/ folder.
# (GitBook reads README.md and SUMMARY.md from that folder by default, so no .gitbook.yaml is needed.)
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
(ROOT / ".gitbook.yaml").unlink(missing_ok=True)  # old v1 config, no longer used

# .gitattributes: keep line endings untouched in the copy (same as content/ and public/)
ga = ROOT / ".gitattributes"
text = ga.read_text(encoding="utf-8") if ga.exists() else ""
if "gitbook/** -text" not in text:
    if text and not text.endswith("\n"):
        text += "\n"
    ga.write_bytes((text + "gitbook/** -text\n").encode("utf-8"))

# ---- verification ----
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


bad = 0
for f in used:
    if not (OUT / f).is_file():
        print("MISSING in gitbook/:", f)
        bad += 1
copied = 0
for p in CONTENT.rglob("*"):
    if p.is_file() and p != CONTENT / "index.md":
        rel = p.relative_to(CONTENT)
        if sha(p) != sha(OUT / rel):
            print("DIFFERS from content/:", rel)
            bad += 1
        copied += 1
nimg = sum(1 for _ in (OUT / "images").rglob("*") if _.is_file())
for p in IMAGES.rglob("*"):
    if p.is_file() and sha(p) != sha(OUT / "images" / p.relative_to(IMAGES)):
        print("IMAGE DIFFERS:", p)
        bad += 1
print(f"SUMMARY entries: {len(used)} | content files copied: {copied} | images: {nimg}")
print("Left out of SUMMARY (no file / duplicate):")
for s in skipped:
    print("  ", s)
print("Skipped content/index.md (stub: 'See HomeContent.js'); README.md is the landing page.")
print("OK" if not bad else f"{bad} PROBLEMS")
sys.exit(1 if bad else 0)
