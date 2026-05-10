# xlsx-writer — REFERENCE

Cookbook de snippets listos para adaptar de los bloques de construcción listados en SKILL.md §7. Carga este fichero cuando el scaffold en SKILL.md §4 no sea suficiente — primitivas específicas, casos borde, patrones avanzados.

Todos los snippets asumen:

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Alignment, Border, Color, Font, PatternFill, Side,
)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

# Tokens de diseño del tema — ver SKILL.md §3 y §4.
DESIGN = {...}

def hx(h: str) -> str:
    return h.lstrip("#").upper()
```

## Banda KPI (cuatro cards, celdas combinadas)

El helper `add_kpi_band` en SKILL.md §4 produce una fila de 4 cards. Usa esta versión cuando necesites conteos de cards diferentes o subtítulos personalizados.

```python
def add_kpi_band(ws, row: int, kpis: list[dict], cols_per_card: int = 3) -> None:
    col = 1
    thin = Side(border_style="thin", color=hx(DESIGN["rule"]))
    bord = Border(left=thin, right=thin, top=thin, bottom=thin)
    for kpi in kpis:
        # Label (fill primary)
        ws.merge_cells(start_row=row, start_column=col,
                       end_row=row, end_column=col + cols_per_card - 1)
        label = ws.cell(row=row, column=col, value=kpi["label"])
        label.fill = PatternFill("solid", fgColor=hx(DESIGN["primary"]))
        label.font = Font(name=DESIGN["body"], size=DESIGN["size_kpi_lbl"],
                          color=hx(DESIGN["primary_ink"]), bold=True)
        label.alignment = Alignment(horizontal="center", vertical="center")
        # Valor (fuente display)
        ws.merge_cells(start_row=row + 1, start_column=col,
                       end_row=row + 2, end_column=col + cols_per_card - 1)
        value = ws.cell(row=row + 1, column=col, value=kpi["value"])
        value.font = Font(name=DESIGN["display"], size=DESIGN["size_kpi"],
                          bold=True, color=hx(DESIGN["ink"]))
        value.alignment = Alignment(horizontal="center", vertical="center")
        # Subtítulo
        ws.merge_cells(start_row=row + 3, start_column=col,
                       end_row=row + 3, end_column=col + cols_per_card - 1)
        sub = ws.cell(row=row + 3, column=col, value=kpi.get("subtitle", ""))
        sub.font = Font(name=DESIGN["body"], size=DESIGN["size_small"],
                        color=hx(DESIGN["muted"]))
        sub.alignment = Alignment(horizontal="center", vertical="center")
        # Bordes alrededor de la card
        for r in range(row, row + 4):
            for c in range(col, col + cols_per_card):
                ws.cell(row=r, column=c).border = bord
        col += cols_per_card
    ws.row_dimensions[row + 1].height = 28
    ws.row_dimensions[row + 2].height = 28
```

## Table nativa

La primitiva preferida para cualquier dato rectangular con cabecera. Proporciona autofilter, sort, banded styling, y preserva el formato al insertar filas.

```python
def add_native_table(
    ws, header: list[str], rows: list[list],
    start_cell: str = "A1", name: str = "DataTable",
    style: str = "TableStyleMedium2",
) -> None:
    first_col = ws[start_cell].column
    first_row = ws[start_cell].row
    ws.cell(row=first_row, column=first_col).value = None  # inicio limpio
    # Escribir cabecera
    for i, h in enumerate(header):
        ws.cell(row=first_row, column=first_col + i, value=h)
    # Escribir filas
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            ws.cell(row=first_row + r, column=first_col + c, value=value)
    # Adjuntar table
    last_col_letter = get_column_letter(first_col + len(header) - 1)
    last_row = first_row + len(rows)
    ref = f"{start_cell}:{last_col_letter}{last_row}"
    tbl = Table(displayName=name, ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name=style, showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(tbl)
```

Los nombres de Table deben ser únicos en el libro y Excel-safe (letras, dígitos, underscore, empezar por letra). `"coverage matrix"` es inválido; usa `"CoverageMatrix"` o `"coverage_matrix"`.

Estilos built-in que conviene conocer:

- `TableStyleLight1` / `Light9` / `Light15` — banding sutil para libros editoriales
- `TableStyleMedium2` (default en Excel) — legible para la mayoría de libros analíticos
- `TableStyleDark1` / `Dark2` — matrices densas donde importa el contraste

## Formato condicional — codificación de estado

Para columnas de estado (OK / KO / WARNING / NOT_EXECUTED), aplica formato condicional DESPUÉS de que la Table esté definida. El formato condicional se capa encima del banding de la Table sin pelearse con él.

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

Para celdas de cobertura con glifos de icono (✓ / ✗ / ◐ / —), extiende la lista de operators para incluir cada glifo.

## Formato condicional — columnas de delta

La varianza vs benchmark / período anterior se lee mejor con una data bar double-ended o una escala de color dividida:

```python
from openpyxl.formatting.rule import ColorScaleRule

def apply_delta_color_scale(ws, ref: str) -> None:
    # Rojo para muy negativo, neutro en cero, verde para muy positivo
    rule = ColorScaleRule(
        start_type="num", start_value=-0.2, start_color=hx(DESIGN["state_danger"]),
        mid_type="num",   mid_value=0,      mid_color=hx(DESIGN["bg_alt"]),
        end_type="num",   end_value=0.2,    end_color=hx(DESIGN["state_ok"]),
    )
    ws.conditional_formatting.add(ref, rule)
```

## Validación de datos — dropdowns

```python
from openpyxl.worksheet.datavalidation import DataValidation

def add_dropdown(ws, ref: str, choices: list[str]) -> None:
    formula = '"{}"'.format(",".join(choices))  # p. ej. '"OK,KO,WARNING"'
    dv = DataValidation(type="list", formula1=formula, allow_blank=True)
    dv.error = "El valor debe ser una de las opciones permitidas"
    dv.errorTitle = "Valor inválido"
    dv.add(ref)
    ws.add_data_validation(dv)
```

Para listas largas de opciones, pon las opciones en una hoja oculta y referencia el rango:

```python
def add_dropdown_from_range(ws, ref: str, range_ref: str) -> None:
    dv = DataValidation(type="list", formula1=range_ref, allow_blank=True)
    dv.add(ref)
    ws.add_data_validation(dv)
```

## Cookbook de formato numérico

Los strings de formato numérico son instrucciones para el renderer de Excel — no mutan el valor numérico subyacente. El mostrado es locale-aware (comas vs puntos los elige el locale del visor).

| Caso de uso | String de formato | Render ejemplo (en-US) |
|---|---|---|
| Entero en miles | `'#,##0'` | `1,234` |
| Entero, negativos con paréntesis | `'#,##0_);(#,##0);"-"'` | `1,234` / `(567)` / `-` |
| Decimal, dos posiciones | `'#,##0.00'` | `1,234.56` |
| Moneda (EUR) | `'[$€-es-ES]#,##0.00'` | `€1,234.56` |
| Moneda genérica (prefijo símbolo) | `'"$"#,##0.00'` | `$1,234.56` |
| Porcentaje, un decimal | `'0.0%'` | `12.3%` |
| Porcentaje, negativos coloreados | `'0.0%;[Red]-0.0%'` | `12.3%` / `-4.5%` (rojo) |
| Fecha ISO | `'yyyy-mm-dd'` | `2026-04-24` |
| Fecha larga | `'d mmm yyyy'` | `24 Apr 2026` |
| Hora 24h | `'hh:mm'` | `14:35` |
| Multiplicador | `'0.0"×"'` | `1.4×` |
| Unidad personalizada | `'#,##0" t"'` | `1,234 t` |

Aplica con `cell.number_format = '#,##0'`.

## Referencia de paleta (XLSX)

El dict `DESIGN` en SKILL.md §4 mapea el tema al styling de celda. Para los tres tonos de libro más comunes sin un tema centralizado, estas semillas son una improvisación razonable:

### sober-audit (default para cobertura de calidad y compliance)

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

### technical-minimal (default para analítico neutro)

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

### editorial-serious (para libros analíticos orientados a narrativa)

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

Son solo fallbacks. Cuando una skill centralizada de theming resuelve un tema, usa sus tokens verbatim.

## Gráficos nativos

Los gráficos nativos de Excel se mantienen editables en Excel. Prefiérelos para libros que son en sí mismos el entregable; para informes donde el gráfico acaba en un PDF / DOCX / PPTX, renderiza un PNG con matplotlib / plotly y embebe como imagen.

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


# Uso
add_bar_chart(
    ws, data_ref="Detail!$C$1:$C$13", categories_ref="Detail!$A$2:$A$13",
    title="Ingresos mensuales", position="F2",
)
```

Line, Pie, Scatter siguen el mismo patrón. Para configuraciones avanzadas (doble eje, series secundarias, etiquetas con insights), ver `openpyxl.chart` — o cae a renderizar PNG y `ws.add_image`.

## Embed de imágenes

```python
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage

def embed_image(ws, image_path: str, anchor: str,
                max_width_px: int = 600) -> None:
    # Dimensiona con pillow primero para que la imagen respete la región objetivo
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

## Rangos con nombre

Los rangos con nombre anclan el libro para usuarios que escriben fórmulas encima. Defínelos en el scope del libro para que cada hoja pueda referenciarlos.

```python
from openpyxl.workbook.defined_name import DefinedName

def add_named_range(wb, name: str, ref: str) -> None:
    wb.defined_names[name] = DefinedName(name=name, attr_text=ref)


# Uso — una región con nombre para la hoja de asunciones
add_named_range(wb, "Assumptions", "Assumptions!$B$2:$B$12")
```

## Freeze panes

```python
ws.freeze_panes = "A2"   # congela solo la primera fila
ws.freeze_panes = "B1"   # congela solo la primera columna
ws.freeze_panes = "B2"   # congela primera fila + primera columna (estándar para Tables)
ws.freeze_panes = None   # descongela
```

Define DESPUÉS de finalizar la Table, no antes — en caso contrario openpyxl puede descolocar la ubicación del pane.

## Hojas protegidas

```python
ws.protection.sheet = True
ws.protection.password = "change-me"  # opcional
ws.protection.enable()

# Permitir al usuario editar celdas específicas pese a la protección
for cell in ws["B2:B12"]:
    for c in cell:
        c.protection = c.protection.copy(locked=False)
```

Las contraseñas en hojas son disuasivas, no seguridad — se bypassean fácilmente. Protege para prevenir ediciones accidentales, no para restringir acceso.

## Validación post-build

### Sanity estructural

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

### Refresco de fórmulas

```bash
python3 <skill-root>/scripts/refresh_formulas.py output.xlsx --json
```

Schema JSON:

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

`ok` es `true` cuando `issues` está vacío. En error (p. ej. LibreOffice ausente, timeout), el JSON tiene `"ok": false` y un campo `"error"`.

### Export visual a PDF

```bash
soffice --headless --convert-to pdf --outdir /tmp/preview libro.xlsx
# abre libro.pdf en /tmp/preview/
```

Abre el PDF y revisa a ojo la hoja de portada, la banda KPI y la matriz de cobertura antes de enviar. Detecta sangrado de celdas combinadas, valores KPI truncados y formato condicional roto sin necesitar Excel.

## Trabajar con un XLSX existente como punto de partida

```python
from openpyxl import load_workbook

wb = load_workbook("templates/company_template.xlsx")

# Inspecciona los nombres definidos que expone el template
for name in wb.defined_names:
    print(f"{name}: {wb.defined_names[name].value}")

# Rellena celdas placeholder — usa nombres definidos cuando estén disponibles
wb["Cover"]["B3"] = "Q4 2026"
wb["Cover"]["B4"] = "2026-04-24"

wb.save("output/branded.xlsx")
```

Al cargar, openpyxl preserva formato condicional, validación de datos, Tables, nombres definidos y la mayoría de definiciones de gráficos. NO preserva macros de `.xlsm` (necesitarías cargar con `keep_vba=True` Y guardar como `.xlsm`).

## Generación batch

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
        # ... aplicar styling estándar / Tables ...
        out = out_dir / f"{slug}-workbook.xlsx"
        wb.save(out)
        produced.append(out)
    return produced
```

Para batches >50 libros, cambia a `Workbook(write_only=True)` para transmitir filas en vez de mantener el libro completo en memoria.

## Limitaciones conocidas (expandido)

- **Macros VBA** — openpyxl preserva binarios de macro en round-trip (`keep_vba=True`) pero no puede crear macros desde cero.
- **Tablas dinámicas** — no se pueden crear. Entrega la Table de origen y deja que el usuario pivote en Excel, o pre-pivota con pandas.
- **Sparklines** — no soportado.
- **`.xlsb` binario** — no soportado para escritura. Escribe siempre `.xlsx`.
- **Comentarios con formato rico** — solo texto plano; bold / italic / colores inline se aplanan.
- **Enlaces externos (libros enlazados)** — openpyxl los preserva en round-trip, pero no puede crearlos nuevos.
- **Objetos OLE (documentos embebidos)** — no soportado.

Cuando una limitación muerda, documéntala en un caveat a nivel de hoja o envía una nota junto al libro.
