# Brutalist Raw (draft v1)

Unpolished, high-contrast, intentionally unornamented. A near-black
surface on off-white, a saturated industrial orange as the accent,
monospace everywhere. The theme reads as "this is data exposed" — built
for raw exploratory reports, developer-facing documents, data dumps and
any deliverable where politeness would feel dishonest.

> **Draft v1** — this theme was designed for this kit from the
> `brutalist-raw` tone defined in `skills-guides/visual-craftsmanship.md`.
> No direct precedent exists in the monorepo. Iterate based on feedback
> from first uses.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #111111 | everything structural — headers, rules, borders |
| ink | #111111 | body text (same as primary — single-chroma theme) |
| muted | #525252 | secondary labels, comments |
| rule | #111111 | thick rules (intended to be used at 2–3 pt weight) |
| bg | #fafafa | off-white page |
| bg_alt | #ededed | blocks, table bands |
| accent | #ff3d00 | the one saturated pop — only for critical emphasis |
| state_ok | #16a34a | positive indicators |
| state_warn | #ff8c00 | alerts (coherent with accent warmth) |
| state_danger | #dc2626 | critical errors |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #111111 | matches primary |
| 2 | #ff3d00 | matches accent |
| 3 | #525252 | mid-gray |
| 4 | #16a34a | industrial green |
| 5 | #ff8c00 | second warm |
| 6 | #737373 | neutral filler |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | IBM Plex Sans | 34 weight 700 | Arial Black, sans-serif |
| h2 | IBM Plex Sans | 22 weight 700 | Arial Black, sans-serif |
| body | IBM Plex Mono | 10 | Consolas, monospace |
| caption | IBM Plex Mono | 9 | Consolas, monospace |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

Heavy sans for headlines, monospace for everything else. The contrast
of weights (bold display against regular monospace) is the theme's
typographic signature.

## Optional extensions

- **Motion budget**: `minimal` (brutalism does not animate)
- **Border radius**: `0px` (hard edges, always)
- **Dark mode variant**: `bg` = `#111111`, `ink` = `#fafafa`, keep
  `primary` and `accent`
- **Chart sequential**: base color `#111111`

## Tone family

`brutalist-raw`.

## Best used for

- Exploratory data analysis reports (first-pass, raw findings)
- Developer-facing documentation and engineering post-mortems
- Data dumps, log analyses, debug reports
- Any artifact where "polished" would feel dishonest about the state
  of the content

## Anti-patterns

- Do not soften with rounded corners, shadows or gradients — those
  directly contradict the tone.
- Do not use for client-facing or executive deliverables.
- Do not expand the accent color into large surfaces; the saturated
  orange is a warning light, not a brand wrap.
