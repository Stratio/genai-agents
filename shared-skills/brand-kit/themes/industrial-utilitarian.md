# Industrial Utilitarian (draft v1)

Slate blue-gray over a neutral page, amber for signaling, a grotesque
sans throughout. Reads as functional and unsentimental — designed for
operations reports, logistics dashboards, SRE post-mortems and any
content where the visual language should echo the physical language of
control rooms and signage.

> **Draft v1** — this theme was designed for this kit from the
> `industrial-utilitarian` tone defined in
> `skills-guides/visual-craftsmanship.md`. Loose inspiration drawn
> from the `corporate-formal` base palette in the monorepo, but the
> tone is shifted deliberately toward functional / signaling. Iterate
> based on feedback from first uses.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #37474f | headers, rules, section markers |
| ink | #1f2933 | body text |
| muted | #52606d | secondary labels |
| rule | #cbd2d9 | dividers, borders |
| bg | #f5f7fa | light neutral page (not white) |
| bg_alt | #e4e7eb | callout blocks, status bars |
| accent | #f5a623 | signaling amber — the "attention" color |
| state_ok | #3d7a3d | operational green |
| state_warn | #f5a623 | alerts (same hue as accent) |
| state_danger | #c62828 | critical errors / incidents |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #37474f | matches primary |
| 2 | #f5a623 | matches accent |
| 3 | #3d7a3d | operational green |
| 4 | #c62828 | incident red |
| 5 | #5c6ac4 | steel blue (categorical diversity) |
| 6 | #6b7b80 | neutral filler |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | Inter | 28 weight 700 | Arial, sans-serif |
| h2 | Inter | 18 weight 600 | Arial, sans-serif |
| body | Inter | 10 | Arial, sans-serif |
| caption | Inter | 9 | Arial, sans-serif |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

Grotesque sans throughout. Smaller body size (10 pt) because the tone
accepts — and expects — denser information in each view.

## Optional extensions

- **Motion budget**: `minimal`
- **Border radius**: `2px`
- **Dark mode variant**: `bg` = `#1f2933`, `ink` = `#e4e7eb`,
  `primary` = `#90a4ae`, keep `accent`
- **Chart sequential**: base color `#37474f`

## Tone family

`industrial-utilitarian`.

## Best used for

- Operations and logistics dashboards, SRE reports
- Incident post-mortems, ops reviews
- Plant / facility reports, supply-chain status documents
- Any context where the aesthetic of signage, control rooms and
  industrial hardware is an appropriate echo

## Anti-patterns

- Do not use for marketing, client-facing or narrative deliverables —
  the tone is deliberately functional and reads as "internal tool".
- Do not substitute the amber accent for a second blue; the warm
  signal against the cool base is the theme's mechanism.
- Do not add decorative iconography or rounded shapes; the theme
  leans toward hard edges and utilitarian geometry.
