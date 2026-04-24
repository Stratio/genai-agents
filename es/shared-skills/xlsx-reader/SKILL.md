---
name: xlsx-reader
description: "Inspecciona, analiza y extrae contenido de libros de Excel (.xlsx, .xlsm y .xls legacy) de forma inteligente. Usa esta skill siempre que necesites leer lo que hay dentro de una hoja de cálculo: datos en celdas, tablas, fórmulas, metadatos, datos de gráficos u hojas ocultas. Cubre datasets estrechos, libros multi-hoja con índice, ficheros con fórmulas cuyos valores cacheados pueden estar obsoletos, referencias entre hojas, .xls binarios legacy y .xlsm con macros que puedes ignorar para extraer datos. Ejecuta siempre un diagnóstico rápido antes de extraer para elegir la estrategia correcta."
argument-hint: "[ruta/al/fichero.xlsx]"
---

# Skill: XLSX Reader

Un enfoque disciplinado para extraer contenido útil de hojas de cálculo. Cada fichero necesita tácticas distintas: una hoja tipo CSV plana se comporta de forma totalmente diferente a un libro cuya portada es un dashboard de KPIs alimentado por fórmulas a través de diez hojas de detalle, y ambos se comportan diferente a un `.xls` legacy guardado desde Office 2003. Diagnostica primero, extrae después.

## 1. Dos modos: rápido y profundo

Esta skill soporta dos formas de trabajar:

**Modo rápido — `scripts/quick_extract.py`**
Extracción one-shot que devuelve salida estructurada (Markdown, CSV o JSON). Úsalo cuando:
- El libro es "normal" (datos tabulares en una o pocas hojas)
- Quieres los valores sin pensar qué librería usar
- Estás procesando muchos ficheros en batch
- Vas a pasar la salida directamente a otro agente o LLM

**Modo profundo — el workflow a continuación**
Diagnóstico y extracción paso a paso. Úsalo cuando:
- El libro tiene fórmulas que necesitas leer como fórmulas (no solo sus valores cacheados)
- Necesitas extraer imágenes embebidas o datos de gráficos
- El modo rápido falló, devolvió celdas vacías donde había valores, o se saltó una hoja
- El fichero es un `.xls` legacy (necesita conversión previa)
- El libro tiene hojas ocultas, celdas combinadas o formato condicional relevante para la interpretación

Por defecto, usa el modo rápido. Cambia al profundo cuando el rápido no sea suficiente.

### Uso del modo rápido

```bash
# Extraer todo (primera hoja, Markdown)
python3 <skill-root>/scripts/quick_extract.py libro.xlsx

# Todas las hojas, un CSV por hoja a stdout
python3 <skill-root>/scripts/quick_extract.py libro.xlsx --sheet all --format csv

# Hoja específica, salida JSON (filas como lista de diccionarios)
python3 <skill-root>/scripts/quick_extract.py libro.xlsx --sheet Summary --format json

# Limitar el número de filas para hojas grandes
python3 <skill-root>/scripts/quick_extract.py libro.xlsx --max-rows 200

# Leer de stdin
cat libro.xlsx | python3 <skill-root>/scripts/quick_extract.py -
```

El script:
- Devuelve el formato elegido en stdout (tablas Markdown por defecto)
- Devuelve diagnósticos en stderr (qué motor corrió, qué hojas, warnings)
- Sale con código 0 en éxito, 1 en fallo
- Autodetecta los motores disponibles y hace fallback por una cadena
- Nunca contamina stdout — la salida se puede pipe a otra herramienta sin problema

La cadena de motores prueba, en orden: **openpyxl (read-only) → pandas (backend openpyxl) → walk de XML en crudo sobre zipfile**. Gana el primero que produzca una hoja no vacía.

## 2. Regla de oro para el modo profundo: diagnostica antes de extraer

Nunca abras un libro a ciegas con `openpyxl`. Un fichero cuyos valores cacheados están obsoletos devolverá `None` donde el usuario espera números. Un libro con diez hojas ocultas puede tener los datos reales fuera de las "visibles". Un `.xls` con extensión `.xlsx` seguirá fallando en `zipfile.ZipFile`. Un diagnóstico de dos segundos ahorra horas depurando la hoja equivocada.

Ejecuta este bloque de inspección primero:

```bash
# ¿Es realmente .xlsx / .xlsm (ZIP) o .xls legacy (OLE compound)?
file target.xlsx

# Para .xlsx / .xlsm, lista el contenido del ZIP. ¿Qué partes contiene?
unzip -l target.xlsx

# ¿Cuántas hojas y sus nombres (incluyendo ocultas)?
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('target.xlsx', read_only=True, data_only=False)
for name in wb.sheetnames:
    st = wb[name].sheet_state  # 'visible' | 'hidden' | 'veryHidden'
    print(f'{st:11s}  {name}')
"

# Metadatos básicos (título, autor, creación / modificación)
unzip -p target.xlsx docProps/core.xml | head -20

# ¿Hay nombres definidos (rangos con nombre) que apunten a regiones nombradas?
unzip -p target.xlsx xl/workbook.xml | grep -oE '<definedName[^>]*>' | head
```

Qué te dice cada salida:

- **`file`** — si reporta `Microsoft Excel 2007+` o `Zip archive data`, es un `.xlsx`/`.xlsm` (ZIP). Si reporta `Composite Document File V2 Document`, es un `.xls` binario legacy y tienes que convertir primero.
- **`unzip -l`** — el inventario de partes es tu mapa. Partes clave: `xl/workbook.xml` (índice de hojas + nombres definidos), `xl/worksheets/sheet*.xml` (una por hoja), `xl/sharedStrings.xml` (tabla de strings deduplicada), `xl/media/` (imágenes embebidas), `xl/styles.xml`, `xl/charts/` (XML de gráficos si existen), `docProps/core.xml` (metadatos).
- **Listado de hojas con `sheet_state`** — `visible` significa que la hoja aparece en la pestaña de Excel; `hidden` que el usuario la ocultó con el comando Ocultar; `veryHidden` que se ocultó programáticamente (vía VBA) y un usuario normal no puede re-mostrarla. Cualquiera de ellas puede contener datos importantes.
- **`docProps/core.xml`** — autor, título, timestamps de creación/modificación. Útil cuando el usuario pregunta "quién produjo esto" o "cuándo se tocó por última vez".
- **`definedName`** — rangos con nombre como `Summary!Revenue` o `Assumptions` suelen ser los anclajes que el dueño del libro espera que leas; revísalos antes de recorrer celdas al azar.

## 3. Elige una estrategia según el tipo de libro

Clasifica mentalmente, luego aplica el workflow correspondiente.

### Datasets tabulares (una hoja, datos rectangulares, cabecera opcional)

Herramienta principal: `pandas` con backend `openpyxl`. Maneja detección de cabecera, coerción de tipos, parsing de fechas y selección de columnas en una sola llamada.

```python
import pandas as pd

# Por defecto: primera hoja, primera fila como cabecera
df = pd.read_excel("dataset.xlsx")

# Leer cada hoja como dict de DataFrames
sheets = pd.read_excel("dataset.xlsx", sheet_name=None)

# Leer solo las columnas que necesitas, forzar dtypes
df = pd.read_excel(
    "dataset.xlsx",
    usecols=["order_id", "customer_id", "amount"],
    dtype={"order_id": str, "customer_id": str},
    parse_dates=["ordered_at"],
)
```

Para un primer vistazo sin pandas:

```python
from openpyxl import load_workbook

wb = load_workbook("dataset.xlsx", read_only=True, data_only=True)
ws = wb.active
for row in ws.iter_rows(values_only=True, max_row=5):
    print(row)
```

### Libros multi-hoja con hoja de portada / índice

Síntoma: la primera hoja nombra otras hojas (p. ej. una hoja "Contents" o "Summary" con enlaces o referencias). El detalle está distribuido en las demás.

Lee primero la portada para entender la semántica de cada hoja de detalle, luego lee solo las que necesitas:

```python
from openpyxl import load_workbook

wb = load_workbook("multi.xlsx", read_only=True, data_only=True)
cover = wb["Summary"]  # o wb.active
tabs_of_interest = [row[0].value for row in cover.iter_rows(min_row=2) if row[0].value]

for tab in tabs_of_interest:
    if tab in wb.sheetnames:
        ws = wb[tab]
        # procesar ws
```

### Libros cuyos valores los calculan fórmulas

Dos modos viven dentro del mismo fichero:

- `data_only=False` (por defecto) — lees la **fórmula** de cada celda (p. ej. `"=SUM(B2:B10)"`).
- `data_only=True` — lees el **último valor calculado** que Excel cacheó al guardar el libro.

Si `data_only=True` devuelve `None` para celdas que el usuario espera con valores, los valores cacheados están obsoletos (nadie abrió el libro en Excel después del último cambio de fórmula). Dos opciones:

1. Pedir al usuario que abra el libro en Excel/LibreOffice, deje que recalcule, guarde y reenvíe.
2. Usar el `scripts/refresh_formulas.py` de la skill compañera `xlsx-writer` para forzar un pase de recálculo headless con LibreOffice — actualiza los valores cacheados in place.

**Nunca guardes un libro que abriste con `data_only=True`**: openpyxl escribe los valores cacheados como constantes literales, destruyendo todas las fórmulas. Extrae, cierra, sigue.

### Libros con referencias entre hojas

Síntoma: fórmulas como `=Summary!B5` o `=Assumptions!Rate * Detail!C10`.

Inspecciona fórmulas con `data_only=False` y los valores resueltos con `data_only=True` en dos pases:

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

### Libros `.xlsm` (con macros habilitadas)

Síntoma: extensión `.xlsm`, o `unzip -l` muestra `xl/vbaProject.bin`.

Para extraer datos, trátalos como un `.xlsx` — `openpyxl` y `pandas` leen las celdas e ignoran los bytes del macro. NO intentes ejecutar los macros. Si los datos del libro los calcula un macro en runtime (raro fuera de herramientas de contabilidad), aplica la regla de los valores cacheados: recalcula vía LibreOffice o pide al usuario que guarde tras abrir.

### Ficheros `.xls` binarios legacy

Síntoma: `file` reporta `Composite Document File V2 Document`, o `zipfile.ZipFile` lanza `BadZipFile`.

Tres caminos, en orden de robustez:

1. Convertir con LibreOffice headless (recomendado — mismo mecanismo que usan docx-reader / pptx-reader):

   ```bash
   soffice --headless --convert-to xlsx --outdir /tmp/xlsx_in target.xls
   # /tmp/xlsx_in/target.xlsx es ahora un .xlsx moderno
   ```

2. Usar `xlrd<2` (solo lectura, limitado). No instales `xlrd>=2` — dejó de soportar `.xls`.
3. Si no hay ninguna opción disponible, devolver un diagnóstico avisando de que el fichero es legacy y no se puede procesar sin LibreOffice ni una versión antigua de `xlrd`.

### `.xlsb` (binario 2007+)

No soportado por `openpyxl`. Convierte con LibreOffice headless (`--convert-to xlsx`) primero, luego trátalo como cualquier `.xlsx`.

### CSV / TSV enviados como "fichero de Excel"

Los usuarios a menudo adjuntan un `.csv` o `.tsv` y lo describen como "un fichero de Excel". Detéctalo vía la firma del fichero (sin bytes mágicos de ZIP, texto plano) y cae a `pandas.read_csv` con valores sensatos (`sep=None, engine="python"` auto-detecta el delimitador). Si el separador sigue fallando, olfatéalo:

```python
import csv
with open("data.csv", newline="") as f:
    sample = f.read(8192)
dialect = csv.Sniffer().sniff(sample)
```

### Libros mixtos

Los ficheros reales mezclan de todo: portada estilizada, dos datasets rectangulares en hojas 2-3, una hoja de parámetros en la 4, una hoja con fórmulas que referencian 2-3 en la 5, y tal vez un apéndice con imágenes. No intentes extraer en una sola pasada:

1. Diagnostica primero (§2). Identifica el rol de cada hoja.
2. Saca datos tabulares con `pandas` por hoja objetivo.
3. Saca fórmulas con `openpyxl(data_only=False)` donde las fórmulas en sí son el artefacto de interés.
4. Extrae imágenes de `xl/media/` con `zipfile` solo si el usuario lo pidió.
5. Expón los metadatos por separado.
6. Une los hallazgos al final en un informe estructurado.

## 4. Consciencia de tokens al pasar contenido a un LLM

Una hoja de cálculo con 50.000 filas serializada como tabla Markdown son aproximadamente 1,5 millones de tokens — casi siempre demasiado. Trabaja inteligentemente:

- Lee solo las columnas y filas que necesitas. `usecols=` y `nrows=` de `pandas` ayudan.
- Resume antes de emitir: head, tail, tipos de columna, conteo de nulls, conteo de únicos — lo suficiente para que un agente decida qué preguntar después.
- Si el libro tiene una hoja de KPIs / resumen, emite **esa** y oculta las hojas de detalle salvo que las pidan.
- Para un vistazo rápido, `--max-rows` en `scripts/quick_extract.py` limita las filas emitidas por hoja.

Coste aproximado de tokens (salida Markdown):
- Hoja tabular pequeña (<100 filas, 5 columnas): ~1.500 tokens
- Hoja media (1.000 filas, 10 columnas): ~25.000 tokens
- Hoja grande (>10.000 filas): NO deberías emitirlo en crudo — agrega primero

## 5. Metadatos

`docProps/core.xml` y `docProps/app.xml` traen los metadatos interesantes:

```python
import zipfile
from lxml import etree

NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}

with zipfile.ZipFile("libro.xlsx") as z:
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

Los datos a nivel de libro (nombres definidos, hoja activa, visibilidad) viven en `xl/workbook.xml` — inspecciona vía `wb.defined_names` y `wb.sheetnames` de `openpyxl` o parsea el XML directamente.

## 6. Limpieza de la salida extraída

La extracción en crudo normalmente necesita un pase pequeño:
- Descartar filas finales con todo-`None` (artefacto común de `openpyxl` sobre-leyendo celdas vacías)
- Convertir booleanos y `datetime` a strings si downstream espera JSON
- Colapsar espacios en blanco dentro de los valores de celda (las celdas multilínea arrastran `\n`)
- Preservar la representación de fórmula cuando el llamador pidió fórmulas — NO conviertas silenciosamente una fórmula como `=A1+B1` en su valor cacheado

## 7. Cuándo cargar `REFERENCE.md`

`REFERENCE.md` cubre patrones avanzados: selección dirigida de columnas con `usecols` y `dtype`, manejo de celdas combinadas al reconstruir DataFrames, iteración de reglas de formato condicional y validación de datos, lectura de datos de gráficos embebidos vía `openpyxl.chart`, inventario de nombres definidos y áreas de impresión, inspección de cachés de tablas dinámicas, recetas de procesamiento en batch, y el mapeo completo entre `.xlsx`, `.xlsm`, `.xlsb` y `.xls`.

## 8. Resumen de dependencias

Python: `openpyxl`, `pandas`, `lxml` (transitiva de openpyxl). Opcional: `xlrd<2` para `.xls` legacy en solo lectura cuando LibreOffice no esté disponible.

Sistema: `libreoffice` / `libreoffice-calc` para conversión de `.xls` legacy y `.xlsb`. Ya forma parte de la imagen del sandbox.

Sin LibreOffice y sin `xlrd<2`, la skill no puede abrir `.xls` ni `.xlsb` legacy. Los `.xlsx` y `.xlsm` modernos funcionan solo con `openpyxl`.

---

Crear, editar, fusionar, dividir, buscar-y-reemplazar, convertir `.xls` legacy, autoría de libros analíticos, producción de matrices de cobertura con formato condicional, y cualquier otra cosa que termine guardando un fichero de hoja de cálculo viven en la skill compañera `xlsx-writer`.
