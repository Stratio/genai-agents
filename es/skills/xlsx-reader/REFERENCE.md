# xlsx-reader — REFERENCE

Patrones avanzados que no pertenecen al SKILL.md principal. Carga este fichero cuando el workflow rápido/profundo de SKILL.md no sea suficiente — features específicas, casos borde, recetas batch.

## Lectura selectiva de columnas (ficheros grandes)

Leer 50 columnas cuando solo necesitas tres es derroche. Ambos motores soportan selección de columnas:

```python
# pandas: por nombre (cabecera inferida) o por letra (sin cabecera)
df = pd.read_excel("big.xlsx", usecols=["order_id", "amount", "ordered_at"])
df = pd.read_excel("big.xlsx", usecols="A,C,F:H")

# openpyxl: limita con max_col al iterar
from openpyxl import load_workbook
wb = load_workbook("big.xlsx", read_only=True, data_only=True)
ws = wb.active
for row in ws.iter_rows(values_only=True, min_col=1, max_col=3):
    ...
```

## Forzar dtypes

Las celdas de fecha de Excel a menudo viajan como floats, y los IDs numéricos de cliente pierden sus ceros a la izquierda. Fuerza el dtype al leer:

```python
df = pd.read_excel(
    "orders.xlsx",
    dtype={"customer_id": str, "order_id": str, "status": "category"},
    parse_dates=["ordered_at", "shipped_at"],
)
```

Para `openpyxl`, las celdas conservan su tipo Python original (`datetime`, `int`, `float`, `str`, `bool`, `None`) — no hace falta coerción.

## Manejo de celdas combinadas al reconstruir un DataFrame

Las celdas combinadas aparecen como una sola celda con el valor y las hermanas como `None` en `openpyxl`. Si pasas las filas crudas a `pandas`, pierdes información. Haz forward-fill en la región combinada:

```python
from openpyxl import load_workbook
from openpyxl.utils import range_boundaries
import pandas as pd

wb = load_workbook("merged.xlsx", data_only=True)
ws = wb.active

data = [list(r) for r in ws.iter_rows(values_only=True)]
# Aplicar forward-fill a celdas combinadas
for merged in ws.merged_cells.ranges:
    min_col, min_row, max_col, max_row = range_boundaries(str(merged))
    top = data[min_row - 1][min_col - 1]
    for r in range(min_row - 1, max_row):
        for c in range(min_col - 1, max_col):
            data[r][c] = top

df = pd.DataFrame(data[1:], columns=data[0])
```

## Gotchas de nombres de hoja

- Los nombres de hoja en Excel están limitados a 31 caracteres. Cadenas más largas se truncan al guardar el libro.
- Los caracteres `\ / * [ ] : ?` son inválidos en nombres de hoja. Normaliza al generar nombres de hoja downstream.
- `wb.sheetnames` devuelve el orden declarado; `wb.active` devuelve la hoja que estaba activa cuando el libro se guardó por última vez.
- Case: el lookup de hoja es case-sensitive en `openpyxl` (`wb["Summary"]`), case-insensitive en `pandas.read_excel(sheet_name="summary")` (depende del motor — más seguro pasar el nombre exacto).

## Hojas ocultas

```python
from openpyxl import load_workbook

wb = load_workbook("report.xlsx", read_only=False)
for name in wb.sheetnames:
    state = wb[name].sheet_state  # 'visible' | 'hidden' | 'veryHidden'
    if state != "visible":
        print(f"NOTA: hoja {name!r} está {state}")
```

Las hojas `veryHidden` siguen siendo legibles vía `openpyxl` — Excel solo impide al usuario normal re-mostrarlas desde la UI.

## Nombres definidos (rangos con nombre)

Los rangos con nombre son los anclajes intencionados del dueño del libro. Prefiérelos frente a direcciones de celda hardcodeadas:

```python
from openpyxl import load_workbook

wb = load_workbook("model.xlsx", data_only=True)
for dn in wb.defined_names.definedName:
    print(f"{dn.name:20s}  {dn.value}")
# Resolver un nombre a un valor
ref = wb.defined_names["Revenue"].value  # p. ej. "Summary!$B$5"
sheet, cell = ref.replace("$", "").split("!")
print(wb[sheet][cell].value)
```

## Fórmulas y valores cacheados en una pasada

Dos handles de libro son más baratos que dos pases completos:

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

Si los valores cacheados están `None` donde deberían tener números, el libro se guardó por última vez desde una herramienta que no recalculó. Ver `scripts/refresh_formulas.py` en la skill compañera `xlsx-writer` para forzar un pase de recálculo con LibreOffice.

## Validación de datos (dropdowns, rangos)

`openpyxl` expone reglas de validación de datos por hoja:

```python
from openpyxl import load_workbook

wb = load_workbook("form.xlsx")
for name in wb.sheetnames:
    ws = wb[name]
    for dv in ws.data_validations.dataValidation:
        print(f"{name}: {dv.type} en {', '.join(str(r) for r in dv.sqref.ranges)}  -> {dv.formula1}")
```

Valores comunes de `dv.type`: `list` (dropdowns), `whole`, `decimal`, `date`, `time`, `textLength`, `custom`.

## Formato condicional

Por cada hoja, las reglas viven bajo `ws.conditional_formatting`:

```python
from openpyxl import load_workbook

wb = load_workbook("coverage.xlsx")
ws = wb.active
for sqref, rules in ws.conditional_formatting._cf_rules.items():
    for rule in rules:
        print(f"{ws.title}  {sqref}  {rule.type}  {rule.formula}")
```

Úsalo para entender cómo el autor del libro señalizó visualmente OK / KO / WARNING — la codificación por color está embebida aquí, no en los fills de celda en sí.

## Imágenes embebidas

Las imágenes viven bajo `xl/media/`. La extracción es un walk de ZIP plano:

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

Para saber a qué hoja pertenece una imagen, inspecciona `xl/worksheets/_rels/sheetN.xml.rels` para el ID de relación de la imagen y la referencia `drawing` en la hoja en sí.

## Datos de gráficos nativos

Los gráficos llevan sus rangos de origen explícitamente. `openpyxl.chart` los expone:

```python
from openpyxl import load_workbook

wb = load_workbook("dashboard.xlsx", data_only=True)
for name in wb.sheetnames:
    ws = wb[name]
    for chart in ws._charts:
        print(f"{name}  {type(chart).__name__}  title={chart.title}")
        for ser in chart.series:
            if ser.val and ser.val.numRef:
                print(f"  valores: {ser.val.numRef.f}")
```

El campo `f` es una referencia A1 a celdas (p. ej. `Summary!$B$2:$B$13`). Resuélvela a valores leyendo esas celdas con `data_only=True`.

## Tablas dinámicas (pivot tables)

`openpyxl` puede exponer tablas dinámicas pero no puede ejecutarlas. Úsalo para leer el rango de origen y la caché del pivot, luego recalcula el pivot con `pandas`:

```python
from openpyxl import load_workbook

wb = load_workbook("analysis.xlsx")
for name in wb.sheetnames:
    ws = wb[name]
    for pt in ws._pivots:
        print(f"{name}  cache_source: {pt.cacheSource.worksheetSource.ref}")
```

Los valores cacheados están en `xl/pivotCache/pivotCacheRecords*.xml`. Para flujos modernos, lee los datos de origen con `pandas` y llama `.pivot_table(...)` — más rápido, más limpio, y evita depender de registros cacheados frágiles.

## Áreas de impresión

```python
ws.print_area  # p. ej. "$A$1:$F$50" o None
```

Cuando está definida, es la selección "qué debería aparecer en papel" del autor — una pista útil sobre qué cuenta como área del informe.

## Receta de procesamiento en batch

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

## Mapeo completo de formatos

| Extensión | Qué es | Motor |
|---|---|---|
| `.xlsx` | Open XML spreadsheet (ZIP) | `openpyxl` |
| `.xlsm` | Open XML spreadsheet + macros VBA (ZIP) | `openpyxl` (macros ignorados para extracción de datos) |
| `.xlsb` | Binario 2007+ (no ZIP) | Convertir vía LibreOffice, luego `openpyxl` |
| `.xls` | OLE compound document (pre-2007) | Convertir vía LibreOffice, o `xlrd<2` solo lectura |
| `.csv` / `.tsv` | Texto plano | `pandas.read_csv` (no openpyxl) |

## Pitfalls comunes

- **`data_only=True` + save destruye fórmulas.** Nunca escribas de vuelta un libro abierto así.
- **`wb.active` no siempre es "la primera hoja".** Es la que estaba activa al guardar el libro por última vez.
- **Filas finales vacías.** `ws.max_row` puede exceder. Recorta filas finales que son todo `None` antes de tratar conteos de filas como significativos.
- **Las celdas combinadas colapsan a un valor.** Haz forward-fill antes de construir un DataFrame (ver arriba).
- **Floats y fechas.** Una fecha de Excel es un float por debajo. Si `pandas` no parsea una columna, el formato de celda era "General", no "Fecha". Pasa `parse_dates=[...]` explícitamente.
- **Unicode en nombres de hoja.** Perfectamente válido; prueba que tu código downstream maneja nombres con acentos.
- **`xlrd>=2` no abre `.xls`.** Fija `xlrd<2` si necesitas el camino legacy sin LibreOffice.
