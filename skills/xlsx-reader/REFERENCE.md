# xlsx-reader — REFERENCE

Advanced patterns that do not belong in the main SKILL.md. Load this file when the quick/deep workflow from SKILL.md is not enough — specific features, edge cases, batch recipes.

## Column-selective reading (large files)

Reading 50 columns when you only need three is wasteful. Both engines support column selection:

```python
# pandas: by name (header inferred) or by letter (no header)
df = pd.read_excel("big.xlsx", usecols=["order_id", "amount", "ordered_at"])
df = pd.read_excel("big.xlsx", usecols="A,C,F:H")

# openpyxl: limit by max_col when iterating
from openpyxl import load_workbook
wb = load_workbook("big.xlsx", read_only=True, data_only=True)
ws = wb.active
for row in ws.iter_rows(values_only=True, min_col=1, max_col=3):
    ...
```

## Forcing dtypes

Excel date cells often round-trip as floats, and numeric customer IDs lose their leading zeros. Force the dtype at read time:

```python
df = pd.read_excel(
    "orders.xlsx",
    dtype={"customer_id": str, "order_id": str, "status": "category"},
    parse_dates=["ordered_at", "shipped_at"],
)
```

For `openpyxl`, cells keep their original Python type (`datetime`, `int`, `float`, `str`, `bool`, `None`) — no coercion needed.

## Handling merged cells when rebuilding a DataFrame

Merged cells appear as one cell carrying the value and the siblings as `None` in `openpyxl`. If you feed the raw rows to `pandas`, you lose information. Forward-fill the merged region:

```python
from openpyxl import load_workbook
from openpyxl.utils import range_boundaries
import pandas as pd

wb = load_workbook("merged.xlsx", data_only=True)
ws = wb.active

data = [list(r) for r in ws.iter_rows(values_only=True)]
# Apply merged-cell fill
for merged in ws.merged_cells.ranges:
    min_col, min_row, max_col, max_row = range_boundaries(str(merged))
    top = data[min_row - 1][min_col - 1]
    for r in range(min_row - 1, max_row):
        for c in range(min_col - 1, max_col):
            data[r][c] = top

df = pd.DataFrame(data[1:], columns=data[0])
```

## Sheet name gotchas

- Excel sheet names are limited to 31 characters. Longer strings get truncated when the workbook is saved.
- Characters `\ / * [ ] : ?` are invalid in sheet names. Normalise when generating sheet names downstream.
- `wb.sheetnames` returns the declared order; `wb.active` returns the sheet that was active when the workbook was last saved.
- Case: sheet lookup is case-sensitive in `openpyxl` (`wb["Summary"]`), case-insensitive in `pandas.read_excel(sheet_name="summary")` (engine-dependent — safer to pass the exact name).

## Hidden sheets

```python
from openpyxl import load_workbook

wb = load_workbook("report.xlsx", read_only=False)
for name in wb.sheetnames:
    state = wb[name].sheet_state  # 'visible' | 'hidden' | 'veryHidden'
    if state != "visible":
        print(f"NOTE: sheet {name!r} is {state}")
```

`veryHidden` sheets are still readable via `openpyxl` — Excel only prevents the normal user from un-hiding them from the UI.

## Defined names (named ranges)

Named ranges are the owner's intended anchors. Prefer them over hardcoded cell addresses:

```python
from openpyxl import load_workbook

wb = load_workbook("model.xlsx", data_only=True)
for dn in wb.defined_names.definedName:
    print(f"{dn.name:20s}  {dn.value}")
# Resolve a name to a value
ref = wb.defined_names["Revenue"].value  # e.g. "Summary!$B$5"
sheet, cell = ref.replace("$", "").split("!")
print(wb[sheet][cell].value)
```

## Formulas and cached values in one pass

Two workbook handles are cheaper than two full passes:

```python
from openpyxl import load_workbook

wb_f = load_workbook("model.xlsx", read_only=True, data_only=False)
wb_v = load_workbook("model.xlsx", read_only=True, data_only=True)

for name in wb_f.sheetnames:
    f_ws, v_ws = wb_f[name], wb_v[name]
    for f_row, v_row in zip(f_ws.iter_rows(), v_ws.iter_rows(values_only=True)):
        for f_cell, v in zip(f_row, v_row):
            if isinstance(f_cell.value, str) and f_cell.value.startswith("="):
                print(f"{name}!{f_cell.coordinate}  {f_cell.value!r} -> {v!r}")
```

If cached values are `None` where they should have numbers, the workbook was last saved from a tool that did not recalculate. See the companion `xlsx-writer` skill's `scripts/refresh_formulas.py` to force a LibreOffice recalc pass.

## Data validation (dropdowns, ranges)

`openpyxl` exposes data-validation rules per sheet:

```python
from openpyxl import load_workbook

wb = load_workbook("form.xlsx")
for name in wb.sheetnames:
    ws = wb[name]
    for dv in ws.data_validations.dataValidation:
        print(f"{name}: {dv.type} on {', '.join(str(r) for r in dv.sqref.ranges)}  -> {dv.formula1}")
```

Common `dv.type` values: `list` (dropdowns), `whole`, `decimal`, `date`, `time`, `textLength`, `custom`.

## Conditional formatting

For each sheet, rules live under `ws.conditional_formatting`:

```python
from openpyxl import load_workbook

wb = load_workbook("coverage.xlsx")
ws = wb.active
for sqref, rules in ws.conditional_formatting._cf_rules.items():
    for rule in rules:
        print(f"{ws.title}  {sqref}  {rule.type}  {rule.formula}")
```

Use this to understand how the workbook's author signalled OK / KO / WARNING visually — the colour coding is embedded here, not in the cell fills themselves.

## Embedded images

Images live under `xl/media/`. Extraction is a plain ZIP walk:

```python
import zipfile
from pathlib import Path

out = Path("/tmp/xlsx_media")
out.mkdir(exist_ok=True)
with zipfile.ZipFile("report.xlsx") as z:
    for name in z.namelist():
        if name.startswith("xl/media/"):
            (out / Path(name).name).write_bytes(z.read(name))
```

To learn which sheet a given image belongs to, inspect `xl/worksheets/_rels/sheetN.xml.rels` for the image relationship ID and the `drawing` reference on the sheet itself.

## Native chart data

Charts carry their source ranges explicitly. `openpyxl.chart` exposes them:

```python
from openpyxl import load_workbook

wb = load_workbook("dashboard.xlsx", data_only=True)
for name in wb.sheetnames:
    ws = wb[name]
    for chart in ws._charts:
        print(f"{name}  {type(chart).__name__}  title={chart.title}")
        for ser in chart.series:
            if ser.val and ser.val.numRef:
                print(f"  values: {ser.val.numRef.f}")
```

The `f` field is an A1 cell reference (e.g. `Summary!$B$2:$B$13`). Resolve it to values by reading those cells with `data_only=True`.

## Pivot tables

`openpyxl` can surface pivot tables but cannot execute them. Use it to read the pivot's source range and cache, then recompute the pivot with `pandas`:

```python
from openpyxl import load_workbook

wb = load_workbook("analysis.xlsx")
for name in wb.sheetnames:
    ws = wb[name]
    for pt in ws._pivots:
        print(f"{name}  cache_source: {pt.cacheSource.worksheetSource.ref}")
```

The cached values are in `xl/pivotCache/pivotCacheRecords*.xml`. For modern workflows, read the source data with `pandas` and call `.pivot_table(...)` — faster, cleaner, and avoids relying on brittle cached records.

## Print areas

```python
ws.print_area  # e.g. "$A$1:$F$50" or None
```

When it is set, it is the author's "what should show up on paper" selection — a useful hint for what counts as the report area.

## Batch-processing recipe

```python
from pathlib import Path
from openpyxl import load_workbook

def summary_for(path: Path) -> dict:
    wb = load_workbook(path, read_only=True, data_only=True)
    return {
        "path": str(path),
        "sheets": [
            {
                "name": ws.title,
                "state": ws.sheet_state,
                "rows": ws.max_row,
                "cols": ws.max_column,
            }
            for ws in wb.worksheets
        ],
    }

for p in Path("inputs").glob("*.xlsx"):
    print(summary_for(p))
```

## Full format mapping

| Extension | What it is | Engine |
|---|---|---|
| `.xlsx` | Open XML spreadsheet (ZIP) | `openpyxl` |
| `.xlsm` | Open XML spreadsheet + VBA macros (ZIP) | `openpyxl` (macros ignored for data extraction) |
| `.xlsb` | Binary 2007+ (not ZIP) | Convert via LibreOffice, then `openpyxl` |
| `.xls` | OLE compound document (pre-2007) | Convert via LibreOffice, or `xlrd<2` read-only |
| `.csv` / `.tsv` | Plain text | `pandas.read_csv` (not openpyxl) |

## Common pitfalls

- **`data_only=True` + save destroys formulas.** Never write back a workbook opened this way.
- **`wb.active` is not always "the first sheet".** It is whichever sheet was active when the workbook was last saved.
- **Empty trailing rows.** `ws.max_row` can overshoot. Strip trailing `None`-only rows before treating row counts as meaningful.
- **Merged cells collapse to one value.** Forward-fill before building a DataFrame (see above).
- **Floats and dates.** An Excel date is a float under the hood. If `pandas` does not parse a column, the cell format was "General", not "Date". Pass `parse_dates=[...]` explicitly.
- **Unicode in sheet names.** Perfectly valid; test your downstream code handles accented names.
- **`xlrd>=2` does not open `.xls`.** Pin `xlrd<2` if you need the legacy path without LibreOffice.
