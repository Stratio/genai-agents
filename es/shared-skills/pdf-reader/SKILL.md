---
name: pdf-reader
description: "Inspecciona, analiza y extrae contenido de archivos PDF de forma inteligente. Usa esta skill cuando necesites leer el contenido de un PDF — extrayendo texto, tablas, imágenes, valores de campos de formulario, adjuntos embebidos o comprendiendo visualmente el diseño de página. Cubre PDFs de texto, documentos escaneados, presentaciones exportadas, formularios rellenables e informes cargados de datos. Ejecuta siempre un diagnóstico rápido antes de la extracción para elegir la estrategia correcta."
argument-hint: "[ruta/al/archivo.pdf]"
---

# Skill: Lector de PDF

Un enfoque disciplinado para obtener contenido útil de archivos PDF. Distintos
PDFs requieren distintas tácticas — un contrato escaneado no se parece en nada
a una exportación de diapositivas, y ninguno de los dos se parece a un informe
financiero lleno de tablas.
Primero el diagnóstico, después la extracción.

## 1. Dos modos: rápido y profundo

Esta skill soporta dos formas de trabajar:

**Modo rápido — `scripts/quick_extract.py`**
Extracción en un solo paso que devuelve Markdown estructurado. Úsalo cuando:
- El PDF es "normal" (basado en texto, no escaneado, no exótico)
- Quieres texto + tablas sin pensar qué librería usar
- Estás procesando muchos archivos en lote
- Vas a pasar el resultado directamente a otro agente o LLM

**Modo profundo — el flujo de trabajo que se describe a continuación**
Diagnóstico y extracción paso a paso. Úsalo cuando:
- El PDF es complejo, escaneado o da problemas
- Necesitas extraer figuras, adjuntos o campos de formulario
- Te importa el diseño, la posición o los gráficos vectoriales
- El modo rápido falló o devolvió basura

Usa el modo rápido por defecto. Recurre al modo profundo cuando el rápido no sea suficiente.

### Uso del modo rápido

```bash
# Extraer todo
python <skill-root>/scripts/quick_extract.py document.pdf

# Páginas específicas
python <skill-root>/scripts/quick_extract.py document.pdf --pages 1-5

# Solo texto, sin tablas
python <skill-root>/scripts/quick_extract.py document.pdf --no-tables

# Forzar un extractor específico
python <skill-root>/scripts/quick_extract.py document.pdf --tool pdfminer

# Leer desde stdin
cat document.pdf | python <skill-root>/scripts/quick_extract.py -

# Si no hay ningún extractor Python instalado, intentar instalar uno
python <skill-root>/scripts/quick_extract.py document.pdf --auto-install
```

El script:
- Devuelve Markdown por stdout (metadatos del documento, secciones por página, tablas)
- Devuelve diagnósticos por stderr (qué herramienta se ejecutó, advertencias)
- Sale con código 0 en caso de éxito, 1 en caso de fallo
- Detecta automáticamente las herramientas disponibles y hace fallback en cadena
- Nunca contamina stdout — la salida es segura para redirigir a otra herramienta

La cadena de extractores prueba, en orden: **pdfplumber → pdfminer.six → pypdf →
pdftotext**. Gana el primero que produzca salida no vacía.

## 2. Regla de oro para el modo profundo: diagnostica antes de extraer

Nunca ejecutes `pypdf` o `pdfplumber` a ciegas sobre un PDF desconocido. Un PDF
escaneado devolverá cadenas vacías. Un PDF con codificación de fuente rota devolverá
mojibake. Un PDF con adjuntos embebidos oculta datos que la extracción de texto
nunca ve. Un paso de diagnóstico de dos segundos ahorra diez minutos de depurar
salida basura.

Ejecuta primero este bloque de inspección:

```bash
# ¿Con qué tratamos? Páginas, tamaño, productor, fecha de creación
pdfinfo target.pdf

# ¿Hay texto extraíble o es un escaneado?
pdftotext -f 1 -l 2 target.pdf - | head -30

# ¿Hay imágenes raster que valga la pena extraer (fotos, figuras)?
pdfimages -list target.pdf | head -20

# ¿Hay archivos embebidos (hojas de cálculo, datos, subdocumentos)?
pdfdetach -list target.pdf

# ¿Están embebidas las fuentes? Las codificaciones personalizadas suelen romper la extracción.
pdffonts target.pdf | head -15
```

Qué te dice cada salida:

- **`pdfinfo`** — el número de páginas indica la escala del trabajo. El productor indica
  el origen (LaTeX, Word, InDesign, un escáner). El tamaño de archivo por página
  da pistas sobre el contenido de imagen.
- **Muestra de `pdftotext`** — si las dos primeras páginas no devuelven nada o solo
  espacios en blanco, tienes un PDF escaneado. Si devuelven prosa legible,
  la extracción de texto es viable. Si devuelven caracteres extraños, probablemente
  tengas una codificación de fuente rota.
- **`pdfimages -list`** — las columnas muestran anchura, altura, espacio de color y
  codificación. Las miniaturas menores de ~50×50 suelen ser decoración; las figuras
  reales son más grandes. Cero imágenes no significa cero figuras — los gráficos
  dibujados como vectores no aparecen aquí.
- **`pdfdetach -list`** — los PDFs pueden embeber otros archivos (hojas de cálculo Excel,
  datos CSV, otros PDFs). Común en informes de negocio y PDF/A-3.
- **`pdffonts`** — mira la columna "emb". Si las fuentes clave no están embebidas
  y usan codificación personalizada o Identity-H, la extracción de texto puede
  producir caracteres incorrectos. Esa es la señal para rasterizar en su lugar.

## 3. Elige una estrategia según el tipo de documento

Clasifica el PDF mentalmente y aplica el flujo de trabajo correspondiente.

### Documentos con mucho texto (informes, artículos, libros, papers)

Herramienta principal: `pdfplumber` para extracción consciente del diseño, o `pdftotext
-layout` desde la línea de comandos.

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    full_text = []
    for page in pdf.pages:
        full_text.append(page.extract_text())
    text = "\n\n".join(full_text)
```

Para diseños multicolumna, `pdftotext -layout` suele preservar las columnas
mejor que `pdfplumber`:

```bash
pdftotext -layout report.pdf report.txt
```

Rasteriza solo las páginas específicas que contengan figuras que necesites inspeccionar
visualmente. Rasterizar el documento completo es excesivo y costoso.

### Documentos escaneados (sin texto extraíble)

Síntoma: `pdftotext` devuelve vacío, o casi vacío. Cada página es
esencialmente una imagen del texto.

Flujo de trabajo: convertir páginas a imágenes, ejecutar OCR.

```python
from pdf2image import convert_from_path
import pytesseract

pages = convert_from_path("scanned.pdf", dpi=300)
text_by_page = []
for i, img in enumerate(pages, 1):
    text = pytesseract.image_to_string(img, lang="eng")  # o "spa", "fra", etc.
    text_by_page.append(f"--- Page {i} ---\n{text}")

full_text = "\n\n".join(text_by_page)
```

Los DPI importan. 300 es un buen valor por defecto; 400+ para texto pequeño y denso; 200 para
mayor velocidad cuando la calidad importa menos. Para documentos en idiomas distintos al inglés, especifica
`lang=` con el paquete de idioma de Tesseract correspondiente instalado.

### Presentaciones exportadas

Síntoma: número de páginas bajo (5–80), cada página visualmente densa, `pdftotext`
devuelve puntos y aparte sin contexto, el diseño se pierde.

La extracción de texto sola raramente es suficiente. Rasteriza cada diapositiva que te importe
y léela como imagen.

```bash
# Renderizar diapositivas específicas como imágenes a resolución de pantalla
pdftoppm -jpeg -r 150 -f 3 -l 5 deck.pdf /tmp/slide
ls /tmp/slide-*.jpg
```

Una nota sobre los nombres de archivo: `pdftoppm` rellena con ceros el sufijo en función del número total de páginas.
Una presentación de 50 páginas produce `slide-03.jpg`; una de 200 páginas produce
`slide-003.jpg`. No escribas el nombre de archivo en duro — lista el directorio.

### Formularios rellenables

Los PDFs con campos AcroForm (formularios de administración, solicitudes, contratos)
almacenan la entrada del usuario como datos estructurados. Extráelos de forma programática
en lugar de analizar el texto visual.

```python
from pypdf import PdfReader

reader = PdfReader("application.pdf")

# Todos los tipos de campo: entradas de texto, casillas, botones de opción, desplegables
fields = reader.get_fields() or {}
for name, field in fields.items():
    value = field.get("/V", "")
    field_type = field.get("/FT", "")  # /Tx texto, /Btn botón, /Ch elección
    print(f"{name} ({field_type}): {value!r}")
```

**Advertencia**: `get_form_text_fields()` solo devuelve campos de texto. Si la
usas en un formulario con casillas o desplegables, perderás datos silenciosamente.
Empieza siempre con `get_fields()`.

Para un volcado completo que incluya opciones y valores por defecto:

```bash
pdftk application.pdf dump_data_fields > fields.txt
```

### Documentos con muchos datos (tablas, gráficos, cuadros de mando)

Tablas — prueba primero con `pdfplumber`:

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("financials.pdf") as pdf:
    dataframes = []
    for page in pdf.pages:
        for raw in page.extract_tables() or []:
            if not raw or len(raw) < 2:
                continue
            headers, *rows = raw
            dataframes.append(pd.DataFrame(rows, columns=headers))

if dataframes:
    combined = pd.concat(dataframes, ignore_index=True)
```

Si las tablas salen con celdas fusionadas, columnas desalineadas o datos faltantes,
`pdfplumber` tiene parámetros de ajuste (`table_settings` con estrategias
como `"lines"`, `"text"`, o líneas verticales/horizontales explícitas). Ver
`REFERENCE.md`.

Los gráficos y figuras dibujados como vectores no salen de
`pdfimages`. Rasteriza la página que los contiene:

```bash
pdftoppm -png -r 200 -f 4 -l 4 financials.pdf /tmp/chart
```

Después lee `/tmp/chart-04.png` (o como se llame) como imagen.

### Documentos mixtos

Muchos PDFs del mundo real son mixtos: texto narrativo, algunas tablas, uno o dos
gráficos, quizás un apéndice escaneado. No intentes manejarlo todo en un solo paso.
Divídelo:

1. Extrae texto de las páginas que tengan texto extraíble.
2. Rasteriza las páginas con figuras.
3. Aplica OCR a las secciones escaneadas por separado.
4. Extrae los adjuntos si los hay.
5. Combina los resultados al final.

## 4. Conciencia de tokens al consumir contenido en un LLM

Si vas a pasar contenido de PDF a Claude u otro LLM, el coste importa.

| Enfoque | Tokens aproximados por página |
|---|---|
| Extracción de texto plano | 200–500 |
| Página rasterizada a 150 DPI | ~1.600 |
| Página rasterizada a 300 DPI | ~2.800 |
| Texto + imagen rasterizada ambos | 2.000–3.300 |

Un PDF de 100 páginas rasterizado a 150 DPI consume alrededor de 160K tokens. La extracción
de texto del mismo documento consume 20K–50K. Reserva la rasterización para
páginas donde el diseño visual realmente importa: gráficos, diagramas, diseños
de formulario, tablas complejas, ecuaciones.

Cuando la precisión importa en una página específica (por ejemplo, un contrato con un
bloque de firma, un estado financiero), enviar tanto el texto como la imagen
cuesta más pero da al LLM el máximo contexto para contrastar.

## 5. Extracción de imágenes embebidas

```bash
# Listado rápido con metadatos
pdfimages -list target.pdf

# Extraer todo como PNG
pdfimages -png target.pdf /tmp/extracted

# Reducir a páginas específicas
pdfimages -png -f 3 -l 5 target.pdf /tmp/extracted

# Preservar el formato original (JPEG se queda como JPEG, PNG como PNG)
pdfimages -all target.pdf /tmp/extracted
```

Espera ruido: `pdfimages` produce muchas máscaras de transparencia y
elementos decorativos junto con las figuras reales. Filtra por tamaño de archivo para
encontrar las sustanciales:

```bash
find /tmp -name "extracted-*.png" -size +10k
```

Para imágenes con sus coordenadas de página (útil cuando necesitas saber
*dónde* en la página aparece una imagen), usa `pypdfium2`:

```python
import pypdfium2 as pdfium
from pypdfium2 import raw

pdf = pdfium.PdfDocument("target.pdf")
for page_num, page in enumerate(pdf, start=1):
    img_index = 0
    for obj in page.get_objects():
        if obj.type != raw.FPDF_PAGEOBJ_IMAGE:
            continue
        # Bounding box en coordenadas de página (puntos)
        left, bottom, right, top = obj.get_bounds()
        # extract() escribe la imagen en su formato nativo (jpg/png/etc.)
        obj.extract(f"/tmp/p{page_num}_i{img_index}_at_{int(left)}_{int(bottom)}")
        img_index += 1
pdf.close()
```

`pypdfium2` tiene licencia Apache 2.0 / BSD y cubre la extracción posicional de imágenes
sin la restricción AGPL de PyMuPDF. Si prefieres trabajar con imágenes PIL en memoria
en lugar de escribir a disco, usa
`obj.get_bitmap(render=False).to_pil()`.

## 6. Extracción de adjuntos embebidos

Los PDFs pueden llevar otros archivos dentro — hojas de cálculo, CSVs, otros PDFs.
Muy común en informes regulados (PDF/A-3) y portfolios de negocio.

```bash
pdfdetach -list target.pdf
mkdir -p /tmp/attachments
pdfdetach -saveall -o /tmp/attachments/ target.pdf
ls -la /tmp/attachments/
```

**Nota de seguridad**: los nombres de archivo de los adjuntos provienen del PDF y pueden contener
secuencias de path traversal como `../../etc/passwd`. Cuando uses APIs de Python
para extraer adjuntos, sanea siempre:

```python
import os
from pypdf import PdfReader

reader = PdfReader("target.pdf")
for raw_name, contents in (reader.attachments or {}).items():
    safe = os.path.basename(raw_name)  # eliminar cualquier componente de ruta
    if not safe:
        continue
    for data in contents:
        with open(f"/tmp/attachments/{safe}", "wb") as f:
            f.write(data)
```

Existen dos mecanismos de adjuntos: adjuntos de anotación a nivel de página (los
iconos de clip que ves en Acrobat) y archivos embebidos a nivel de documento
(árbol de nombres EmbeddedFiles). Tanto `pdfdetach` como pypdf manejan los casos comunes.
Las anotaciones de medios enriquecidos (audio, video, 3D) aparecen raramente y
requieren inspeccionar directamente el diccionario `/Annots` de la página con
`pypdf`:

```python
from pypdf import PdfReader

reader = PdfReader("target.pdf")
for page_num, page in enumerate(reader.pages, start=1):
    annots = page.get("/Annots")
    if not annots:
        continue
    for annot_ref in annots:
        annot = annot_ref.get_object()
        if annot.get("/Subtype") == "/RichMedia":
            # Inspeccionar el diccionario /RichMediaContent para los activos
            content = annot.get("/RichMediaContent", {})
            print(f"Page {page_num}: rich media annotation:", content)
```

La extracción de medios enriquecidos es genuinamente rara en la práctica — la mayoría de los casos
de "medios dentro de PDF" acaban siendo adjuntos embebidos normales que
`pdfdetach` ya maneja.

## 7. Cuando la extracción de texto sale garbled

Síntomas: caracteres extraños, letras faltantes, todo desplazado una posición,
mojibake.

Ejecuta `pdffonts target.pdf` y mira:

- **Columna emb** — ¿está la fuente realmente embebida? Si dice "no", el
  PDF hace referencia a una fuente por nombre y depende del visor para
  sustituirla. La extracción probablemente fallará.
- **Columna enc** — "Custom" o "Identity-H" sin mapas CIDToGID correctos
  significa que los códigos de carácter no se mapean de vuelta a Unicode legible.

Cuando te encuentres con esto, deja de pelear con la extracción de texto. Rasteriza la
página a 300 DPI y aplica OCR, o envía la imagen a un modelo de visión. La
salida visual es la única representación fidedigna.

## 8. PDFs protegidos con contraseña

Si el PDF está cifrado y tienes la contraseña:

```python
from pypdf import PdfReader

reader = PdfReader("locked.pdf")
if reader.is_encrypted:
    reader.decrypt("the-password-here")

for page in reader.pages:
    print(page.extract_text())
```

Si hay una contraseña de propietario que impide la extracción (pero no hay contraseña de usuario
que impida abrirlo), `pypdf` a veces permite leer sin la
contraseña. Si no, crear una copia desbloqueada es un trabajo para `pdf-writer`,
no para esta skill.

## 9. Hoja de referencia rápida

| Tarea | Herramienta | Comando |
|---|---|---|
| Inspeccionar metadatos | pdfinfo | `pdfinfo file.pdf` |
| Muestra de texto rápida | pdftotext | `pdftotext -f 1 -l 2 file.pdf -` |
| Texto con diseño preservado | pdftotext | `pdftotext -layout file.pdf out.txt` |
| Texto consciente del diseño en Python | pdfplumber | `page.extract_text()` |
| Tablas | pdfplumber | `page.extract_tables()` |
| Rasterizar páginas | pdftoppm | `pdftoppm -jpeg -r 150 -f N -l N file.pdf prefix` |
| Extraer imágenes raster | pdfimages | `pdfimages -png file.pdf prefix` |
| Listar adjuntos | pdfdetach | `pdfdetach -list file.pdf` |
| Extraer adjuntos | pdfdetach | `pdfdetach -saveall -o dir/ file.pdf` |
| Diagnóstico de fuentes | pdffonts | `pdffonts file.pdf` |
| Leer valores de campos de formulario | pypdf | `reader.get_fields()` |
| OCR de páginas escaneadas | pytesseract + pdf2image | Ver sección documentos-escaneados |

## 10. Cuándo cargar REFERENCE.md

- Ajuste avanzado de tablas con `pdfplumber`
- Manejo de PDFs corruptos y recuperación con `qpdf --fix-qdf`
- Pipelines de procesamiento en lote
- Trabajo con PDFs firmados / certificados
- Librerías Python alternativas (`pypdfium2` para rasterización rápida,
  `pdfminer.six` para codificaciones inusuales)

## 11. Instalación

Esta skill espera que esté disponible un conjunto de herramientas estándar de procesamiento de PDF.
Para uso cotidiano, instala todo de una vez y olvídate.

### Instalación en un solo paso (Debian / Ubuntu)

```bash
sudo apt update && sudo apt install -y \
    poppler-utils qpdf pdftk \
    tesseract-ocr tesseract-ocr-spa tesseract-ocr-fra \
    tesseract-ocr-deu tesseract-ocr-ita tesseract-ocr-por \
    ghostscript

pip install \
    pypdf pdfplumber pdfminer.six pypdfium2 \
    pytesseract pdf2image pillow pandas ocrmypdf
```

### Instalación en un solo paso (macOS)

```bash
brew install poppler qpdf pdftk-java tesseract tesseract-lang ghostscript

pip install \
    pypdf pdfplumber pdfminer.six pypdfium2 \
    pytesseract pdf2image pillow pandas ocrmypdf
```

### Qué proporciona cada dependencia

| Paquete | Usado por | Propósito |
|---|---|---|
| `poppler-utils` | modo profundo, fallback del modo rápido | `pdfinfo`, `pdftotext`, `pdftoppm`, `pdfimages`, `pdfdetach`, `pdffonts` |
| `qpdf` | `pdf-writer` | operaciones estructurales, reparación de PDFs corruptos |
| `pdftk` | modo profundo (inspección de formularios) | `dump_data_fields` |
| `tesseract-ocr` + paquetes de idioma | flujo OCR | extracción de texto de escaneados |
| `ghostscript` | modo profundo (PDFs corruptos) | reparación de último recurso / rasterización |
| `pypdf` | modo rápido, formularios | lectura básica de PDF, formularios |
| `pdfplumber` | modo rápido (principal) | texto + tablas conscientes del diseño |
| `pdfminer.six` | modo rápido (fallback) | extracción de texto en Python puro |
| `pypdfium2` | modo profundo (renderizado) | rasterización rápida de páginas, licencia Apache 2.0 |
| `pytesseract` + `pdf2image` | flujo OCR | wrapper Python sobre tesseract |
| `ocrmypdf` | modo profundo | escaneado → PDF con texto buscable |

### Nota sobre licencias

Todos los paquetes de la instalación por defecto anterior tienen **licencia permisiva**
(MIT, BSD, Apache 2.0, MPL, LGPL). Ninguno impone obligaciones copyleft sobre
tu proyecto.

Esta skill deliberadamente **no** incluye PyMuPDF (`fitz`). PyMuPDF
es rico en funcionalidades pero se distribuye bajo AGPL v3, que es incompatible con
la mayoría de licencias propietarias o de código fuente disponible. Todo lo que esta skill
documenta es alcanzable con las alternativas permisivas anteriores.

### Instalación bajo demanda

El script de modo rápido puede instalar `pdfminer.six` al vuelo cuando no hay nada
más disponible:

```bash
python scripts/quick_extract.py document.pdf --auto-install
```

Esto es una red de seguridad, no el camino normal. Para flujos de trabajo en modo profundo, la
skill asume que los paquetes anteriores ya están instalados y sugerirá
comandos `pip install <pkg>` cuando falte algo concreto.



La creación, fusión, división, rotación, marcas de agua, cifrado,
relleno de formularios y el aplanamiento OCR de documentos escaneados a PDFs con texto buscable
están en la skill compañera `pdf-writer`.
