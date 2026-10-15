# ORCA — website + store-listing enhancement audit

Audited: 2026-10-15. Scope: the 13 published pages in this repo, the live Chrome Web Store
listing for `bohdghgjgkellecnjkmahfiocaefgbki`, and current (2026) conversion/design references.
Method: read every page and the store listing, then graded the site against what AI/automation
products that convert actually do. Nothing below asks you to invent a claim.

**Status after Phase 1 (2026-10-15):** everything below marked ✅ shipped is live in this repo;
the execution order and the owner split are in [`PHASES.md`](PHASES.md). P0.1, P0.2 and P0.5 stay
open because they need a screen recording and access to the store dashboard. Two side effects
worth noting: the site is now 20 pages (up from 13), and `python3 tools/check-site.py --strict`
is the command that keeps it honest — it runs in CI before anything is published.

---

## 0. Diagnosis in one line

The site **explains** ORCA well and **shows** it hardly at all: no motion, no proof, and only one
soft push. Three layers are missing — a demo you can watch, process proof you can inspect, and a
single repeated action with the risk removed.

Reference points used: conversion element impact table and section-order template
([landing-page-generator skill](https://github.com/borghei/Claude-Skills/blob/main/marketing/landing-page-generator/SKILL.md)),
B2B layout patterns for abstract AI products ([flowtrix](https://www.flowtrix.co/blogs/12-b2b-landing-page-design-examples-for-2026)),
"show real UI, not abstract illustration" + video-first hero data
([SaaSHero](https://www.saashero.net/design/landing-page-design-inspiration-2026/)),
early-stage proof advice "show process proof, not fake enterprise theater"
([Lovart](https://www.lovart.ai/blog/01-industry-saas-landing-page)),
pricing-section adoption data ([Web Anatomy, 114 pricing sections](https://www.webanatomy.ai/best-landing-pages/sections/pricing)),
CWS ranking factors and listing spec ([cwspy](https://cwspy.com/blog/chrome-web-store-seo),
[ExtensionBooster](https://extensionbooster.net/blog/chrome-web-store-listing-optimization-guide/),
[Google's own listing doc](https://developer.chrome.com/docs/webstore/cws-dashboard-listing)).

---

## 1. Scorecard

| Page | Clarity | Proof | Desire | Action | Speed | Mobile | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `/` homepage | strong | **none** | medium | medium | fair (5 hot-linked 1280px images) | good | reads well, sells weakly |
| `/products/` | strong | **none** | medium | medium | good | good | the CSS schematic is the only "demo" |
| `/pricing/` | good | weak | medium | medium | good | cards stack, no comparison table | missing the two highest-value blocks |
| `/about/` | good | n/a | low | low | good | good | fine, short |
| `/blog/` (4 posts) | good | n/a | n/a | weak | good | good | no internal path to a template |
| CWS listing | ok | **0 ratings, 11 users** | fair | ok | — | — | name has no keyword, no video, no promo tile |

The two pages that should convert hardest (`/`, `/pricing/`) are the two with the least proof.

---

## 2. P0 — highest lift per hour, do this week

### P0.1 Ship a 30–45s product film in the hero
This is the biggest single gap. For an abstract product, "the product moving" beats every
paragraph: video demos are credited with up to ~80% lift, video testimonials ~34% median, and
"if your product can be demonstrated, let visitors interact with it directly" is the recurring
2026 pattern ([ref](https://www.flowtrix.co/blogs/12-b2b-landing-page-design-examples-for-2026),
[ref](https://www.saashero.net/design/landing-page-design-inspiration-2026/)).

Spec, so it stays cheap and fast:

- 3 scenes, no voiceover: **pick an element → add a rule (retry/delay/condition) → run, log ticks, done.**
- Under 90 seconds; muted, `autoplay loop playsinline poster="…"`; lazy-load anything below the fold.
- Capture in a clean Chrome profile at 2× then downscale; **seed believable data, not "Test1"**
  (the advice in the Lovart teardown: "seed demo data that looks like a believable company").
- `assets/demo/orca-hero.webm` (VP9) + `.mp4` (H.264), target ≤6 MB, `preload="none"` +
  IntersectionObserver start/stop. Add captions — 88% of B2B buyers watch product video, often muted.
- Respect `prefers-reduced-motion`: show the poster still instead of the loop.
- End card: the store URL, not a logo sting.
- **Re-use the same clip as the store's YouTube video field** — it's an accepted asset you currently
  don't have ([doc](https://developer.chrome.com/docs/webstore/cws-dashboard-listing)).

Copy for the block when it lands: `Watch a workflow being built and run — 41 seconds, no narration.`

### P0.2 Replace the static hero visual with that clip (screenshot becomes the poster)
Keep the frame, swap `<img>` → `<video poster>`. One visual, two jobs: it names the category and it
proves the product. No captions about where the assets came from — provenance belongs in a small
grey line, never in a headline (that was the mistake in the last pass).

### P0.3 ✅ Process proof, because you honestly have no social proof yet
11 users and 0 ratings is the real number, so do **not** manufacture logos, counts or quotes.
What 2026 early-stage pages use instead: "show process proof (audit logs, templates, sample
outputs) instead of fake enterprise theater" ([ref](https://www.lovart.ai/blog/01-industry-saas-landing-page)).
Publish:

1. **A real run log** — the actual output of one run (timestamps, retries, extraction rows), as a
   screenshot and as text. Nobody else shows this; it is your most credible asset.
2. **Sample outputs** — the sheet/CSV a template produces, before/after.
3. **A public changelog** (`/changelog/`) — dated, plain. It answers "is this abandoned?" better
   than any badge, and recency is a ranking input for the store.
4. **Named human** — "Built and supported by Muhammad Abubakar, the developer of ORCA; support
   answered within 48h." A named indie author is trust, not weakness. Only publish if you'll keep it true.
5. **Usage counter only if real** — if you show "N installs", pull the store number and label the
   date. No live-activity pop-ups.

Placement rule: proof within the first two scrolls **and** next to each CTA (that's where the lifts
are reported: 37% median for social proof, +18% from a single proof line under the button —
[ref](https://dev.to/alpo190010/landing-page-best-practices-2026-what-actually-converts-from-someone-who-got-it-wrong-first-2f9e)).

### P0.4 ✅ Risk reversal on every ask
You already grant a 7-day money-back guarantee (≤10% AI consumption) — it was **only** on
`/refund-policy/`. Refund guarantees lift conversion 12–18% ([ref](https://influenceflow.io/resources/saas-pricing-page-best-practices-complete-guide-for-2026/)).
Now surfaced on `/`, `/products/`, `/pricing/` (this pass). Next: put it inside the store
description's last paragraph, where the install decision is actually made.

### P0.5 Fix the Chrome Web Store listing — it outconverts the website
Store search ranks on keyword match in name/summary, installs, rating **count**, retention and
listing completeness ([ref](https://cwspy.com/blog/chrome-web-store-seo)). Current state:

| Field | Today | Fix |
| --- | --- | --- |
| Name | `ORCA` — 4 chars, ranks for nothing | `ORCA — Auto Clicker, Form Filler & Web Automation` (49 chars; ~35 visible) |
| Summary | `Universal and intelligent auto-clicker with visual element picker and smart rule engine.` (reads like internals, not benefit) | `Automate clicks, form filling and data extraction on any site. Visual element picker, rule engine, scheduler. No code, no API keys.` (131/132) |
| Screenshots | 5 full-window tiles, no captions | One idea per image + a headline caption; lead with the core value, close with "Install ORCA" |
| Video | none | Upload the P0.1 clip, paste the YouTube URL |
| Small promo tile 440×280 | missing | Make it: logo + name + one line. Cheap, used in browse surfaces |
| Marquee 1400×560 | missing | Only needed for editorial placement — build after the tile |
| Ratings | 0 | Ask after a *successful run*, in-panel; reply publicly to every review |
| Category | Tools | Check where the ranking auto-clickers sit; match, don't guess |
| Description story | "auto-clicker + rule engine" | **Same story as the site** — see P0.6 |

### P0.6 One product story, written in both places
The site sold "a browser agent that learns the work you repeat"; the listing says "intelligent
auto-clicker with visual element picker and smart rule engine". Two stories cost you twice: the
store rejects/muffles mismatched claims, and users who install for one and get the other churn —
and uninstall rate is a ranking input. Decision to make, then apply to both:

- **A. "Auto-clicker that doesn't break"** — honest, searchable, defensible. Keywords: auto clicker,
  form filler, web automation, data extraction, scheduler.
- **B. "Browser agent"** — bigger story, harder to prove today, weaker search match.

Recommended: **A on the store, A-then-B on the site** (lead with the concrete category in the
hero, then earn the "agent" language in the AI-planner section once the planner is genuinely good).

---

## 3. P1 — structure and persuasion (next two weeks)

### P1.1 ✅ Re-order the homepage to the converter template
Hero → proof bar → **problem** → solution → how it works → features with benefits → process proof →
pricing → FAQ → final CTA with risk reversal
([section order](https://github.com/borghei/Claude-Skills/blob/main/marketing/landing-page-generator/SKILL.md)).
You are missing a **problem** section entirely. Two paragraphs is enough, and they must be specific:
"Insurer portals, ticket queues and admin consoles have no API and no budget for RPA. So the same
12 clicks stay yours, 40 times a week."

### P1.2 ✅ "Built for" — name the jobs, not the features
Four cards: back-office & ops, sales/CS (CRM hygiene), recruiting & research, solo founders. Each
card = one sentence + one link to a template. This is how Bardeen won its category: narrow, named
jobs (lead scraping → sheet → CRM) rather than a feature list
([ref](https://phantombuster.com/blog/tools/bardeen-chrome-extension/)).

### P1.3 ✅ A template library — the compounding asset
10–12 templates as real pages under `/templates/`, each with: what it does, the steps rendered
visually, run time, an "import into ORCA" one-liner, and the exact rule list. Bardeen ships 100+
and it is the reason people adopt it ([ref](https://automationatlas.io/tools/bardeen/)).
Why it matters three times over: onboarding (first value in minutes), long-tail SEO
("auto fill a form every monday chrome"), and proof (each template *is* a demonstration).

### P1.4 ✅ If video slips: build the demo in CSS instead
Animate the existing panel schematic — steps tick green one by one, a progress bar advances, the
log types out. Loop 6s, honour `prefers-reduced-motion`, keep the honest "schematic" label. Cost:
one afternoon, no assets, no fake UI text. This is the cheapest way to get "product in motion"
on the page, which is the thing reviewers keep crediting with the lift.

### P1.5 ✅ Comparison block (you have four credible neighbours)
A table, not prose: **ORCA / macro recorder (AutoClicker) / API connectors (Zapier, Make) / desktop
RPA**. Rows: works on sites with no API · survives layout change · runs in your logged-in session ·
no code · runs locally · retries and waits · scheduling · price · Windows/Mac/Linux. Only tick what
you can defend in a support ticket. Comparison tables are reported at +18% on pricing pages.

### P1.6 ✅ Honest ROI and a cost estimator

> Shipped as the "Do the arithmetic on your own week" block on the homepage: three inputs (minutes
> per run, runs per week, minutes still spent reading the log) and one output, computed in
> `assets/site.js` from what the visitor typed. No per-step dollar estimate, because the cost of an
> AI step is not documented anywhere I can verify.
Specific and testable beats adjectives ("Save an average of X" is the Ramp pattern —
[ref](https://www.metabrand.digital/learn/best-startup-website-examples-2026)). Publish the maths,
not a claim: "10 steps × 2 min saved × 40 runs/week ≈ 80 min/week." Then a slider: runs/week ×
minutes-saved → hours/month, plus "AI steps this week ≈ $0.40 of your $12 balance". Only if the
per-step cost is genuinely predictable — otherwise publish the worked example you already have.

### P1.7 ✅ `/pricing/` — two missing blocks
1. **Feature comparison table**, grouped (Automation · AI · Scheduling · Support), ✓ and — explicitly,
   sticky header on desktop, stacked on mobile. 90% of good pricing sections treat it as table
   stakes ([ref](https://www.webanatomy.ai/best-landing-pages/sections/pricing)).
2. **Annual toggle.** Two months free = 16.7% off, which outperforms round-number discounts on
   annual adoption ([ref](https://successknocks.com/b2b-saas-pricing-page-best-practices/)). Only if
   Lemon Squeezy has an annual price to point at.
Also add: "what happens when the balance runs out" (does a run fail, queue, or fall back to rules?),
plan FAQ (upgrade/downgrade/proration), and keep three tiers — 4+ tiers convert ~31% worse.

### P1.8 ✅ `/security/` page — for an extension, this is a sales page
A permission table (which permission, why, what it can and cannot do), a data-flow diagram
("nothing leaves the browser except the page context you approve for an AI step"), retention and
deletion, subprocessors, and the "we do not sell or proxy your credentials" line you already have.
Link it under the install CTA, not only from the footer. Your blog post on
`all-urls` permission is 70% of this page — promote it into a real doc.

### P1.9 ✅ Docs / quickstart (retention is ranking)
`/guides/first-workflow/` with the 3-minute GIF, `/guides/when-a-step-fails/` (element not found,
retry counts, dynamic delays, conditions), shortcut list, and a "run report" explainer. Uninstalls
right after install hurt store ranking; onboarding fixes that more cheaply than any ad.

> Shipped: `/guides/first-workflow/` carries the five-step recipe and, in the same page, "When the
> first run misbehaves" (element not found, half-typed value, verification gate, missed alarm,
> empty extraction). A separate `/guides/when-a-step-fails/` was deliberately not published: it
> would duplicate that content, and thin near-duplicate pages cost more than they earn. Split it
> out when there is more to say than a paragraph each.

### P1.10 Headline work (A/B the hero)
The hero passes the "outcome in ≤8 words" rule but not the "stranger can name the category in
3 seconds" rule. Keep *Show it once. Let it run.* as the brand line and let the subhead do the
naming, or test these:

| # | H1 | Note |
| --- | --- | --- |
| 1 | Show it once. Let it run. | current; abstract, memorable |
| 2 | The clicks you repeat, automated. | names the job |
| 3 | Automate the sites with no API. | sharpest differentiator, best for /showcase |
| 4 | Auto-clicker that doesn't break when the page moves. | keyword-matched, unglamorous, likely best from paid search |

Subhead that fixes clarity for all four: *"ORCA is a Chrome extension: pick the buttons and fields
you use, set retries, delays and conditions, then run the workflow on demand or on a timer."*

---

## 4. P2 — craft, speed, measurement

- **P2.1 Serve your own images.** Right now 5 full-size 1280px PNG/JPEGs are hot-linked from
  Google's CDN: no WebP/AVIF, no `srcset`, a foreign origin on the critical path, and cache headers
  you don't control. Export at 1280/800/480 widths, `loading="lazy"` below the fold (done), hero
  preloaded (done this pass). Budget: LCP < 2.5s, CLS < 0.1, total page weight < 500 KB without video.
- **P2.2 Mobile is a product decision, not a resize.** 58% of pricing-page traffic is mobile
  ([ref](https://influenceflow.io/resources/saas-pricing-page-best-practices-complete-guide-for-2026/)):
  stack tiers (done), turn `.shots` into a `scroll-snap` row, keep the CTA in the first 500px
  (verified: ~460px of hero content at 375×667 today), 44px+ targets (48px ✓), one still instead of
  the loop on mobile if weight gets close to budget.
- **P2.3 Motion.** You have one fade. Add per-item stagger (150ms), hover elevation on interactive
  things only, `animation-timeline: view()` where supported with a plain fallback, and never more
  than two simultaneous animations on a screen.
- **P2.4 Typography discipline.** Serif display is working. Cap measure at ~66ch (currently 650px
  ≈ 68–75 chars at 1.1rem — close), align the section-heading rhythm to one scale, and try replacing
  the 999px pill buttons with 10px-radius rectangles — pill-shaped CTAs are the most
  template-identifying element on modern AI sites. Do it as a branch, look at both, pick one.
- **P2.5 Colour budget.** Ink + violet + one mint. Peach/yellow/mint simultaneously reads as a
  palette generator rather than a brand. The gradient CTA panel is the other "AI SaaS" tell: an
  ink panel with a violet hairline carries the same weight, more calmly.
- **P2.6 One goal per page.** Remove outbound store links from the nav (keep the header CTA), and
  repeat the install CTA at three scroll points — hero, mid-page after proof, end — with identical
  wording each time ("the final CTA repeats the hero offer verbatim" is the pattern).
- **P2.7 Instrument before you optimise.** Your consent-gated `GA_MEASUREMENT_ID` hook is already in
  `site.js`; fill it and extend `script-src`/`connect-src`. Events worth defining now:
  `store_click`, `video_play`, `pricing_view`, `checkout_click`, `template_open`, `faq_open`,
  `scroll_depth`, `changelog_view`. Add UTM links on the store buttons so you can attribute installs
  to the site at all — the store dashboard won't tell you where the click came from.
- **P2.8 Share cards.** `twitter:site`, per-template `og:image`, and `og:video` once the clip exists
  (video in the preview card is the cheapest reach you can buy for free).
- **P2.9 SEO hygiene.** `Article` + `BreadcrumbList` JSON-LD on posts; internal links from each post
  to the two templates it mentions; a `/blog/` index that says how many posts exist. Long-tail pages
  ("auto click every 5 seconds chrome", "fill web form automatically without code") are winnable now;
  they are not after someone else's template library gets bigger.
- **P2.10 Small honesty repairs already made this pass** — kept here so they don't regress: no
  section headline may talk about asset provenance; no `<picture>` may contain generated UI; every
  alt describes only what is verifiably in the image; `site.js` hides any tile whose image 404s.

---

## 5. Do-not-do list

| Temptation | Why not |
| --- | --- |
| Testimonial quotes with generated faces | Explicitly a trust hazard; and it's fraud in most jurisdictions ([ref](https://www.lovart.ai/blog/01-industry-saas-landing-page)) |
| "Trusted by teams at …" logo strip | You don't have them; the strip is the first thing a buyer pattern-matches as fake |
| Live "John from Berlin installed 5 minutes ago" pop-ups | Works on impressions, destroys trust with the audience that buys automation |
| Countdown/urgency timers on a tool subscription | Mismatched category signal |
| "Browser agent that learns anything" | Not what the store listing claims today; costs you both credibility and store search relevance |
| Scraping-LinkedIn-as-headline use case | It is what the category's reviews fixate on and what pushes you toward ToS and store-policy trouble; describe data extraction generically instead |

---

## 6. Two-week plan

| Day | Work | Done means |
| --- | --- | --- |
| 1 | Clean Chrome profile, seed data, record 3 scenes | raw clips, 2× capture |
| 2 | Cut 41s, no narration, captions, encode webm+mp4 ≤6 MB, hero swap | LCP still < 2.5s |
| 3 | Store: name, summary, annotated screenshots, promo tile, upload video, review prompt | new listing submitted |
| 4 | Process-proof block (run log + sample output + named developer) on `/` and `/products/` | proof above the 2nd scroll |
| 5 | `/changelog/` + `/refund-policy/` summary next to CTAs | two dated entries live |
| 6–8 | `/templates/` with 3 real templates + import snippets | 3 indexable pages |
| 9–10 | Pricing: comparison table, annual toggle, "balance runs out" explainer | table on mobile without horizontal scroll |
| 11–12 | `/security/` page + docs quickstart | linked from the install CTA |
| 13–14 | GA4 events, UTMs, baseline metrics recorded | dashboard exists |
| then | A/B the four H1s one at a time, 2–4 weeks each | one variable at a time |

Baselines to record on day 1 so the changes are measurable: store impressions, store install rate,
uninstall rate at 7 days, rating count, site→store clicks per session, pricing→checkout clicks,
scroll depth at 50%, mobile share of sessions.
