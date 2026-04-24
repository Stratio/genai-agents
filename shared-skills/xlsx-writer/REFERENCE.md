# xlsx-writer — REFERENCE

Cookbook of ready-to-adapt snippets for the building blocks listed in
SKILL.md §7. Load this file when the scaffold in SKILL.md §4 is not
enough — specific primitives, edge cases, advanced patterns.

All snippets assume:

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Alignment, Border, Color, Font, PatternFill, Side,
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

# Design tokens from the theme — see SKILL.md §3 and §4.
DESIGN = {...}

def hx(h: str) -> str:
    return h.lstrip("#").upper()
```

## KPI band (four cards, merged-cell)

The `add_kpi_band` helper in SKILL.md §4 produces a 4-card row. Use
this version when you need different card counts or custom subtitles.

```python
def add_kpi_band(ws, row: int, kpis: list[dict], cols_per_card: int = 3) -> None:
    col = 1
    thin = Side(border_style="thin", color=hx(DESIGN["rule"]))
    bord = Border(left=thin, right=thin, top=thin, bottom=thin)
    for kpi in kpis:
        # Label (primary-filled)
        ws.merge_cells(start_row=row, start_column=col,
                       end_row=row, end_column=col + cols_per_card - 1)
        label = ws.cell(row=row, column=col, value=kpi["label"])
        label.fill = PatternFill("solid", fgColor=hx(DESIGN["primary"]))
        label.font = Font(name=DESIGN["body"], size=DESIGN["size_kpi_lbl"],
                          color=hx(DESIGN["primary_ink"]), bold=True)
        label.alignment = Alignment(horizontal="center", vertical="center")
        # Value (display font)
        ws.merge_cells(start_row=row + 1, start_column=col,
                       end_row=row + 2, end_column=col + cols_per_card - 1)
        value = ws.cell(row=row + 1, column=col, value=kpi["value"])
        value.font = Font(name=DESIGN["display"], size=DESIGN["size_kpi"],
                          bold=True, color=hx(DESIGN["ink"]))
        value.alignment = Alignment(horizontal="center", vertical="center")
        # Subtitle
        ws.merge_cells(start_row=row + 3, start_column=col,
                       end_row=row + 3, end_column=col + cols_per_card - 1)
        sub = ws.cell(row=row + 3, column=col, value=kpi.get("subtitle", ""))
        sub.font = Font(name=DESIGN["body"], size=DESIGN["size_small"],
                        color=hx(DESIGN["muted"]))
        sub.alignment = Alignment(horizontal="center", vertical="center")
        # Borders around the card
        for r in range(row, row + 4):
            for c in range(col, col + cols_per_card):
                ws.cell(row=r, column=c).border = bord
        col += cols_per_card
    ws.row_dimensions[row + 1].height = 28
    ws.row_dimensions[row + 2].height = 28
```

## Native Table

The preferred primitive for any rectangular data with a header row.
Provides autofilter, sort, banded styling, and preserves formatting on
row insert.

```python
def add_native_table(
    ws, header: list[str], rows: list[list],
    start_cell: str = "A1", name: str = "DataTable",
    style: str = "TableStyleMedium2",
) -> None:
    first_col = ws[start_cell].column
    first_row = ws[start_cell].row
    ws.cell(row=first_row, column=first_col).value = None  # ensure clean start
    # Write header
    for i, h in enumerate(header):
        ws.cell(row=first_row, column=first_col + i, value=h)
    # Write rows
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            ws.cell(row=first_row + r, column=first_col + c, value=value)
    # Attach table
    last_col_letter = get_column_letter(first_col + len(header) - 1)
    last_row = first_row + len(rows)
    ref = f"{start_cell}:{last_col_letter}{last_row}"
    tbl = Table(displayName=name, ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name=style, showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(tbl)
```

Table names must be unique within the workbook and Excel-safe
(letters, digits, underscore, start with a letter). `"coverage matrix"`
is invalid; use `"CoverageMatrix"` or `"coverage_matrix"`.

Built-in styles worth knowing:

- `TableStyleLight1` / `Light9` / `Light15` — subtle banding for
  editorial workbooks
- `TableStyleMedium2` (default in Excel) — readable for most analytical
  workbooks
- `TableStyleDark1` / `Dark2` — dense matrices where contrast matters

## Conditional formatting — state coding

For status columns (OK / KO / WARNING / NOT_EXECUTED), apply
conditional formatting AFTER the Table is defined. Conditional
formatting layers on top of the Table's banding without fighting it.

```python
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import PatternFill

def apply_state_rules(ws, ref: str) -> None:
    for status, token in (
        ("OK",  "state_ok"),
        ("KO",  "state_danger"),
        ("WARNING", "state_warn"),
        ("NOT_EXECUTED", "state_muted"),
    ):
        fill = PatternFill("solid", fgColor=hx(DESIGN[token]))
        rule = CellIsRule(operator="equal", formula=[f'"{status}"'], fill=fill)
        ws.conditional_formatting.add(ref, rule)
```

For coverage cells with icon characters (✓ / ✗ / ◐ / —), extend the
operator list to include each glyph.

## Conditional formatting — delta columns

Variance vs benchmark / previous period reads better with a
double-ended data bar or a split color scale:

```python
from openpyxl.formatting.rule import ColorScaleRule

def apply_delta_color_scale(ws, ref: str) -> None:
    # Red for strongly negative, neutral at zero, green for strongly positive
    rule = ColorScaleRule(
        start_type="num", start_value=-0.2, start_color=hx(DESIGN["state_danger"]),
        mid_type="num",   mid_value=0,      mid_color=hx(DESIGN["bg_alt"]),
        end_type="num",   end_value=0.2,    end_color=hx(DESIGN["state_ok"]),
    )
    ws.conditional_formatting.add(ref, rule)
```

## Data validation — dropdowns

```python
from openpyxl.worksheet.datavalidation import DataValidation

def add_dropdown(ws, ref: str, choices: list[str]) -> None:
    formula = '"{}"'.format(",".join(choices))  # e.g. '"OK,KO,WARNING"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    dv.error = "Value must be one of the allowed options"
    dv.errorTitle = "Invalid value"
    dv.add(ref)
    ws.add_data_validation(dv)
```

For long choice lists, put the options on a hidden sheet and reference
the range:

```python
def add_dropdown_from_range(ws, ref: str, range_ref: str) -> None:
    dv = DataValidation(type="list", formula1=range_ref, allow_blank=True)
    dv.add(ref)
    ws.add_data_validation(dv)
```

## Number format cookbook

Number format strings are instructions for Excel's renderer — they do
not mutate the underlying numeric value. The display is locale-aware
(commas vs dots are chosen by the viewer's locale).

| Use case | Format string | Example render (en-US) |
|---|---|---|
| Integer thousands | `'#,##0'` | `1,234` |
| Integer, parenthesised negatives | `'#,##0_);(#,##0);"-"'` | `1,234` / `(567)` / `-` |
| Decimal, two places | `'#,##0.00'` | `1,234.56` |
| Currency (EUR) | `'[$€-es-ES]#,##0.00'` | `€1,234.56` |
| Currency generic (symbol prefix) | `'"$"#,##0.00'` | `$1,234.56` |
| Percentage, one decimal | `'0.0%'` | `12.3%` |
| Percentage, coloured negatives | `'0.0%;[Red]-0.0%'` | `12.3%` / `-4.5%` (red) |
| Date ISO | `'yyyy-mm-dd'` | `2026-04-24` |
| Date long | `'d mmm yyyy'` | `24 Apr 2026` |
| Time 24h | `'hh:mm'` | `14:35` |
| Multiplier | `'0.0"×"'` | `1.4×` |
| Custom unit | `'#,##0" t"'` | `1,234 t` |

Apply with `cell.number_format = '#,##0'`.

## Palette reference (XLSX)

The `DESIGN` dict in SKILL.md §4 maps the theme onto cell styling. For
the three most common workbook tones without a centralized theme, these
seeds are a reasonable improvisation:

### sober-audit (default for quality-coverage and compliance)

```python
DESIGN = {
    "primary":       "1F3A5F",
    "primary_ink":   "FFFFFF",
    "ink":           "1A202C",
    "muted":         "6B7280",
    "rule":          "D1D5DB",
    "bg":            "FFFFFF",
    "bg_alt":        "F3F4F6",
    "state_ok":      "047857",
    "state_warn":    "B45309",
    "state_danger":  "B91C1C",
    "state_muted":   "9CA3AF",
    "display":  "Inter",
    "body":     "Inter",
    "mono":     "Consolas",
    "size_title": 18, "size_kpi": 22, "size_kpi_lbl": 10,
    "size_header": 11, "size_body": 10, "size_small": 9,
}
```

### technical-minimal (default for neutral analytical)

```python
DESIGN = {
    "primary":       "2D3748",
    "primary_ink":   "FFFFFF",
    "ink":           "1A202C",
    "muted":         "718096",
    "rule":          "E2E8F0",
    "bg":            "FFFFFF",
    "bg_alt":        "F7FAFC",
    "state_ok":      "2F855A",
    "state_warn":    "C05621",
    "state_danger":  "C53030",
    "state_muted":   "A0AEC0",
    "display":  "Inter",
    "body":     "Inter",
    "mono":     "JetBrains Mono",
    "size_title": 18, "size_kpi": 22, "size_kpi_lbl": 10,
    "size_header": 11, "size_body": 10, "size_small": 9,
}
```

### editorial-serious (for narrative-oriented analytical workbooks)

```python
DESIGN = {
    "primary":       "1A365D",
    "primary_ink":   "FFFFFF",
    "ink":           "1F2937",
    "muted":         "6B7280",
    "rule":          "D1D5DB",
    "bg":            "FFFFFF",
    "bg_alt":        "F9FAFB",
    "state_ok":      "065F46",
    "state_warn":    "92400E",
    "state_danger":  "991B1B",
    "state_muted":   "9CA3AF",
    "display":  "Fraunces",
    "body":     "Inter",
    "mono":     "Consolas",
    "size_title": 20, "size_kpi": 24, "size_kpi_lbl": 10,
    "size_header": 11, "size_body": 10, "size_small": 9,
}
```

These are only fallbacks. When a centralized theming skill resolves a
theme, use its tokens verbatim.

## Native charts

Excel-native charts stay editable in Excel. Prefer them for workbooks
that are themselves the deliverable; for reports where the chart ends
up in a PDF / DOCX / PPTX, render a PNG with matplotlib / plotly and
embed as an image instead.

```python
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

def add_bar_chart(ws, data_ref: str, categories_ref: str,
                  title: str, position: str) -> None:
    chart = BarChart()
    chart.title = title
    chart.style = 2
    data = Reference(ws, range_string=data_ref)
    cats = Reference(ws, range_string=categories_ref)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    chart.height = 10
    chart.width = 18
    ws.add_chart(chart, position)


# Usage
add_bar_chart(
    ws, data_ref="Detail!$C$1:$C$13", categories_ref="Detail!$A$2:$A$13",
    title="Monthly revenue", position="F2",
)
```

Line, Pie, Scatter follow the same pattern. For advanced configurations
(dual axis, secondary series, data labels with insights), see
`openpyxl.chart` — or fall back to a PNG render and `ws.add_image`.

## Embed images

```python
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage

def embed_image(ws, image_path: str, anchor: str,
                max_width_px: int = 600) -> None:
    # Size with pillow first so the image respects the target region
    src = PILImage.open(image_path)
    if src.width > max_width_px:
        ratio = max_width_px / src.width
        src.thumbnail((max_width_px, int(src.height * ratio)))
        sized = image_path.replace(".", "_sized.")
        src.save(sized)
        image_path = sized
    img = XLImage(image_path)
    ws.add_image(img, anchor)
```

## Named ranges

Named ranges anchor the workbook for users who write formulas on top
of it. Define them in the workbook scope so every sheet can reference
them.

```python
from openpyxl.workbook.defined_name import DefinedName

def add_named_range(wb, name: str, ref: str) -> None:
    wb.defined_names[name] = DefinedName(name=name, attr_text=ref)


# Usage — a named region for the assumptions sheet
add_named_range(wb, "Assumptions", "Assumptions!$B$2:$B$12")
```

## Freeze panes

```python
ws.freeze_panes = "A2"   # freeze first row only
ws.freeze_panes = "B1"   # freeze first column only
ws.freeze_panes = "B2"   # freeze first row + first column (standard for Tables)
ws.freeze_panes = None   # unfreeze
```

Set AFTER you finalise the Table, not before — otherwise openpyxl may
shuffle the pane location.

## Protected sheets

```python
ws.protection.sheet = True
ws.protection.password = "change-me"  # optional
ws.protection.enable()

# Allow the user to edit specific cells despite protection
for cell in ws["B2:B12"]:
    for c in cell:
        c.protection = c.protection.copy(locked=False)
```

Passwords on sheets are deterrent, not security — they are easily
bypassed. Protect to prevent accidental edits, not to restrict access.

## Post-build validation

### Structural sanity

```python
from openpyxl import load_workbook

def validate_structure(path: str) -> dict:
    wb = load_workbook(path, read_only=True, data_only=False)
    summary = {
        "sheets": len(wb.sheetnames),
        "tables_by_sheet": {
            name: len(list(wb[name].tables)) for name in wb.sheetnames
        },
        "rows_by_sheet": {
            name: wb[name].max_row for name in wb.sheetnames
        },
    }
    return summary
```

### Formula refresh

```bash
python3 <skill-root>/scripts/refresh_formulas.py output.xlsx --json
```

JSON schema:

```json
{
  "ok": true,
  "formula_cells": 42,
  "sheets_touched": ["Summary", "Detail"],
  "issues": [
    {"sheet": "Detail", "cell": "C10", "type": "#DIV/0!"}
  ]
}
```

`ok` is `true` when `issues` is empty. On error (e.g. LibreOffice
missing, timeout), the JSON has `"ok": false` and an `"error"` field.

### Visual PDF export

```bash
soffice --headless --convert-to pdf --outdir /tmp/preview workbook.xlsx
# opens workbook.pdf in /tmp/preview/
```

Open the PDF and eyeball the cover sheet, KPI band and coverage matrix
before shipping. Catches merged-cell bleed, truncated KPI values, and
broken conditional formatting without needing Excel.

## Working with an existing XLSX as a starting point

```python
from openpyxl import load_workbook

wb = load_workbook("templates/company_template.xlsx")

# Inspect the named ranges the template exposes
for name in wb.defined_names:
    print(f"{name}: {wb.defined_names[name].value}")

# Fill placeholder cells — use named ranges when available
wb["Cover"]["B3"] = "Q4 2026"
wb["Cover"]["B4"] = "2026-04-24"

wb.save("output/branded.xlsx")
```

When loading, openpyxl preserves conditional formatting, data
validation, Tables, named ranges, and most chart definitions. It does
NOT preserve macros from `.xlsm` (you would need to load with
`keep_vba=True` AND save as `.xlsm`).

## Batch generation

```python
from pathlib import Path
from openpyxl import Workbook

def generate_batch(datasets: dict[str, list[list]], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []
    for slug, rows in datasets.items():
        wb = Workbook()
        ws = wb.active
        ws.title = "Data"
        for row in rows:
            ws.append(row)
        # ... apply standard styling / Tables ...
        out = out_dir / f"{slug}-workbook.xlsx"
        wb.save(out)
        produced.append(out)
    return produced
```

For batches >50 workbooks, switch to `Workbook(write_only=True)` to
stream rows instead of holding the whole workbook in memory.

## Known limitations (expanded)

- **VBA macros** — openpyxl preserves macro binaries on round-trip
  (`keep_vba=True`) but cannot author macros from scratch.
- **Pivot tables** — cannot be authored. Ship the source Table and
  let the user pivot in Excel, or pre-pivot with pandas.
- **Sparklines** — not supported.
- **`.xlsb` binary** — not supported for writing. Always write `.xlsx`.
- **Comments with rich formatting** — basic text only; inline bold /
  italic / colors are flattened.
- **External links (linked workbooks)** — openpyxl can preserve them on
  round-trip, but cannot create new ones.
- **OLE objects (embedded documents)** — not supported.

When a limitation bites, document it in a sheet-level caveat or ship a
note alongside the workbook.
