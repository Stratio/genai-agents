# pptx-reader — REFERENCE

Patrones avanzados para casos que el SKILL.md principal mantiene a
alto nivel. Carga este fichero cuando el workflow rápido no encaje
con el deck que tienes delante.

## 1. Heurísticas de detección de título

`python-pptx` expone `slide.shapes.title` cuando un slide tiene un
placeholder de título (`ph type="title"` o `ph type="ctrTitle"`).
Pero muchos decks reales usan un text box posicionado como título
en vez de un placeholder real. Cae con elegancia:

```python
from pptx.enum.text import PP_ALIGN

def find_title(slide) -> str | None:
    # Preferido: placeholder de título real
    title_shape = slide.shapes.title
    if title_shape is not None and title_shape.has_text_frame:
        text = title_shape.text_frame.text.strip()
        if text:
            return text

    # Fallback: primer text frame no vacío cerca de la parte superior
    candidates = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text.strip()
        if not text:
            continue
        top = shape.top or 0
        candidates.append((top, text))
    if not candidates:
        return None
    # El más arriba gana
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]
```

Caveat: para slides divisores de sección donde el "título" está
centrado en la página (no arriba), esta heurística devuelve lo
equivocado. Documéntalo en los diagnósticos de extracción.

## 2. Herencia de tema (los estilos fluyen master → layout → slide)

El texto en un placeholder hereda face, tamaño y color de la fuente
desde el layout, que hereda del master. `python-pptx` no resuelve
automáticamente la herencia por ti — `run.font.name` puede devolver
`None` aun cuando el slide renderizado muestra Calibri 18pt, porque
el valor real vive en el layout o el master.

Cuando necesites la fuente efectiva:

```python
from pptx.util import Pt

def effective_font_name(run, default="Calibri"):
    name = run.font.name
    if name:
        return name
    # Sube: placeholder del párrafo → layout → master
    # python-pptx no expone directamente este walker; para la mayoría
    # de workflows de lectura puedes tratar un nombre ausente como
    # "hereda del tema" y parar ahí.
    return default
```

Para extracción del lado lectura esto raramente importa — el texto
es el texto. Si necesitas el estilo renderizado efectivo (p.ej. para
reproducirlo en otro sitio), rasteriza el slide e inspecciona
visualmente en vez de perseguir la cadena de herencia.

## 3. Detección de tipo de chart desde OOXML

`ppt/charts/chart*.xml` envuelve los datos del chart dentro de un
`<c:plotArea>` con un elemento hijo específico del tipo. Detecta
el tipo antes de leer los datos de serie:

```python
from lxml import etree

NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"

CHART_TYPES = {
    "barChart":       "bar/column",
    "lineChart":      "line",
    "pieChart":       "pie",
    "doughnutChart":  "doughnut",
    "areaChart":      "area",
    "scatterChart":   "scatter",
    "bubbleChart":    "bubble",
    "radarChart":     "radar",
    "stockChart":     "stock",
    "surfaceChart":   "surface",
}

def chart_type(chart_xml_path: str) -> str:
    tree = etree.parse(chart_xml_path)
    plot = tree.find(f".//{{{NS_C}}}plotArea")
    if plot is None:
        return "unknown"
    for child in plot:
        tag = etree.QName(child).localname
        if tag in CHART_TYPES:
            return CHART_TYPES[tag]
    return "unknown"
```

Para `barChart`, `<c:barDir val="bar"/>` significa horizontal;
`"col"` significa vertical (column). El mismo elemento XML cubre
ambos.

## 4. Etiquetas del eje de categorías

Además de los valores de serie, las etiquetas de categoría (eje X
en columnas, etiquetas de año en series temporales) viven bajo
`c:cat/c:strRef/c:strCache` o `c:cat/c:numRef/c:numCache`:

```python
from lxml import etree

NS = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}

def chart_categories_and_series(chart_xml_path: str):
    tree = etree.parse(chart_xml_path)
    cats_el = tree.find(".//c:cat", NS)
    categories = []
    if cats_el is not None:
        for pt in cats_el.iterfind(".//c:pt/c:v", NS):
            categories.append((pt.text or "").strip())

    series = []
    for ser in tree.iterfind(".//c:ser", NS):
        name_el = ser.find(".//c:tx//c:v", NS)
        name = (name_el.text or "").strip() if name_el is not None else ""
        values = [float(v.text) for v in ser.iterfind(".//c:val//c:v", NS) if v.text]
        series.append({"name": name, "values": values})

    return categories, series
```

Forma de salida — fácil de convertir en DataFrame de pandas:

```python
import pandas as pd
categories, series = chart_categories_and_series(path)
df = pd.DataFrame({s["name"]: s["values"] for s in series}, index=categories)
```

## 5. Comillas tipográficas, caracteres de anchura cero, guiones suaves

PowerPoint inserta a menudo caracteres que parecen invisibles pero
envenenan el procesamiento posterior del texto:

- Espacio de anchura cero `\u200b`
- No-joiner de anchura cero `\u200c`
- Byte-order mark `\ufeff`
- Guion suave `\u00ad`
- Comillas tipográficas `\u2018`, `\u2019`, `\u201c`, `\u201d`

Normaliza durante la extracción:

```python
ZW_CHARS = "\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad"
SMART_MAP = {
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-",  # en/em dashes
    "\u2026": "...",
}

def normalize_text(s: str) -> str:
    for ch in ZW_CHARS:
        s = s.replace(ch, "")
    for k, v in SMART_MAP.items():
        s = s.replace(k, v)
    return s
```

Aplica la normalización después de extraer, no antes de la llamada
a python-pptx — la librería gestiona su decodificación correctamente.

## 6. Custom XML parts

Algunos decks embeben `customXml/item1.xml` con metadatos fuera de
banda (IDs de workflow, referencias ERP, estado de tracked changes).
Ni `python-pptx` ni `markitdown` los exponen:

```bash
unzip -l deck.pptx | grep '^customXml/'
```

Si están presentes, inspecciona con lxml. Raro en la práctica pero
común en decks generados por empresa (SharePoint, plantillas de
Microsoft Lists).

## 7. Recuperar texto de un deck corrupto

Cuando `python-pptx` lanza `PackageNotFoundError` o `KeyError` sobre
un fichero aparentemente válido, prueba el fallback degradado:

```bash
# LibreOffice re-guarda el fichero, a menudo sanando la corrupción
soffice --headless --convert-to pptx --outdir /tmp/ broken.pptx

# O convierte directamente a texto — pierde estructura pero recupera palabras
soffice --headless --convert-to txt --outdir /tmp/ broken.pptx
cat /tmp/broken.txt
```

Para ficheros muy degradados,
`strings deck.pptx | grep -v '^[[:space:]]*$'` puede aflorar
fragmentos legibles incluso cuando el parseo estructurado falla.
Trata el output como forensia, no como datos.

## 8. Presupuesto de extracción para decks muy grandes

Decks con 100+ slides (cursos de formación, decks de onboarding)
pueden tardar 30+ segundos en parsearse completos con `python-pptx`
y producir 30K–50K tokens de texto.

Estrategias:
- Extrae solo los slides sobre los que el usuario preguntó
  (`--pages 10-20` en modo rápido).
- Extrae títulos + primeros 3 bullets por slide para construir
  una tabla de contenidos barata, luego profundiza solo en los
  slides de interés.
- En decks de formación las notas contienen a menudo la narrativa y
  los slides solo llevan keywords — extrae solo las notas
  (`--no-tables --notes-only`) para reducir el coste a la mitad.

## 9. Cuándo la extracción es suficiente

Puedes parar cuando:
- El output se lee limpio y tiene la estructura que la tarea
  posterior necesita (headings por slide, bullets a la indentación
  correcta, tablas en formato markdown, notas unidas al slide
  correcto).
- Los slides ocultos están contabilizados (incluidos o explícitamente
  omitidos con un conteo en diagnósticos).
- Las tablas y charts que llevan sustancia numérica se capturaron
  como tablas markdown o como DataFrames de pandas reconstruidos.
- Notas del presentador y comentarios se extrajeron cuando la tarea
  es editorial o narrativa.

No necesitas capturar animaciones, transiciones, metadatos de tema
del slide master ni workbooks de Excel embebidos salvo que la tarea
lo pida explícitamente.
