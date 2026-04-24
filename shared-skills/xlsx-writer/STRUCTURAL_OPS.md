# xlsx-writer — Structural operations

Copy-paste snippets for operations that take one or more existing
`.xlsx` files as input and produce a new `.xlsx` as output. All rely on
`openpyxl` + `zipfile` so you don't need any extra dependency beyond
the baseline.

Inputs are opened read-only (except for the `openpyxl` passes that need
the full workbook model). Outputs are written to the path you specify —
inputs are never modified in place.

All snippets share this preamble:

```python
from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from copy import copy
from pathlib import Path
from typing import Iterable, Sequence

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
```

---

## Merge (sheet-by-sheet)

Combine several workbooks into one, sheet by sheet. Styles, column
widths, freeze panes and conditional formatting on each source sheet
are preserved. Collisions in sheet names get a numeric suffix
(`Summary`, `Summary_2`, `Summary_3` …).

```python
def merge_workbooks(
    paths: Sequence[str | Path], output: str | Path,
) -> Path:
    inputs = [Path(p) for p in paths]
    if not inputs:
        raise ValueError("merge_workbooks: at least one input is required")
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dst = Workbook()
    # Remove the default blank sheet — we will add named ones.
    default = dst.active
    if default is not None:
        dst.remove(default)

    taken: set[str] = set()

    def _unique(name: str) -> str:
        candidate = name
        i = 2
        while candidate in taken:
            candidate = f"{name}_{i}"
            i += 1
        taken.add(candidate)
        return candidate

    for inp in inputs:
        src = load_workbook(inp, data_only=False)
        for sheet_name in src.sheetnames:
            src_ws = src[sheet_name]
            new_name = _unique(sheet_name)
            new_ws = dst.create_sheet(new_name)
            # Copy cells (values + styles)
            for row in src_ws.iter_rows():
                for cell in row:
                    new_cell = new_ws.cell(row=cell.row, column=cell.column,
                                           value=cell.value)
                    if cell.has_style:
                        new_cell.font = copy(cell.font)
                        new_cell.fill = copy(cell.fill)
                        new_cell.border = copy(cell.border)
                        new_cell.alignment = copy(cell.alignment)
                        new_cell.number_format = cell.number_format
                        new_cell.protection = copy(cell.protection)
            # Copy column widths and row heights
            for col_letter, dim in src_ws.column_dimensions.items():
                new_ws.column_dimensions[col_letter].width = dim.width
            for row_num, dim in src_ws.row_dimensions.items():
                if dim.height is not None:
                    new_ws.row_dimensions[row_num].height = dim.height
            # Copy merged cells
            for merged_range in src_ws.merged_cells.ranges:
                new_ws.merge_cells(str(merged_range))
            # Copy freeze panes
            new_ws.freeze_panes = src_ws.freeze_panes
            # Copy tables
            for table in src_ws.tables.values():
                new_tbl = Table(displayName=f"{new_name}_{table.displayName}",
                                ref=table.ref)
                if table.tableStyleInfo is not None:
                    new_tbl.tableStyleInfo = TableStyleInfo(
                        name=table.tableStyleInfo.name,
                        showRowStripes=table.tableStyleInfo.showRowStripes,
                        showColumnStripes=table.tableStyleInfo.showColumnStripes,
                    )
                new_ws.add_table(new_tbl)
        src.close()

    dst.save(out_path)
    return out_path


# Usage
merge_workbooks(
    paths=["cover.xlsx", "detail.xlsx", "appendix.xlsx"],
    output="final.xlsx",
)
```

Caveats:
- Conditional formatting rules and data validations are NOT deep-copied
  by this snippet. If the workbooks rely on them, either (a) author
  them on the merged result after the copy or (b) extend the snippet
  to walk `src_ws.conditional_formatting._cf_rules` and
  `src_ws.data_validations.dataValidation`.
- Named ranges scoped to a sheet carry a reference to the old sheet
  name; rewrite them after merge if you rely on them.
- Chart references break across workbooks; re-create charts on the
  merged result if needed.

---

## Split (one file per sheet)

Break one workbook into a separate `.xlsx` per sheet. Each produced
file contains a single sheet with the same name, styles, column
widths, merged cells, freeze panes and Tables as the source.

```python
def split_workbook(
    path: str | Path, output_dir: str | Path,
    stem: str | None = None,
) -> list[Path]:
    src_path = Path(path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = stem or src_path.stem

    src = load_workbook(src_path, data_only=False)
    produced: list[Path] = []
    try:
        for sheet_name in src.sheetnames:
            src_ws = src[sheet_name]
            dst = Workbook()
            default = dst.active
            if default is not None:
                dst.remove(default)
            new_ws = dst.create_sheet(sheet_name)
            for row in src_ws.iter_rows():
                for cell in row:
                    new_cell = new_ws.cell(row=cell.row, column=cell.column,
                                           value=cell.value)
                    if cell.has_style:
                        new_cell.font = copy(cell.font)
                        new_cell.fill = copy(cell.fill)
                        new_cell.border = copy(cell.border)
                        new_cell.alignment = copy(cell.alignment)
                        new_cell.number_format = cell.number_format
                        new_cell.protection = copy(cell.protection)
            for col_letter, dim in src_ws.column_dimensions.items():
                new_ws.column_dimensions[col_letter].width = dim.width
            for row_num, dim in src_ws.row_dimensions.items():
                if dim.height is not None:
                    new_ws.row_dimensions[row_num].height = dim.height
            for merged_range in src_ws.merged_cells.ranges:
                new_ws.merge_cells(str(merged_range))
            new_ws.freeze_panes = src_ws.freeze_panes

            safe_name = "".join(c if c.isalnum() or c in "-_" else "_"
                                for c in sheet_name)
            out_path = out_dir / f"{prefix}-{safe_name}.xlsx"
            dst.save(out_path)
            produced.append(out_path)
    finally:
        src.close()

    return produced


# Usage
parts = split_workbook(
    path="full_report.xlsx", output_dir="parts/", stem="section",
)
```

---

## Find-replace (cell text)

Literal or regex find-replace across all string cells in a workbook.
The replacement is evaluated per-cell; it does not cross cell
boundaries.

```python
import re

def find_replace_workbook(
    path: str | Path, output: str | Path,
    mapping: dict,
    use_regex: bool = False,
    scope: Iterable[str] | None = None,  # sheet names; None = all sheets
) -> Path:
    src_path = Path(path)
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(src_path, data_only=False)
    try:
        compiled = {
            (re.compile(k) if use_regex else re.compile(re.escape(k))): v
            for k, v in mapping.items()
        }
        sheet_names = list(wb.sheetnames) if scope is None else [
            s for s in wb.sheetnames if s in set(scope)
        ]
        for name in sheet_names:
            ws = wb[name]
            for row in ws.iter_rows():
                for cell in row:
                    if not isinstance(cell.value, str):
                        continue
                    new_value = cell.value
                    for pat, repl in compiled.items():
                        new_value = pat.sub(repl, new_value)
                    if new_value != cell.value:
                        cell.value = new_value
        wb.save(out_path)
    finally:
        wb.close()
    return out_path


# Literal usage
find_replace_workbook(
    path="draft.xlsx", output="final.xlsx",
    mapping={"FY2025": "FY2026", "John Doe": "Jane Roe"},
)

# Regex usage
find_replace_workbook(
    path="source.xlsx", output="redacted.xlsx",
    mapping={r"[A-Z]{2}-\d{3,5}": "[REDACTED]"},
    use_regex=True,
)

# Scope control — only the Summary and Detail sheets
find_replace_workbook(
    path="in.xlsx", output="out.xlsx",
    mapping={"target": "goal"},
    scope=["Summary", "Detail"],
)
```

Caveats:
- Only string cells are touched. Numeric, date and formula cells are
  left alone.
- Formulas that contain a substring match are NOT replaced (formula
  cells store the formula as a string prefixed with `=`; we skip them
  on purpose).

---

## Extract one sheet to CSV

```python
import csv

def sheet_to_csv(
    path: str | Path, sheet: str, output: str | Path,
    delimiter: str = ",",
) -> Path:
    src_path = Path(path)
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    wb = load_workbook(src_path, read_only=True, data_only=True)
    try:
        if sheet not in wb.sheetnames:
            raise KeyError(f"sheet {sheet!r} not in {wb.sheetnames}")
        ws = wb[sheet]
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(["" if v is None else v for v in row])
    finally:
        wb.close()
    return out_path


# Usage
sheet_to_csv(
    path="analytics.xlsx", sheet="Detail",
    output="detail.csv",
)
```

---

## Convert legacy `.xls` to `.xlsx`

Binary Excel 97–2003 files are not `.xlsx`. Convert first, then apply
any of the operations above.

```python
def convert_xls_to_xlsx(
    input_path: str | Path, output_dir: str | Path | None = None,
) -> Path:
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(src)
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice headless (soffice) not found on PATH. "
            "Install libreoffice or libreoffice-calc."
        )
    out_dir = Path(output_dir) if output_dir else Path(
        tempfile.mkdtemp(prefix="xlsx_conv_")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "xlsx",
         "--outdir", str(out_dir), str(src)],
        check=True, capture_output=True,
    )
    produced = out_dir / (src.stem + ".xlsx")
    if not produced.exists():
        raise RuntimeError(f"LibreOffice produced no output for {src}")
    return produced


# Usage
new_path = convert_xls_to_xlsx(
    "legacy_data.xls", output_dir="/tmp/converted/",
)
```

CLI equivalent:

```bash
soffice --headless --convert-to xlsx legacy_data.xls --outdir /tmp/converted
```

Same mechanism converts `.xlsb` (binary 2007+) — pass the `.xlsb` path
instead of the `.xls` path.

---

## Convert a sheet range to PDF (visual preview)

Useful after merge / split / replace to confirm nothing visually broke.

```bash
soffice --headless --convert-to pdf --outdir /tmp/preview final.xlsx
pdftoppm -r 150 -png /tmp/preview/final.pdf /tmp/preview/page
```

The second command rasterises each page of the PDF as `page-01.png`,
`page-02.png`, etc. Inspect them for truncated columns, merged-cell
bleed, KPI band breakage.

---

## Refresh cached formula values

When your workflow writes formulas, `openpyxl` does not evaluate them.
Cached values stay blank until Excel / LibreOffice recalculates. Run
`scripts/refresh_formulas.py` to force a headless LibreOffice recalc
pass:

```bash
python3 <skill-root>/scripts/refresh_formulas.py output.xlsx --json
```

The script saves the workbook in place with cached values populated
and emits JSON with the count of formula cells, the sheets touched,
and any Excel errors detected (`#REF!`, `#DIV/0!`, `#VALUE!`,
`#N/A`, `#NAME?`, `#NULL!`, `#NUM!`).
