# Orcamatic site — phased completion plan

The audit in [`website-audit.md`](website-audit.md) listed the problems. This file is the
execution order, with an owner on every line: **agent** means it happens in this repo and
needs nothing from you; **you** means it needs the extension, the store dashboard, or a
decision from you.

Nothing in the **agent** rows is a stub, a placeholder, or a claim that needs verifying
afterwards. Anything illustrative on the site is labelled as illustrative on the page.

---

## Phase 0 — trust and imagery hygiene · owner: agent · **done**

- Removed every decorative eyebrow/kicker label site-wide.
- Deleted fabricated product imagery; all product imagery is the real Chrome Web Store
  screenshot set, hot-linked from Google's CDN with a JS fallback if a URL ever dies.
- Rewrote headline copy so it sells the product instead of arguing about asset provenance.
- Rebuilt the Open Graph image (`tools/build-og-image.py`).

## Phase 1 — conversion architecture and proof · owner: agent · **done**

| # | Shipped | Where |
|---|---|---|
| 1.1 | Problem block (no API / no budget / no patience) between the trust strip and the how-it-works steps | `#problem` on `index.html` |
| 1.2 | Animated proof panel: build → run → log, drawn in CSS with real feature names, reduced-motion off-switch | `.demo` on `index.html` |
| 1.3 | Four persona cards, each linking to the workflow template that matches the job | `.persona-grid` on `index.html` |
| 1.4 | Process proof: a finished run's log and its extracted rows, headed *example data* | `.proof-grid` on `index.html` |
| 1.5 | Eight-row comparison against macro recorders, API connectors and desktop RPA | `table.compare` on `index.html` |
| 1.6 | Template library: `/templates/` plus three written-out workflow templates | `templates/` |
| 1.7 | Quickstart guide with a five-step recipe and the five failure modes people actually hit | `/guides/first-workflow/` |
| 1.8 | Security page: every permission with its reason, data-flow columns, store disclosures | `/security/` |
| 1.9 | Pricing reconciled with the privacy policy: same feature set on all tiers, tier = AI balance; two new FAQ answers; full comparison table | `#pricing` on `index.html`, `/pricing/` |
| 1.10 | Templates in the primary nav and the footer on all 19 pages; six new URLs in `sitemap.xml` | `*.html`, `sitemap.xml` |
| 1.11 | Blog → template/guide/security cross-links; `HowTo`, `ItemList` and `FAQPage` structured data on the new pages | `blog/*`, `templates/*` |
| 1.12 | Mobile: nav bar tightened before the 800px drawer switch; screenshot rail with scroll-snap; sticky comparison column | `assets/site.css` |
| 1.13 | Scroll reveals stagger by 90ms so sections read top-to-bottom | `assets/site.js` |
| 1.14 | Screenshot/promo-tile capture tool for store assets | `tools/prepare-screenshots.py` |
| 1.15 | Honest arithmetic block: minutes per run × runs per week − log checking, computed from what the visitor types | `#roi-title` on `index.html` |
| 1.16 | Full feature-comparison table and a "what happens when the balance runs out" panel on `/pricing/` | `pricing/index.html` |

### Two sentences that need 60 seconds of your eyes

`/security/` describes `offscreen` as the mechanism that keeps long runs alive while the service
worker is idle, and `webNavigation` as step timing and redirect detection. Both are the standard
Manifest V3 uses for those jobs, and both match what the extension's behaviour on the store page
implies — but only your manifest and background script can confirm the wording. If either is used
differently, change those two table rows and nothing else on the page moves.

Verification run at the end of the phase: HTML tag balance on every page, `css-tree` parse
of `assets/site.css`, `node --check` on `assets/site.js`, class cross-check (no class used
in markup without a rule), zero inline `style=` attributes (the CSP forbids them), every
internal `href` resolving to a file, sitemap XML valid with unique URLs, all 19 pages
returning 200 from a local server.

## Phase 2 — the recording · owner: **you** · status: waiting

This is the single highest-value item left, and it cannot be produced from the repo: it is
a screen recording of the extension running on a real page.

Spec, so one take is enough:

- Length 45–75 seconds. Silent or captions only — no voiceover needed for the homepage.
- 1280×800, 60fps, one workflow start to finish: pick target → add retry → run → log →
  extracted values. Zoom the panel to ~150%; do not zoom the whole desktop.
- Real, non-sensitive page. Mask or use a demo tenant for anything customer-facing.
- Export both `demo.webm` (VP9, CRF 34, target ≤ 6 MB) and `demo.mp4` (H.264, CRF 23).
- Keep a 1280×800 still from the log frame; it doubles as a store screenshot.
- Optional: a 6-second silent loop of just the picker hover, for the hero.

Drop the files in `assets/` named `demo.webm` / `demo.mp4`, tell me, and I will wire the
`<video autoplay muted loop playsinline poster>` block in with a `prefers-reduced-motion`
gate and swap the animated panel to the still.

## Phase 3 — store listing · owner: **you** · status: waiting

The strings are ready in [`website-audit.md`](website-audit.md) (§Chrome Web Store ASO):
a 75-character name, a 132-character summary, screenshot order and captions. Paste them in
the CWS dashboard. For the promo tiles run:

```bash
pip install playwright pillow && playwright install chromium
python3 tools/prepare-screenshots.py --extension path/to/unpacked/build --only promo-440x280,marquee-1400x560
```

Reply to every review, including the short ones: rating count is a ranking input and the
listing currently has zero reviews.

## Phase 4 — decisions I should not make for you · owner: **you** · status: waiting

1. **Annual billing.** Research says an annual toggle at roughly two months free lifts
   paid conversion. It needs a Lemon Squeezy price and a refund rule. Say the word and I
   build the toggle; I will not advertise a discount that does not exist.
2. **Feature gating.** The privacy policy and the pricing page now agree that all tiers get
   the same features. If you would rather gate the scheduler or multi-step workflows to a
   higher tier, tell me and both pages flip back together.
3. **Free tier wording.** Nothing on the site promises a free plan, because the store only
   says "offers in-app purchases". If there is a real free tier, name its limits and I will
   put it in the table.
4. **Support promise.** There is no stated response time anywhere. A real one (even "two
   business days") converts better than "we reply fast"; I will not invent it.
5. **Named proof.** Eleven users today, so no logo wall and no customer quotes. As soon as
   one user will say something specific, send it and I will place it next to the pricing CTA.

## Phase 5 — measure, then sharpen · owner: agent, after Phases 2 and 3 land

- `GA_MEASUREMENT_ID` in `assets/site.js` is still empty, so nothing is measured and no
  consent banner appears. Setting it turns analytics on for the whole site — your call, and
  it needs the CSP plus the privacy policy analytics section to be updated in the same commit.
- Once real numbers exist: check LCP and CLS at 375px, then A/B the four H1 candidates in
  the audit against the current line.
- Grow the template library one entry at a time, from actual support requests, and only for
  workflows we can verify the extension performs today.
- Revisit whether the hero still needs its drawn artwork once the real recording exists.

## Deliberately not done

No fabricated metrics, no stock logo wall, no AI-drawn UI mockups, no invented importable
profile files (templates are written recipes, because that is what is verifiable today), no
countdown timers, no "limited spots left", no price anchoring against a fake enterprise plan.
