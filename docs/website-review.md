# Homepage post-mortem: what the 15:48 snapshot actually showed

Reported: "you messed up the whole website — squeezed images and lots of problems", with a
full-page snapshot of `orcamatic.com` taken 2026-10-15 15:48 (`1852x19148` px).

Read this first if you are trying to work out what is broken. Two separate things are mixed
together in that picture: a stale stylesheet that made intact markup look destroyed, and a
handful of real defects in the source. The first is not a repo bug; the second is.

---

## 1. Most of the screenshot is new HTML painted with a five-hour-old CSS

The snapshot is not the current build of `index.html` + `assets/site.css`. It is the current
HTML with `site.css` from commit `07f8c10` (11:33, four hours before the merge at 15:46).
Nothing in the repo produced those broken sections - the browser never had the rules for them.

Four measurements from the screenshot, all pointing the same way:

1. **The page was laid out as desktop.** Content spans device x 202..1650. That is the
   `--container: 1160px` box inside a 1481px viewport at DPR 1.25 (`min(100% - 40px, 1160px)`
   = 1160 → 1450 device px, 201 device px of margin). So the stylesheet was loaded, and
   `.container` works - this is not "the CSS 404'd".
2. **The gallery tiles are 40px short on each side.** The four screenshots span x 251..1600,
   while every other section spans 202..1650. 40px is exactly the browser default
   `figure { margin-inline: 40px }`, which `.shots figure { margin: 0 }` normally overrides.
   One-per-row at container width, with UA margins, is what an *unstyled* `.shots` grid looks
   like - not what a 4-column grid looks like.
3. **The hero printed its own apology.** "The Chrome Web Store preview could not be loaded
   here" is visible in the snapshot *below an image that loaded fine*. In the current CSS that
   paragraph is `display: none` until a `data-shot-failed` attribute arrives. It showed because
   `.shot-fallback` did not exist in that revision of the file.
4. **The list of broken sections matches the file's history exactly.** Everything unstyled in
   the snapshot is a selector that `2c23146` (12:23) added and `07f8c10` (11:33) does not
   contain; everything that looks fine is in both. Checked mechanically across seven revisions:

   | selector | 07f8c10 (11:33) | HEAD | as it looked in the snapshot |
   | --- | --- | --- | --- |
   | `.container`, `.hero-grid`, `.step-card`, `.plans-grid`, `.plan-card.featured::before`, `.privacy-band`, `.local-card`, `.logo-strip-list`, `.faq-list`, `.cta-panel` | yes | yes | styled |
   | `.shots`, `.shot-frame`, `.shot-fallback`, `.facts`, `.cta-note` | no | yes | raw `figure`/`ul` defaults |
   | `.feature-grid`, `.persona-grid`, `.problem li`, `.demo*`, `.proof-*`, `.roi-*`, `.table-wrap` | no | yes | flattened into paragraphs |

Deploy 15 for `9548f17` finished `completed / success` at 15:46, two minutes before the
snapshot. A deploy replaces files on independent URLs: `index.html` came back new, and
`/assets/site.css` - same URL, same cached copy - came back old. That mismatch is the entire
reason for the version stamp in §2.1, and it is why "reload the page" was never going to be a
satisfying answer.

**How to confirm it yourself:** open DevTools → Network → "Disable cache" → reload, and check
that the demo, the proof cards, the gallery row and the ROI block all come back. Or compare
sizes: `curl -s https://orcamatic.com/assets/site.css | wc -l` should be 669-odd lines, not 536.

---

## 2. The real defects in the source, and what changed

Everything below was true at `9548f17` regardless of any cache. Fixed in this branch.

### 2.1 P0 · A page could render with no content at all
`[data-reveal] { opacity: 0 }` lived in CSS, and only `site.js` lifted it. One failed
`site.js` request, one thrown exception above the observer, or the same HTML/CSS skew as §1 -
and the hero copy, every section heading, the cards, the demo, the gallery and the pricing grid
stay at `opacity: 0` forever. An invisible page hiding behind a working stylesheet.

Now the reveal is scroll-driven CSS inside `@supports (animation-timeline: view())`, guarded by
`prefers-reduced-motion: no-preference`. A browser that does not know `view()` shows the
content statically; a script that never runs cannot hide anything. The `IntersectionObserver`,
the `is-visible` class and the `data-reveal-index` stagger are gone, and `site.js` lost 14
lines with nothing lost from the animation.

### 2.2 P0 · The images were illegible by design ("squeezed")
- Every visual was requested as `=s1280-w1280-h800`. That pair is not a size hint, it is a
  **crop box**: the CDN fits the source and then cuts it to 16:10. Today the store tiles are
  already 1280x800, so nothing was cut; the moment a tile is uploaded at another ratio, its
  caption or a button label loses its head. The URLs now ask for one width (`=w1024`, `=w1152`)
  and never a box.
- The showcase was `repeat(4, 1fr)` in a 1160px container: **279px per tile** for a 1280px-wide
  screenshot of a UI. Every label inside those tiles rendered at 3-4px. A screenshot nobody can
  read is decoration, and expensive decoration at that. It is now two-up (~570px) with a caption
  each, so the type inside is roughly the size it was designed for.
- Nothing reserved a box for a tile. A frame that is 8:5 today and 5:3 tomorrow pushed the
  sections under it around while images arrived. `.shot-frame` and the gallery links now carry
  `aspect-ratio: 8 / 5` with `object-fit: cover`, and the `width`/`height` attributes stay, so a
  change of ratio letterboxes or trims a little instead of squashing the UI or moving the page.
- `tools/check-site.py` had an advisory that *told you to add the crop box*: "store image
  without a size suffix (add =s1280-w1280-h800)". The checker was pushing the bug. Replaced
  with three checks that fire instead (verified by mutation): `=w<N>` required and a `-w-h` box
  rejected, `width`/`height`/`alt` required on every `<img>`, and a `rel=preload as=image` that
  no `<img>` on the page uses - the hero preload URL has to match the `<img>` src exactly, or
  the biggest image on the page is fetched twice.

### 2.3 P1 · The mobile gallery was broken in the CSS, not in the cache
`@media (max-width: 580px)` set `.shots { grid-template-columns: 1fr }`, and a *different*,
later block at `max-width: 800px` turned the same grid into a horizontal rail
(`grid-auto-flow: column; grid-auto-columns: 74%`) without clearing the explicit template.
Below 580px the first tile therefore filled the whole explicit column and the rest got the 74%
auto columns - one oversized tile, then a rail of small ones. The rail rule now sets
`grid-template-columns: none`, and `scroll-snap-align` moved from `center` to `start` so a
tile's caption stays with it.

### 2.4 P1 · Labels and values were glued together by the markup
`<li><b>No API</b><span>Connector tools stop where…</span></li>` only separates its two halves
with `display: grid`. Without that rule - stale CSS, a print stylesheet, an RSS or reader view,
a text copy - it reads "**No APIConnector** tools stop…". Same pattern in the demo header
("step 4 of 5Schematic drawn in CSS"), the progress row ("Live execution tracking3.2s"), the
proof card headers ("extract-list-to-sheetexample data"), the privacy stats, and the arithmetic
output ("14hours a month handed back·52 runs").

The separators are now carried by block-level children (`<div>`, `<p>`) inside the same
flex/grid containers - blockified as flex and grid items, so nothing moved a pixel when styled -
and the demo log lines got a real space after each glyph. A missing stylesheet now degrades to a
flat list of sentences instead of a wall of run-together words.

### 2.4b P2 · The hero visual was 40px out of line in the current build
`figure { margin: 1em 40px }` is a browser default and this stylesheet had no reset for it, while
`.shots figure { margin: 0 }` only covered the gallery. On the three pages that place a single
`figure.shot` beside a text column - the hero, `/products/`, `/about/` - the image was therefore
indented 40px from the container edge and carried a stray 1em of vertical space, so the picture
did not line up with anything next to it. (It is also the fingerprint that identified the stale
CSS in §1: the gallery tiles in the snapshot end at x1600 while every other section ends at
x1650.) A `figure { margin: 0 }` in the base layer now covers all three pages and any future one.

### 2.5 P2 · Small things worth naming
- A dead hero state: an image that failed showed "could not be loaded here" *and* kept the
  frame, *and* offered two links to the same listing. The fallback now sits inside the reserved
  frame with one sentence, the caption is text, and the store link appears once per view instead
  of twice (that was 5 links to the listing on one screen, now 4 with the nav, hero and CTA band).
- `site.js` gave up on the first `error`. It retries once with a cache-busting query - enough for
  a transient 5xx or a poisoned cached miss - and clears the failed state if a later load
  succeeds. A hot-linked image from someone else's CDN is the one asset on this site you cannot
  make reliable, so it gets the cheapest possible second chance.
- A duplicated `.logo-strip-list` rule inside `@media (max-width: 580px)` (0.68rem, then 0.86rem
  further down) - consolidated, computed style unchanged.
- `figure.shot` markup is now guarded by the checker (§2.2's last bullet covers the image rules),
  so a frame without its fallback note fails the build instead of the page.

---

## 3. What is still yours to do

1. **Stop hot-linking the imagery.** Five `<img>`s on this page are Google's copy of the store
   listing: they can be re-cropped, re-ordered or revoked, and `no-referrer` is a workaround for
   a dependency that should not exist. The repo already knows this - README says so, and
   `tools/prepare-screenshots.py` captures the real UI at exactly 1280x800. Save the listing's
   five images into `assets/screenshots/orca-1.png … orca-5.png`, swap the URLs, drop
   `https://lh3.googleusercontent.com` from `img-src` and the `preconnect` in every page head,
   and the whole fallback path in `site.js` can go away. Until then the `=w<N>` sizes are worth
   keeping: they are what stops the browser downloading a 1280px raster for a 279px slot.
2. **Real screenshots, or the film.** These five images are marketing *tiles*: each has its own
   headline baked in ("Your browser. On autopilot."), which is why the page reads as a stack of
   posters with a competing voice - and why the hero tile's own H1 fights the page H1. Tiles are
   the right thing for the store; they are the wrong thing for a product page. P0.1/P0.2 in the
   audit (a 30-45s film, and the screenshot as its poster) is still the biggest open item, and
   only a running extension can produce it.
   *Resolved 2026-10-15: item 1, and the tile problem in item 2. The store images are off the
   site entirely, replaced by drawn illustrations, and the CSP is back to `img-src 'self'` (see
   Phase 1d in [`PHASES.md`](PHASES.md)). The film is still open.*
3. **The listing has 0 ratings and 11 users.** Every "proof" block on this site is a schematic or
   a log sample. That is honest, and it is all we can publish without store access.

---

## 4. Guardrails added with this change

| command | what it now catches |
| --- | --- |
| `python3 tools/version-assets.py` | writes `?v=<sha256[:10]>` onto `/assets/site.css`, `/assets/site.js` in all 20 pages, and onto each font `url()` inside the CSS. Idempotent. |
| `python3 tools/version-assets.py --check` | lists any page whose stamp does not match the current file. |
| `python3 tools/check-site.py --strict` | the above as an error, plus the image rules from §2.2 and the `figure.shot` contract from §2.5. |
| `.github/workflows/deploy-github-pages.yml` | now runs `--strict`, so a stale stamp or a cropped store URL stops the deploy. |

The stamp is the part that pays for itself: it turns §1 from "the site looks destroyed for one
user for ten minutes" into "impossible", without a build step, without a CDN purge, and without
anything to remember apart from running one script.
