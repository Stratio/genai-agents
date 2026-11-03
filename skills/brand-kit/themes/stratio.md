# Stratio

Stratio's own look, the one GenAI UI already wears: Deep Navy titles and Stratio
Blue (action-7) for what can be clicked and the figures that matter, over white and the
cool space-1 surfaces in light mode; GenAI UI's space-17 ground and space-14
surfaces in dark mode. Every color comes from the SDS scales (space, action,
turquoise, peach, coral, lavender). The default when nobody asks for another
look.

## Color palette (core)

| Token | Hex | Role |
|---|---|---|
| primary | #0f1b27 | titles, top rules, cover accents (Deep Navy, space-17) |
| ink | #27323d | body text (space-13) |
| muted | #566574 | captions, footnotes (space-8) |
| rule | #cdd6df | thin dividers and subtle borders (space-3) |
| bg | #ffffff | page / main surface |
| bg_alt | #f3f6f8 | table bands, callout fills (space-1) |
| accent | #0059b8 | CTAs, links, key figures (action-7: Stratio Blue that white text reads on) |
| state_ok | #006466 | positive indicators (turquoise-8) |
| state_warn | #8a5403 | alerts (peach-9) |
| state_danger | #c92822 | critical errors (coral-7) |

## Chart categorical (5–8 ordered colors)

| # | Hex | Notes |
|---|---|---|
| 1 | #0076df | Stratio Blue (action-6) |
| 2 | #008c8a | turquoise-7 |
| 3 | #b0740c | peach-8, the brand's gold dark enough for marks |
| 4 | #ef4034 | coral-6 |
| 5 | #823eff | lavender-6 |
| 6 | #566574 | space-8 (filler for long series) |

## Typography

| Role | Family | Size (pt) | Fallback |
|---|---|---|---|
| display (h1) | Inter | 28 weight 700 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| h2 | Inter | 18 weight 600 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| body | Inter | 11 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| caption | Inter | 9 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| mono | Roboto Mono | 10 | SF Mono, Menlo, Consolas, monospace |

Inter and Roboto Mono are the brand's faces. Where they are not installed, the
system sans (San Francisco, Segoe UI, Roboto) is close enough to keep the look.

## Optional extensions

- **Motion budget**: `restrained` (web-craft transitions, pptx animations)
- **Border radius**: `4px` (web-craft)
- **Dark mode variant**: see [Dark mode](#dark-mode)
- **Chart sequential**: `#0076df` (the SDS action scale, action-0 `#e6f3ff` to action-9 `#002d6b`)

## Print variant (for pdf-writer)

| Token | Hex | Notes |
|---|---|---|
| paper | #ffffff | white, as the brand's documents |
| ink | #0f1b27 | Deep Navy body text prints crisper than space-13 |
| rule | #cdd6df | space-3 |
| accent | #0059b8 | unchanged |

## Dark mode

| Token | Hex |
|---|---|
| bg | #0f1b27 |
| bg_alt | #212c38 |
| ink | #f3f6f8 |
| muted | #aab7c4 |
| rule | #3d4a57 |
| primary | #ffffff |
| accent | #6db3f3 |
| state_ok | #41ccbc |
| state_warn | #fdbd2b |
| state_danger | #ff998a |
| on_primary | #0f1b27 |
| on_accent | #0f1b27 |

Chart categorical: `#399aef`, `#1fbfb2`, `#fdbd2b`, `#fc7060`, `#be8fff`, `#9aa9b8`

## Tone family

`technical-minimal` (see `guides/visual-craftsmanship.md`).

## Best used for

- Any deliverable when nobody asks for another look
- Reports, dashboards and documents shared outside with the Stratio brand
- Pages that sit next to GenAI UI and should look like part of it

## Anti-patterns

- Stratio Blue only for what can be clicked, key figures and the first series;
  titles stay in Deep Navy.
- White on Stratio Blue `#0076df` reads 4.45:1, short of 4.5: buttons and links
  take action-7 `#0059b8` (the accent); `#0076df` stays for chart series and
  large marks.
- Do not swap the space grays for neutral ones: their blue bias is the brand.
