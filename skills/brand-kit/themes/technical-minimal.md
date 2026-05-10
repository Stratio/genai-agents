# Technical Minimal

A functional, low-chroma surface anchored on a crisp primary blue, with an
amber accent reserved for the one thing the reader must notice. Built for
dashboards, engineering documentation and runbooks — content where the
data is the story and the theme should step back.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #0369a1 | section titles, primary rules, KPI highlights |
| ink | #111827 | body text |
| muted | #4b5563 | captions, secondary labels |
| rule | #e5e7eb | dividers, table borders |
| bg | #ffffff | page / main surface |
| bg_alt | #f9fafb | table bands, callout fills |
| accent | #f59e0b | the single "look here" color |
| state_ok | #047857 | positive indicators |
| state_warn | #b45309 | alerts |
| state_danger | #b91c1c | critical errors |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #0369a1 | matches primary |
| 2 | #f59e0b | matches accent |
| 3 | #059669 | teal-green |
| 4 | #dc2626 | red (used sparingly, coherent with state_danger) |
| 5 | #8b5cf6 | violet for categorical diversity |
| 6 | #6b7280 | muted gray |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | IBM Plex Sans | 28 | Inter, Arial, sans-serif |
| h2 | IBM Plex Sans | 20 | Inter, Arial, sans-serif |
| body | IBM Plex Sans | 11 | Inter, Arial, sans-serif |
| caption | IBM Plex Sans | 9 | Inter, Arial, sans-serif |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

## Optional extensions

- **Motion budget**: `minimal` (tight transitions, no decorative motion)
- **Border radius**: `4px`
- **Dark mode variant**: not shipped (derive with `bg` = `#0b1220`,
  `ink` = `#e5e7eb`, keep primary and accent)
- **Chart sequential**: base color `#0369a1`

## Tone family

`technical-minimal`.

## Best used for

- Engineering dashboards, internal tools, SRE / ops documentation
- Runbooks, API docs, technical specifications
- Dense data views where the chrome must stay out of the way

## Anti-patterns

- Do not add warm background surfaces — the low chroma is the point.
- Do not use display type larger than the sizes above; this theme
  whispers, it does not announce.
- Do not pair with ornamental iconography or textured backgrounds.
