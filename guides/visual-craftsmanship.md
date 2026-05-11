# Visual Craftsmanship Guide

Shared principles for every skill that produces visual output — interactive interfaces, static artifacts, typographic documents, dashboards, reports. Treat this as the source of truth for aesthetic decisions across the monorepo.

## Why this guide exists

Generated visual output defaults to an unmistakable look: Inter or system sans everywhere, soft purples on off-white, evenly spaced cards with identical shadows, tables that sit in the middle of a page with no margin personality. That aesthetic is *safe* in the worst sense — it communicates "no one decided anything".

The skills that reference this guide resist that default. Every artifact that reaches a user should carry the fingerprint of a deliberate choice: a tone committed to, a palette with saturation, typography chosen for meaning rather than availability, space arranged with intent. Even a one-minute chart deserves three minutes of visual judgement beforehand.

## Core principles

### 1. Design before code
State the aesthetic direction in words before writing a single line of markup, reportlab, or CSS. A two-paragraph intent is cheaper than refactoring a finished artifact.

Five decisions, in this order:
1. **Artifact class** — what is this thing? (Dashboard, executive brief, poster, certificate, technical report, invoice, zine, landing page.) Its class governs everything downstream.
2. **Tone** — pick one and commit. Editorial-serious, technical-minimal, warm-magazine, brutalist-raw, luxury-refined, industrial-utilitarian, playful-toy, forensic-audit. A lukewarm mix of two is worse than either extreme.
3. **Type pairing** — one display face for headings or display moments, one body face for prose or data. Two typefaces cover nearly every artifact; three is the practical ceiling.
4. **Palette** — one dominant accent with real saturation, one deep neutral for text (rarely pure black), one pale neutral for backgrounds or rules, plus optional accents used sparingly.
5. **Rhythm** — margins, column structure, baseline grid, motion budget (for interactive artifacts). Generous margins read as confidence; cramped margins read as a word-processor default.

### 2. Commit to the direction
Intensity matters less than coherence. Minimal and maximalist both work; a "bit of everything" never does. Once the direction is chosen, every element — background texture, hover state, chart colour, table border — earns its place by serving that direction or being removed.

### 3. Craftsmanship as a standard, not a slogan
A finished artifact should carry the marks of deliberate labour: consistent baseline, aligned margins, purposeful contrast, no accidental stock patterns, no orphaned legends, no overlapping text. The final pass is for polish, not for adding. If the instinct is to draw one more shape, stop and refine what is already there.

### 4. Make it unmistakable
One memorable move beats ten polite touches. Unusual typography contrast, a single hero moment that breaks the grid, a background texture that matches the topic, a hover state that surprises — any of these, executed with care, elevates an artifact from generic to considered.

## Anti-patterns to refuse

These are the tells of default output. None is absolutely forbidden, but each should be a conscious choice against the alternative, not a reflex.

- **Generic sans as the only typeface**: Arial, Helvetica, Roboto, Inter, and unstyled system-ui everywhere. If the artifact deserves attention, its typography should be part of what earns it.
- **Washed palettes**: pastel tints without saturation, greys without temperature, and especially purple-on-white gradients (the single most overused AI aesthetic).
- **Symmetry by habit**: everything centred, identical card shadows, equal margins on all four sides when the content does not demand it.
- **Bootstrap-shaped cards**: rectangles with a 6–8 px shadow and 1 rem padding, arranged in a three-column grid, on every page, regardless of content.
- **Three-font crowd**: display + body + "accent" fonts layered without reason. Two is enough for almost every artifact.
- **Chart decor**: gridlines in every direction, 3D bars, rainbow categorical palettes, legends floating through data.
- **Table as blackbox**: zebra striping by default, heavy inner borders, centred numeric columns.
- **Loose white rectangles**: headings that sit in the middle of whitespace with no structural anchor (no rule, no margin cue, no background variation).

## Palette roles

Define colours by role, not by shade name. Four roles cover almost every artifact:

| Role | Purpose | Guidance |
|---|---|---|
| Dominant accent | The one colour that signals the brand or subject of the artifact. | Use real saturation. Apply to 5–15 % of the visible area — headings, key marks, hero moments. |
| Deep neutral | Body text, primary strokes, dense data. | Rarely `#000`. Prefer a desaturated charcoal, a warm espresso, a deep indigo. |
| Pale neutral | Backgrounds, rules, table dividers. | Not pure white. Off-white, bone, a barely-tinted surface reads more intentional. |
| Acceptable accents | Second and third colours for state (positive/negative, success/error, annotations). | Sparing. Saturation consistent with the dominant — no stray neon next to a muted primary. |

Six rendered colours is plenty. Tokenise them; never hand-type hex twice.

## Type pairing philosophy

Pick one display face and one body face. The pairing should create deliberate contrast, not a safe match.

Useful contrast axes:
- Serif display + sans body (classic editorial).
- Sans display + serif body (modern magazine).
- Mono display + sans body (technical-forensic).
- Condensed sans display + wide-tracked sans body (editorial-graphic).

Rules of thumb:
- Body face: wide language coverage, humanist enough to read at 9–11 pt for prose, with italic and bold.
- Display face: earns attention at 24 pt and above. Can be idiosyncratic; does not need full italic.
- Treat numerals seriously. If the artifact shows lots of figures, use a monospaced or tabular-lining face for them.
- Do not mix two serifs or two sans-serifs with similar silhouettes. The pairing should be legible at a glance: *these are clearly different*.

Each skill that uses this guide should define its own short list of pairings by artifact class. This guide does not prescribe specific families — foundries change, licences change, and each medium has different constraints.

## Craftsmanship checklist

Before delivering, take one last pass. The goal of this pass is restraint, not addition.

- Every aligned element actually aligns. Baselines, left edges, column tops.
- Margins are consistent and honour the intended rhythm.
- No overlapping text, no orphaned labels, no legends leaking into the plot area.
- Colours appear in the numbers they were designed for. A palette with five colours should not show seven.
- Typography has no unintended weights or styles. A "light" font weight did not slip into a heading.
- Every image, texture, or pattern has a reason. If one can be removed without weakening the artifact, remove it.
- Any text that looks like filler — "Lorem ipsum", placeholder captions, default demo strings — is gone.
- For artifacts with motion: motion respects reduced-motion preferences; no animation loops without reason; nothing moves where the user needs to read.

## Disambiguation between visual skills

Three skills in this monorepo produce visual output and intentionally share this guide. They are complementary, not overlapping.

| Skill | Medium | When to use |
|---|---|---|
| `web-craft` | Interactive frontend (HTML/CSS/JS, React, Vue) | Components, pages, landing sites, dashboards, interactive artifacts. The artifact is alive in a browser. |
| `canvas-craft` | Static single-page artifact (PDF or PNG) | Posters, covers, certificates, marketing one-pagers, infographics. Visual composition dominates (roughly seventy per cent or more of the surface). Minimal text, typography as visual element. |
| `pdf-writer` | Multi-page typographic document, or single-page document dominated by prose, tables, or data (PDF) | Analytical reports, financial statements, invoices, contracts, editorial zines, technical documentation. Type and rhythm dominate; arrangement serves reading. |

### Boundary cases

- **Executive one-pager, dense prose and KPIs** → `pdf-writer`. The artifact reads; it does not pose.
- **Marketing one-pager, hero image and a claim** → `canvas-craft`. The artifact poses; it does not read.
- **Interactive dashboard with KPIs** → `web-craft`. Interaction is the point.
- **Report with a designed cover** → combined pipeline: `canvas-craft` produces the cover, `pdf-writer` assembles the body, final merge with `pypdf`.

When none of these fits cleanly, the artifact probably needs more definition before tool selection. Return to the five decisions at the top of this guide and classify the artifact first.

## Note on standalone distribution

If this guide is bundled into a single skill package for external distribution (without the other visual skills alongside), the disambiguation table above still serves as context. It signals that the skill is part of a three-skill family with distinct responsibilities. Consumers without the companion skills can still use the principles — the tone selection, anti-patterns, palette roles, and checklist are self-contained and do not depend on the other skills.
