# Luxury Refined (draft v1)

Warm neutral over cream, serif display, generous spacing, a single
restrained metallic accent. The theme reads as considered, premium,
unhurried — built for board decks, executive summaries and
premium-client deliverables where the form itself communicates quality.

> **Draft v1** — this theme was designed for this kit from the
> `luxury-refined` tone defined in `skills-guides/visual-craftsmanship.md`.
> No direct precedent exists in the monorepo. Iterate based on feedback
> from first uses.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #2a211a | headers, drop caps, rule accents |
| ink | #2a211a | body text (same as primary for tonal cohesion) |
| muted | #7a6f63 | captions, attributions |
| rule | #e8dfd2 | delicate dividers |
| bg | #f8f0e3 | cream page |
| bg_alt | #efe5d3 | sidebar, pull quotes |
| accent | #8b6f47 | bronze / metallic restraint |
| state_ok | #4d7c3a | positive (muted, not vivid) |
| state_warn | #a17c2a | alerts (coordinated with accent bronze) |
| state_danger | #7a2121 | critical errors (deep, not urgent-red) |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #2a211a | matches primary |
| 2 | #8b6f47 | matches accent |
| 3 | #4d7c3a | muted green |
| 4 | #5c4a6c | aubergine |
| 5 | #a17c2a | second metallic |
| 6 | #7a6f63 | neutral filler |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | Italiana | 34 | Didot, Bodoni, serif |
| h2 | Italiana | 22 | Didot, Bodoni, serif |
| body | Crimson Pro | 11 | Georgia, serif |
| caption | Crimson Pro Italic | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

High-contrast display serif (Italiana is thin-stroked and elegant)
paired with a sturdy book serif for the body.

## Optional extensions

- **Motion budget**: `restrained` (slow reveals, never jumpy)
- **Border radius**: `1px`
- **Dark mode variant**: not shipped (luxury themes rarely go dark —
  the cream-page warmth is the point)
- **Chart sequential**: base color `#8b6f47`

## Tone family

`luxury-refined`.

## Best used for

- Board decks, chair letters, annual overview books
- Private-client advisory deliverables
- Steering-committee and executive-summary documents
- Any artifact where "premium" is part of the message

## Anti-patterns

- Do not use vivid saturated chart colors — the whole palette lives
  in muted warms and a restrained metallic.
- Do not use for dense data dashboards; the generous spacing and
  elegant display type are wasted on small, repeated components.
- Do not substitute the cream `bg` for pure white; the off-white warmth
  is what separates this theme from generic corporate.
