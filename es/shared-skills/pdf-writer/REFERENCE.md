# pdf-writer — Referencia Avanzada

Carga este documento cuando el scaffold de SKILL.md no sea suficiente: diseños
multicolumna, marcadores, vectores embebidos, generación de índices, renderizado
por lotes o tipografía condicional.

## Tabla de contenidos

1. Diseños multicolumna
2. Marcadores y esquema del documento
3. Índices de contenido (generación automática)
4. Incrustación de gráficos vectoriales SVG
5. Inserción de gráficas directamente en PDFs
6. Cabeceras, pies de página y títulos corridos
7. Contador total de páginas con NumberedCanvas
8. Diseños de impresión a doble cara (márgenes en espejo)
9. Patrones de generación por lotes
10. Conformidad PDF/A y salida de archivo
11. Adjuntar archivos dentro de un PDF
12. Fusión preservando marcadores

---

## 1. Diseños multicolumna

Usa `BaseDocTemplate` con múltiples objetos `Frame` por página:

```python
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

page_w, page_h = A4
mx, my = 20 * mm, 25 * mm
gutter = 8 * mm
col_w = (page_w - 2 * mx - gutter) / 2

doc = BaseDocTemplate("/tmp/twocol.pdf", pagesize=A4,
                      leftMargin=mx, rightMargin=mx,
                      topMargin=my, bottomMargin=my)

frame_left  = Frame(mx,               my, col_w, page_h - 2*my, id="left")
frame_right = Frame(mx + col_w + gutter, my, col_w, page_h - 2*my, id="right")

doc.addPageTemplates([
    PageTemplate(id="twocol", frames=[frame_left, frame_right]),
])
```

El contenido fluye primero a `frame_left`; cuando se llena, continúa en
`frame_right` y luego en la página siguiente.

### Mezcla de diseños (portada + cuerpo a dos columnas)

```python
cover_frame = Frame(mx, my, page_w - 2*mx, page_h - 2*my, id="cover")
body_left   = Frame(mx, my, col_w, page_h - 2*my, id="bl")
body_right  = Frame(mx + col_w + gutter, my, col_w, page_h - 2*my, id="br")

doc.addPageTemplates([
    PageTemplate(id="cover",  frames=[cover_frame]),
    PageTemplate(id="twocol", frames=[body_left, body_right]),
])

from reportlab.platypus import NextPageTemplate, PageBreak
story = [
    Paragraph("Title", cover_style),
    NextPageTemplate("twocol"),
    PageBreak(),
    # ... contenido del cuerpo
]
```

## 2. Marcadores y esquema del documento

Los marcadores aparecen en el panel lateral de cualquier visor de PDF.
Imprescindibles en documentos extensos.

```python
from reportlab.platypus import Paragraph
from reportlab.platypus.doctemplate import ActionFlowable

class Bookmark(ActionFlowable):
    def __init__(self, title, key, level=0):
        self.title, self.key, self.level = title, key, level
    def apply(self, doc):
        doc.canv.bookmarkPage(self.key)
        doc.canv.addOutlineEntry(self.title, self.key, level=self.level, closed=False)

story = [
    Bookmark("Chapter 1", "ch1", level=0),
    Paragraph("Chapter 1", h1),
    # ...
    Bookmark("1.1 Background", "ch1_1", level=1),
    Paragraph("1.1 Background", h2),
]
```

## 3. Índices de contenido (generación automática)

reportlab incluye un `TableOfContents` nativo que recopila entradas a medida
que avanza la construcción:

```python
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus import Paragraph

toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle("toc1", fontName="Body-Bold", fontSize=11, leftIndent=0,  leading=16),
    ParagraphStyle("toc2", fontName="Body",      fontSize=10, leftIndent=14, leading=14),
]

def heading(text, level, story):
    style = h1 if level == 0 else h2
    p = Paragraph(text, style)
    story.append(p)
    # Alimentar el TOC
    doc.notify("TOCEntry", (level, text, doc.page))

# La construcción requiere multiBuild para resolver los números de página
doc.multiBuild(story)
```

Nota: `multiBuild` realiza dos pasadas — la primera recopila las entradas,
la segunda las coloca con los números de página correctos.

## 4. Incrustación de gráficos vectoriales SVG

Los SVG escalan sin pérdida a cualquier tamaño. Instala `svglib`:

```python
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

drawing = svg2rlg("/path/to/logo.svg")
# Escalar
scale = 0.6
drawing.width  *= scale
drawing.height *= scale
drawing.scale(scale, scale)

# Insertar en un story de Platypus
from reportlab.platypus import Flowable
class SVGFlowable(Flowable):
    def __init__(self, drawing):
        super().__init__()
        self.drawing = drawing
        self.width  = drawing.width
        self.height = drawing.height
    def draw(self):
        renderPDF.draw(self.drawing, self.canv, 0, 0)

story.append(SVGFlowable(drawing))
```

## 5. Inserción de gráficas directamente en PDFs

reportlab dispone de primitivas de gráficas nativas. Para cualquier cosa
más allá de barras/líneas, usa matplotlib e incrusta la salida como SVG o PNG:

```python
import matplotlib.pyplot as plt
from reportlab.platypus import Image

plt.figure(figsize=(6, 3.5), dpi=200)
plt.plot([1, 2, 3, 4], [10, 14, 12, 18], linewidth=2, color="#B84C2C")
plt.gca().spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("/tmp/chart.png", dpi=200, bbox_inches="tight")
plt.close()

story.append(Image("/tmp/chart.png", width=150*mm, height=80*mm))
```

Para una salida nítida a cualquier nivel de zoom, guarda como SVG e incrusta
mediante `svglib`.

## 6. Cabeceras, pies de página y títulos corridos

Usa el callback `onPage` de `PageTemplate`. La lógica condicional basada en el
número de página va dentro del callback:

```python
def draw_header(canvas, doc):
    canvas.saveState()

    # Primera página: sin cabecera
    if doc.page == 1:
        canvas.restoreState()
        return

    # Páginas impares: título del documento a la izquierda
    # Páginas pares: capítulo a la derecha
    canvas.setFont("Body", 8)
    canvas.setFillColor(MUTED)
    if doc.page % 2 == 1:
        canvas.drawString(MARGIN_X, A4[1] - 12*mm, "Annual Report — 2026")
    else:
        canvas.drawRightString(A4[0] - MARGIN_X, A4[1] - 12*mm,
                               getattr(doc, "current_chapter", ""))

    canvas.restoreState()
```

Actualiza `doc.current_chapter` cada vez que encuentres un encabezado de capítulo.

## 7. Contador total de páginas con NumberedCanvas

`canvas.getPageNumber()` devuelve la página actual, pero reportlab no tiene
forma de conocer el total hasta que todas las páginas se han compuesto.
El patrón canónico es una subclase de `Canvas` que captura el estado de
cada página en `showPage()` y lo repinta en `save()` cuando el total
ya es conocido:

```python
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_page_number(total)
            super().showPage()
        super().save()

    def _draw_page_number(self, total):
        self.setFont("Body", 8)
        self.setFillColor(MUTED)
        self.drawRightString(
            A4[0] - MARGIN_X, 15 * mm,
            f"{self._pageNumber} / {total}",
        )

doc.build(story, canvasmaker=NumberedCanvas)
```

Combínalo con el callback `draw_header` de §6 para tener "chrome"
arriba y paginación `X / Y` abajo — ambos pasan por el mismo canvas
en cada página.

## 8. Diseños de impresión a doble cara (márgenes en espejo)

Para folletos y libros, alterna los márgenes interior/exterior:

```python
INNER, OUTER = 28 * mm, 18 * mm

def frame_for(page_num):
    if page_num % 2 == 1:  # recto (página derecha)
        left, right = INNER, OUTER
    else:                   # verso (página izquierda)
        left, right = OUTER, INNER
    return Frame(left, my,
                 page_w - left - right, page_h - 2*my,
                 id=f"f{page_num}")
```

O bien define dos objetos `PageTemplate`, uno por paridad, y alterna con
`NextPageTemplate`.

## 9. Patrones de generación por lotes

Generación de cientos de facturas, certificados o cartas a partir de un conjunto
de datos:

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import csv

def render_one(record):
    # record es un dict de una fila de CSV
    out_path = Path(f"/tmp/invoices/INV-{record['id']}.pdf")
    # Construir el documento para este registro
    build_invoice(out_path, record)
    return out_path

def build_invoice(out_path, record):
    # tu constructor existente — parametrizado por record
    ...

with open("customers.csv") as f:
    records = list(csv.DictReader(f))

Path("/tmp/invoices").mkdir(exist_ok=True)
with ProcessPoolExecutor(max_workers=8) as ex:
    for path in ex.map(render_one, records):
        print("done:", path)
```

Importante: **registra las fuentes dentro de la función worker**, no en el
proceso principal. Los registros TTF no siempre sobreviven la frontera
fork/spawn.

## 10. Conformidad PDF/A y salida de archivo

PDF/A es el estándar ISO para archivado a largo plazo. Requisitos clave:
las fuentes deben estar embebidas, sin transparencias, sin cifrado, sin
referencias externas y con espacios de color estándar.

reportlab no produce PDF/A directamente. El flujo de trabajo práctico es:

```bash
# Generar con reportlab normalmente y luego convertir
gs -dPDFA=2 -dBATCH -dNOPAUSE -sProcessColorModel=DeviceRGB \
   -sDEVICE=pdfwrite -sPDFACompatibilityPolicy=1 \
   -o output_pdfa.pdf input.pdf
```

O usa una librería dedicada como `pikepdf` con inyección manual de metadatos.

## 11. Adjuntar archivos dentro de un PDF

Útil para entregar un PDF acabado con sus datos en bruto (CSV, Excel)
embebidos:

```python
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ByteStringObject, DictionaryObject, NameObject

src = PdfReader("/tmp/report.pdf")
out = PdfWriter()
for page in src.pages:
    out.add_page(page)

with open("/tmp/raw_data.csv", "rb") as f:
    csv_bytes = f.read()

out.add_attachment("raw_data.csv", csv_bytes)

with open("/tmp/report_with_data.pdf", "wb") as f:
    out.write(f)
```

Los visores mostrarán un icono de clip; los usuarios podrán extraer el adjunto
desde el documento.

## 12. Fusión preservando marcadores

`PdfWriter.append` conserva las entradas del esquema (marcadores) de cada
fuente:

```python
from pypdf import PdfWriter

out = PdfWriter()
out.append("part_1.pdf", outline_item="Part 1 — Background")
out.append("part_2.pdf", outline_item="Part 2 — Analysis")
out.append("part_3.pdf", outline_item="Part 3 — Conclusions")

with open("/tmp/combined.pdf", "wb") as f:
    out.write(f)
```

Los marcadores propios de cada fuente pasan a ser hijos de la entrada de
esquema de nivel superior que especifiques.

## Tabla de referencia rápida de combinaciones tipográficas

Cuando la categoría del documento no aparece en la taxonomía principal de SKILL.md:

| Estilo | Display | Cuerpo | Mono |
|---|---|---|---|
| Serio / editorial | Instrument Serif | Crimson Pro | IBM Plex Mono |
| Corporativo / limpio | Instrument Sans (bold) | Work Sans | JetBrains Mono |
| Cálido / libresco | Young Serif | Lora | DM Mono |
| Técnico / documentación | Outfit (bold) | IBM Plex Serif | IBM Plex Mono |
| Creativo / singular | Boldonse | Crimson Pro | Red Hat Mono |
| Brutalista / cartel | Big Shoulders | Work Sans | JetBrains Mono |
| Ceremonial | Italiana | Libre Baskerville | — |
| Retro / tecnológico | Tektur | Outfit | JetBrains Mono |

Incrusta siempre las fuentes; nunca dependas de la sustitución del visor.
