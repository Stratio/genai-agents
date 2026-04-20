---
name: pdf-writer
description: "Crea, manipula y produce archivos PDF con un diseño cuidado. Usa esta skill cuando el usuario quiera generar un nuevo PDF (informes, facturas, certificados, boletines, folletos, recibos, cartas) o transformar PDFs existentes (combinar, dividir, rotar, añadir marcas de agua, cifrar, aplanar, añadir páginas). Esta skill se toma el diseño en serio — cada PDF que produce tiene tipografía, color y maquetación intencionales, no los valores por defecto genéricos. Para rellenar campos de formulario interactivos en PDFs existentes, carga FORMS.md."
argument-hint: "[tipo de documento o descripción]"
---

# Skill: Escritor de PDF

Esta skill produce PDFs que parecen diseñados, no generados. La mayoría
de los PDFs automatizados son visualmente inertes: cuerpo en Helvetica,
negro sobre blanco, márgenes de 2,5 cm en todos los lados, y un título
azul si tienes suerte. Ese es el punto de partida que esta skill rechaza
activamente.

Antes de escribir una sola línea de código, define una dirección de
diseño. El código está al servicio del diseño, no al contrario.

## 1. Flujo de trabajo centrado en el diseño

Toda tarea de generación de PDF, independientemente de su tamaño, sigue
cinco pasos:

1. **Clasifica el documento** — ¿a qué categoría pertenece? (Ver la
   taxonomía más abajo.) Esto condiciona todo lo demás.
2. **Elige un tono visual** — editorial, técnico-minimalista,
   corporativo-formal, revista-cálida, brutalista, lúdico,
   lujo-refinado. Elige uno y ejecútalo con decisión. Un PDF
   indeciso "con un poco de todo" es el peor resultado posible.
3. **Selecciona una combinación tipográfica** — una fuente de display
   para títulos y encabezados, una fuente de texto para el cuerpo.
   Dos tipografías casi siempre son suficientes; tres es el máximo.
4. **Define una paleta** — un color de acento dominante, un neutro
   oscuro para el texto (raramente negro puro), un neutro claro para
   fondos o líneas divisoras. Usa colores con saturación real, no
   pasteles desvaídos por defecto.
5. **Establece la cuadrícula** — márgenes, número de columnas,
   interlineado. Los márgenes generosos transmiten confianza; los
   márgenes estrechos dan aspecto de documento Word.

Solo entonces abre reportlab.

### Taxonomía de documentos y puntos de partida

| Categoría | Tono habitual | Tamaño de página | Combinación sugerida |
|---|---|---|---|
| Informe analítico | Editorial-serio | A4 / Letter | Crimson Pro (cuerpo) + Instrument Sans (display) |
| Estado financiero | Técnico-minimalista | A4 / Letter | IBM Plex Serif (cuerpo) + IBM Plex Mono (datos) |
| Factura / recibo | Limpio-utilitario | A4 / Letter | Instrument Sans (todo) + JetBrains Mono (cifras) |
| Boletín | Revista-cálida | Letter | Lora (cuerpo) + Big Shoulders (display) |
| Contrato / documento legal | Comedido-preciso | A4 / Letter | Libre Baskerville (cuerpo) + Instrument Sans (pies de foto) |
| Folleto / fanzine | Editorial-lúdico | A5 | Crimson Pro (cuerpo) + Italiana o Erica One (display) |

Estos son puntos de partida, no mandatos. Rómpelos cuando el encargo
lo exija. Lo importante es **no recurrir nunca a la Helvetica
integrada de reportlab**.

### Cuándo esta skill no es la adecuada

Esta skill produce documentos tipográficos multi-página donde la prosa,
las tablas o los datos estructurados llevan el significado. Algunos
encargos se parecen pero pertenecen a otra herramienta:

- **Artefactos de una sola página en los que domina la composición** —
  pósters, certificados, one-pagers de marketing, infografías. En esas
  piezas, aproximadamente el setenta por ciento o más de la superficie
  es composición visual más que prosa o datos. La tipografía se
  convierte en elemento visual. Otra skill se ocupa de ese medio;
  consulta `skills-guides/visual-craftsmanship.md` para el criterio de
  selección.
- **Interfaces web interactivas** — componentes, páginas, dashboards
  que viven en un navegador. El PDF es estático; esos encargos piden
  HTML/CSS.

Para un informe que necesita una portada diseñada, produce la portada
con la skill dedicada a artefactos visuales, ensambla aquí el cuerpo
multi-página, y mergea ambos con `pypdf` como paso final. Mantén los
márgenes de la última página de la portada consistentes con los de la
primera página del cuerpo para una transición limpia.

## 2. Registro de fuentes personalizadas (hazlo primero)

reportlab incluye fuentes Type 1 integradas (Helvetica, Times, Courier).
Producen PDFs feos. Esta skill incluye un conjunto seleccionado de
fuentes OFL en el directorio `fonts/` — regístralas al inicio de cada
script.

```python
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS_DIR = Path(__file__).parent / "fonts"

def register_fonts():
    pdfmetrics.registerFont(TTFont("CrimsonPro",      FONTS_DIR / "CrimsonPro-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("CrimsonPro-Bold", FONTS_DIR / "CrimsonPro-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("CrimsonPro-It",   FONTS_DIR / "CrimsonPro-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("InstrumentSans",  FONTS_DIR / "InstrumentSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("InstrumentSans-Bold", FONTS_DIR / "InstrumentSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("JetBrainsMono",   FONTS_DIR / "JetBrainsMono-Regular.ttf"))
    # ... registra las familias que vayas a utilizar realmente

    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily(
        "CrimsonPro",
        normal="CrimsonPro",
        bold="CrimsonPro-Bold",
        italic="CrimsonPro-It",
    )

register_fonts()
```

Registra solo lo que vayas a usar — cada registro incrusta la fuente
en el PDF de salida y añade aproximadamente 80–150 KB al tamaño del
archivo.

## 3. Una plantilla de partida adecuada

En lugar de recurrir a los valores por defecto de reportlab, usa esto
como base y adáptala:

```python
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, PageBreak,
)

# === FONTS ===
FONTS = Path(__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Body",        FONTS / "CrimsonPro-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold",   FONTS / "CrimsonPro-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Display",     FONTS / "InstrumentSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono",        FONTS / "JetBrainsMono-Regular.ttf"))

# === DESIGN TOKENS ===
INK    = HexColor("#1A1A1A")   # near-black for body copy
ACCENT = HexColor("#B84C2C")   # terracotta accent
MUTED  = HexColor("#6E6E6E")   # captions, metadata
RULE   = HexColor("#E5E0D8")   # hairlines, subtle dividers
PAPER  = HexColor("#FAF8F4")   # warm off-white background (optional)

MARGIN_X = 22 * mm
MARGIN_Y = 25 * mm

# === STYLES ===
body = ParagraphStyle(
    "body",
    fontName="Body",
    fontSize=10.5,
    leading=15,             # ~1.42x line-height
    textColor=INK,
    spaceAfter=6,
)
h1 = ParagraphStyle(
    "h1",
    fontName="Display",
    fontSize=28,
    leading=32,
    textColor=INK,
    spaceAfter=12,
    spaceBefore=0,
)
h2 = ParagraphStyle(
    "h2",
    fontName="Display",
    fontSize=15,
    leading=20,
    textColor=ACCENT,
    spaceAfter=6,
    spaceBefore=18,
)
caption = ParagraphStyle(
    "caption",
    fontName="Body",
    fontSize=8.5,
    leading=12,
    textColor=MUTED,
)

# === PAGE TEMPLATE ===
def draw_chrome(canvas, doc):
    """Se ejecuta en cada página — úsalo para cabecera, pie, número de página y líneas."""
    canvas.saveState()
    w, h = A4
    # Top hairline
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(MARGIN_X, h - MARGIN_Y + 10 * mm,
                w - MARGIN_X, h - MARGIN_Y + 10 * mm)
    # Footer: page number + document identifier
    canvas.setFont("Body", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 15 * mm, "Annual Report — 2026")
    canvas.drawRightString(w - MARGIN_X, 15 * mm, f"{doc.page:02d}")
    canvas.restoreState()

def build(output_path, story):
    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_Y,  bottomMargin=MARGIN_Y,
        title="Annual Report 2026",
        author="Acme Analytics",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        id="main", showBoundary=0,
    )
    doc.addPageTemplates([PageTemplate(id="default", frames=[frame],
                                        onPage=draw_chrome)])
    doc.build(story)

# === CONTENT ===
story = [
    Paragraph("The State of the Market", h1),
    Paragraph("Quarterly outlook — April 2026", caption),
    Spacer(1, 14),
    Paragraph(
        "Markets closed the quarter with restrained optimism, tempered "
        "by persistent uncertainty around rate policy. Capital flows "
        "favored defensive sectors throughout the period.",
        body,
    ),
    Paragraph("Sector performance", h2),
    Paragraph(
        "Energy and healthcare led on a relative basis, while "
        "consumer discretionary lagged. Tech recovered ground lost in "
        "the previous quarter but remains volatile.",
        body,
    ),
]

build("/tmp/annual_report.pdf", story)
```

Esta plantilla ya te proporciona:
- Tipografía personalizada (sin Helvetica)
- Paleta de colores intencional con un acento y neutros apagados
- Márgenes generosos que respiran
- Chrome que dibuja una línea y el número de página en cada hoja
- Metadatos (título, autor) para propiedades PDF correctas

Adapta la plantilla; no la fuerces.

## 4. Tablas que no parecen capturas de pantalla de Excel

Las tablas por defecto de reportlab son horribles. Una tabla con diseño
necesita:

- Sin líneas verticales (las tablas modernas usan solo líneas horizontales)
- Relleno de fila ajustado, no el espaciado cavernoso por defecto
- Números alineados a la derecha, cadenas alineadas a la izquierda
- Una fila de cabecera sombreada sutilmente o en negrita
- Fuente monoespaciada para cifras (JetBrainsMono, IBMPlexMono, DMMono)

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

data = [
    ["Region",      "Revenue",    "Change"],
    ["North",       "€ 2,840,112",   "+ 12.3 %"],
    ["South",       "€ 1,905,660",    "+ 4.1 %"],
    ["East",        "€ 1,220,438",    "– 2.7 %"],
    ["West",        "€ 3,410,002",   "+ 18.5 %"],
]

tbl = Table(data, colWidths=[55*mm, 55*mm, 35*mm])
tbl.setStyle(TableStyle([
    # Header
    ("FONTNAME",   (0, 0), (-1, 0), "Display"),
    ("FONTSIZE",   (0, 0), (-1, 0), 9),
    ("TEXTCOLOR",  (0, 0), (-1, 0), MUTED),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ("LINEBELOW",  (0, 0), (-1, 0), 0.8, INK),

    # Body
    ("FONTNAME",   (0, 1), (0, -1), "Body"),
    ("FONTNAME",   (1, 1), (-1, -1), "Mono"),
    ("FONTSIZE",   (0, 1), (-1, -1), 10),
    ("TEXTCOLOR",  (0, 1), (-1, -1), INK),
    ("ALIGN",      (1, 1), (-1, -1), "RIGHT"),
    ("TOPPADDING", (0, 1), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
    ("LINEBELOW",  (0, 1), (-1, -1), 0.3, RULE),
]))
```

## 5. Problemas frecuentes con reportlab

### Subíndices y superíndices Unicode

Nunca pegues caracteres como ₂ o ⁵ directamente en la salida de
reportlab. Las fuentes Type 1 integradas no contienen esos glifos y
obtendrás rectángulos negros en el PDF. Usa las etiquetas `<sub>` y
`<super>` dentro de los objetos Paragraph:

```python
Paragraph("Water is H<sub>2</sub>O, and E = mc<super>2</super>", body)
```

Si usas una TTF personalizada que sí incluye esos glifos (la mayoría
de las fuentes modernas lo hacen), el Unicode directo funciona — pero
es más seguro usar las etiquetas.

### Emojis y escrituras no latinas

Las fuentes integradas solo cubren el alfabeto latino. Para cualquier
texto no ASCII, registra una fuente que contenga realmente los glifos
que necesitas. Para emojis, usa una fuente como Noto Color Emoji —
pero ten en cuenta que el soporte de emojis en color de reportlab es
limitado.

### Imágenes pixeladas

Si pasas una imagen rasterizada pequeña a `Image()` sin especificar
el tamaño, reportlab la dibuja con sus dimensiones nativas en píxeles.
Para una salida de impresión de alta calidad, ajusta tus imágenes
fuente a 300 DPI para el tamaño de impresión objetivo. Las alternativas
vectoriales (SVG mediante `svglib`) escalan sin pérdida de calidad.

### Tablas muy largas

`Table` no se divide entre páginas por defecto. Usa `LongTable` para
tablas que puedan superar una página:

```python
from reportlab.platypus import LongTable
tbl = LongTable(data, colWidths=[...], repeatRows=1)
```

`repeatRows=1` mantiene la fila de cabecera en la parte superior de
cada página.

## 6. Combinar, dividir y rotar PDFs

Para operaciones estructurales, `pypdf` es la herramienta adecuada.
No uses reportlab para esto — es para crear contenido, no para
reorganizarlo.

### Combinar

```python
from pypdf import PdfWriter, PdfReader

out = PdfWriter()
for source in ["cover.pdf", "body.pdf", "appendix.pdf"]:
    src = PdfReader(source)
    for page in src.pages:
        out.add_page(page)

with open("/tmp/merged.pdf", "wb") as f:
    out.write(f)
```

### Dividir (un archivo por página)

```python
from pypdf import PdfReader, PdfWriter

src = PdfReader("/tmp/merged.pdf")
for i, page in enumerate(src.pages, 1):
    out = PdfWriter()
    out.add_page(page)
    with open(f"/tmp/page_{i:03d}.pdf", "wb") as f:
        out.write(f)
```

### Extraer un rango de páginas

```python
src = PdfReader("/tmp/merged.pdf")
out = PdfWriter()
for page in src.pages[4:9]:  # páginas 5–9 (índice 0)
    out.add_page(page)
with open("/tmp/section.pdf", "wb") as f:
    out.write(f)
```

### Rotar

```python
src = PdfReader("/tmp/scanned.pdf")
out = PdfWriter()
for page in src.pages:
    page.rotate(90)  # 90, 180 o 270
    out.add_page(page)
with open("/tmp/rotated.pdf", "wb") as f:
    out.write(f)
```

### Equivalentes en línea de comandos con `qpdf`

Cuando estés en una shell y no necesites Python:

```bash
# Combinar
qpdf --empty --pages cover.pdf body.pdf appendix.pdf -- merged.pdf

# Extraer páginas 5–9
qpdf input.pdf --pages . 5-9 -- section.pdf

# Rotar la página 1 90°
qpdf input.pdf --rotate=+90:1 rotated.pdf
```

## 7. Marcas de agua

Una marca de agua es un PDF superpuesto sobre otro PDF, página a página.
El enfoque más sencillo: crea la marca de agua con reportlab y luego
combínala.

```python
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from pypdf import PdfReader, PdfWriter

# 1. Generar la marca de agua
c = rl_canvas.Canvas("/tmp/watermark.pdf", pagesize=A4)
c.saveState()
c.translate(A4[0] / 2, A4[1] / 2)
c.rotate(35)
c.setFont("Display", 84)
c.setFillColor(Color(0.85, 0.15, 0.15, alpha=0.15))  # rojo translúcido
c.drawCentredString(0, 0, "CONFIDENTIAL")
c.restoreState()
c.save()

# 2. Aplicar sobre el documento fuente
watermark = PdfReader("/tmp/watermark.pdf").pages[0]
src = PdfReader("/tmp/report.pdf")
out = PdfWriter()
for page in src.pages:
    page.merge_page(watermark)
    out.add_page(page)

with open("/tmp/report_watermarked.pdf", "wb") as f:
    out.write(f)
```

Para una marca de agua visible pero menos intrusiva, reduce el valor
de alpha a 0,06–0,10.

## 8. Cifrado y permisos

```python
from pypdf import PdfReader, PdfWriter

src = PdfReader("/tmp/report.pdf")
out = PdfWriter()
for page in src.pages:
    out.add_page(page)

out.encrypt(
    user_password="readonly",    # requerida para abrir
    owner_password="fullaccess", # requerida para imprimir / copiar / modificar
    use_128bit=True,
)

with open("/tmp/report_encrypted.pdf", "wb") as f:
    out.write(f)
```

Nota: El cifrado PDF no es una barrera de seguridad real. Cualquiera
puede eliminarlo con la herramienta adecuada. Es una barrera de cortesía,
no una caja fuerte.

## 9. Convertir PDFs escaneados a PDFs con texto buscable

Usa OCRmyPDF cuando esté disponible — preserva el escaneo original y
añade una capa de texto invisible:

```bash
ocrmypdf --language spa+eng scanned.pdf scanned_searchable.pdf
```

El equivalente en Python hecho a mano — rasterizar + OCR + reconstruir —
es posible pero engorroso. OCRmyPDF gestiona todos los casos límite.

## 10. Cuándo cargar archivos adicionales

- **`FORMS.md`** — rellenar campos AcroForm interactivos en PDFs existentes
- **`REFERENCE.md`** — patrones avanzados de reportlab, incrustación de SVG,
  generación de índices, marcadores, renderizado por lotes
- **`fonts/`** — los propios archivos TTF, con los avisos de licencia OFL

## 11. Instalación

Esta skill requiere reportlab y algunas bibliotecas de apoyo. Si ya
instalaste `pdf-reader`, la mayor parte ya está en su lugar.

### Instalación de una sola vez (Debian / Ubuntu)

```bash
sudo apt update && sudo apt install -y poppler-utils qpdf pdftk ghostscript
pip install reportlab pypdf pdfplumber svglib pillow
```

### Instalación de una sola vez (macOS)

```bash
brew install poppler qpdf pdftk-java ghostscript
pip install reportlab pypdf pdfplumber svglib pillow
```

### Qué proporciona cada dependencia

| Paquete | Propósito |
|---|---|
| `reportlab` | Motor principal para generar PDFs desde cero |
| `pypdf` | Combinar, dividir, rotar, marcas de agua, cifrar, rellenar formularios |
| `pdfplumber` | Leer tablas de PDFs fuente cuando se reutiliza su contenido |
| `svglib` | Incrustar gráficos vectoriales SVG en PDFs de reportlab |
| `pillow` | Gestión de imágenes para los flowables `Image()` |
| `qpdf` | Operaciones estructurales en línea de comandos, más rápido que pypdf para archivos grandes |
| `pdftk` | `FORMS.md`: aplanado robusto de formularios rellenos, inspección de campos |
| `ghostscript` | Conversión a PDF/A, aplanado de último recurso |
| `poppler-utils` | `pdfinfo`, `pdftotext` para inspeccionar PDFs fuente |

### Fuentes incluidas

El directorio `fonts/` incluye archivos TTF bajo la licencia SIL Open
Font License. No se necesita ninguna instalación adicional de fuentes —
la skill las registra directamente desde ese directorio. Consulta
`fonts/README.md` para ver la lista completa y las notas de licencia.



La extracción de texto, la lectura de tablas, la rasterización de páginas
para inspección, el OCR de escaneos existentes, la extracción de adjuntos
y el diagnóstico de fuentes se encuentran en la skill complementaria
`pdf-reader`.
