#!/usr/bin/env python3
"""Static-site checks for the Orcamatic pages. stdlib only, no build step.

    python3 tools/check-site.py            # errors fail the run
    python3 tools/check-site.py --strict   # advisories fail too
    python3 tools/check-site.py --verbose  # list every page that passed a check

Why this exists: the site is plain HTML copied straight to GitHub Pages, so nothing
stands between a typo and a broken page in production. These are the checks that
matter for this repo specifically - the CSP in each page's <meta> blocks inline
styles and inline scripts, product imagery is hot-linked from the store CDN,
every page carries its own duplicated head tags that have to stay in sync, and
/assets/site.css is cached independently of the HTML, so it has to be versioned.

The image checks exist because two specific mistakes were made here and are easy to
make again: asking the store CDN for a fixed -w1280-h800 box (it crops, so a tile
whose real ratio differs loses its caption or its button labels) and displaying a
1280px-wide tile in a slot a fraction of that size (the type inside the screenshot
ends up a few pixels tall). Both read as "the images are squashed".
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
REQUIRED_HEAD = {
    "charset": re.compile(r'<meta charset="utf-8"', re.I),
    "viewport": re.compile(r'<meta name="viewport"'),
    "description": re.compile(r'<meta name="description" content=".+?"'),
    "canonical": re.compile(r'<link rel="canonical" href="https://orcamatic\.com/'),
    "csp": re.compile(r'<meta http-equiv="Content-Security-Policy"'),
    "stylesheet": re.compile(r'<link rel="stylesheet" href="/assets/site\.css(\?v=[0-9a-f]{10})?">'),
    "title": re.compile(r'<title>[^<]{18,70}</title>'),
    "og:image": re.compile(r'<meta property="og:image" content="https://orcamatic\.com/assets/og-image\.jpg">'),
}


ASSET_LENGTH = 10


def digest(path: pathlib.Path) -> str:
    """The stamp tools/version-assets.py writes: the first 10 hex of the file's sha256.

    Duplicated rather than imported on purpose - both tools have to run from a plain
    checkout with nothing installed, and a shared module would be a third file to keep
    in step. If you change one, change the other.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()[:ASSET_LENGTH]


def check_asset_versions(files: list[pathlib.Path]) -> list[str]:
    """An HTML/CSS mismatch is invisible in the source and obvious on the page.

    Every file is cached on its own URL, so a deploy that lands while an edge or a
    browser still holds the previous site.css paints new markup with old rules. A
    ?v=<hash> on the reference makes the new build a new URL, which is the only
    defence a static host has. These three checks keep the stamp honest.
    """
    problems: list[str] = []
    versions = {}
    for name in ("assets/site.css", "assets/site.js"):
        path = ROOT / name
        if not path.exists():
            problems.append("%s is missing" % name)
            continue
        versions[name] = digest(path)

    css = (ROOT / "assets" / "site.css").read_text() if (ROOT / "assets" / "site.css").exists() else ""
    for match in re.finditer(r'url\("(/assets/[^"]+?)(\?v=[0-9a-f]{%d})?"\)' % ASSET_LENGTH, css):
        if not match.group(2):
            problems.append("assets/site.css: %s has no ?v= stamp (run tools/version-assets.py)" % match.group(1))
        elif not (ROOT / match.group(1).lstrip("/")).exists():
            problems.append("assets/site.css: %s has no file behind it" % match.group(1))

    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        html = f.read_text()
        for pattern, key in ((r'<link rel="stylesheet" href="/assets/site\.css', "assets/site.css"),
                             (r'<script src="/assets/site\.js', "assets/site.js")):
            if key not in versions:
                continue
            want = versions[key]
            found = re.search(pattern + r'(\?v=([0-9a-f]+))?"', html)
            if not found:
                problems.append("%s: no versioned reference to %s to check" % (rel, key))
            elif found.group(2) != want:
                problems.append("%s: %s is stamped %s, the file is %s - run tools/version-assets.py"
                                % (rel, key, found.group(2) or "nothing", want))
    return problems


def pages() -> list[pathlib.Path]:
    out = []
    for f in sorted(ROOT.rglob("*.html")):
        rel = f.relative_to(ROOT).as_posix()
        if rel.startswith(("_site/", ".git/")) or "/Unselected files/" in rel:
            continue
        out.append(f)
    return out


class Checker(HTMLParser):
    """Tag balance plus the handful of things only a parser can see."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.h1 = 0
        self.classes: set[str] = set()
        self.inline_style = 0
        self.handlers = 0
        self.links: list[str] = []
        self.assets: list[str] = []
        self.remote_imgs: list[str] = []
        self.imgs: list[dict] = []
        self.preload_imgs: list[str] = []
        self.in_ldjson = False
        self.ldjson: list[str] = []
        self.inline_scripts: list[str] = []
        self.inline_styles = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == "h1":
            self.h1 += 1
        if tag == "script":
            if a.get("type") == "application/ld+json":
                self.in_ldjson = True
                self.ldjson.append("")
            elif not a.get("src"):
                self.inline_scripts.append("line %d" % self.getpos()[0])
        if tag == "style":
            self.inline_styles += 1
        style = a.get("style")
        if style is not None:
            self.inline_style += 1
        for name, value in attrs:
            if name.startswith("on") and value:
                self.handlers += 1
        for cls in (a.get("class") or "").split():
            self.classes.add(cls)
        href = a.get("href")
        if href:
            self.links.append(href)
        src = a.get("src")
        if src:
            self.assets.append(src)
        if tag == "img":
            src = src or ""
            self.imgs.append({"src": src, "width": a.get("width") or "", "height": a.get("height") or "",
                             "alt": a.get("alt")})
            if src.startswith("https://lh3.googleusercontent.com"):
                self.remote_imgs.append(src)
        if tag == "link" and a.get("rel") == "preload" and a.get("as") == "image" and a.get("href"):
            self.preload_imgs.append(a["href"])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
            if tag == "script":
                self.in_ldjson = False
        elif tag in self.stack:
            self.errors.append("unexpected </%s> (open: %s)" % (tag, ">".join(self.stack[-3:])))
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            self.stack.pop()
            if tag == "script":
                self.in_ldjson = False
        else:
            self.errors.append("stray </%s>" % tag)

    def handle_data(self, data):
        if self.in_ldjson and self.ldjson:
            self.ldjson[-1] += data


def check_page(rel: str, html: str, parsed: Checker, defined_classes: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    real_open = [t for t in parsed.stack if t not in ("html", "body")]
    if real_open:
        errors.append("unclosed tags: " + ", ".join(real_open[-4:]))
    if parsed.errors:
        errors.extend(parsed.errors[:6])

    if parsed.h1 != 1:
        errors.append("expected exactly one <h1>, found %d" % parsed.h1)
    if parsed.inline_style:
        errors.append("%d inline style attribute(s): the CSP (style-src 'self') blocks them at runtime"
                      % parsed.inline_style)
    if parsed.handlers:
        errors.append("%d inline event handler(s) (on*=): blocked by script-src 'self'" % parsed.handlers)

    if parsed.inline_scripts:
        errors.append("inline <script> at %s: script-src 'self' blocks it (only application/ld+json is allowed)"
                      % ", ".join(parsed.inline_scripts[:3]))
    if parsed.inline_styles:
        errors.append("%d inline <style> block(s): style-src 'self' blocks them" % parsed.inline_styles)

    # A 404 is never indexed, so it legitimately skips canonical/description/OG.
    skip = {"canonical", "description", "og:image"} if rel == "404.html" else set()
    for name, pat in REQUIRED_HEAD.items():
        if name in skip:
            continue
        if not pat.search(html):
            errors.append("head is missing %s" % name)
    if rel == "404.html" and 'name="robots" content="noindex"' not in html:
        errors.append("404.html should carry <meta name=\"robots\" content=\"noindex\">")

    desc = re.search(r'<meta name="description" content="(.*?)"', html)
    if desc and len(desc.group(1)) > 165:
        warnings.append("meta description is %d chars; keep it under 165 so it is not truncated" % len(desc.group(1)))
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    if title and len(title.group(1)) > 62:
        warnings.append("title is %d chars; search results truncate near 60" % len(title.group(1)))

    canonical = re.search(r'<link rel="canonical" href="https://orcamatic\.com(/[^"]*)"', html)
    if canonical:
        want = "/" if rel == "index.html" else "/" + rel[: -len("index.html")]
        got = canonical.group(1)
        if rel == "index.html":
            got_root = got.rstrip("/") == ""
            if not got_root:
                errors.append("canonical %s should be https://orcamatic.com/" % got)
        elif not got.startswith(want):
            errors.append("canonical %s does not match the page path %s" % (got, want))

    undefined = sorted(c for c in parsed.classes if c not in defined_classes)
    if undefined:
        errors.append("classes with no rule in assets/site.css: " + ", ".join(undefined[:8]))

    for href in parsed.links:
        if href.startswith(("mailto:", "tel:", "#", "http://", "https://", "data:")):
            continue
        if not href.startswith("/"):
            errors.append("root-relative URLs only, found %s" % href)
            continue
        target = ROOT / href.lstrip("/").split("#")[0].split("?")[0]
        if not (target.exists() or (target / "index.html").exists()):
            errors.append("internal link has no file: %s" % href)
    for src in parsed.assets:
        if src.startswith(("http://", "https://", "data:")):
            continue
        if not (ROOT / src.lstrip("/").split("?")[0]).exists():
            errors.append("local asset missing: %s" % src)

    # Store images are hot-linked, so a missing request is a visible hole in the
    # page; and a URL that asks for a fixed box makes the CDN crop the tile.
    for img in parsed.imgs:
        if not img["src"]:
            errors.append("<img> with no src")
            continue
        if not (img["width"] and img["height"]):
            errors.append("<img> without width and height attributes paints over the "
                          "layout while it loads: %s" % img["src"][-46:])
        if img["alt"] is None:
            errors.append("<img> with no alt attribute at all: %s" % img["src"][-46:])
    for src in parsed.remote_imgs:
        suffix = src.split("=")[-1] if "=" in src.split("/")[-1] else ""
        if re.search(r"-w\d+-h\d+", suffix):
            errors.append("store image asks the CDN for a fixed box (=…-w1280-h800), which crops "
                          "the tile to that ratio: %s" % src[-40:])
        elif not re.search(r"^w\d{3,4}$", suffix):
            errors.append("store image should ask for one width (=w<N>, the width it displays at x2): "
                          "%s" % src[-40:])
    for href in parsed.preload_imgs:
        if href not in {img["src"] for img in parsed.imgs}:
            errors.append("preloaded image is not used by an <img> on this page, so it is "
                          "downloaded twice or wasted: %s" % href[-40:])

    # A single-figure picture (class="shot": the hero, the product page) has to carry
    # its own fallback note; a dead hot-link would otherwise leave a broken icon where
    # the visual should be. Gallery tiles (.shots figure) are dropped by CSS instead.
    for match in re.finditer(r'<figure[^>]*class="shot"[^>]*>([\s\S]*?)</figure>', html):
        if "shot-fallback" not in match.group(1):
            errors.append("figure.shot has no <p class=\"shot-fallback\"> to fall back on")
        if "shot-frame" not in match.group(1):
            errors.append("figure.shot has no .shot-frame, so nothing reserves its box")

    import json
    for blob in parsed.ldjson:
        blob = blob.strip()
        if not blob:
            errors.append("empty application/ld+json block")
            continue
        try:
            data = json.loads(blob)
        except ValueError as exc:
            errors.append("structured data is not valid JSON: %s" % exc)
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict) or "@context" not in item or "@type" not in item:
                errors.append("structured data needs @context and @type")

    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Check the Orcamatic static site for the mistakes this repo can actually make.")
    ap.add_argument("--strict", action="store_true", help="treat advisories as failures")
    ap.add_argument("--verbose", action="store_true", help="print clean pages too")
    args = ap.parse_args()

    css = (ROOT / "assets" / "site.css").read_text()
    defined_classes = set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", css))
    if css.count("{") != css.count("}"):
        print("assets/site.css: brace mismatch (%d open, %d close)" % (css.count("{"), css.count("}")))
        return 1

    files = pages()
    version_problems = check_asset_versions(files)
    all_errors: list[str] = list(version_problems)
    all_warnings: list[str] = []
    clean = 0

    for f in files:
        rel = f.relative_to(ROOT).as_posix()
        html = f.read_text()
        parsed = Checker()
        parsed.feed(html)
        parsed.close()
        errors, warnings = check_page(rel, html, parsed, defined_classes)
        all_errors += ["%s: %s" % (rel, e) for e in errors]
        all_warnings += ["%s: %s" % (rel, w) for w in warnings]
        if not errors and not warnings:
            clean += 1
        elif args.verbose:
            print("clean: %s" % rel)

    # Sitemap: every published page should be listed exactly once, 404 excluded.
    sm = ROOT / "sitemap.xml"
    if sm.exists():
        xml = sm.read_text()
        locs = re.findall(r"<loc>(.*?)</loc>", xml)
        if len(locs) != len(set(locs)):
            all_errors.append("sitemap.xml: duplicate <loc> entries")
        listed = {l.replace("https://orcamatic.com", "") or "/" for l in locs}
        for f in files:
            rel = f.relative_to(ROOT).as_posix()
            if rel == "404.html":
                continue
            want = "/" if rel == "index.html" else "/" + rel[: -len("index.html")]
            if want not in listed:
                all_errors.append("sitemap.xml: missing %s" % want)
        for l in listed:
            target = ROOT / l.lstrip("/")
            if not (target.exists() or (target / "index.html").exists()):
                all_errors.append("sitemap.xml: %s has no file behind it" % l)
    else:
        all_errors.append("sitemap.xml is missing")

    robots = (ROOT / "robots.txt").read_text() if (ROOT / "robots.txt").exists() else ""
    if robots and "sitemap.xml" not in robots:
        all_warnings.append("robots.txt: add a Sitemap: https://orcamatic.com/sitemap.xml line")

    print("%d pages checked, %d clean" % (len(files), clean))
    for line in dict.fromkeys(all_errors):
        print("ERROR   " + line)
    for line in dict.fromkeys(all_warnings):
        print("ADVISORY " + line)
    if all_errors or (args.strict and all_warnings):
        print("failed: %d error(s), %d advisory" % (len(set(all_errors)), len(set(all_warnings))))
        return 1
    print("passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
