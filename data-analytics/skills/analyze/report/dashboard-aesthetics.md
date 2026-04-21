# Dashboard and Report Aesthetics

Interactive-specific guidance loaded by `report.md` (Phase 4 of `/analyze`) when the user picks **Design-first** in question 3. Consume this alongside the shared principles in `skills-guides/visual-craftsmanship.md` (provided at the agent root).

## Type pairings by artifact class

Pair a display face with a body face. The display appears on headings, hero KPIs and page marks; the body appears on prose, table cells and labels.

| Artifact class | Display | Body | Good for |
|---|---|---|---|
| Executive dashboard | Fraunces (variable) | Inter | Board-level, quarterly, strategic |
| Technical report | Instrument Serif | IBM Plex Sans | Engineering audiences, incident reviews |
| Editorial brief | Crimson Pro | Inter or Work Sans | Narrative reports, recommendations |
| Forensic audit | IBM Plex Serif | IBM Plex Mono | Regulatory, audit, QA documents |
| Maximalist analytical | Archivo Black | Inter | Launch decks, highly visual KPIs |
| Brutalist data | Archivo Black | IBM Plex Mono | Research previews, release notes |

Serve fonts via `@import` from a foundry or Google Fonts in the generated HTML, or bundle WOFF2 copies alongside the artifact and reference them with `@font-face`. Two faces are enough; three is the ceiling.

## Palette direction by subject

Derive the dominant accent from the data's subject matter. One colour does most of the work; the supporting neutrals carry the composition.

| Subject | Dominant accent | Deep neutral | Pale neutral |
|---|---|---|---|
| Finance, banking | `#0a2540` (deep navy) or `#8a3324` (oxblood) | `#201a16` | `#f5ecdf` (cream) |
| Operations, supply chain | `#1f4a3a` (forest) or `#315a82` (steel) | `#16191f` | `#eef3f7` |
| Audit, compliance | `#5a1c1c` (deep red) | `#121212` | `#f2ebe8` (bone) |
| Consumer products | `#d9472b` (tomato) or `#7a3ea6` (berry) | `#1a1a1f` | `#f6f1e7` |
| Health, pharma | `#135169` (teal-blue) | `#16222b` | `#edf2f3` |
| Industrial, energy | `#c28b2c` (amber) or `#3c3c3c` (graphite) | `#111111` | `#efece7` |

When emitting `palette_override`, stick to CSS tokens that the chosen base style declares:

- `corporate` and `modern` define `--primary`, `--accent`, `--text-primary`, `--bg-light`, `--font-main`, `--font-mono`.
- **Caveat — `academic`** does not define `--primary`. Its `primary` palette role maps to `--heading-color` (see `_PALETTE_MAP` in `tools/css_builder.py`). Overriding `--primary` for `academic` has no effect; override `--heading-color` or switch to `corporate` as the base style.

## Motion (dashboards only)

CSS-only, no JS. Use keyframes prefixed `dashboard-*` to avoid collisions with any host page. Honour `prefers-reduced-motion: reduce` by cancelling animations and transitions.

| Budget | When to pick | What it emits |
|---|---|---|
| `none` | Static-reading dashboards, printouts, contexts where motion distracts | Nothing extra |
| `minimal` | Most dashboards | 320 ms `dashboard-fade-in` on KPI cards and sections |
| `expressive` | Launch dashboards, hero reveals, product narratives | Staggered `dashboard-rise` on KPI cards (80 ms steps), section reveal, card hover lift |

Keep page-load motion under ~500 ms total. Plotly performs its own chart animation imperatively — do not attach CSS animations to `.js-plotly-plot` descendants.

## Backgrounds

The `background_style` key supports four modes; each is rendered inline without external assets.

- `solid` — no extra CSS, the base surface wins.
- `gradient-mesh` — layered radial gradients tinted by the accent; good for editorial dashboards.
- `noise` — a static SVG noise filter layered behind the content; good for maximalist or brutalist dashboards.
- `grain` — fine dotted pattern at 3 px pitch; good for analog or editorial tones.

Avoid noise on dense data tables — it lowers contrast.

## Hover and focus states

Every interactive element (filter, sort handle, nav link, KPI card in drill-down mode) needs a deliberate hover and focus state. Rules of thumb:

- **Hover**: a 1–2 px translate up or a 180 ms shadow expansion. Colour-only hover reads as accidental.
- **Focus**: an outline in the accent colour, visible on keyboard navigation (`:focus-visible`).
- **Active**: a depressed state — return to baseline translate, slightly darker surface.

## `aesthetic.json` canonical schema

This is the file `report.md` writes to `output/[ANALYSIS_DIR]/aesthetic.json` and passes to every generator.

```json
{
  "tone": "editorial-serious",
  "palette_override": {
    "--primary": "#0a2540",
    "--accent": "#d9472b",
    "--text-primary": "#1a1a1f"
  },
  "font_pair": ["Fraunces", "Inter"],
  "motion_budget": "expressive",
  "background_style": "gradient-mesh"
}
```

All keys are optional; unknown keys are rejected by `md_to_report.py --aesthetic` and by the internal validator. `font_pair` must be a two-item list `[display, body]`. `tone` is currently informational (used for traceability in `reasoning.md`); it does not directly drive CSS — the palette and fonts do.

### How generators consume it

| Target | Tool | Entry point | What changes |
|---|---|---|---|
| HTML dashboard | `DashboardBuilder(aesthetic_direction=…)` | `.build()` | CSS tokens overridden, display font rule, motion CSS, background rules |
| PDF (from scaffold/HTML) | `PDFGenerator(aesthetic_direction=…)` | `.render_scaffold()` / `.render_from_html()` | CSS tokens overridden |
| DOCX | `DOCXGenerator(aesthetic_direction=…)` | `.render_scaffold()` / `.render_from_markdown()` | palette overridden (fonts only affect heading fills today) |
| PPTX | `create_presentation(style, aesthetic_direction=…)` | returns `(prs, palette)` | palette overridden |
| Charts | `chart_layout.get_chart_colors(style, n, aesthetic_direction=…)` | returns hex list | Plotly figure colours match the rest of the artifact |
| CLI (markdown → PDF) | `md_to_report.py --aesthetic aesthetic.json` | argparse | flows through `convert()` to PDF + optional DOCX |
