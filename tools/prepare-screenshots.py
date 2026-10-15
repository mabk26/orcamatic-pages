#!/usr/bin/env python3
"""Capture Chrome Web Store assets from the real extension UI.

Why this exists: the store listing needs 1280x800 screenshots (plus an optional
440x280 promo tile and 1400x560 marquee banner), and they have to show the real
ORCA panel. Screenshots of a running product cannot be produced from a static
website repo, so this script drives a browser on your machine and writes the
files at exactly the sizes the store wants.

Setup (once):
    python3 -m venv .venv-shots
    source .venv-shots/bin/activate
    pip install playwright pillow        # pillow optional, for exact resizing
    playwright install chromium

Typical use - capture the built-in ORCA panel pages from an unpacked build:
    python3 tools/prepare-screenshots.py --extension ~/orca/dist --headed

    The script prints the chrome-extension://<id>/ URL once the service worker
    boots, so you can paste that id into SHOTS below, or use --open.

Just capture a URL you already have open (a staging page, a demo tenant):
    python3 tools/prepare-screenshots.py --only picker,run --open \
        "chrome-extension://abcdefghijklmnop/panel.html"

Keep a login between runs (portal work needs a signed-in page):
    python3 tools/prepare-screenshots.py --persistent ./.shots-profile --headed

Output:
    <out>/<name>.png            master capture
    <out>/<name>.jpg            store-ready (quality 92), if Pillow is installed
    <out>/report.txt            what was captured, at what size, how many bytes

Everything below is editable; nothing is uploaded anywhere.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import sys

# --------------------------------------------------------------------------
# What to capture. `url` may be relative to --open. `steps` are literal
# Playwright snippets executed in order, which is how a screenshot gets a
# filled-in field or an open dropdown without faking anything in Photoshop.
# --------------------------------------------------------------------------
SHOTS = [
    {
        "name": "01-element-picker",
        "url": "",  # filled from --open, or set an absolute URL here
        "viewport": [1280, 800],
        "wait_for": "body",
        "steps": [
            "page.click('[data-demo-picker], #orca-picker, button:has-text(\"Pick element\")')",
            "page.wait_for_timeout(600)",
        ],
        "caption": "Visual element picker pointing at a control on a live page.",
    },
    {
        "name": "02-rule-engine",
        "url": "",
        "viewport": [1280, 800],
        "steps": [
            "page.click('button:has-text(\"Add rule\")')",
            "page.wait_for_timeout(400)",
        ],
        "caption": "Smart Rule Engine: click and retry, dynamic delay, condition check.",
    },
    {
        "name": "03-multi-step-workflow",
        "url": "",
        "viewport": [1280, 800],
        "steps": ["page.wait_for_timeout(400)"],
        "caption": "A multi-step workflow: wait, type, select, extract, submit.",
    },
    {
        "name": "04-live-tracking-log",
        "url": "",
        "viewport": [1280, 800],
        "steps": [
            "page.click('button:has-text(\"Run\")')",
            "page.wait_for_timeout(2500)",
        ],
        "caption": "Live execution tracking: per-step status, retries and timings.",
    },
    {
        "name": "05-scheduler",
        "url": "",
        "viewport": [1280, 800],
        "steps": ["page.wait_for_timeout(400)"],
        "caption": "Built-in task scheduler on a recurring plan.",
    },
    # Optional store tiles. Only these two sizes are worth rendering from a
    # screenshot; do not stretch a 1280-wide capture into them by hand.
    {
        "name": "promo-440x280",
        "url": "",
        "viewport": [440, 280],
        "crop_to": [440, 280],
        "steps": ["page.wait_for_timeout(400)"],
        "caption": "Small promo tile (store search results).",
    },
    {
        "name": "marquee-1400x560",
        "url": "",
        "viewport": [1400, 560],
        "crop_to": [1400, 560],
        "steps": ["page.wait_for_timeout(400)"],
        "caption": "Marquee banner tile.",
    },
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="store-shots", help="output directory (default: store-shots)")
    ap.add_argument("--only", default="", help="comma-separated names to capture")
    ap.add_argument("--open", dest="open_url", default="", help="base URL every shot starts from")
    ap.add_argument("--extension", default="", help="path to an unpacked extension build to load")
    ap.add_argument("--persistent", default="", help="user-data dir to reuse (keeps you signed in)")
    ap.add_argument("--headed", action="store_true", help="show the browser (needed for logins/CAPTCHAs)")
    ap.add_argument("--scale", type=float, default=1.0, help="device scale factor (2 for retina masters)")
    ap.add_argument("--config", default="", help="JSON file replacing the built-in SHOTS list")
    ap.add_argument("--full-page", action="store_true", help="capture the whole scrollable page")
    ap.add_argument("--list", action="store_true", help="print the configured shots and exit")
    ap.add_argument("--hide", default=".site-header, .site-footer, [data-shot-ignore]",
                    help="CSS selector for chrome to hide before capture (\"\" to keep)")
    return ap.parse_args()


def load_shots(args: argparse.Namespace) -> list[dict]:
    if args.config:
        shots = json.loads(pathlib.Path(args.config).read_text())
    else:
        shots = [dict(s) for s in SHOTS]
    if args.only:
        wanted = {w.strip() for w in args.only.split(",") if w.strip()}
        shots = [s for s in shots if s["name"] in wanted]
        missing = wanted - {s["name"] for s in shots}
        if missing:
            sys.exit("unknown shot name(s): " + ", ".join(sorted(missing)))
    for shot in shots:
        if not shot.get("url"):
            shot["url"] = args.open_url
    return shots


def main() -> int:
    args = parse_args()
    shots = load_shots(args)

    if args.list:
        for shot in shots:
            w, h = shot.get("viewport", [1280, 800])
            print("%-24s %sx%-4s %s" % (shot["name"], w, h, shot.get("caption", "")))
        return 0

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        sys.exit("Playwright is not installed. Run:\n"
                 "  pip install playwright pillow && playwright install chromium")

    try:
        from PIL import Image  # type: ignore
        have_pillow = True
    except ImportError:
        have_pillow = False

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    report: list[str] = []
    notes: list[str] = []

    launch = {"headless": not args.headed}
    if args.extension:
        ext = str(pathlib.Path(args.extension).expanduser().resolve())
        if not pathlib.Path(ext).is_dir():
            sys.exit("--extension path does not exist: " + ext)
        launch["args"] = ["--disable-extensions-except=%s" % ext, "--load-extension=%s" % ext]

    with sync_playwright() as pw:
        ctx_kwargs = {
            "viewport": {"width": 1280, "height": 800},
            "device_scale_factor": args.scale,
        }
        if args.persistent:
            context = pw.chromium.launch_persistent_context(args.persistent, **ctx_kwargs, **launch)
            browser = None
        else:
            browser = pw.chromium.launch(**launch)
            context = browser.new_context(**ctx_kwargs)

        if args.extension:
            for worker in context.service_workers:
                print("service worker:", worker.url)
                notes.append("service worker: " + worker.url)
            print("Open the panel in the browser, then copy its chrome-extension:// URL")
            print("into --open (or the shot's url) and re-run without --headed confusion.")
            print("Waiting for you to navigate: press Enter once the ORCA panel is visible.")
            if not args.open_url:
                try:
                    input()
                except EOFError:
                    pass

        for shot in shots:
            url = shot.get("url") or args.open_url
            if not url:
                notes.append("skipped %s: no url (pass --open or set url in SHOTS)" % shot["name"])
                continue
            page = context.new_page()
            w, h = shot.get("viewport", [1280, 800])
            page.set_viewport_size({"width": w, "height": h})
            page.goto(url, wait_until="networkidle" if not url.startswith("chrome-extension") else "load")
            target = shot.get("wait_for")
            if target:
                try:
                    page.wait_for_selector(target, timeout=8000)
                except Exception as exc:  # noqa: BLE001 - report and keep going
                    notes.append("%s: wait_for failed (%s)" % (shot["name"], exc.__class__.__name__))
            page.wait_for_timeout(int(shot.get("settle_ms", 700)))
            if args.hide:
                page.eval_on_selector_all(args.hide, "els => els.forEach(e => e.style.display = 'none')")
            for step in shot.get("steps", []):
                try:
                    exec(step, {"page": page})
                except Exception as exc:  # noqa: BLE001
                    notes.append("%s: step failed: %s -> %s" % (shot["name"], step, exc.__class__.__name__))
            page.wait_for_timeout(int(shot.get("after_ms", 300)))

            png = out / ("%s.png" % shot["name"])
            page.screenshot(path=str(png), full_page=args.full_page)
            lines = ["%-24s png %8d bytes" % (shot["name"], png.stat().st_size)]

            crop_to = shot.get("crop_to") or [w, h]
            if have_pillow:
                from PIL import ImageOps  # type: ignore
                img = Image.open(png)
                if tuple(img.size) != tuple(crop_to):
                    img = ImageOps.fit(img, tuple(crop_to), Image.LANCZOS)
                    img.save(png)
                jpg = out / ("%s.jpg" % shot["name"])
                img.convert("RGB").save(jpg, "JPEG", quality=92, optimize=True, progressive=True)
                lines.append("%-24s jpg %8d bytes  %dx%d" % (shot["name"], jpg.stat().st_size, *crop_to))
                if jpg.stat().st_size > 5 * 1024 * 1024:
                    notes.append("%s: jpg above the 5 MB store limit" % shot["name"])
            else:
                lines.append("%-24s (Pillow not installed: no jpg, no exact %dx%d crop)"
                             % (shot["name"], crop_to[0], crop_to[1]))
            report.extend(lines)
            page.close()

        context.close()
        if browser:
            browser.close()

    (out / "report.txt").write_text("\n".join(report + ([""] * bool(notes)) + notes) + "\n")
    print("\n".join(report) or "nothing captured")
    if notes:
        print("\nnotes:")
        for n in notes:
            print("  - " + n)
    if not have_pillow:
        print("\ninstall Pillow for exact store dimensions and .jpg export: pip install pillow")

    # Store-side checklist, printed every run because the rules are easy to miss.
    print(
        "\nStore checklist\n"
        "  1. Screenshots must be 1280x800, one idea each, in the order you want them shown.\n"
        "  2. Small promo tile 440x280, marquee 1400x560 - both optional, both improve placement.\n"
        "  3. Anything cropped must not cut off a caption or a button label.\n"
        "  4. Real data only: no invented customer names or made-up metric overlays.\n"
        "  5. A short trailer (<2 min) lifts conversion; a 30-90s silent GIF/webm works too.\n"
        "  6. Report file: %s\n" % (out / "report.txt")
    )
    if shutil.which("jpegoptim") is None and have_pillow:
        print("  tip: jpegoptim/pngquant squeeze another 10-25 percent if you want them smaller.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
