#!/usr/bin/env python3
"""Content-address the published CSS, JS and fonts so a page and its stylesheet
can never come from two different builds.

    python3 tools/version-assets.py           # stamp every page
    python3 tools/version-assets.py --check   # report, change nothing (CI)

Why this exists: the site is copied straight to GitHub Pages and every file is
cached on its own. A deploy that lands while a browser or a CDN edge still holds
the previous /assets/site.css serves new markup against an old stylesheet - which
is how a whole page can look "messed up" (unstyled demo, gallery stacked full
width, labels glued to their text) while every file in the repo is correct.

The fix is a version in the URL: each reference becomes
/assets/site.css?v=<first 10 hex of the file's sha256>, so a new build is a new
URL and a stale cache can never be used by accident. tools/check-site.py repeats
the same computation and fails the run when a page carries any other stamp, so
forgetting to run this script is caught in CI instead of in a screenshot.

Font files get the same treatment, since they are referenced from inside the CSS.
Order matters and is fixed here: fonts first, then the stylesheet hash - and both
steps are idempotent, so running it twice changes nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LENGTH = 10
FONT_URL = re.compile(r'url\("(/assets/fonts/[^"?]+\.woff2)(?:\?v=[0-9a-f]{%d})?"\)' % LENGTH)
STYLESHEET = re.compile(r'(<link rel="stylesheet" href=")(/assets/site\.css)(\?v=[0-9a-f]{%d})?("[^>]*>)' % LENGTH)
SCRIPT = re.compile(r'(<script src=")(/assets/site\.js)(\?v=[0-9a-f]{%d})?(" defer>)' % LENGTH)


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:LENGTH]


def pages() -> list[pathlib.Path]:
    out = []
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(("_site/", ".git/")):
            continue
        out.append(f)
    return out


def stamped_css(css: str) -> tuple[str, list[str]]:
    """Append each font's own hash to its url() inside site.css."""
    problems: list[str] = []

    def repl(match: re.Match) -> str:
        target = ROOT / match.group(1).lstrip("/")
        if not target.exists():
            problems.append("site.css points at a font that has no file: %s" % match.group(1))
            return match.group(0)
        return 'url("%s?v=%s")' % (match.group(1), digest(target))

    return FONT_URL.sub(repl, css), problems


def stamp_page(html: str, versions: dict[str, str]) -> str:
    def by_path(match: re.Match) -> str:
        path = match.group(2).lstrip("/")
        version = versions.get(path)
        if version is None:
            return match.group(0)
        return "%s%s?v=%s%s" % (match.group(1), match.group(2), version, match.group(4))

    return SCRIPT.sub(by_path, STYLESHEET.sub(by_path, html))


def main() -> int:
    ap = argparse.ArgumentParser(description="Stamp /assets/site.css, site.js and the fonts with a content hash.")
    ap.add_argument("--check", action="store_true", help="exit non-zero if any page is not up to date")
    args = ap.parse_args()

    css_path = ROOT / "assets" / "site.css"
    js_path = ROOT / "assets" / "site.js"
    for path in (css_path, js_path):
        if not path.exists():
            print("missing %s" % path.relative_to(ROOT).as_posix())
            return 1

    css, problems = stamped_css(css_path.read_text())
    if problems:
        for line in problems:
            print("ERROR   " + line)
        return 1

    versions = {"assets/site.css": digest(css_path), "assets/site.js": digest(js_path)}
    if css_path.read_text() != css:
        versions["assets/site.css"] = digest_of_text(css)

    wanted: list[tuple[pathlib.Path, str]] = [(css_path, css)]
    for page in pages():
        wanted.append((page, stamp_page(page.read_text(), versions)))

    if args.check:
        stale = [p.relative_to(ROOT).as_posix() for p, text in wanted if p.read_text() != text]
        if stale:
            for rel in stale:
                print("STALE   %s does not carry the current asset build" % rel)
            print("run: python3 tools/version-assets.py")
            return 1
        print("assets stamped at css %s / js %s" % (versions["assets/site.css"], versions["assets/site.js"]))
        return 0

    changed = 0
    for path, text in wanted:
        if path.read_text() != text:
            path.write_text(text)
            changed += 1
            print("stamped %s" % path.relative_to(ROOT).as_posix())
    print("css %s  js %s" % (versions["assets/site.css"], versions["assets/site.js"]))
    if not changed:
        print("already up to date")
    return 0


def digest_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:LENGTH]


if __name__ == "__main__":
    sys.exit(main())
