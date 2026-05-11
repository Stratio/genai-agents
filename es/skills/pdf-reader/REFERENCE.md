# pdf-reader — Referencia avanzada

Carga este archivo solo cuando el SKILL.md base no sea suficiente: tablas
complejas, archivos corruptos, pipelines por lotes o bibliotecas alternativas.

## Tabla de contenidos

1. Extracción avanzada de tablas con `pdfplumber`
2. Bibliotecas alternativas y cuándo usarlas
3. PDFs corruptos y no conformes
4. Patrones de procesamiento por lotes
5. PDFs firmados y certificados
6. Soporte de idiomas para OCR
7. Consejos de rendimiento

---

## 1. Extracción avanzada de tablas con `pdfplumber`

El método `page.extract_tables()` predeterminado funciona cuando las tablas
tienen líneas de separación visibles. Cuando falla, generalmente hay que
ayudar a `pdfplumber` a entender dónde están los límites de la tabla.

### Parámetro de estrategia

```python
import pdfplumber

with pdfplumber.open("messy-report.pdf") as pdf:
    page = pdf.pages[0]
    tables = page.extract_tables(table_settings={
        "vertical_strategy": "text",     # infer columns from text alignment
        "horizontal_strategy": "lines",  # use visible horizontal rules for rows
        "snap_tolerance": 3,
        "intersection_tolerance": 3,
    })
```

Estrategias disponibles:
- `"lines"` — usa las líneas detectadas (mejor para tablas clásicas con bordes)
- `"lines_strict"` — igual pero solo líneas que forman rectángulos
- `"text"` — infiere los límites a partir de la alineación del texto (mejor para tablas sin bordes)
- `"explicit"` — defines tú mismo las coordenadas x/y

### Límites de columna explícitos

Cuando `pdfplumber` sigue fusionando dos columnas o dividiendo una, define
los límites tú mismo:

```python
page = pdf.pages[0]
tables = page.extract_tables(table_settings={
    "vertical_strategy": "explicit",
    "explicit_vertical_lines": [50, 180, 310, 440, 560],  # page x-coordinates
    "horizontal_strategy": "text",
})
```

Encuentra las coordenadas x correctas visualizando:

```python
im = page.to_image(resolution=150)
im.debug_tablefinder().save("/tmp/debug.png")
```

Abre la imagen e inspecciona dónde cree `pdfplumber` que están las líneas.

### Tablas que abarcan varias páginas

Cóselas manualmente:

```python
def extract_spanning_table(pdf, start_page, end_page, settings=None):
    first = pdf.pages[start_page].extract_tables(settings)[0]
    headers = first[0]
    rows = first[1:]
    for p in range(start_page + 1, end_page + 1):
        continuation = pdf.pages[p].extract_tables(settings)
        if continuation:
            rows.extend(continuation[0])  # skip duplicated header if present
    return headers, rows
```

---

## 2. Bibliotecas alternativas y cuándo usarlas

### `pypdfium2` — bindings de PDFium de Google

Renderizado rápido y, en general, el mejor motor para calidad de rasterización.
Útil cuando `pdftoppm` no está disponible o cuando se prefiere permanecer en Python.

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("target.pdf")
page = pdf[0]
bitmap = page.render(scale=2.0)  # 2x = ~144 DPI; 4x = ~288 DPI
pil_image = bitmap.to_pil()
pil_image.save("/tmp/page-01.png")
pdf.close()
```

### `pypdfium2` — uso avanzado (texto + posiciones)

Para obtener coordenadas a nivel de palabra sin necesitar PyMuPDF, usa la
API de página de texto de `pypdfium2`:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("target.pdf")
page = pdf[0]
textpage = page.get_textpage()

# Iterate over every text rectangle (logical chunk) with its bounding box
for i in range(textpage.count_rects()):
    left, bottom, right, top = textpage.get_rect(i)
    text = textpage.get_text_bounded(left, bottom, right, top)
    print(f"({left:.0f},{bottom:.0f})-({right:.0f},{top:.0f}) {text!r}")

# Search for a specific string and get positions for each match
searcher = textpage.search("Total", match_case=False)
match = searcher.get_next()
while match is not None:
    char_index, char_count = match
    # Each matched character has its own bounding box
    left, bottom, _, _    = textpage.get_charbox(char_index)
    _, _, right, top      = textpage.get_charbox(char_index + char_count - 1)
    print(f"'Total' found at ({left:.0f},{bottom:.0f},{right:.0f},{top:.0f})")
    match = searcher.get_next()
searcher.close()

textpage.close()
pdf.close()
```

Conceptos clave:
- **Rects** son fragmentos lógicos de texto (normalmente palabras o líneas).
- **Charbox** proporciona las cajas delimitadoras por carácter.
- **Search** devuelve tuplas `(char_index, char_count)` — conviértelas a
  cajas delimitadoras mediante `get_charbox` sobre el primer y el último carácter.

Esto cubre la mayoría de los casos reales de "qué texto está en qué posición
de la página" sin necesitar bibliotecas con licencia AGPL.

### `pdfminer.six` — la más antigua, sigue siendo útil para trabajo a nivel de carácter

```python
from pdfminer.high_level import extract_text
text = extract_text("target.pdf")
```

Más lenta que `pdfplumber`, pero gestiona mejor algunos casos extremos
(codificaciones inusuales). Para detalles de maquetación a nivel de carácter:

```python
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

for page_layout in extract_pages("target.pdf"):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                for char in text_line:
                    if isinstance(char, LTChar):
                        print(char.get_text(), char.bbox, char.fontname, char.size)
```

### Matriz de decisión

| Necesidad | Mejor opción |
|---|---|
| Texto + tablas simples | pdfplumber |
| Renderizado rápido | pypdfium2 |
| Texto con posiciones de palabra/carácter | pypdfium2 (API de página de texto) o pdfplumber |
| Máxima tolerancia de codificación | pdfminer.six |
| Información de fuente por carácter | pdfminer.six |
| Solo volcado de texto | pdftotext CLI |

Todas las opciones anteriores tienen licencias permisivas. Si en algún momento
necesitas iteración de anotaciones o funciones multimedia que solo ofrece
PyMuPDF, verifica que tu proyecto pueda aceptar AGPL v3 antes de instalarlo.

---

## 3. PDFs corruptos y no conformes

Síntomas: "EOF marker not found", "xref table not found", "invalid
object"; los parsers fallan o se bloquean.

### Reparación con `qpdf`

`qpdf` puede reconstruir la tabla de referencias cruzadas y reescribir el
archivo en un formato limpio:

```bash
qpdf --qdf --object-streams=disable broken.pdf fixed.pdf
# Then retry your extraction against fixed.pdf
```

### Reparación con Ghostscript (más pesado pero exhaustivo)

```bash
gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress broken.pdf
```

Esto vuelve a parsear y renderizar el documento, por lo que el formato
puede cambiar ligeramente, pero el archivo queda legible.

### Recuperación parcial cuando incluso la reparación falla

Rasteriza el documento completo y aplica OCR. Se pierde la estructura, pero
se recupera el contenido:

```python
from pdf2image import convert_from_path
import pytesseract

pages = convert_from_path("damaged.pdf", dpi=300, strict=False)
text = "\n\n".join(pytesseract.image_to_string(p) for p in pages)
```

---

## 4. Patrones de procesamiento por lotes

### Extracción paralela de múltiples PDFs

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import pdfplumber

def extract_one(path):
    try:
        with pdfplumber.open(path) as pdf:
            return path.name, "\n\n".join(
                (p.extract_text() or "") for p in pdf.pages
            )
    except Exception as exc:
        return path.name, f"__ERROR__ {exc}"

pdfs = list(Path("/data/pdfs").glob("*.pdf"))
with ProcessPoolExecutor(max_workers=8) as ex:
    for name, text in ex.map(extract_one, pdfs):
        Path(f"/data/text/{name}.txt").write_text(text)
```

Procesos, no hilos — pdfplumber retiene el GIL durante el parsing.

### Modo streaming para PDFs muy grandes

No cargues todas las páginas en memoria:

```python
from pypdf import PdfReader

reader = PdfReader("huge.pdf")
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    # write / process each page immediately
    with open(f"/tmp/page_{i:04d}.txt", "w") as f:
        f.write(text or "")
    # don't accumulate `text` in a list
```

---

## 5. PDFs firmados y certificados

Los PDFs firmados incrustan firmas criptográficas en un blob PKCS#7 de Adobe.

### Detectar firmas

```python
from pypdf import PdfReader

reader = PdfReader("contract.pdf")
fields = reader.get_fields() or {}
signatures = [
    name for name, f in fields.items()
    if f.get("/FT") == "/Sig"
]
print(f"Found {len(signatures)} signature field(s): {signatures}")
```

### Inspeccionar detalles de firma con `pyhanko`

```python
# pip install pyhanko
from pyhanko.pdf_utils.reader import PdfFileReader

with open("contract.pdf", "rb") as f:
    reader = PdfFileReader(f)
    for name, sig in reader.embedded_signatures:
        print(f"Signer: {sig.signer_cert.subject}")
        print(f"Signed at: {sig.signer_info.signing_time}")
        print(f"Intact: {sig.compute_integrity_info().intact}")
```

La verificación de firmas frente a un ancla de confianza es un tema en sí
mismo — consulta la documentación de `pyhanko`. Para una lectura sencilla,
con detectar que el documento está firmado e identificar al firmante suele
ser suficiente.

---

## 6. Soporte de idiomas para OCR

Tesseract utiliza códigos ISO de tres letras:

| Idioma | Código | Paquete (Debian/Ubuntu) |
|---|---|---|
| Inglés | `eng` | por defecto |
| Español | `spa` | `tesseract-ocr-spa` |
| Francés | `fra` | `tesseract-ocr-fra` |
| Alemán | `deu` | `tesseract-ocr-deu` |
| Italiano | `ita` | `tesseract-ocr-ita` |
| Portugués | `por` | `tesseract-ocr-por` |
| Catalán | `cat` | `tesseract-ocr-cat` |
| Árabe | `ara` | `tesseract-ocr-ara` |
| Chino simplificado | `chi_sim` | `tesseract-ocr-chi-sim` |
| Japonés | `jpn` | `tesseract-ocr-jpn` |

Varios idiomas a la vez (útil para contratos multilingües):

```python
text = pytesseract.image_to_string(image, lang="spa+eng")
```

Listar los idiomas instalados:

```bash
tesseract --list-langs
```

Instalar los que falten:

```bash
sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra
```

---

## 7. Consejos de rendimiento

### La extracción de texto está limitada por E/S a escala

Con miles de PDFs, el cuello de botella son las lecturas en disco, no la CPU.
Los SSDs importan más que el número de núcleos.

### La rasterización está limitada por la CPU

Tanto `pdftoppm` como `pypdfium2` escalan bien con los núcleos. Usa
`ProcessPoolExecutor` entre archivos, no entre páginas de un mismo archivo.

### Cachea de forma agresiva

La extracción de texto es determinista. Si estás iterando sobre la lógica de
análisis, cachea el texto extraído en disco una sola vez y cárgalo desde la
caché:

```python
from pathlib import Path
import json, hashlib

def cached_text(pdf_path, cache_dir=Path("/tmp/pdf-cache")):
    cache_dir.mkdir(exist_ok=True)
    key = hashlib.sha256(Path(pdf_path).read_bytes()).hexdigest()[:16]
    cached = cache_dir / f"{key}.txt"
    if cached.exists():
        return cached.read_text()
    # ... extract and save
    text = extract_somehow(pdf_path)
    cached.write_text(text)
    return text
```

### Evita el trabajo duplicado

Si tu pipeline extrae texto y rasteriza páginas, abre el PDF una sola vez
y realiza ambas operaciones en un único pasada con `pypdfium2`:

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("report.pdf")
for page_num, page in enumerate(pdf, start=1):
    # Text
    textpage = page.get_textpage()
    text = textpage.get_text_bounded()
    textpage.close()

    # Rasterized image of the same page
    bitmap = page.render(scale=150 / 72)  # 150 DPI
    bitmap.to_pil().save(f"/tmp/page_{page_num:03d}.png")
    bitmap.close()

    # process text and image together
pdf.close()
```

Para un enfoque más sencillo (dos pasadas pero sin dependencias adicionales),
usa `pdfplumber` para texto y `pdftoppm` para imágenes. La versión de pasada
única mostrada arriba solo merece la pena a alto volumen.
