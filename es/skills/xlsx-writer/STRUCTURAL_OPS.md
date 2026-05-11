# xlsx-writer — Operaciones estructurales

Snippets copia-pega para operaciones que toman uno o más ficheros `.xlsx` existentes como entrada y producen un nuevo `.xlsx` como salida. Todos se apoyan en `openpyxl` + `zipfile`, así que no necesitas ninguna dependencia adicional más allá del baseline.

Las entradas se abren en read-only (excepto los pases de `openpyxl` que necesitan el modelo completo del libro). Las salidas se escriben en la ruta que especifiques — las entradas nunca se modifican in place.

Todos los snippets comparten este preámbulo:

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

## Merge (hoja por hoja)

Combina varios libros en uno, hoja por hoja. Se preservan estilos, anchos de columna, freeze panes y formato condicional de cada hoja origen. Las colisiones en nombres de hoja reciben un sufijo numérico (`Summary`, `Summary_2`, `Summary_3` …).

```python
def merge_workbooks(
    paths: Sequence[str | Path], output: str | Path,
) -> Path:
    inputs = [Path(p) for p in paths]
    if not inputs:
        raise ValueError("merge_workbooks: se requiere al menos una entrada")
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dst = Workbook()
    # Elimina la hoja por defecto vacía — añadiremos las nombradas.
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
            # Copiar celdas (valores + estilos)
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
            # Copiar anchos de columna y alturas de fila
            for col_letter, dim in src_ws.column_dimensions.items():
                new_ws.column_dimensions[col_letter].width = dim.width
            for row_num, dim in src_ws.row_dimensions.items():
                if dim.height is not None:
                    new_ws.row_dimensions[row_num].height = dim.height
            # Copiar celdas combinadas
            for merged_range in src_ws.merged_cells.ranges:
                new_ws.merge_cells(str(merged_range))
            # Copiar freeze panes
            new_ws.freeze_panes = src_ws.freeze_panes
            # Copiar tables
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


# Uso
merge_workbooks(
    paths=["cover.xlsx", "detail.xlsx", "appendix.xlsx"],
    output="final.xlsx",
)
```

Caveats:
- Las reglas de formato condicional y validaciones de datos NO se copian en profundidad por este snippet. Si los libros dependen de ellas, o (a) las autoras sobre el resultado fusionado tras la copia, o (b) extiendes el snippet para recorrer `src_ws.conditional_formatting._cf_rules` y `src_ws.data_validations.dataValidation`.
- Los rangos con nombre scoped a una hoja llevan una referencia al viejo nombre de hoja; reescríbelos tras el merge si dependes de ellos.
- Las referencias de gráfico se rompen entre libros; re-crea los gráficos sobre el resultado fusionado si hacen falta.

---

## Split (un fichero por hoja)

Divide un libro en un `.xlsx` separado por hoja. Cada fichero producido contiene una sola hoja con el mismo nombre, estilos, anchos de columna, celdas combinadas, freeze panes y Tables que la fuente.

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


# Uso
parts = split_workbook(
    path="full_report.xlsx", output_dir="parts/", stem="section",
)
```

---

## Buscar-y-reemplazar (texto de celda)

Buscar-y-reemplazar literal o regex en todas las celdas de tipo string de un libro. El reemplazo se evalúa por celda; no cruza fronteras de celda.

```python
import re

def find_replace_workbook(
    path: str | Path, output: str | Path,
    mapping: dict,
    use_regex: bool = False,
    scope: Iterable[str] | None = None,  # nombres de hojas; None = todas
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


# Uso literal
find_replace_workbook(
    path="draft.xlsx", output="final.xlsx",
    mapping={"FY2025": "FY2026", "Juan Pérez": "María Rodríguez"},
)

# Uso con regex
find_replace_workbook(
    path="source.xlsx", output="redacted.xlsx",
    mapping={r"[A-Z]{2}-\d{3,5}": "[REDACTED]"},
    use_regex=True,
)

# Control de scope — solo las hojas Summary y Detail
find_replace_workbook(
    path="in.xlsx", output="out.xlsx",
    mapping={"target": "objetivo"},
    scope=["Summary", "Detail"],
)
```

Caveats:
- Solo se tocan celdas string. Celdas numéricas, de fecha y de fórmula se dejan en paz.
- Las fórmulas que contienen un substring de match NO se reemplazan (las celdas de fórmula almacenan la fórmula como string prefijada con `=`; las saltamos a propósito).

---

## Extraer una hoja a CSV

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
            raise KeyError(f"sheet {sheet!r} no está en {wb.sheetnames}")
        ws = wb[sheet]
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(["" if v is None else v for v in row])
    finally:
        wb.close()
    return out_path


# Uso
sheet_to_csv(
    path="analytics.xlsx", sheet="Detail",
    output="detail.csv",
)
```

---

## Convertir `.xls` legacy a `.xlsx`

Los ficheros binarios de Excel 97–2003 no son `.xlsx`. Convierte primero, luego aplica cualquiera de las operaciones anteriores.

```python
def convert_xls_to_xlsx(
    input_path: str | Path, output_dir: str | Path | None = None,
) -> Path:
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(src)
    if shutil.which("soffice") is None:
        raise RuntimeError(
            "LibreOffice headless (soffice) no encontrado en PATH. "
            "Instala libreoffice o libreoffice-calc."
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
        raise RuntimeError(f"LibreOffice no produjo salida para {src}")
    return produced


# Uso
new_path = convert_xls_to_xlsx(
    "legacy_data.xls", output_dir="/tmp/converted/",
)
```

Equivalente CLI:

```bash
soffice --headless --convert-to xlsx legacy_data.xls --outdir /tmp/converted
```

El mismo mecanismo convierte `.xlsb` (binario 2007+) — pasa la ruta del `.xlsb` en vez de la del `.xls`.

---

## Convertir un rango de hoja a PDF (preview visual)

Útil tras merge / split / replace para confirmar que nada se rompió visualmente.

```bash
soffice --headless --convert-to pdf --outdir /tmp/preview final.xlsx
pdftoppm -r 150 -png /tmp/preview/final.pdf /tmp/preview/page
```

El segundo comando rasteriza cada página del PDF como `page-01.png`, `page-02.png`, etc. Inspecciónalas buscando columnas truncadas, sangrado de celdas combinadas, rotura de banda KPI.

---

## Refrescar valores cacheados de fórmulas

Cuando tu flujo escribe fórmulas, `openpyxl` no las evalúa. Los valores cacheados se quedan en blanco hasta que Excel / LibreOffice recalcule. Ejecuta `scripts/refresh_formulas.py` para forzar un pase de recálculo con LibreOffice headless:

```bash
python3 <skill-root>/scripts/refresh_formulas.py output.xlsx --json
```

El script guarda el libro in place con valores cacheados poblados y emite JSON con el conteo de celdas con fórmula, las hojas tocadas, y cualquier error de Excel detectado (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`).
