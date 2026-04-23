# Editorial Serious

Serif-led typography over a near-white page, deep navy as the anchor and a
warm terracotta as the single intentional pop. Conveys institutional
gravitas without ornament — the tone of a long-form policy paper or a
multi-page analytical report.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #0a2540 | titles, top rules, cover accents |
| ink | #1f2937 | body text |
| muted | #6b7280 | captions, footnotes |
| rule | #d1d5db | thin dividers and subtle borders |
| bg | #ffffff | page / main surface |
| bg_alt | #f3f4f6 | table bands, callout fills |
| accent | #b84c2c | CTAs, highlights, intentional pops |
| state_ok | #047857 | positive indicators |
| state_warn | #b45309 | alerts |
| state_danger | #b91c1c | critical errors |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #0a2540 | matches primary |
| 2 | #b84c2c | matches accent |
| 3 | #047857 | green (balances the red accent) |
| 4 | #6366f1 | indigo (wide hue separation) |
| 5 | #b45309 | amber (reads as a distinct warm) |
| 6 | #6b7280 | muted gray (filler for long series) |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | Instrument Serif | 32 | Georgia, serif |
| h2 | Instrument Serif | 22 | Georgia, serif |
| body | Crimson Pro | 11 | Georgia, serif |
| caption | Crimson Pro | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

## Optional extensions

- **Motion budget**: `restrained` (web-craft transitions, pptx animations)
- **Border radius**: `2px` (web-craft)
- **Dark mode variant**: not shipped (derive by swapping `bg` ↔ `ink`,
  keep primary and accent)
- **Chart sequential**: not shipped

## Print variant (for pdf-writer)

On paper, the screen palette needs a warm off-white in place of pure
white and a warm near-black instead of the regular ink:

| Token | Hex | Notes |
|---|---|---|
| paper | #faf8f4 | warm off-white page |
| ink | #1a1a1a | warm near-black body text |
| rule | #e5e0d8 | hairline tint coordinated with paper |
| accent | #b84c2c | unchanged — terracotta prints well |

Font sizes and typography are the same as in the core block.

## Tone family

`editorial-serious` (see `skills-guides/visual-craftsmanship.md`).

## Best used for

- Multi-page analytical and BI reports (5+ pages)
- Legal briefs, policy documents, long-form prose
- Institutional and steering-committee deliverables

## Anti-patterns

- Do not pair with aggressive transitions or gradients in PPTX.
- Avoid as the hero palette of a tech-product landing page.
- Do not substitute the accent for a second primary blue — the single
  warm pop is what makes the theme read as editorial rather than
  anonymous-corporate.
