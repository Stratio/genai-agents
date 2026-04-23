# Corporate Formal

The traditional office palette — a deep corporate navy, a brighter
business blue for secondary emphasis, system-safe typography that
renders identically on every machine. Built for steering committees,
board packets and regulated reporting where the deliverable must feel
institutional and universally readable.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #1a365d | headers, footers, cover blocks |
| ink | #1a202c | body text |
| muted | #4a5568 | captions, footnotes |
| rule | #e2e8f0 | dividers, table borders |
| bg | #ffffff | page / main surface |
| bg_alt | #f7fafc | table bands, callouts |
| accent | #3182ce | secondary emphasis, links, chart highlights |
| state_ok | #38a169 | positive indicators |
| state_warn | #d69e2e | alerts |
| state_danger | #e53e3e | critical errors |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #1a365d | matches primary |
| 2 | #3182ce | matches accent |
| 3 | #38a169 | business green |
| 4 | #d69e2e | corporate amber |
| 5 | #805ad5 | violet (categorical diversity) |
| 6 | #e53e3e | red (used sparingly, coherent with state_danger) |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | Calibri | 24 | Aptos, Arial, sans-serif |
| h2 | Calibri | 16 | Aptos, Arial, sans-serif |
| body | Calibri | 11 | Aptos, Arial, sans-serif |
| caption | Calibri | 9 | Aptos, Arial, sans-serif |
| mono | Consolas | 10 | Courier New, monospace |

The system-safe choice (Calibri / Aptos / Arial) is deliberate: corporate
reports must render identically on every machine, including Office
installations without custom fonts embedded.

## Optional extensions

- **Motion budget**: `minimal` (corporate content does not animate)
- **Border radius**: `2px`
- **Dark mode variant**: not shipped
- **Chart sequential**: base color `#1a365d`

## Print variant (for pdf-writer)

Corporate print documents benefit from a slightly warmer paper and a
softer near-black to avoid the clinical feel of pure white + pure black:

| Token | Hex | Notes |
|---|---|---|
| paper | #fafaf8 | near-white, very slight warmth |
| ink | #1a1a1a | warm near-black (softer than pure black) |
| rule | #dcdfe4 | hairline tint, slightly warmer than the screen rule |
| accent | #3182ce | unchanged — business blue prints well |

Font sizes and typography are the same as in the core block.

## Tone family

`editorial-serious` (corporate variant with system-safe typography).

## Best used for

- Board packets and steering-committee reports
- Regulatory filings, annual reports, quarterly business reviews
- Internal memos and corporate policy documents
- Any deliverable where "it must render the same on every laptop" is
  a hard constraint

## Anti-patterns

- Do not substitute the system-safe fonts for a custom family — the
  theme's whole point is universal renderability.
- Do not add warm or vivid accents; the palette must stay within the
  corporate blue range.
- Do not use for consumer-facing marketing, where it reads as dated
  and generic.
