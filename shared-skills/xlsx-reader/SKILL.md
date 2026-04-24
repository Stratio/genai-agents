---
name: xlsx-reader
description: "Inspect, analyze, and extract content from Excel workbooks (.xlsx, .xlsm, and legacy .xls) intelligently. Use this skill whenever you need to read what is inside a spreadsheet — cell data, tables, formulas, metadata, chart data, or hidden sheets. Covers narrow datasets, multi-sheet workbooks with an index, files with formulas that depend on cached values, cross-sheet references, legacy binary .xls, and .xlsm with macros that can be ignored for data extraction. Always run a quick diagnostic before extraction to pick the right strategy."
argument-hint: "[path/to/file.xlsx]"
---

# Skill: XLSX Reader

A disciplined approach to getting useful content out of spreadsheets. Different files need different tactics — a flat CSV-like sheet behaves nothing like a workbook whose cover sheet is a KPI dashboard fed by formulas across ten detail sheets, and neither behaves like a legacy `.xls` saved from Office 2003. Diagnose first, extract second.

## 1. Two modes: quick and deep

This skill supports two ways of working:

**Quick mode — `scripts/quick_extract.py`**
One-shot extraction that returns structured output (Markdown, CSV, or JSON). Use it when:
- The workbook is "normal" (tabular data on one or a few sheets)
- You want values without thinking about which library to use
- You're batch-processing many files
- You're feeding the output directly to another agent or LLM

**Deep mode — the workflow below**
Step-by-step diagnosis and extraction. Use it when:
- The workbook has formulas you need to read as formulas (not just their cached values)
- You need to extract embedded images or chart data
- Quick mode failed, returned empty cells where values were visible, or skipped a sheet
- The file is a legacy binary `.xls` (needs conversion first)
- The workbook has hidden sheets, merged cells, or conditional formatting that matters for interpretation

Default to quick mode. Fall back to deep mode when quick mode isn't enough.

### Quick mode usage

```bash
# Extract everything (first sheet, Markdown)
python3 <skill-root>/scripts/quick_extract.py workbook.xlsx

# All sheets, one CSV per sheet to stdout
python3 <skill-root>/scripts/quick_extract.py workbook.xlsx --sheet all --format csv

# Specific sheet, JSON output (rows as list of dicts)
python3 <skill-root>/scripts/quick_extract.py workbook.xlsx --sheet Summary --format json

# Cap the row count for large sheets
python3 <skill-root>/scripts/quick_extract.py workbook.xlsx --max-rows 200

# Read from stdin
cat workbook.xlsx | python3 <skill-root>/scripts/quick_extract.py -
```

The script:
- Returns the chosen format on stdout (Markdown tables by default)
- Returns diagnostics on stderr (which engine ran, which sheets, warnings)
- Exits 0 on success, 1 on failure
- Auto-detects available engines and falls back through a chain
- Never pollutes stdout — the output is safe to pipe into another tool

The engine chain tries, in order: **openpyxl (read-only) → pandas (openpyxl backend) → raw-XML walk over zipfile**. The first one that produces a non-empty sheet wins.

## 2. Golden rule for deep mode: diagnose before you extract

Never open a workbook blindly with `openpyxl`. A file whose cached formula values are stale will return `None` where a user expects numbers. A workbook with ten hidden sheets may have the actual data outside the "visible" ones. A `.xls` with a `.xlsx` extension still fails `zipfile.ZipFile`. A two-second diagnostic saves hours of debugging the wrong sheet.

Run this inspection block first:

```bash
# Is it actually a .xlsx / .xlsm (ZIP) or a legacy .xls (OLE compound)?
file target.xlsx

# For a .xlsx / .xlsm, list the ZIP contents. What parts are inside?
unzip -l target.xlsx

# How many sheets, and their names (including hidden ones)?
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('target.xlsx', read_only=True, data_only=False)
for name in wb.sheetnames:
    st = wb[name].sheet_state  # 'visible' | 'hidden' | 'veryHidden'
    print(f'{st:11s}  {name}')
"

# Core metadata (title, author, creation / modification)
unzip -p target.xlsx docProps/core.xml | head -20

# Any defined names (named ranges) that hint at named data regions?
unzip -p target.xlsx xl/workbook.xml | grep -oE '<definedName[^>]*>' | head
```

What each output tells you:

- **`file`** — if it reports `Microsoft Excel 2007+` or `Zip archive data`, it is a `.xlsx`/`.xlsm` (ZIP). If it reports `Composite Document File V2 Document`, it is a legacy binary `.xls` and you must convert first.
- **`unzip -l`** — the part inventory is your map. Key parts: `xl/workbook.xml` (sheet index + defined names), `xl/worksheets/sheet*.xml` (one per sheet), `xl/sharedStrings.xml` (deduplicated string table), `xl/media/` (embedded images), `xl/styles.xml`, `xl/charts/` (chart XML when present), `docProps/core.xml` (metadata).
- **Sheet listing with `sheet_state`** — `visible` means the sheet is shown in Excel's tab bar; `hidden` means the user hid it via the Hide command; `veryHidden` means it was hidden programmatically (via VBA) and a normal user cannot re-show it. Any of those can still hold important data.
- **`docProps/core.xml`** — author, title, created/modified timestamps. Useful when the user asks "who produced this" or "when was this last touched".
- **`definedName`** — named ranges like `Summary!Revenue` or `Assumptions` are often the anchors the workbook's owner expects you to read; check them before rescanning random cells.

## 3. Pick a strategy based on what the workbook contains

Classify in your head, then apply the matching workflow.

### Tabular datasets (one sheet, rectangular data, maybe a header row)

Primary tool: `pandas` with the `openpyxl` backend. It handles header detection, type coercion, date parsing and column selection in one call.

```python
import pandas as pd

# Default: first sheet, first row as header
df = pd.read_excel("dataset.xlsx")

# Read every sheet as a dict of DataFrames
sheets = pd.read_excel("dataset.xlsx", sheet_name=None)

# Read only the columns you need, force dtypes
df = pd.read_excel(
    "dataset.xlsx",
    usecols=["order_id", "customer_id", "amount"],
    dtype={"order_id": str, "customer_id": str},
    parse_dates=["ordered_at"],
)
```

For a first look without pandas:

```python
from openpyxl import load_workbook

wb = load_workbook("dataset.xlsx", read_only=True, data_only=True)
ws = wb.active
for row in ws.iter_rows(values_only=True, max_row=5):
    print(row)
```

### Multi-sheet workbooks with a cover / index sheet

Symptom: the first sheet names other sheets (e.g. a "Contents" or "Summary" sheet with links or references). The detail is spread across the others.

Read the cover first to figure out the semantic of each detail sheet, then read only the sheets you need:

```python
from openpyxl import load_workbook

wb = load_workbook("multi.xlsx", read_only=True, data_only=True)
cover = wb["Summary"]  # or wb.active
tabs_of_interest = [row[0].value for row in cover.iter_rows(min_row=2) if row[0].value]

for tab in tabs_of_interest:
    if tab in wb.sheetnames:
        ws = wb[tab]
        # process ws
```

### Workbooks whose values are driven by formulas

Two modes live inside the same file:

- `data_only=False` (default) — you read each cell's **formula** (e.g. `"=SUM(B2:B10)"`).
- `data_only=True` — you read the **last calculated value** Excel cached when the workbook was saved.

If `data_only=True` returns `None` for cells the user expects to have values, the cached values are stale (nobody opened the workbook in Excel after the last formula change). Two options:

1. Ask the user to open the workbook in Excel/LibreOffice, let it recalculate, save and resend.
2. Use the companion `xlsx-writer` skill's `scripts/refresh_formulas.py` to force a LibreOffice recalc pass — it updates cached values in place.

**Never save a workbook that you opened with `data_only=True`**: openpyxl writes the cached values as literal constants, destroying every formula. Extract, close, move on.

### Workbooks with cross-sheet references

Symptom: formulas like `=Summary!B5` or `=Assumptions!Rate * Detail!C10`.

Inspect formulas with `data_only=False` and the resolved values with `data_only=True` in two passes:

```python
from openpyxl import load_workbook

wb_formulas = load_workbook("model.xlsx", read_only=True, data_only=False)
wb_values = load_workbook("model.xlsx", read_only=True, data_only=True)

for sheet_name in wb_formulas.sheetnames:
    f_ws = wb_formulas[sheet_name]
    v_ws = wb_values[sheet_name]
    for f_row, v_row in zip(f_ws.iter_rows(values_only=True),
                             v_ws.iter_rows(values_only=True)):
        for f_cell, v_cell in zip(f_row, v_row):
            if isinstance(f_cell, str) and f_cell.startswith("="):
                print(f"{sheet_name}: {f_cell!r} -> {v_cell!r}")
```

### `.xlsm` (macro-enabled) workbooks

Symptom: extension is `.xlsm`, or `unzip -l` shows `xl/vbaProject.bin`.

For data extraction, treat them like a `.xlsx` — `openpyxl` and `pandas` read the cells and ignore the macro bytes. Do NOT attempt to execute the macros. If the workbook's data is computed at runtime by a macro (rare outside of accounting tools), the cached values apply: recalc via LibreOffice or ask the user to save after opening.

### Legacy binary `.xls` files

Symptom: `file` reports `Composite Document File V2 Document`, or `zipfile.ZipFile` raises `BadZipFile`.

Three paths, in order of robustness:

1. Convert with LibreOffice headless (recommended — same mechanism used by docx-reader / pptx-reader):

   ```bash
   soffice --headless --convert-to xlsx --outdir /tmp/xlsx_in target.xls
   # /tmp/xlsx_in/target.xlsx is now a modern .xlsx
   ```

2. Use `xlrd<2` (read-only, limited). Do not install `xlrd>=2` — it dropped `.xls` support.
3. If neither is available, return a diagnostic telling the caller the file is legacy and cannot be processed without LibreOffice or an older `xlrd`.

### `.xlsb` (binary 2007+)

Not supported by `openpyxl`. Convert with LibreOffice headless (`--convert-to xlsx`) first, then treat the output like any `.xlsx`.

### CSV / TSV sent as "an Excel file"

Users often attach a `.csv` or `.tsv` and describe it as "an Excel file". Detect via the file signature (no ZIP magic bytes, plain text) and fall back to `pandas.read_csv` with sensible defaults (`sep=None, engine="python"` auto-detects the delimiter). If the separator still fails, sniff it:

```python
import csv
with open("data.csv", newline="") as f:
    sample = f.read(8192)
dialect = csv.Sniffer().sniff(sample)
```

### Mixed workbooks

Real-world files mix everything: a styled cover sheet, two rectangular datasets on sheets 2-3, a sheet of parameters on 4, a sheet with formulas referencing 2-3 on 5, and maybe an appendix with images. Don't try to extract in one pass:

1. Diagnose first (§2). Identify the role of each sheet.
2. Pull tabular data with `pandas` per target sheet.
3. Pull formulas with `openpyxl(data_only=False)` where the formulas themselves are the artifact of interest.
4. Extract images from `xl/media/` with `zipfile` only if the user asked for them.
5. Surface metadata separately.
6. Join findings at the end as a structured report.

## 4. Token-awareness when feeding content into an LLM

A spreadsheet with 50,000 rows serialised as a Markdown table is roughly 1.5 million tokens — almost always too much. Work smart:

- Read only the columns and rows you need. `pandas` `usecols=` and `nrows=` help.
- Summarise before emitting: head, tail, column types, null counts, unique counts — enough for an agent to decide what to ask next.
- If the workbook has a KPI / summary sheet, emit **that one** and hide the detail sheets unless asked.
- For a quick glance, `--max-rows` on `scripts/quick_extract.py` caps the emitted rows per sheet.

Rough token cost (Markdown output):
- Small tabular sheet (<100 rows, 5 columns): ~1,500 tokens
- Medium sheet (1,000 rows, 10 columns): ~25,000 tokens
- Large sheet (>10,000 rows): you should NOT be emitting this raw — aggregate first

## 5. Metadata

`docProps/core.xml` and `docProps/app.xml` carry the interesting metadata:

```python
import zipfile
from lxml import etree

NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}

with zipfile.ZipFile("workbook.xlsx") as z:
    with z.open("docProps/core.xml") as f:
        core = etree.parse(f).getroot()

def _get(xpath):
    node = core.find(xpath, NS)
    return node.text if node is not None else None

print({
    "title": _get("dc:title"),
    "author": _get("dc:creator"),
    "created": _get("dcterms:created"),
    "modified": _get("dcterms:modified"),
})
```

Workbook-level data (defined names, active sheet, visibility) lives in `xl/workbook.xml` — inspect via `openpyxl`'s `wb.defined_names` and `wb.sheetnames` or parse the XML directly.

## 6. Cleaning extracted output

Raw extraction usually needs a small pass:
- Drop all-`None` trailing rows (common artifact of `openpyxl` over-reading empty cells)
- Coerce booleans and `datetime` to strings if downstream expects JSON
- Collapse whitespace inside cell values (multi-line cells carry `\n`)
- Preserve the cell formula representation when the caller asked for formulas — do NOT stringify a formula like `=A1+B1` into its cached value silently

## 7. When to load `REFERENCE.md`

`REFERENCE.md` covers advanced patterns: targeted column selection with `usecols` and `dtype`, handling merged cells when reconstructing DataFrames, iterating conditional formatting and data validation rules, reading embedded chart data via `openpyxl.chart`, surveying defined names and print areas, inspecting pivot table caches, batch-processing recipes, and the full mapping between `.xlsx`, `.xlsm`, `.xlsb` and `.xls`.

## 8. Dependencies recap

Python: `openpyxl`, `pandas`, `lxml` (transitive from openpyxl). Optional: `xlrd<2` for read-only legacy `.xls` when LibreOffice is not available.

System: `libreoffice` / `libreoffice-calc` for legacy `.xls` and `.xlsb` conversion. Already part of the sandbox image.

Without LibreOffice and without `xlrd<2`, the skill cannot open legacy binary `.xls` or `.xlsb`. Modern `.xlsx` and `.xlsm` work with `openpyxl` alone.

---

Creating, editing, merging, splitting, finding-replacing, converting legacy `.xls`, authoring analytical workbooks, producing coverage matrices with conditional formatting, and anything else that ends with saving a spreadsheet file live in the companion `xlsx-writer` skill.
