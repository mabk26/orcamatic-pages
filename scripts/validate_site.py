#!/usr/bin/env python3
"""Validate the static website using only Python's standard library (no network)."""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        for name in ("href", "src", "poster"):
            if attributes.get(name):
                self.references.append(attributes[name])

    handle_startendtag = handle_starttag


def validate_site(root):
    root = root.resolve()
    errors = []
    required = (
        "index.html", "404.html", ".nojekyll", "CNAME", "assets/site.css",
        "assets/site.js", "site.webmanifest", "robots.txt", "sitemap.xml",
    )
    for name in required:
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    if errors:
        return errors, 0, 0

    domain = (root / "CNAME").read_text(encoding="utf-8").strip()
    if domain != "orcamatic.com":
        return ["CNAME must contain only orcamatic.com"], 0, 0
    origin = f"https://{domain}/"
    documents = {
        path: Document(path.read_text(encoding="utf-8"))
        for path in sorted(root.rglob("*.html"))
    }
    checked = 0

    def check_reference(source, reference):
        nonlocal checked
        source_url = urljoin(origin, source.relative_to(root).as_posix())
        url = urlsplit(urljoin(source_url, reference))
        if url.scheme not in ("http", "https") or url.netloc != domain:
            return
        checked += 1
        target = (root / unquote(url.path).lstrip("/")).resolve()
        label = source.relative_to(root)
        if not target.is_relative_to(root):
            errors.append(f"{label}: URL escapes the site: {reference}")
            return
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            errors.append(f"{label}: missing local target: {reference}")
        elif url.fragment and target in documents:
            if unquote(url.fragment) not in documents[target].ids:
                errors.append(f"{label}: missing anchor: {reference}")

    for path, document in documents.items():
        for reference in document.references:
            check_reference(path, reference)

    for path in root.rglob("*.css"):
        for reference in re.findall(r"url\(\s*['\"]?([^'\"\s)]+)", path.read_text(encoding="utf-8")):
            check_reference(path, reference)

    manifest_path = root / "site.webmanifest"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        check_reference(manifest_path, manifest["start_url"])
        for icon in manifest["icons"]:
            check_reference(manifest_path, icon["src"])
    except (ValueError, KeyError, TypeError) as error:
        errors.append(f"Invalid site.webmanifest: {error}")

    sitemap_path = root / "sitemap.xml"
    try:
        sitemap = ET.parse(sitemap_path)
        locations = [item.text or "" for item in sitemap.findall("{*}url/{*}loc")]
        if not locations:
            errors.append("sitemap.xml contains no page URLs")
        for location in locations:
            if not location.startswith(origin):
                errors.append(f"Sitemap URL must use {origin}: {location}")
            else:
                check_reference(sitemap_path, location)
        for path in documents:
            relative = path.relative_to(root).as_posix()
            if relative == "404.html":
                continue
            route = relative.removesuffix("index.html")
            if urljoin(origin, route) not in locations:
                errors.append(f"Page missing from sitemap.xml: {relative}")
    except ET.ParseError as error:
        errors.append(f"Invalid sitemap.xml: {error}")

    robots = (root / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {origin}sitemap.xml" not in robots:
        errors.append("robots.txt must advertise the production sitemap")

    return errors, len(documents), checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-root", type=Path,
        default=Path(__file__).resolve().parents[1] / "git_page_wa",
    )
    args = parser.parse_args()
    errors, pages, references = validate_site(args.site_root)
    if errors:
        print("Site validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(
        f"Validated {pages} HTML pages and {references} local references, "
        "including assets, anchors, manifest and sitemap."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
