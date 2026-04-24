# Quality Report Layout — Guide

Guide consumed by the writer skills (`pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`) when the agent delegates a quality-coverage report deliverable through the `quality-report` skill.

This guide captures the conventions that make a data quality coverage report recognisable across formats: a stable six-section anatomy (cover → executive summary → coverage matrix → rules detail → gaps → recommendations), a fixed iconography for rule status, KPI cards tuned for audit readability, and a deterministic layout so the same dataset reproduces the same skeleton month after month. The writer skills still apply their own craft on top of this guide — tokens come from the centralized theming skill selected in the host agent's branding cascade; this guide contributes the **quality-report patterns**.

## 1. Purpose and scope

Apply this guide whenever the agent produces a quality-coverage report in a file format (PDF, DOCX, PPTX, Dashboard web, Poster/Infographic) via the `quality-report` skill. Skip it for the Chat format — the chat response is free-form markdown, no format-specific decisions are needed.

The guide is format-agnostic where possible (same anatomy everywhere) and format-specific where a deliverable type dictates composition (section §6).

## 2. Canonical sections

Every file-format deliverable contains these six sections in this order. Section names render in the user's language (the agent passes `lang` to the writer); values that are codes (`OK`, `KO`, `WARNING`, `NOT_EXECUTED`, `CRITICO`, `ALTO`, `MEDIO`, `BAJO`) are not translated.

1. **Cover / Header** — title, domain, scope (full domain or specific tables), generation date, agent that produced the report.
2. **Executive summary** — tables analysed, rules total, rules breakdown (OK / KO / WARNING / NOT_EXECUTED), coverage estimate, gaps by criticality (CRITICO / ALTO / MEDIO / BAJO), rules created in this session (if any).
3. **Coverage by table** — matrix: one row per table, columns for each dimension (Completeness, Uniqueness, Validity, Consistency, plus any domain-specific dimensions provided by `get_quality_rule_dimensions`) + a coverage estimate column.
4. **Rules detail** — per table: list of existing rules with name, dimension, status, % pass, description. KO and WARNING rules visually highlighted (bold or colour-coded via `state_danger` / `state_warn`).
5. **Identified gaps** — prioritised list: table, column (or `—` if applies to the full table), missing dimension, priority, description/impact, recommendation.
6. **Recommendations and next steps** — prioritised bullets: KO/WARNING rules to investigate first, critical gaps to cover, effort estimate for full coverage.

If the user ran `create-quality-rules` during the current session, an optional **Rules created in this session** section goes between §4 and §5, with rule name, table, dimension, SQL logic and calculated status (OK / KO / WARNING / SIN_DATOS / created).

## 3. Iconography and status codes

Rule and dimension status is colour-coded and icon-coded. Writer skills pick the exact rendering (Unicode glyph in PDF/DOCX, CSS icon in web-craft, typographic glyph in canvas-craft) — the semantic mapping is fixed:

| Status | Icon (Unicode baseline) | Brand token |
|---|---|---|
| `OK` | ✓ (U+2713) | `state_ok` |
| `KO` | ✗ (U+2717) | `state_danger` |
| `WARNING` | ⚠ (U+26A0) | `state_warn` |
| `NOT_EXECUTED` | ○ (U+25CB) | `muted` |

For dimension coverage cells:

| Coverage | Icon | Brand token |
|---|---|---|
| Full rule covers the dimension | ✓ | `state_ok` |
| No rule for the dimension | ✗ | `state_danger` |
| Partial / only some columns covered | ◐ (U+25D0) | `state_warn` |
| Dimension not applicable for the table | — | `muted` |

Do not rely on colour alone — always pair icon + label. Colourblind-safe by contract: the icons carry the message even in a black-and-white print.

## 4. Gap prioritisation

Priorities are codes (`CRITICO`, `ALTO`, `MEDIO`, `BAJO`) — not translated. They render with a visual weight that matches their severity:

| Priority | Meaning | Visual treatment |
|---|---|---|
| `CRITICO` | Primary or foreign key without coverage; core business rule missing. Blocks safe use of the data. | Bold, `state_danger` accent, first in the list. |
| `ALTO` | Key descriptive column without coverage; mandatory business dimension missing. | Regular weight, `state_warn` accent. |
| `MEDIO` | Secondary column or optional dimension without rule, but business still functional. | Regular weight, `ink` default. |
| `BAJO` | Cosmetic or low-impact gap (e.g. format validation on an audit field). | `muted` colour, deprioritised visually. |

Sort gaps by priority first, then by table name (alphabetical). Within a priority group, order by column (alphabetical) so repeated executions produce the same sequence.

## 5. KPI cards (executive summary header)

Exactly four KPI cards sit at the top of the Executive summary. Order is fixed:

1. **Coverage %** — estimated coverage across the scope. Value formatted as percentage. Subtitle: "across N tables".
2. **Rules OK %** — fraction of executed rules that are OK. Value formatted as percentage. Subtitle: "N of M rules".
3. **Critical gaps** — count of gaps with priority `CRITICO`. Value formatted as integer. Subtitle: "require immediate action".
4. **Rules created this session** — count of rules created via `create-quality-rules` in this conversation; `—` if none. Subtitle: "new in this report".

Each KPI card contains:

- **Label** (one short line, user's language).
- **Value** (large display, formatted for locale).
- **Subtitle** (one short context line).
- Optional: a micro-indicator showing whether the value is healthier or worse than a previous report in the same folder history (if one exists). When no previous report exists, omit the indicator — do not fabricate a trend.

HTML/CSS pattern (for `web-craft`):

```html
<div class="kpi-card" data-kpi="coverage">
  <div class="kpi-label">Coverage</div>
  <div class="kpi-value">87%</div>
  <div class="kpi-subtitle">across 24 tables</div>
</div>
```

```css
.kpi-card {
  background: var(--bg-alt);
  border-left: 4px solid var(--primary);
  padding: 1.25rem 1.5rem;
  border-radius: 4px;
}
.kpi-value { font-family: var(--font-display); font-size: 2.25rem; }
.kpi-subtitle { color: var(--muted); font-size: 0.875rem; }
```

For PDF/DOCX, render the four cards as a 4-column table row (or a 2×2 grid if page width is tight). The value uses the theme's `display` font; the label and subtitle use `body`.

For PPTX, the KPI cards occupy slide 2 (after the cover), laid out horizontally. If the theme declares `display` + `body` typography, honour them.

For canvas-craft (Poster), the four KPIs form the top band of the composition — Coverage % dominant, the other three supporting it.

## 6. Per-format composition

Same content, different framing.

### 6.1 PDF (multi-page, typographic)

- Header on every page: domain name (left) and generation date (right), thin rule below.
- Footer: page number (right), report title (left), thin rule above.
- Cover page is full-bleed optional; otherwise, the report starts with the title + metadata block at the top of page 1.
- Executive summary on page 1 (may continue into page 2 if the four KPI cards + a paragraph overflow). Coverage matrix can span multiple pages — repeat the header row at the top of each page.
- Rules detail: group by table, one sub-heading per table. Avoid orphan sub-headings at the bottom of a page.
- No landscape orientation unless the dimension count exceeds 8; if so, the coverage matrix only goes landscape, the rest stays portrait.

### 6.2 DOCX (editable Word)

- Use native Word tables (not HTML tables rendered as images). Grader will edit them.
- Same header/footer/cover as PDF.
- Status icons: prefer Unicode glyphs so copy-paste from Word stays legible.
- Preserve heading styles (`Heading 1`, `Heading 2`, …) so the user can regenerate a table of contents.

### 6.3 PPTX (executive summary deck, 16:9)

Target ≤12 slides. Outline:

1. Cover — title, domain, date, agent.
2. Executive summary — the four KPI cards laid out horizontally.
3. Coverage heatmap — the matrix from §2.3 as a visual heatmap. One row per table, one column per dimension. Colour-coded cells.
4. Rules status breakdown — pie or stacked bar (OK / KO / WARNING / NOT_EXECUTED) + the breakdown numbers.
5. Top gaps — list of the 10 most critical gaps (priority `CRITICO` first). One slide.
6. Rules created in this session (if any) — list with SQL excerpt and status. Otherwise skip.
7. Recommendations — 3–5 bullets of the highest-impact next steps.
8. Appendix (optional) — full rules inventory if the exec audience asked for detail.

16:9 aspect ratio by default. Fall back to 4:3 only if the user asks explicitly. Do not embed raster screenshots of tables — render native PPTX tables so the data stays editable.

### 6.4 Dashboard web (interactive HTML)

Consume this layout guide **and** the host agent's local `analytical-dashboard.md` if declared. The analytical-dashboard guide provides the generic dashboard patterns (global filters, sortable tables, KPI cards, Plotly via CDN); this guide layers the quality-specific content:

- KPI cards: exactly the four from §5.
- Coverage matrix as an interactive heatmap (Plotly `heatmap` with discrete colorway mapped to the status codes).
- Filters: one dropdown for dimension, one for status (OK/KO/WARNING/NOT_EXECUTED), one for priority (for the gaps section).
- Sortable table for rules detail (columns: rule, table, dimension, status, % pass).
- Sortable table for gaps (columns: table, column, dimension, priority, recommendation).

Data budget: quality reports are dense but not transactional. One row per rule + one row per gap is typical (<5,000 rows). Embed as `DASHBOARD_DATA` directly — no pre-aggregation needed in most cases.

### 6.5 Poster / Infographic (single-page visual)

- Top band: the four KPI cards, Coverage % dominant in the centre.
- Middle: the coverage heatmap as the central visual.
- Bottom left column: top 3 critical gaps with priority + recommendation.
- Bottom right column: top 3 recommendations (from §6).
- Format: A3 portrait by default, single PDF or PNG. Let the user pick the size if they state a preference.

## 7. Brand tokens integration

The theme fixed in the agent's branding cascade produces a token bundle. Quality reports consume it like any other deliverable:

- `primary` — section rules, KPI card left border, cover accents.
- `accent` — callouts, KPI card highlights (sparingly — quality reports read as sober documents, not marketing).
- `ink` — body text.
- `muted` — captions, footnotes, subtitle lines.
- `rule` — dividers, header/footer thin rules, table border lines.
- `bg` — page / main surface.
- `bg_alt` — table bands (alternate row shading), KPI card background.
- `state_ok` / `state_warn` / `state_danger` — rule status icons and gap priority colour coding (see §3, §4).
- `chart_categorical` — heatmap colour mapping for the coverage matrix. Map the four statuses to stable positions:
  - Position 0 → OK
  - Position 1 → WARNING
  - Position 2 → KO
  - Position 3 → NOT_EXECUTED
- Typography: `display` for KPI values and section H1; `body` for running text; `mono` for SQL excerpts and rule names (rule names often contain underscores — mono reads better).

If the theme declares `print` extensions, `pdf-writer` and `canvas-craft` honour them (a cream `paper` beats a pure white `bg` on paper).

## 8. Language

- `lang` is passed by the agent to each writer skill. Every heading, label, subtitle, KPI label, column header, footer text renders in that language.
- The `<html lang="...">` attribute (web-craft) and the DOCX language property (docx-writer) must match.
- Status codes (`OK`, `KO`, `WARNING`, `NOT_EXECUTED`) and priority codes (`CRITICO`, `ALTO`, `MEDIO`, `BAJO`) are NOT translated — they are canonical identifiers and must read the same across languages so cross-locale audit diffs align.
- Dimension names come from `get_quality_rule_dimensions` — they are domain-specific and locale-specific per the governance model; pass them through as-is.

`web-craft` should include a `LABELS` object following the pattern from `analytical-dashboard.md` §12 so UI strings (section names, filter labels, sort labels) are easy to regenerate in a different language.

## 9. What this guide does NOT dictate

The writer skills keep control of these decisions:

- Specific tone (editorial-serious, forensic-audit, technical-minimal, etc.) — comes from the theme.
- Exact typography — comes from `display` / `body` / `mono` in the theme.
- Exact accent and neutral values — come from the theme.
- The micro-composition of individual sections (KPI card inner padding, cover page layout, table cell styling, SQL code highlighting) — each writer skill designs these per its own workflow, coherent with the theme.
- Motion, hover, backgrounds for web-craft — see `analytical-dashboard.md` §9–§11 and web-craft's five decisions.
- PPTX slide transitions, speaker notes styling — pptx-writer decides per its workflow.

This guide constrains the **quality-report contract** (what the report contains and in what order); the writer skills provide the **visual voice**.

## 10. Mandatory content of the internal `quality-report.md`

The agent composes an internal `quality-report.md` in the user's language, inside `output/YYYY-MM-DD_HHMM_quality_<slug>/`, before delegating to any writer skill. This file is the single source of truth the writer skills consume. It must contain the following sections, even if a section has no data (in that case, write an explicit "No X detected" sentence rather than omitting the heading):

- **Cover** — title, domain, scope, generation date, agent name.
- **Executive summary** — tables analysed, rules total, rules breakdown (OK / KO / WARNING / NOT_EXECUTED), coverage estimate, gaps breakdown by priority, rules created this session.
- **Coverage by table** — one row per table in scope, with a column per dimension and a coverage estimate.
- **Rules detail** — grouped by table. If a table has no rules, an explicit line ("No rules defined for this table yet"). Otherwise the list of rules with name, dimension, status, % pass, description.
- **Identified gaps** — prioritised list. If there are no gaps, an explicit line ("No gaps detected in the current scope").
- **Rules created in this session** — only if at least one rule was created via `create-quality-rules` in the current conversation. Otherwise omit the whole section heading.
- **Recommendations and next steps** — at least one bullet. If coverage is already full and there are no gaps, the recommendation may be something like "Schedule periodic re-evaluation every N months" — but at least one bullet must be present.

No section heading is omitted silently (with the only exception of the conditional "Rules created in this session" — whose presence is itself a signal). This keeps month-over-month diffs readable: readers scan the same structure each time.

## 11. Deterministic layout for audit

For reports repeated periodically (governance, compliance) the structural skeleton must be stable across executions. The writer skills still have typographic and chromatic freedom within the theme, but the following rules are non-negotiable:

- **Section order is fixed**: Cover → Executive summary → Coverage by table → Rules detail → Gaps → (Rules created in this session) → Recommendations. Do not reorder.
- **KPI cards**: exactly the four from §5, in the exact order from §5. Do not add a fifth, do not remove one, do not reorder.
- **Coverage matrix columns**: Table name (first), then the dimensions in a stable order — Completeness, Uniqueness, Validity, Consistency, then any domain-specific dimensions returned by `get_quality_rule_dimensions` in alphabetical order, then Coverage % (last). Keep this order across executions even when a dimension has no coverage for any table in the current scope (render the column with all cells empty or `—`).
- **Rules detail grouping**: grouped by table, not by dimension. One sub-section per table, in alphabetical order of table name.
- **Gaps ordering**: priority (CRITICO → ALTO → MEDIO → BAJO) → table (alphabetical) → column (alphabetical).
- **Item limits per format**:
  - PDF / DOCX: up to 20 gaps visible; rest aggregated into a `"… and N more gaps of lower priority"` line.
  - PPTX: top 10 gaps only (one slide).
  - Dashboard web: no limit — use filters and sortable tables.
  - Poster / Infographic: top 3 critical + top 3 recommendations.
- **Empty-section markers**: every canonical section (§2.1–§2.6) always emits its heading. If it has no content, a single explicit line replaces the content ("No rules defined for this table yet", "No gaps detected in the current scope", "No rules created in this session"). The section is never skipped silently — the heading presence is what makes month-over-month diffs align.
- **Generation date format**: ISO 8601 (`YYYY-MM-DD`) in the document metadata and internal `quality-report.md`. The writer skills may render a localised display form (`24 April 2026` / `24 de abril de 2026`) in the cover, but the underlying metadata field stays ISO.
- **Filenames**: `<slug>-quality-report.<ext>` for PDF/DOCX/HTML, `<slug>-quality-summary.pptx`, `<slug>-quality-poster.pdf` or `.png`. `<slug>` is the normalised domain or scope (lowercase ASCII, underscores, ≤30 chars). Consistent filenames let tools diff across folders.

The combination of fixed section order, fixed KPI order, fixed column order, fixed ordering rules and filename convention makes two runs of the same dataset produce visually comparable reports — which is what audit readers expect.
