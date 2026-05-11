# Academic Sober

The look of a scholarly journal — generous margins, a classical serif
throughout, restrained chroma, and careful typographic hierarchy. Built
for research papers, whitepapers and long-form policy documents where
the form mirrors established academic conventions.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #312e81 | title, running head, section markers |
| ink | #1f2937 | body text |
| muted | #6b7280 | captions, footnotes, references |
| rule | #d4d4d8 | dividers, table grids |
| bg | #ffffff | page / main surface |
| bg_alt | #fafafa | abstract, quote blocks, pull quotes |
| accent | #312e81 | same as primary — the theme resists pops |
| state_ok | #166534 | positive indicators |
| state_warn | #92400e | alerts |
| state_danger | #991b1b | critical errors |

Note: `accent` collapses into `primary` deliberately. Academic writing
does not highlight things with a second color — it highlights with
italics, citations and hierarchy.

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #312e81 | matches primary |
| 2 | #525252 | neutral gray tone |
| 3 | #0e7490 | teal |
| 4 | #92400e | ochre |
| 5 | #6b21a8 | muted violet |
| 6 | #166534 | deep green |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | Libre Baskerville | 22 | Georgia, serif |
| h2 | Libre Baskerville | 16 | Georgia, serif |
| body | Libre Baskerville | 11 | Georgia, serif |
| caption | Libre Baskerville Italic | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

Single-family typography is traditional for academic publications. The
italic of the same family carries the role of captions and references.

## Optional extensions

- **Motion budget**: `minimal`
- **Border radius**: `0px`
- **Dark mode variant**: not shipped
- **Chart sequential**: base color `#312e81`

## Print variant (for pdf-writer)

Academic paper benefits from a classic warm paper stock reference
instead of pure white:

| Token | Hex | Notes |
|---|---|---|
| paper | #f9f6f0 | classical academic warm off-white |
| ink | #1f1f1f | warm near-black (slightly warmer than the screen ink) |
| rule | #d6d3cc | hairline tint coordinated with paper |
| accent | #312e81 | unchanged — deep indigo prints well as a restrained mark |

Margins in print editions should be on the generous side (≥ 2.5 cm).

## Tone family

`editorial-serious` (academic variant — note: the visual-craftsmanship
guide does not currently list an academic tone; this theme inherits
from editorial-serious with the classical serif typography as the
distinguishing trait).

## Best used for

- Academic research papers, dissertations, working papers
- Whitepapers with formal citation apparatus
- Policy analysis and long-form think-tank publications

## Anti-patterns

- Do not introduce a second typeface family — the single-serif
  austerity is the tone.
- Do not use for product marketing or customer-facing communications.
- Do not tighten margins to fit content; academic pages must breathe.
