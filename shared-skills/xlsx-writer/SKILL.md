---
name: xlsx-writer
description: "Create Excel workbooks (.xlsx) with intentional structure, and perform structural operations on existing ones. Use this skill whenever you need to produce a polished spreadsheet (analytical workbook with cover/KPI, pivot, tabular export, coverage matrix, catalog, quantitative model) or manipulate existing XLSX files (merge, split, find-replace, convert legacy .xls, refresh cached formula values). This skill treats tabular output seriously — every workbook it produces has intentional header formatting, typography, conditional formatting and native Tables, never the generic white-grid-on-white default. Do NOT use for: multi-page typographic PDF (pdf-writer), single-page visual piece (canvas-craft), interactive web (web-craft), text-heavy Word document (docx-writer). For advanced patterns (data validation, charts, named ranges, image embedding), load REFERENCE.md. For merge / split / find-replace / legacy .xls conversion, load STRUCTURAL_OPS.md. When invoked from quality-report, follow the multi-sheet contract in quality-report-layout.md §6.6."
argument-hint: "[workbook type or description]"
---

# Skill: XLSX Writer

Excel is the surface where tabular data is expected to land. A workbook generated
without structural attention looks like a raw CSV dump — white grid on white
grid, unstyled headers, no freeze panes, no state coding, columns sized to
defaults. That's the baseline this skill actively resists.

Before writing a single line of code, commit to a structure. The code serves
the structure, not the other way around.

## 1. Design-first workflow

Every XLSX generation task, regardless of size, follows five decisions:

1. **Classify the workbook** — what kind of deliverable is it? (See the
   taxonomy below.) This governs sheet count, sheet order, and which
   primitives (KPI cards, Table objects, conditional formatting, charts)
   get used downstream.
2. **Pick a visual tone** — sober-audit, technical-minimal, editorial-serious,
   corporate-formal. Tabular artefacts are sober by default: real saturation
   only on headers and state indicators, everything else monochrome. Pick one
   and execute it confidently.
3. **Select a type pairing** — one body face for cell values, one display
   face for headers and KPI values. Calibri / Aptos / Arial / Cambria /
   Georgia degrade gracefully across machines (XLSX uses the reader's
   installed fonts unless you embed — and embedding is not a standard flow
   for workbooks).
4. **Define a palette** — one dominant `primary` for header fill and KPI card
   borders (used for 5-15% of surface), one deep `ink` for body text, one
   pale `bg_alt` for alternating band rows, plus state colors
   (`state_ok` / `state_warn` / `state_danger`) used sparingly for
   conditional formatting. Concrete values come from the theme (§3),
   not from this skill.
5. **Set the rhythm** — column widths (never default 10), row heights for
   KPI bands, freeze first row + first column where it matters, set the
   print area so a user who prints gets a sensible landscape page.

Only then open `openpyxl`.

### Workbook taxonomy and starting points

| Category | Typical shape | Primitives |
|---|---|---|
| Cover/KPI analytical workbook | Cover sheet with KPIs + parameters + detail sheets + appendix | KPI merged-cell bands, Table objects, conditional formatting, freeze panes |
| Pivot / cross-tab | Rows × columns matrix of a single metric | One dense Table with alternating bands; column totals and row totals in bold |
| Coverage matrix (quality) | Rows = entities, columns = dimensions, cells = status icons | Native Table, conditional formatting per status, freeze first row + first column |
| Tabular export (anotado) | One or two sheets, header + rows + footer note | Native Table with autofilter, frozen header, number formats per column type |
| Catalog / data dictionary | One sheet per entity type (term, column, domain) | Native Tables, narrow columns for codes, wide columns for prose |
| Quantitative model | Cover / assumptions / detail / output, formulas throughout | Assumption cells fill-coded, formulas in black, state colors for variance |

These are starting points, not mandates. Break them when the brief calls
for it. The point is **never default to openpyxl's blank Calibri 11pt cells
with no structure**.

### When this skill is not the right fit

- **Multi-page typographic document** (contract, whitepaper, prose-heavy
  policy) — `docx-writer` or `pdf-writer` preserve typography and reading
  flow; XLSX is a tabular surface, not a prose surface.
- **Single-page visual piece** (poster, cover, infographic, one-pager) —
  `canvas-craft`.
- **Interactive frontend** — `web-craft`.
- **Quality coverage report in a narrative format** — the `quality-report`
  skill composes the canonical six-section structure and delegates to the
  writer skill per format. When invoked *from* quality-report for the XLSX
  option, this skill follows the multi-sheet contract in
  `quality-report-layout.md` §6.6 (see §9 below).

## 2. Page setup

XLSX prints differently from DOCX: unless you set the print area and page
orientation, Excel will split your sheet across dozens of pages at its own
discretion. For any workbook that will be printed or exported to PDF:

```python
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.properties import PageSetupProperties

ws.print_area = "A1:H50"
ws.page_setup.orientation = "landscape"  # or "portrait"
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.6, bottom=0.6)
ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0  # 0 = as many pages as needed vertically
```

Landscape is the default for coverage matrices, pivot tables, and any
rectangular table wider than ~8 columns. Portrait is the default for
narrow tabular exports, catalogs and cover/KPI sheets.

## 3. Theme application

Design tokens (colors, typography, sizes) do not live in this skill —
they come from the theme chosen for the deliverable.

- If a centralized theming skill is available (brand-kit-style),
  run its workflow BEFORE authoring; it returns a token set that maps
  onto the `DESIGN` dict below.
- Otherwise, improvise tokens coherent with the deliverable following
  the tonal palette roles in `skills-guides/visual-craftsmanship.md`.

The `DESIGN` dict in the scaffold uses placeholders (`<hex>`,
`<font-family>`, `<pt>`) — fill them from the theme, don't hard-code.

For XLSX specifically:
- **Header fill** uses `primary` (saturated), header text white or very
  pale neutral.
- **Body bands** alternate between `bg` (transparent / white) and
  `bg_alt` (pale neutral) on even rows.
- **State fills** use `state_ok` / `state_warn` / `state_danger` /
  `muted` in conditional formatting — never as direct cell fills, so the
  user can filter / sort without the fills fighting the Table's own
  banded theme.
- **KPI values** use the theme's `display` font at ~2× the body font size;
  KPI labels and subtitles use `body` at the body size.
- **Typography fallback**: XLSX reads the user's system fonts. Pair your
  theme fonts with safe defaults (`Inter, Calibri, Arial, sans-serif`)
  via `Font(name=...)` so the workbook degrades gracefully on machines
  without the exotic face.

## 4. A proper starting template

Instead of reaching for `Workbook()` and hoping, use this scaffold
and adapt:

```python
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from pathlib import Path

# 1. Commit to design tokens up front — they never change mid-workbook.
#    Fill these from the chosen theme (see §3). Do not hard-code values
#    here; the skeleton is stable, the values are branding.
DESIGN = {
    # Palette (hex strings — 6 chars, no leading #)
    "primary":       "<hex>",   # header fills, KPI card borders
    "primary_ink":   "FFFFFF",  # text on primary fill
    "ink":           "<hex>",   # body text
    "muted":         "<hex>",   # captions, subtitles
    "rule":          "<hex>",   # borders
    "bg":            "FFFFFF",  # base surface
    "bg_alt":        "<hex>",   # alternate band rows
    "state_ok":      "<hex>",
    "state_warn":    "<hex>",
    "state_danger":  "<hex>",
    "state_muted":   "<hex>",
    # Typography (system-safe first, theme face as fallback)
    "display":  "<font-family>",  # KPI values, main titles
    "body":     "<font-family>",  # cell values, labels
    "mono":     "Consolas",       # code excerpts, SQL
    # Sizes (pt)
    "size_title":    18,
    "size_kpi":      22,
    "size_kpi_lbl":  10,
    "size_header":   11,
    "size_body":     10,
    "size_small":    9,
}


def hx(h: str) -> str:
    """Return a 6-char hex uppercased, stripping leading '#' if present."""
    return h.lstrip("#").upper()


# 2. Build the workbook and remove the default blank sheet if we want
#    explicit sheet names from the start.
wb = Workbook()
ws_cover = wb.active
ws_cover.title = "Cover"


# 3. Small helpers for the compositions you'll repeat.
def set_col_widths(ws, widths: dict[str, float]) -> None:
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width


def style_header_row(ws, row: int, first_col: int, last_col: int) -> None:
    fill = PatternFill("solid", fgColor=hx(DESIGN["primary"]))
    font = Font(name=DESIGN["body"], size=DESIGN["size_header"],
                bold=True, color=hx(DESIGN["primary_ink"]))
    align = Alignment(horizontal="left", vertical="center")
    for col in range(first_col, last_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = fill
        cell.font = font
        cell.alignment = align


def add_kpi_band(ws, row: int, kpis: list[dict]) -> None:
    """Four-cell KPI band at the given row. Each dict has
    {label, value, subtitle}. Each KPI spans 3 columns with a merged
    header cell on top (primary) and a merged body below (display font).
    """
    col = 1
    thin = Side(border_style="thin", color=hx(DESIGN["rule"]))
    bord = Border(left=thin, right=thin, top=thin, bottom=thin)
    for kpi in kpis:
        # Label row (primary-filled)
        ws.merge_cells(start_row=row, start_column=col,
                       end_row=row, end_column=col + 2)
        label_cell = ws.cell(row=row, column=col, value=kpi["label"])
        label_cell.fill = PatternFill("solid", fgColor=hx(DESIGN["primary"]))
        label_cell.font = Font(name=DESIGN["body"],
                               size=DESIGN["size_kpi_lbl"],
                               color=hx(DESIGN["primary_ink"]), bold=True)
        label_cell.alignment = Alignment(horizontal="center", vertical="center")
        # Value row
        ws.merge_cells(start_row=row + 1, start_column=col,
                       end_row=row + 2, end_column=col + 2)
        value_cell = ws.cell(row=row + 1, column=col, value=kpi["value"])
        value_cell.font = Font(name=DESIGN["display"],
                               size=DESIGN["size_kpi"], bold=True,
                               color=hx(DESIGN["ink"]))
        value_cell.alignment = Alignment(horizontal="center", vertical="center")
        # Subtitle row
        ws.merge_cells(start_row=row + 3, start_column=col,
                       end_row=row + 3, end_column=col + 2)
        sub_cell = ws.cell(row=row + 3, column=col, value=kpi.get("subtitle", ""))
        sub_cell.font = Font(name=DESIGN["body"], size=DESIGN["size_small"],
                             color=hx(DESIGN["muted"]))
        sub_cell.alignment = Alignment(horizontal="center", vertical="center")
        # Borders around the card
        for r in range(row, row + 4):
            for c in range(col, col + 3):
                ws.cell(row=r, column=c).border = bord
        col += 3
    ws.row_dimensions[row + 1].height = 28
    ws.row_dimensions[row + 2].height = 28


def add_native_table(ws, ref: str, name: str, style: str = "TableStyleMedium2") -> None:
    """Attach an openpyxl Table to the given range. Name must be unique
    within the workbook and Excel-safe (letters, digits, underscore).
    """
    tbl = Table(displayName=name, ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name=style, showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(tbl)


# 4. Compose the cover sheet.
ws_cover["A1"] = "Report Title"
ws_cover["A1"].font = Font(name=DESIGN["display"], size=DESIGN["size_title"],
                           bold=True, color=hx(DESIGN["primary"]))
ws_cover.merge_cells("A1:L1")

ws_cover["A3"] = "Scope"
ws_cover["B3"] = "<domain or scope>"
ws_cover["A4"] = "Generated"
ws_cover["B4"] = "<YYYY-MM-DD>"

add_kpi_band(
    ws_cover, row=6,
    kpis=[
        {"label": "KPI one",   "value": "42",   "subtitle": "context"},
        {"label": "KPI two",   "value": "87%",  "subtitle": "context"},
        {"label": "KPI three", "value": "3",    "subtitle": "context"},
        {"label": "KPI four",  "value": "—",    "subtitle": "context"},
    ],
)

set_col_widths(ws_cover, {chr(c): 14 for c in range(ord("A"), ord("L") + 1)})


# 5. Build detail sheet with a native Table.
ws_detail = wb.create_sheet("Detail")
headers = ["ID", "Name", "Value", "Status"]
ws_detail.append(headers)
for row in sample_rows:  # iterable of lists you already have
    ws_detail.append(row)
set_col_widths(ws_detail, {"A": 14, "B": 28, "C": 14, "D": 14})
add_native_table(
    ws_detail,
    ref=f"A1:{get_column_letter(len(headers))}{ws_detail.max_row}",
    name="DetailTable",
)
ws_detail.freeze_panes = "A2"


out_path = Path("output/workbook.xlsx")
out_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(out_path)
```

Four rules the scaffold enforces:

- **Never rely on the default column widths.** openpyxl's default (~8.43)
  truncates almost any real data. Set widths explicitly per column.
- **Always use native Table objects for rectangular data.** They give the
  user autofilter + sort out of the box and preserve banding on insert.
- **Compute colors, fonts and sizes from design tokens**, never inline
  literals mid-workbook. If the accent color changes, only `DESIGN` changes.
- **Compose with primitives + small helpers**. Reach for a small
  module-local helper the moment you repeat a pattern three times.

## 5. Fonts

XLSX uses the reader's installed fonts. Safe defaults across Windows /
macOS / Linux: **Calibri, Aptos, Arial, Cambria, Georgia, Courier New,
Consolas**.

Font embedding exists in the XLSX spec but support is uneven across viewers
(Excel 2019+ on Windows only, ignored by LibreOffice, macOS Excel, Excel
Online and Google Sheets). Do not embed for workbooks; rely on safe
fallbacks and, if the brief demands an exact face, render the cover region
as a PNG and embed it as an image.

Recommendation: pick theme fonts that degrade gracefully. `Inter, Calibri,
Arial, sans-serif` is the universal body default; `DM Sans, Calibri, Arial,
sans-serif` or `Fraunces, Cambria, Georgia, serif` give character without
breaking anyone.

## 6. Palette guidance

A designed workbook has at most three color families on any given sheet:
primary (one accent, saturated, used for 5-15% of surface — header fills,
KPI card borders), neutral (cell text and band rows), and state colors
(ok / warn / danger) used sparingly for conditional formatting.

Never mix two different blues, two different reds, or two different accent
saturations in the same workbook. Commit to concrete values up front and
apply them uniformly across every sheet.

Where those concrete values come from depends on what the agent has:

- If a centralized theming skill is available, the chosen theme
  supplies a complete, coherent token set (primary, ink, muted, rule,
  bg_alt, accent, state colors, typography, sizes). Use it verbatim.
- Otherwise, improvise from the tonal palette roles in
  `skills-guides/visual-craftsmanship.md`. For XLSX-specific defaults
  (sober-audit, technical-minimal) see `REFERENCE.md` §Palette reference.

## 7. Workbook building blocks

These are the building blocks worth mastering. Snippets for each live
in `REFERENCE.md`; here is the menu.

- **KPI band** — 4 merged-cell cards in a horizontal row: label on top,
  value in display font, subtitle below. Border and primary fill on the
  label row.
- **Native Table** (`openpyxl.worksheet.table.Table`) — preferred for any
  rectangular data with a header row. Enables autofilter, sort, banded
  styling, and preserves on row insert.
- **Freeze panes** — `ws.freeze_panes = "B2"` to freeze the first row
  and first column. Standard for any Table with >20 rows or >6 columns.
- **Column widths** — `ws.column_dimensions["A"].width = 28`. Always
  explicit; never default.
- **Row heights** — `ws.row_dimensions[row].height = 28` for KPI bands
  and section headers.
- **Number format strings** — `cell.number_format = '#,##0'` /
  `'0.0%'` / `'yyyy-mm-dd'`. Examples in `REFERENCE.md`; not mandates.
- **Conditional formatting** — cell-rule fills for state coding. Never
  use direct fills for state coding (it breaks banding); conditional
  formatting layers cleanly on top of a Table's own bands.
- **Data validation** — dropdowns and range constraints via
  `openpyxl.worksheet.datavalidation`. Snippet in `REFERENCE.md`.
- **Charts** — native Excel charts via `openpyxl.chart` (Bar / Line / Pie
  / Scatter). Limited compared to Excel-native but editable in Excel.
  Use only when the workbook is the final surface; otherwise render a
  PNG with matplotlib and embed.
- **Images** — `openpyxl.drawing.image.Image` for PNG / JPG embedding.
  Size via pillow first so the image fits the target cell range.

## 8. Analytical workbook composition

When this skill is invoked from `/analyze`'s Phase 4 deliverable
generation, produce an analytical workbook with this stable structure:

1. **Cover / KPI sheet** (always first) — title, scope, period,
   generation date, a KPI band of 3-4 key metrics (from the report's
   executive summary), a one-paragraph lead sentence pointing at the
   most important finding.
2. **Parameters sheet** (when the analysis used filters, date ranges,
   or segment selections) — a narrow two-column sheet documenting every
   filter applied. Lets the reader reproduce the slice in Excel.
3. **Detail sheets, one per principal dimension** — each holds a Table
   of the underlying data for that dimension (region × metric, month ×
   metric, segment × metric, etc.). Apply conditional formatting on the
   delta columns (vs previous period, vs benchmark, vs target).
4. **Hypothesis validation sheet** (optional, Standard/Deep depths) —
   for each hypothesis: statement, criterion, actual, result
   (CONFIRMED / REFUTED / PARTIAL), evidence pointer.
5. **Appendix — raw data** (optional, when the dataset is small enough
   to fit). Native Table with autofilter, frozen header row.

Filenames follow the `/analyze` convention: `<slug>-workbook.xlsx`.
Brand tokens applied via the branding cascade of the host agent.

## 9. Quality-coverage workbook composition

When this skill is invoked from the `quality-report` orchestrator for
the XLSX format, follow the multi-sheet contract in
`shared-skills/quality-report/quality-report-layout.md §6.6`. Summary:

1. **Cover** — title, domain, scope, generation date, 4-cell KPI band
   (Coverage %, Rules OK %, Critical gaps, Rules created this session).
2. **Coverage** — native Table of tables × dimensions with status icons
   (✓ / ✗ / ◐ / —) and conditional formatting tinted by state. Freeze
   first row + first column.
3. **Rules** — native Table grouped by table: rule name, dimension,
   status, % pass, description.
4. **Gaps** — prioritised Table: priority, table, column, dimension,
   description, recommendation. Priority cell tinted by priority code.
5. **Rules created in this session** (conditional).
6. **Recommendations** — numbered bullets, prose sheet.

The layout guide is the contract; follow it verbatim for audit stability
across reruns. No Excel formulas (all values are displayed data). No
native charts (the coverage matrix is itself the heatmap).

Filename: `<slug>-quality-report.xlsx`.

## 10. Formulas

Excel formulas are a first-class citizen when the workbook is a
**quantitative model** (budget, forecast, scenario analysis). For
**analytical reports** and **coverage matrices**, prefer displayed
values — the workbook is a deliverable, not a computation environment.

When you do write formulas:

- Assumption cells get their own sheet (or a clearly demarcated region).
  Their fill is distinct (`state_warn` or a very pale `bg_alt`) so the
  reader knows which cells they can change.
- Use **cell references**, not hard-coded values, so a change to an
  assumption propagates: `=B5*(1+$B$6)` not `=B5*1.05`.
- Document any hard-coded values in a cell comment, citing the source.
- After writing formulas with `openpyxl`, **cached values are not
  updated** — the workbook opens with blanks in viewers that don't
  recalculate (LibreOffice does; Google Sheets does; a Python process
  reading with `data_only=True` sees `None`).

To refresh cached values post-build:

```bash
python3 <skill-root>/scripts/refresh_formulas.py output/model.xlsx --json
```

The script runs a headless LibreOffice recalc pass, saves the workbook
in place, and emits JSON summarising formula count, sheets touched, and
any errors detected (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`,
`#NULL!`, `#NUM!`). Flags: `--timeout <seconds>`, `--json`, `--quiet`.

## 11. Post-build validation

After building, always verify the result. Three checks:

- **Structural sanity** — reopen the saved XLSX with `openpyxl` and
  count sheets, rows per sheet, Table objects, merged ranges. Catches
  file corruption or silently-dropped data before delivery.
- **Formula refresh** (only if formulas are present) — run
  `scripts/refresh_formulas.py` as above. The JSON output lets you
  decide whether to ship or regenerate.
- **Visual check** (recommended for cover sheets and KPI bands) —
  convert to PDF via LibreOffice headless
  (`soffice --headless --convert-to pdf`) and open the PDF. Cheaper
  than opening Excel; catches merged-cell bleed, truncated KPI values,
  broken conditional formatting.

Full snippets in `REFERENCE.md` §Post-build validation.

## 12. User-provided templates

When a user provides a corporate template with their logo, letterhead,
styles and colour palette — ignore the scaffold in §4 and load their
file:

```python
from openpyxl import load_workbook

wb = load_workbook("templates/company_template.xlsx")
ws = wb["Cover"]
ws["B3"] = "Q4 2026"
# reuse the template's defined names and styles; don't redefine them
wb.save("output/branded.xlsx")
```

When using a client template:

- **Do not redefine the theme fills** if the template has them.
- **Do reuse the template's named ranges** (they often anchor the cover
  title, scope, date fields).
- **Still validate** — a template can be out-of-date or partially broken;
  you'll catch it only by rendering and inspecting.

## 13. Structural operations

For manipulating existing workbooks (merge hoja-a-hoja preserving
styles, split per sheet, find-replace across cells with text, convert
legacy binary `.xls` to `.xlsx`, extract one sheet to CSV), see
`STRUCTURAL_OPS.md`. Those are copy-paste snippets; run them from a
small script, don't try to import them as a module.

## 14. Pitfalls

Reality-checked against `openpyxl` 3.1 and the ECMA-376 spec:

- **Merged cells and sort / filter.** A Table with merged cells inside
  it will refuse to sort. Never merge inside a data region — only in
  the cover / KPI / title rows.
- **`data_only=True` + save destroys formulas.** Never open a workbook
  with `data_only=True` and then `wb.save(...)` — you'll write the
  cached values as literal constants and lose every formula. For
  read-only flows use `xlsx-reader`; for write flows keep
  `data_only=False`.
- **Number format strings are locale-dependent at display time.**
  `'#,##0'` renders as `1,234` in en-US and `1.234` in es-ES. That
  behaviour is correct — let Excel do the locale work; do not
  pre-format numbers as strings in your code.
- **openpyxl does not evaluate formulas.** Cached values are missing
  after build. Use `scripts/refresh_formulas.py` or ask the user to
  open + save in Excel / LibreOffice.
- **Row heights reset on Excel recalc** if you did not freeze them with
  `row_dimensions[n].height = ...`. Set heights explicitly for KPI
  bands and title rows.
- **Table names must be unique per workbook** and must be Excel-safe
  (letters, digits, underscore, start with a letter). `"coverage-matrix"`
  is invalid; use `"CoverageMatrix"` or `"coverage_matrix"`.
- **Do not use `solid` pattern fill with identical foreground /
  background colors.** Some viewers collapse that to black, producing
  the "why is my cell black?" bug. Always set `fgColor` explicitly.
- **Conditional formatting on a Table range gets evaluated per cell.**
  Formulas inside the rule use the cell being evaluated, not the
  range — write rules relative to the first cell of the range.

## 15. Known limitations

`openpyxl` covers ~85% of real-world XLSX authoring cleanly. The
remaining 15% either needs raw OOXML manipulation or is not supported:

- **VBA macros (`.xlsm` creation)** — openpyxl can preserve a macro
  layer if it was present in an input file, but it cannot author new
  macros. Creating `.xlsm` workbooks with custom macros is not
  supported.
- **Pivot tables (authoring)** — openpyxl does not create pivot tables
  programmatically. Create the source data and let the user pivot in
  Excel, or render the pivoted result with pandas and ship a flat Table.
- **Sparklines** — not supported. Use native charts or render PNGs.
- **`.xlsb` binary format** — not supported. Write `.xlsx` and, if the
  user needs `.xlsb`, they can Save As from Excel.
- **Cell comments with rich formatting** — basic comments work; rich
  text inside them is flattened.

Document the limitation in a sheet-level caveat when it affects the
deliverable.

## 16. Quick-reference cheat sheet

| Task | Approach |
|---|---|
| Create workbook | `Workbook()` then set sheet titles and column widths |
| Add sheet | `wb.create_sheet("Name")` |
| Column width | `ws.column_dimensions["A"].width = 28` |
| Row height | `ws.row_dimensions[1].height = 28` |
| Native Table | see §4 scaffold and REFERENCE.md §Native Table |
| KPI band | see §4 scaffold `add_kpi_band` helper |
| Conditional formatting | see REFERENCE.md §Conditional formatting |
| Number format | `cell.number_format = '#,##0'` / `'0.0%'` / `'yyyy-mm-dd'` |
| Freeze panes | `ws.freeze_panes = "B2"` |
| Print area | `ws.print_area = "A1:H50"` + page setup |
| Native chart | see REFERENCE.md §Native charts |
| Embed image | `openpyxl.drawing.image.Image(path)` + `ws.add_image` |
| Refresh formulas | `python3 scripts/refresh_formulas.py file.xlsx --json` |
| Merge / split / find-replace | see `STRUCTURAL_OPS.md` |
| Convert `.xls` legacy | `soffice --headless --convert-to xlsx old.xls` |
| User-provided template | load `.xlsx` directly; reuse its styles and named ranges |

## 17. When to load REFERENCE.md

- Full snippets for each building block (KPI band, native Table,
  conditional formatting, data validation, native charts, image
  embedding, named ranges, protected sheets)
- Palette reference for XLSX (sober-audit, technical-minimal,
  editorial-serious defaults)
- Number format cookbook (currency with units, percentages,
  parenthesised negatives, date/time, multiples)
- Post-build validation (structural sanity, formula refresh, visual
  PDF export)
- Working with an existing XLSX as a starting point
- Batch generation (N workbooks from a dataset)

---

Reading cells, tables, formulas, metadata and workbook structure from
existing files — plus diagnose-first extraction, quick mode via
`quick_extract.py`, legacy `.xls` ingest — all live in the companion
`xlsx-reader` skill.
