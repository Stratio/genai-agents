---
name: xlsx-writer
description: "Crea libros de Excel (.xlsx) con estructura intencional, y realiza operaciones estructurales sobre libros existentes. Usa esta skill siempre que necesites producir una hoja de cálculo pulida (libro analítico con portada/KPI, pivot, export tabular, matriz de cobertura, catálogo, modelo cuantitativo) o manipular ficheros XLSX existentes (merge, split, buscar-y-reemplazar, conversión de .xls legacy, refresco de valores cacheados de fórmulas). Esta skill toma la salida tabular en serio — todo libro que produce tiene cabeceras con formato intencional, tipografía, formato condicional y Tables nativas, nunca el default genérico de cuadrícula blanca sobre blanco. NO usar para: PDF tipográfico multi-página (pdf-writer), pieza visual de una sola página (canvas-craft), web interactivo (web-craft), documento Word con mucho texto (docx-writer). Para patrones avanzados (validación de datos, gráficos, rangos con nombre, imágenes), carga REFERENCE.md. Para merge / split / buscar-y-reemplazar / conversión .xls legacy, carga STRUCTURAL_OPS.md. Cuando se invoca desde quality-report, sigue el contrato multi-hoja en quality-report-layout.md §6.6."
argument-hint: "[tipo de libro o descripción]"
---

# Skill: XLSX Writer

Excel es la superficie donde se espera que aterricen los datos tabulares. Un libro generado sin atención estructural parece un dump CSV en crudo — cuadrícula blanca sobre blanco, cabeceras sin estilo, sin freeze panes, sin codificación de estado, columnas dimensionadas por defecto. Ese es el baseline que esta skill rechaza activamente.

Antes de escribir una sola línea de código, comprométete con una estructura. El código sirve a la estructura, no al revés.

## 1. Workflow design-first

Toda tarea de generación XLSX, independientemente del tamaño, sigue cinco decisiones:

1. **Clasifica el libro** — ¿qué tipo de entregable es? (Ver taxonomía debajo.) Esto gobierna el número de hojas, su orden, y qué primitivas (KPI cards, Table objects, formato condicional, gráficos) se usan downstream.
2. **Elige un tono visual** — sober-audit, technical-minimal, editorial-serious, corporate-formal. Los artefactos tabulares son sobrios por defecto: saturación real solo en cabeceras e indicadores de estado, todo lo demás monocromo. Elige uno y ejecútalo con convicción.
3. **Selecciona un pairing tipográfico** — una cara de body para valores de celda, una de display para cabeceras y valores de KPI. Calibri / Aptos / Arial / Cambria / Georgia degradan elegantemente entre máquinas (XLSX usa las fuentes instaladas del lector salvo que embebas — y embeber no es flujo estándar para libros).
4. **Define una paleta** — un `primary` dominante para fill de cabecera y borde de KPI cards (usado para 5-15% de la superficie), un `ink` profundo para texto de cuerpo, un `bg_alt` pálido para filas alternadas en banda, más colores de estado (`state_ok` / `state_warn` / `state_danger`) usados con moderación en formato condicional. Los valores concretos vienen del tema (§3), no de esta skill.
5. **Marca el ritmo** — anchos de columna (nunca el default 10), alturas de fila para bandas KPI, freeze primera fila + primera columna donde importe, define el área de impresión para que el usuario que imprima obtenga una página landscape razonable.

Solo entonces abres `openpyxl`.

### Taxonomía de libros y puntos de partida

| Categoría | Forma típica | Primitivas |
|---|---|---|
| Libro analítico con portada/KPI | Portada con KPIs + parámetros + hojas de detalle + apéndice | Bandas KPI con celdas combinadas, Table objects, formato condicional, freeze panes |
| Pivot / cross-tab | Filas × columnas con matriz de una métrica | Una Table densa con bandas alternadas; totales de columna y fila en negrita |
| Matriz de cobertura (calidad) | Filas = entidades, columnas = dimensiones, celdas = iconos de estado | Table nativa, formato condicional por estado, freeze primera fila + primera columna |
| Export tabular (anotado) | Una o dos hojas, cabecera + filas + nota al pie | Table nativa con autofilter, cabecera congelada, formato numérico por tipo de columna |
| Catálogo / diccionario de datos | Una hoja por tipo de entidad (término, columna, dominio) | Tables nativas, columnas estrechas para códigos, anchas para prosa |
| Modelo cuantitativo | Portada / asunciones / detalle / salida, fórmulas por todas partes | Celdas de asunción con fill coded, fórmulas en negro, colores de estado para varianza |

Estos son puntos de partida, no mandatos. Rómpelos cuando el brief lo pida. La clave es **nunca caer al default de openpyxl de celdas Calibri 11pt en blanco sin estructura**.

### Cuándo esta skill no es la adecuada

- **Documento tipográfico multi-página** (contrato, whitepaper, política con mucho texto) — `docx-writer` o `pdf-writer` preservan tipografía y flujo de lectura; XLSX es una superficie tabular, no una superficie de prosa.
- **Pieza visual de una sola página** (póster, portada, infografía, one-pager) — `canvas-craft`.
- **Frontend interactivo** — `web-craft`.
- **Informe de cobertura de calidad en formato narrativo** — la skill `quality-report` compone la estructura canónica de seis secciones y delega al writer skill por formato. Cuando se invoca *desde* quality-report para la opción XLSX, esta skill sigue el contrato multi-hoja en `quality-report-layout.md` §6.6 (ver §9 abajo).

## 2. Configuración de página

XLSX imprime diferente a DOCX: salvo que definas área de impresión y orientación de página, Excel partirá tu hoja en docenas de páginas a su discreción. Para cualquier libro que se vaya a imprimir o exportar a PDF:

```python
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.properties import PageSetupProperties

ws.print_area = "A1:H50"
ws.page_setup.orientation = "landscape"  # o "portrait"
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_margins = PageMargins(left=0.5, right=0.5, top=0.6, bottom=0.6)
ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0  # 0 = tantas páginas verticales como necesarias
```

Landscape es el default para matrices de cobertura, pivot tables y cualquier tabla rectangular más ancha de ~8 columnas. Portrait es el default para exports tabulares estrechos, catálogos y hojas de portada/KPI.

## 3. Aplicación de tema

Los tokens de diseño (colores, tipografía, tamaños) no viven en esta skill — vienen del tema elegido para el entregable.

- Si hay disponible una skill centralizada de theming (estilo brand-kit), ejecuta su workflow ANTES de autorizar; devuelve un set de tokens que mapea sobre el dict `DESIGN` debajo.
- Si no, improvisa tokens coherentes con el entregable siguiendo los roles de paleta tonal en `skills-guides/visual-craftsmanship.md`.

El dict `DESIGN` en el scaffold usa placeholders (`<hex>`, `<font-family>`, `<pt>`) — rellénalos desde el tema, no hardcodees.

Específico para XLSX:
- **Fill de cabecera** usa `primary` (saturado), texto de cabecera en blanco o un neutro muy pálido.
- **Bandas de cuerpo** alternan entre `bg` (transparente / blanco) y `bg_alt` (neutro pálido) en filas pares.
- **Fills de estado** usan `state_ok` / `state_warn` / `state_danger` / `muted` en formato condicional — nunca como fills directos de celda, para que el usuario pueda filtrar / ordenar sin que los fills peleen con el propio banding del Table.
- **Valores de KPI** usan la fuente `display` del tema a ~2× el tamaño de body; labels y subtítulos de KPI usan `body` al tamaño body.
- **Fallback tipográfico**: XLSX lee las fuentes del sistema del usuario. Empareja tus fuentes de tema con safe defaults (`Inter, Calibri, Arial, sans-serif`) vía `Font(name=...)` para que el libro degrade elegantemente en máquinas sin la cara exótica.

## 4. Un template de partida adecuado

En vez de ir a `Workbook()` y esperar lo mejor, usa este scaffold y adáptalo:

```python
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from pathlib import Path

# 1. Comprométete con tokens de diseño al inicio — nunca cambian durante el libro.
#    Rellénalos del tema elegido (ver §3). No hardcodees valores aquí;
#    el esqueleto es estable, los valores son branding.
DESIGN = {
    # Paleta (strings hex — 6 chars, sin # inicial)
    "primary":       "<hex>",   # fills de cabecera, bordes de KPI cards
    "primary_ink":   "FFFFFF",  # texto sobre fill primary
    "ink":           "<hex>",   # texto de cuerpo
    "muted":         "<hex>",   # captions, subtítulos
    "rule":          "<hex>",   # bordes
    "bg":            "FFFFFF",  # superficie base
    "bg_alt":        "<hex>",   # filas alternadas en banda
    "state_ok":      "<hex>",
    "state_warn":    "<hex>",
    "state_danger":  "<hex>",
    "state_muted":   "<hex>",
    # Tipografía (safe defaults del sistema primero, cara del tema como fallback)
    "display":  "<font-family>",  # valores KPI, títulos principales
    "body":     "<font-family>",  # valores de celda, labels
    "mono":     "Consolas",       # excerpts de código, SQL
    # Tamaños (pt)
    "size_title":    18,
    "size_kpi":      22,
    "size_kpi_lbl":  10,
    "size_header":   11,
    "size_body":     10,
    "size_small":    9,
}


def hx(h: str) -> str:
    """Devuelve un hex de 6 caracteres en mayúsculas, quitando '#' inicial si lo hay."""
    return h.lstrip("#").upper()


# 2. Construye el libro y elimina la hoja por defecto vacía si queremos
#    nombres de hoja explícitos desde el inicio.
wb = Workbook()
ws_cover = wb.active
ws_cover.title = "Cover"


# 3. Helpers pequeños para composiciones que repetirás.
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
    """Banda de 4 celdas KPI en la fila dada. Cada dict tiene
    {label, value, subtitle}. Cada KPI ocupa 3 columnas con una cabecera
    combinada arriba (primary) y un cuerpo combinado debajo (fuente display).
    """
    col = 1
    thin = Side(border_style="thin", color=hx(DESIGN["rule"]))
    bord = Border(left=thin, right=thin, top=thin, bottom=thin)
    for kpi in kpis:
        # Fila de label (fill primary)
        ws.merge_cells(start_row=row, start_column=col,
                       end_row=row, end_column=col + 2)
        label_cell = ws.cell(row=row, column=col, value=kpi["label"])
        label_cell.fill = PatternFill("solid", fgColor=hx(DESIGN["primary"]))
        label_cell.font = Font(name=DESIGN["body"],
                               size=DESIGN["size_kpi_lbl"],
                               color=hx(DESIGN["primary_ink"]), bold=True)
        label_cell.alignment = Alignment(horizontal="center", vertical="center")
        # Fila de valor
        ws.merge_cells(start_row=row + 1, start_column=col,
                       end_row=row + 2, end_column=col + 2)
        value_cell = ws.cell(row=row + 1, column=col, value=kpi["value"])
        value_cell.font = Font(name=DESIGN["display"],
                               size=DESIGN["size_kpi"], bold=True,
                               color=hx(DESIGN["ink"]))
        value_cell.alignment = Alignment(horizontal="center", vertical="center")
        # Fila de subtítulo
        ws.merge_cells(start_row=row + 3, start_column=col,
                       end_row=row + 3, end_column=col + 2)
        sub_cell = ws.cell(row=row + 3, column=col, value=kpi.get("subtitle", ""))
        sub_cell.font = Font(name=DESIGN["body"], size=DESIGN["size_small"],
                             color=hx(DESIGN["muted"]))
        sub_cell.alignment = Alignment(horizontal="center", vertical="center")
        # Bordes alrededor de la card
        for r in range(row, row + 4):
            for c in range(col, col + 3):
                ws.cell(row=r, column=c).border = bord
        col += 3
    ws.row_dimensions[row + 1].height = 28
    ws.row_dimensions[row + 2].height = 28


def add_native_table(ws, ref: str, name: str, style: str = "TableStyleMedium2") -> None:
    """Adjunta una Table de openpyxl al rango dado. Name debe ser único
    en el libro y Excel-safe (letras, dígitos, underscore).
    """
    tbl = Table(displayName=name, ref=ref)
    tbl.tableStyleInfo = TableStyleInfo(
        name=style, showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(tbl)


# 4. Compón la hoja de portada.
ws_cover["A1"] = "Título del informe"
ws_cover["A1"].font = Font(name=DESIGN["display"], size=DESIGN["size_title"],
                           bold=True, color=hx(DESIGN["primary"]))
ws_cover.merge_cells("A1:L1")

ws_cover["A3"] = "Alcance"
ws_cover["B3"] = "<dominio o alcance>"
ws_cover["A4"] = "Generado"
ws_cover["B4"] = "<YYYY-MM-DD>"

add_kpi_band(
    ws_cover, row=6,
    kpis=[
        {"label": "KPI uno",    "value": "42",   "subtitle": "contexto"},
        {"label": "KPI dos",    "value": "87%",  "subtitle": "contexto"},
        {"label": "KPI tres",   "value": "3",    "subtitle": "contexto"},
        {"label": "KPI cuatro", "value": "—",    "subtitle": "contexto"},
    ],
)

set_col_widths(ws_cover, {chr(c): 14 for c in range(ord("A"), ord("L") + 1)})


# 5. Construye hoja de detalle con una Table nativa.
ws_detail = wb.create_sheet("Detail")
headers = ["ID", "Name", "Value", "Status"]
ws_detail.append(headers)
for row in sample_rows:  # iterable de listas que ya tienes
    ws_detail.append(row)
set_col_widths(ws_detail, {"A": 14, "B": 28, "C": 14, "D": 14})
add_native_table(
    ws_detail,
    ref=f"A1:{get_column_letter(len(headers))}{ws_detail.max_row}",
    name="DetailTable",
)
ws_detail.freeze_panes = "A2"


out_path = Path("output/libro.xlsx")
out_path.parent.mkdir(parents=True, exist_ok=True)
wb.save(out_path)
```

Cuatro reglas que el scaffold impone:

- **Nunca te apoyes en los anchos de columna por defecto.** El default de openpyxl (~8.43) trunca casi cualquier dato real. Define anchos explícitos por columna.
- **Usa siempre Table objects nativos para datos rectangulares.** Dan al usuario autofilter + sort de serie y preservan el banding al insertar.
- **Calcula colores, fuentes y tamaños desde tokens de diseño**, nunca literales en línea. Si cambia el color de acento, solo cambia `DESIGN`.
- **Compón con primitivas + helpers pequeños**. Tira de un helper local en cuanto repites un patrón tres veces.

## 5. Fuentes

XLSX usa las fuentes instaladas del lector. Safe defaults cross-platform en Windows / macOS / Linux: **Calibri, Aptos, Arial, Cambria, Georgia, Courier New, Consolas**.

El embedding de fuentes existe en la especificación XLSX pero el soporte es desigual entre visores (Excel 2019+ solo en Windows, ignorado por LibreOffice, Excel macOS, Excel Online y Google Sheets). No embebas para libros; apóyate en fallbacks seguros y, si el brief exige una cara exacta, renderiza la región de portada como PNG y embébela como imagen.

Recomendación: elige fuentes de tema que degraden elegantemente. `Inter, Calibri, Arial, sans-serif` es el body default universal; `DM Sans, Calibri, Arial, sans-serif` o `Fraunces, Cambria, Georgia, serif` dan carácter sin romperle a nadie.

## 6. Guía de paleta

Un libro diseñado tiene como máximo tres familias de color en cualquier hoja: primary (un acento, saturado, usado para 5-15% de superficie — fills de cabecera, bordes de KPI cards), neutral (texto de celda y filas de banda) y colores de estado (ok / warn / danger) usados con moderación en formato condicional.

Nunca mezcles dos azules distintos, dos rojos distintos o dos saturaciones de acento distintas en el mismo libro. Comprométete con valores concretos al inicio y aplícalos uniformemente en todas las hojas.

De dónde vienen esos valores concretos depende de lo que el agente tenga:

- Si hay una skill centralizada de theming disponible, el tema elegido suministra un set de tokens completo y coherente (primary, ink, muted, rule, bg_alt, accent, colores de estado, tipografía, tamaños). Úsalo verbatim.
- Si no, improvisa desde los roles de paleta tonal en `skills-guides/visual-craftsmanship.md`. Para defaults específicos de XLSX (sober-audit, technical-minimal) ver `REFERENCE.md` §Palette reference.

## 7. Bloques de construcción de libros

Estos son los bloques que merece la pena dominar. Los snippets de cada uno viven en `REFERENCE.md`; aquí el menú.

- **Banda de KPI** — 4 cards con celdas combinadas en una fila horizontal: label arriba, valor en fuente display, subtítulo abajo. Borde y fill primary en la fila del label.
- **Table nativa** (`openpyxl.worksheet.table.Table`) — preferida para cualquier dato rectangular con cabecera. Habilita autofilter, sort, banded styling, y preserva al insertar filas.
- **Freeze panes** — `ws.freeze_panes = "B2"` para congelar la primera fila y primera columna. Estándar para toda Table con >20 filas o >6 columnas.
- **Anchos de columna** — `ws.column_dimensions["A"].width = 28`. Siempre explícito; nunca por defecto.
- **Alturas de fila** — `ws.row_dimensions[row].height = 28` para bandas KPI y cabeceras de sección.
- **Strings de formato numérico** — `cell.number_format = '#,##0'` / `'0.0%'` / `'yyyy-mm-dd'`. Ejemplos en `REFERENCE.md`; no mandatos.
- **Formato condicional** — fills por cell-rule para codificar estado. Nunca uses fills directos para codificar estado (rompe el banding); el formato condicional se capa limpiamente sobre las bandas propias del Table.
- **Validación de datos** — dropdowns y restricciones de rango vía `openpyxl.worksheet.datavalidation`. Snippet en `REFERENCE.md`.
- **Gráficos** — gráficos nativos de Excel vía `openpyxl.chart` (Bar / Line / Pie / Scatter). Limitados comparados con Excel nativo pero editables en Excel. Úsalos solo cuando el libro ES el entregable final; si no, renderiza PNG con matplotlib y embebe.
- **Imágenes** — `openpyxl.drawing.image.Image` para embed PNG / JPG. Dimensiona con pillow primero para que la imagen quepa en el rango de celda objetivo.

## 8. Composición de libro analítico

Cuando esta skill se invoca desde la generación de entregables de Phase 4 de `/analyze`, produce un libro analítico con esta estructura estable:

1. **Hoja Cover / KPI** (siempre primera) — título, alcance, período, fecha de generación, una banda KPI de 3-4 métricas clave (del executive summary del informe), una frase lead de un párrafo apuntando al hallazgo más importante.
2. **Hoja Parameters** (cuando el análisis usó filtros, rangos de fecha o selecciones de segmento) — hoja estrecha de dos columnas documentando cada filtro aplicado. Permite al lector reproducir el slice en Excel.
3. **Hojas Detail, una por dimensión principal** — cada una contiene una Table de los datos subyacentes para esa dimensión (región × métrica, mes × métrica, segmento × métrica, etc.). Aplica formato condicional en las columnas de delta (vs período anterior, vs benchmark, vs target).
4. **Hoja Validación de hipótesis** (opcional, profundidad Standard/Deep) — para cada hipótesis: enunciado, criterio, valor real, resultado (CONFIRMED / REFUTED / PARTIAL), puntero de evidencia.
5. **Apéndice — datos brutos** (opcional, cuando el dataset cabe). Table nativa con autofilter, cabecera congelada.

Los filenames siguen la convención de `/analyze`: `<slug>-workbook.xlsx`. Tokens de marca aplicados vía la cascada de branding del agente host.

## 9. Composición de libro de cobertura de calidad

Cuando esta skill se invoca desde el orquestador `quality-report` para el formato XLSX, sigue el contrato multi-hoja en `shared-skills/quality-report/quality-report-layout.md §6.6`. Resumen:

1. **Cover** — título, dominio, alcance, fecha de generación, banda KPI de 4 celdas (Coverage %, Rules OK %, Critical gaps, Rules created this session).
2. **Coverage** — Table nativa de tablas × dimensiones con iconos de estado (✓ / ✗ / ◐ / —) y formato condicional tintado por estado. Freeze primera fila + primera columna.
3. **Rules** — Table nativa agrupada por tabla: nombre de regla, dimensión, estado, % pass, descripción.
4. **Gaps** — Table priorizada: prioridad, tabla, columna, dimensión, descripción, recomendación. La celda de prioridad tintada por código de prioridad.
5. **Rules created in this session** (condicional).
6. **Recommendations** — bullets numerados, hoja de prosa.

La guía de layout es el contrato; síguela verbatim para estabilidad de auditoría entre reruns. Sin fórmulas de Excel (todos los valores son datos displayed). Sin gráficos nativos (la matriz de cobertura es en sí misma el heatmap).

Filename: `<slug>-quality-report.xlsx`.

## 10. Fórmulas

Las fórmulas de Excel son ciudadano de primera cuando el libro es un **modelo cuantitativo** (presupuesto, forecast, análisis de escenarios). Para **informes analíticos** y **matrices de cobertura**, prefiere valores mostrados — el libro es un entregable, no un entorno de cómputo.

Cuando sí escribes fórmulas:

- Las celdas de asunción tienen su propia hoja (o una región claramente demarcada). Su fill es distintivo (`state_warn` o un `bg_alt` muy pálido) para que el lector sepa qué celdas puede cambiar.
- Usa **referencias de celda**, no valores hardcodeados, para que un cambio en una asunción propague: `=B5*(1+$B$6)`, no `=B5*1.05`.
- Documenta cualquier valor hardcodeado en un comentario de celda, citando la fuente.
- Tras escribir fórmulas con `openpyxl`, **los valores cacheados no se actualizan** — el libro abre con blancos en visores que no recalculan (LibreOffice lo hace; Google Sheets lo hace; un proceso Python leyendo con `data_only=True` verá `None`).

Para refrescar valores cacheados post-build:

```bash
python3 <skill-root>/scripts/refresh_formulas.py output/model.xlsx --json
```

El script corre un pase de recálculo con LibreOffice headless, guarda el libro in place, y emite JSON resumiendo conteo de fórmulas, hojas tocadas, y cualquier error detectado (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`). Flags: `--timeout <segundos>`, `--json`, `--quiet`.

## 11. Validación post-build

Tras construir, verifica siempre el resultado. Tres comprobaciones:

- **Sanity estructural** — reabre el XLSX guardado con `openpyxl` y cuenta hojas, filas por hoja, Table objects, rangos combinados. Detecta corrupción de fichero o datos silenciosamente perdidos antes de entregar.
- **Refresco de fórmulas** (solo si hay fórmulas) — corre `scripts/refresh_formulas.py` como arriba. La salida JSON te deja decidir si enviar o regenerar.
- **Check visual** (recomendado para hojas de portada y bandas KPI) — convierte a PDF vía LibreOffice headless (`soffice --headless --convert-to pdf`) y abre el PDF. Más barato que abrir Excel; detecta sangrado de celdas combinadas, valores KPI truncados, formato condicional roto.

Snippets completos en `REFERENCE.md` §Post-build validation.

## 12. Templates aportados por el usuario

Cuando un usuario aporta un template corporativo con su logo, carta, estilos y paleta de colores — ignora el scaffold de §4 y carga su fichero:

```python
from openpyxl import load_workbook

wb = load_workbook("templates/company_template.xlsx")
ws = wb["Cover"]
ws["B3"] = "Q4 2026"
# reusa los nombres definidos y estilos del template; no los redefinas
wb.save("output/branded.xlsx")
```

Al usar un template de cliente:

- **No redefinas los fills del tema** si el template los tiene.
- **Reusa los rangos con nombre del template** (a menudo anclan los campos título, alcance, fecha de la portada).
- **Aun así valida** — un template puede estar desactualizado o parcialmente roto; solo lo cogerás renderizando e inspeccionando.

## 13. Operaciones estructurales

Para manipular libros existentes (merge hoja-a-hoja preservando estilos, split por hoja, buscar-y-reemplazar en celdas con texto, convertir `.xls` binario legacy a `.xlsx`, extraer una hoja a CSV), ver `STRUCTURAL_OPS.md`. Son snippets copia-pega; ejecútalos desde un script pequeño, no intentes importarlos como módulo.

## 14. Pitfalls

Reality-checked contra `openpyxl` 3.1 y la especificación ECMA-376:

- **Celdas combinadas y sort / filter.** Una Table con celdas combinadas dentro rechazará ordenar. Nunca combines dentro de una región de datos — solo en las filas de portada / KPI / título.
- **`data_only=True` + save destruye fórmulas.** Nunca abras un libro con `data_only=True` y luego `wb.save(...)` — escribirás los valores cacheados como constantes literales y perderás todas las fórmulas. Para flujos de solo lectura usa `xlsx-reader`; para flujos de escritura mantén `data_only=False`.
- **Los strings de formato numérico dependen del locale al mostrar.** `'#,##0'` se renderiza como `1,234` en en-US y `1.234` en es-ES. Ese comportamiento es correcto — deja que Excel haga el trabajo de locale; no pre-formatees números como strings en tu código.
- **openpyxl no evalúa fórmulas.** Los valores cacheados faltan tras build. Usa `scripts/refresh_formulas.py` o pide al usuario que abra + guarde en Excel / LibreOffice.
- **Las alturas de fila se resetean en recálculo de Excel** si no las fijaste con `row_dimensions[n].height = ...`. Fija alturas explícitas para bandas KPI y filas de título.
- **Los nombres de Table deben ser únicos por libro** y Excel-safe (letras, dígitos, underscore, empezar por letra). `"coverage-matrix"` es inválido; usa `"CoverageMatrix"` o `"coverage_matrix"`.
- **No uses fill pattern `solid` con foreground / background idénticos.** Algunos visores lo colapsan a negro, produciendo el bug "¿por qué mi celda está negra?". Define siempre `fgColor` explícitamente.
- **El formato condicional sobre un rango de Table se evalúa por celda.** Las fórmulas dentro de la regla usan la celda evaluada, no el rango — escribe reglas relativas a la primera celda del rango.

## 15. Limitaciones conocidas

`openpyxl` cubre ~85% de la autoría XLSX del mundo real limpiamente. El 15% restante o necesita manipulación OOXML cruda o no se soporta:

- **Macros VBA (creación de `.xlsm`)** — openpyxl puede preservar una capa de macros si estaba en un fichero de entrada, pero no puede crear macros nuevos. Crear libros `.xlsm` con macros personalizados no se soporta.
- **Tablas dinámicas (creación)** — openpyxl no crea tablas dinámicas programáticamente. Crea los datos de origen y deja que el usuario pivote en Excel, o renderiza el resultado pivotado con pandas y entrega una Table plana.
- **Sparklines** — no soportado. Usa gráficos nativos o renderiza PNGs.
- **Formato binario `.xlsb`** — no soportado. Escribe `.xlsx` y, si el usuario necesita `.xlsb`, puede Guardar Como desde Excel.
- **Comentarios de celda con formato rico** — los comentarios básicos funcionan; el texto rico dentro de ellos se aplana.

Documenta la limitación en un caveat a nivel de hoja cuando afecte al entregable.

## 16. Cheat sheet de referencia rápida

| Tarea | Abordaje |
|---|---|
| Crear libro | `Workbook()` luego define títulos de hoja y anchos de columna |
| Añadir hoja | `wb.create_sheet("Name")` |
| Ancho de columna | `ws.column_dimensions["A"].width = 28` |
| Alto de fila | `ws.row_dimensions[1].height = 28` |
| Table nativa | ver scaffold §4 y REFERENCE.md §Native Table |
| Banda KPI | ver scaffold §4 helper `add_kpi_band` |
| Formato condicional | ver REFERENCE.md §Conditional formatting |
| Formato numérico | `cell.number_format = '#,##0'` / `'0.0%'` / `'yyyy-mm-dd'` |
| Freeze panes | `ws.freeze_panes = "B2"` |
| Área de impresión | `ws.print_area = "A1:H50"` + page setup |
| Gráfico nativo | ver REFERENCE.md §Native charts |
| Embed imagen | `openpyxl.drawing.image.Image(path)` + `ws.add_image` |
| Refrescar fórmulas | `python3 scripts/refresh_formulas.py fichero.xlsx --json` |
| Merge / split / buscar-y-reemplazar | ver `STRUCTURAL_OPS.md` |
| Convertir `.xls` legacy | `soffice --headless --convert-to xlsx old.xls` |
| Template aportado por usuario | carga `.xlsx` directamente; reusa sus estilos y nombres definidos |

## 17. Cuándo cargar REFERENCE.md

- Snippets completos para cada bloque de construcción (banda KPI, Table nativa, formato condicional, validación de datos, gráficos nativos, embed de imágenes, rangos con nombre, hojas protegidas)
- Referencia de paleta para XLSX (defaults sober-audit, technical-minimal, editorial-serious)
- Cookbook de formato numérico (moneda con unidades, porcentajes, negativos parenteteados, fecha/hora, múltiples)
- Validación post-build (sanity estructural, refresco de fórmulas, export visual a PDF)
- Trabajar con un XLSX existente como punto de partida
- Generación batch (N libros desde un dataset)

---

Leer celdas, tablas, fórmulas, metadatos y estructura de libros desde ficheros existentes — más extracción diagnose-first, modo rápido vía `quick_extract.py`, ingest de `.xls` legacy — todo vive en la skill compañera `xlsx-reader`.
