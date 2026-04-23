---
name: pptx-reader
description: "Inspecciona, analiza y extrae contenido de ficheros PowerPoint (.pptx) inteligentemente. Usa esta skill siempre que necesites leer lo que hay dentro de un deck — extraer texto de slide, listas de bullets, tablas, notas del presentador, imágenes embebidas, datos de charts, comentarios, o entender visualmente la composición de los slides. Cubre pitch decks, briefings ejecutivos, decks de formación, slides académicos y dashboards con datos pesados. También maneja ficheros `.ppt` legacy vía conversión con LibreOffice. Ejecuta siempre un diagnóstico rápido antes de extraer para elegir la estrategia adecuada."
argument-hint: "[ruta/al/fichero.pptx]"
---

# Skill: PPTX Reader

Un enfoque disciplinado para sacar contenido útil de ficheros
PowerPoint. Distintos decks necesitan distintas tácticas — un policy
brief con mucho texto se comporta completamente distinto a un
dashboard hecho de charts rasterizados, y ninguno se comporta como
una presentación llena de charts OOXML nativos con datos editables.
Diagnosticar primero, extraer después.

## 1. Dos modos: rápido y profundo

Esta skill soporta dos formas de trabajar:

**Modo rápido — `scripts/quick_extract.py`**
Extracción one-shot que devuelve Markdown estructurado. Úsalo cuando:
- El deck es "normal" (nativo `.pptx`, sin contraseña)
- Quieres texto + bullets + tablas + notas del presentador sin pensar en XML
- Estás procesando muchos ficheros en batch
- Vas a pasar el output directamente a otro agente o LLM

**Modo profundo — el workflow de abajo**
Diagnóstico paso a paso y extracción. Úsalo cuando:
- El deck tiene charts embebidos con datos numéricos que necesitas como tabla
- Necesitas previews rasterizados por slide para un modelo de visión
- Notas del presentador, comentarios o slides ocultos requieren manejo a medida
- El fichero es un `.ppt` binario legacy
- El modo rápido devolvió texto vacío o basura

Por defecto, modo rápido. Vuelve al modo profundo cuando el rápido no sea suficiente.

### Uso del modo rápido

```bash
# Extraer todo
python <skill-root>/scripts/quick_extract.py deck.pptx

# Solo texto, sin tablas
python <skill-root>/scripts/quick_extract.py deck.pptx --no-tables

# Solo texto, sin notas del presentador
python <skill-root>/scripts/quick_extract.py deck.pptx --no-notes

# Incluir slides ocultos (se omiten por defecto)
python <skill-root>/scripts/quick_extract.py deck.pptx --include-hidden

# Forzar un extractor concreto
python <skill-root>/scripts/quick_extract.py deck.pptx --tool python-pptx

# Leer desde stdin
cat deck.pptx | python <skill-root>/scripts/quick_extract.py -
```

El script:
- Devuelve Markdown por stdout (secciones por slide con headings, bullets,
  tablas, notas del presentador en bloques `> Notes:`)
- Devuelve diagnóstico por stderr (conteo de slides, slides ocultos, qué
  herramienta se ejecutó, features omitidas)
- Sale con código 0 en éxito, 1 en fallo
- Auto-detecta herramientas disponibles y cae en cadena de fallback
- Nunca contamina stdout — el output es seguro para piping a otra herramienta

La cadena de extractores intenta, en este orden: **python-pptx → zipfile XML
walk → conversión a texto con soffice**. El primero que produzca output
no vacío gana.

### Utilidad complementaria — `scripts/rasterize_slides.py`

One-shot separado que convierte un deck a PNGs, uno por slide. Útil
cuando quieres pasar imágenes de slides a un modelo de visión sin
ejecutar el pipeline completo de extracción.

```bash
# Rasterizar cada slide a 150 DPI (~1.500 tokens/slide para vision)
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides

# DPI mayor para contenido denso
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides --dpi 300

# Solo slides concretos
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides --pages 3-7
```

Ejecuta `soffice --headless --convert-to pdf` seguido de `pdftoppm`.
Ambos deben estar disponibles en `$PATH`.

## 2. Regla de oro del modo profundo: diagnostica antes de extraer

Nunca ejecutes `python-pptx` a ciegas sobre un deck desconocido. Un
fichero `.ppt` legacy lanzará un error oscuro. Un deck con slides
ocultos te dará contenido distinto del que el autor presentó. Una
presentación con fuentes custom no instaladas se renderiza con
substitución que no detectas solo desde el texto extraído. Dos
segundos de diagnóstico ahorran diez minutos depurando basura.

Ejecuta este bloque de inspección primero:

```bash
# ¿Qué tenemos? ¿Un ZIP (.pptx moderno) o un CFB (.ppt legacy)?
file target.pptx

# Listar el contenido del ZIP — slides, masters, medios, notas
unzip -l target.pptx | head -40

# ¿Cuántos slides hay?
unzip -l target.pptx | grep -c 'ppt/slides/slide[0-9]'

# ¿Slides ocultos?
unzip -p target.pptx ppt/presentation.xml | grep -o 'show="0"' | wc -l

# ¿Notas del presentador?
unzip -l target.pptx | grep -c 'ppt/notesSlides/notesSlide'

# ¿Comentarios?
unzip -l target.pptx | grep -c 'ppt/comments/'

# ¿Medios embebidos?
unzip -l target.pptx | grep 'ppt/media/' | head -20

# Metadatos
unzip -p target.pptx docProps/core.xml
```

Qué te dice cada salida:

- **`file`** — `Microsoft PowerPoint 2007+` significa `.pptx` moderno
  (basado en ZIP, legible por `python-pptx`). `Composite Document File
  V2` o `CFB` significa `.ppt` legacy — hay que convertir primero
  (ver §11).
- **`unzip -l` contando `ppt/slides/slide*.xml`** — conteo de slides.
  Decks con 50+ slides se benefician de extracción por rango de
  páginas en lugar de un dump completo.
- **Conteo `show="0"`** — número de slides ocultos. El autor los
  ocultó adrede; decide si incluirlos o omitirlos (por defecto
  quick_extract los omite).
- **Conteo `notesSlides`** — notas del presentador presentes.
  Esencial en pitch decks y briefings donde el mensaje verbal vive
  en las notas.
- **`comments/`** — comentarios del revisor (marcas de revisión).
  Extrae esto separadamente cuando la tarea es revisión editorial.
- **`ppt/media/`** — lista todas las imágenes embebidas (PNG, JPG),
  audio (WAV, MP3), vídeo (MP4). El tamaño sugiere su peso.
- **`docProps/core.xml`** — autor, timestamps de creado/modificado,
  título, subject, keywords.

## 3. Elige una estrategia según el tipo de deck

Clasifica el deck mentalmente, luego aplica el workflow que toque.

### Decks con mucho texto (policy briefs, pitch decks, briefings internos)

Herramienta principal: `python-pptx` para extracción de texto por
shape, por slide.

```python
from pptx import Presentation

prs = Presentation("brief.pptx")
for slide_num, slide in enumerate(prs.slides, start=1):
    # Omite slides ocultos salvo que el usuario pida lo contrario
    if getattr(slide, "element", None) is not None:
        if slide.element.get("show") == "0":
            continue

    title = _find_title(slide)
    print(f"## Slide {slide_num}: {title or '(sin título)'}\n")

    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = "".join(r.text for r in para.runs).strip()
                if not text:
                    continue
                # Niveles de bullet: para.level 0-8
                prefix = "  " * (para.level or 0) + "- "
                print(prefix + text)
```

El helper `_find_title` prefiere el placeholder de título; si no
existe, cae al primer text frame del slide. Ver el patrón completo
en REFERENCE.md.

Convención de output: un heading `## Slide N: Título` por slide,
bullets con indentación que refleja `para.level`, líneas en blanco
entre slides.

### Decks con muchos datos (dashboards, reports con charts)

Un chart dentro de un PPTX puede vivir en dos formas:

1. **Chart OOXML nativo** (`<c:chart>` en `ppt/charts/chart*.xml`) —
   editable por el usuario; los datos subyacentes son accesibles
   como XML. Puedes reconstruir el dataframe sin visión.
2. **Imagen rasterizada** (chart exportado desde Excel/matplotlib/
   plotly y pegado como PNG/JPG) — los datos no son recuperables
   del fichero; necesitas OCR o un modelo de visión.

Detecta cuál está presente:

```bash
# Charts OOXML nativos
unzip -l deck.pptx | grep -c 'ppt/charts/chart'

# Imágenes de charts rasterizados
unzip -l deck.pptx | grep -E 'ppt/media/.*\.(png|jpg|jpeg|tiff)$'
```

Para charts nativos, parsea el XML:

```python
import zipfile
from lxml import etree

NS = {
    "c":  "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "a":  "http://schemas.openxmlformats.org/drawingml/2006/main",
}

with zipfile.ZipFile("deck.pptx") as z:
    for name in sorted(z.namelist()):
        if not name.startswith("ppt/charts/chart") or not name.endswith(".xml"):
            continue
        tree = etree.parse(z.open(name))
        # Los valores de serie viven bajo c:ser/c:val/c:numRef/c:numCache/c:pt/c:v
        for ser in tree.iterfind(".//c:ser", NS):
            name_el = ser.find(".//c:tx//c:v", NS)
            ser_name = (name_el.text or "").strip() if name_el is not None else ""
            values = [float(v.text) for v in ser.iterfind(".//c:val//c:v", NS) if v.text]
            print(f"{name}: series='{ser_name}' values={values}")
```

Para charts rasterizados, rasteriza el slide que los contiene y
pásalo a un modelo de visión (ver §4).

### Decks exportados (todo el contenido como imágenes de página)

Síntoma: cada slide es una imagen rasterizada a sangre sin text
frames. Pasa cuando alguien exporta slides desde Keynote o una
herramienta basada en imagen y los re-guarda como PPT. `python-pptx`
devuelve texto vacío por slide.

Workflow: salta la extracción de texto y rasteriza cada slide.

```bash
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides --dpi 200
```

Alimenta los PNG resultantes a un modelo de visión. Espera ~1.600
tokens/slide a 150 DPI, ~2.800 tokens/slide a 300 DPI.

### Decks mixtos

La mayoría de decks reales son mixtos: una intro con prosa, unos
cuantos slides de bullets, dos dashboards con charts nativos, un
slide legacy escaneado, un slide de conclusiones con un screenshot.
No intentes extraer todo de una pasada. Divídelo:

1. Ejecuta `quick_extract.py` para las partes de prosa.
2. Parsea `ppt/charts/chart*.xml` para datos de chart nativo.
3. Rasteriza solo los slides que contengan charts rasterizados o screenshots.
4. Extrae notas del presentador separadamente si llevan sustancia.
5. Une los hallazgos en tu resumen final.

## 4. Conciencia de tokens al consumir contenido en un LLM

Si estás pasando contenido de deck a Claude u otro LLM, el coste importa.

| Aproximación | Tokens aprox. por slide |
|---|---|
| Extracción de texto plano (prosa + bullets + tablas) | 100–300 |
| Solo notas del presentador (como prosa) | 50–200 |
| Slide rasterizado a 150 DPI | ~1.600 |
| Slide rasterizado a 300 DPI | ~2.800 |
| Texto + imagen rasterizada a la vez | 1.800–3.100 |

Un deck de 40 slides rasterizado a 150 DPI gasta ~64K tokens. La
extracción de texto del mismo deck gasta 4K–12K. Reserva la
rasterización para slides donde la composición visual sí importa:
dashboards, diagramas, screenshots, tablas complejas donde el
layout encoda el significado.

Cuando la precisión importa para un slide concreto (un dashboard
con KPIs posicionados en coordenadas específicas, un slide-cita
donde la tipografía carga el mensaje), mandar texto E imagen cuesta
más pero le da al LLM el máximo contexto para cross-check.

## 5. Notas del presentador

Las notas viven en `ppt/notesSlides/notesSlide{N}.xml` (una por
slide que tenga notas). El texto está bajo el namespace DrawingML,
no PresentationML.

```python
from pptx import Presentation

prs = Presentation("brief.pptx")
for idx, slide in enumerate(prs.slides, start=1):
    notes_slide = slide.notes_slide if slide.has_notes_slide else None
    if notes_slide is None:
        continue
    notes_text = "\n".join(
        p.text for p in notes_slide.notes_text_frame.paragraphs if p.text.strip()
    )
    if notes_text:
        print(f"--- Notas del slide {idx} ---\n{notes_text}\n")
```

En pitch decks y briefings ejecutivos, las notas contienen a menudo
la narrativa verbal ("Aquí decimos X por la evidencia Y"). Extraer
solo las notas puede responder a "¿qué dice este deck?" de forma
más compacta que los propios bullets del slide.

## 6. Comentarios (marcas de revisión)

Los comentarios del revisor viven en `ppt/comments/comment{N}.xml`.
Están separados de las notas y suelen llevar feedback editorial
("Reformular esta afirmación", "Citar fuente").

```python
import zipfile
from lxml import etree

NS = {
    "p188": "http://schemas.microsoft.com/office/powerpoint/2012/main",
    "p":    "http://schemas.openxmlformats.org/presentationml/2006/main",
}

with zipfile.ZipFile("brief.pptx") as z:
    comment_files = [n for n in z.namelist() if n.startswith("ppt/comments/")]
    for name in sorted(comment_files):
        tree = etree.parse(z.open(name))
        for cm in tree.iterfind(".//p:cm", NS):
            author_idx = cm.get("authorId")
            text_el = cm.find(".//p:text", NS)
            text = (text_el.text or "").strip() if text_el is not None else ""
            if text:
                print(f"[{name} author={author_idx}] {text}")
```

Para revisiones editoriales y workflows de redlining, extraer los
comentarios permite aflorar el feedback sin presentar el contenido
completo del deck.

## 7. Tablas

Las tablas en PPT son shapes con `has_table = True`. Extrae celda
a celda. Las celdas combinadas comparten el mismo `_tc` subyacente,
así que deduplica por identidad.

```python
from pptx import Presentation

def table_to_markdown(shape) -> str:
    rows = []
    for row in shape.table.rows:
        seen = []
        cells = []
        for cell in row.cells:
            cid = id(cell._tc)
            if cid in seen:
                continue
            seen.append(cid)
            text = cell.text.strip().replace("|", "\\|") or " "
            cells.append(text)
        rows.append(cells)
    if not rows:
        return ""
    max_cols = max(len(r) for r in rows)
    rows = [r + [" "] * (max_cols - len(r)) for r in rows]
    header = "| " + " | ".join(rows[0]) + " |"
    sep = "| " + " | ".join(["---"] * max_cols) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join([header, sep, *body])

prs = Presentation("report.pptx")
for slide_num, slide in enumerate(prs.slides, start=1):
    for shape in slide.shapes:
        if shape.has_table:
            print(f"### Tabla en slide {slide_num}\n")
            print(table_to_markdown(shape))
```

Cuidado con:
- **Fondos de fila alternados**: codificados en shading de celda, no
  aparecen en markdown. Ignóralo salvo que la tarea sea inspección
  de diseño.
- **Celdas combinadas**: el check `id(cell._tc)` deduplica. Las
  celdas combinadas aparecen como una sola celda con el contenido
  combinado o vecinas vacías — documenta la convención en tu output.
- **Formateo numérico**: `cell.text` da el texto renderizado, no el
  número subyacente. Para reconstruir datos, prefiere el XML de chart
  nativo OOXML antes que raspar una tabla renderizada.

## 8. Metadatos

`docProps/core.xml` lleva los metadatos a nivel de documento:

```python
from pptx import Presentation

prs = Presentation("deck.pptx")
cp = prs.core_properties
print(f"Título:   {cp.title}")
print(f"Autor:    {cp.author}")
print(f"Subject:  {cp.subject}")
print(f"Keywords: {cp.keywords}")
print(f"Creado:   {cp.created}")
print(f"Modif.:   {cp.modified}")
print(f"Último modificador: {cp.last_modified_by}")
print(f"Revisión: {cp.revision}")
```

`docProps/app.xml` tiene metadatos adicionales a nivel de software
(versión de app, conteo de slides, título del show, empresa). Parsea
con `lxml` cuando los necesites — python-pptx solo expone las core
properties.

## 9. Medios embebidos (imágenes, audio, vídeo)

Listados bajo `ppt/media/` dentro del ZIP.

```bash
# Listar todo
unzip -l deck.pptx | grep 'ppt/media/'

# Extraer todos los medios
mkdir -p /tmp/media
unzip deck.pptx 'ppt/media/*' -d /tmp/
```

Las imágenes (PNG, JPG) suelen ser el grueso. Audio (WAV, MP3) y
vídeo (MP4, MOV) aparecen en decks de formación y producto.
Extracción en Python:

```python
import zipfile

with zipfile.ZipFile("deck.pptx") as z:
    media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    for name in media:
        data = z.read(name)
        out_path = f"/tmp/{name.split('/')[-1]}"
        with open(out_path, "wb") as f:
            f.write(data)
        print(f"{name}: {len(data):,} bytes → {out_path}")
```

**Aviso**: los nombres en `ppt/media/` los asigna PowerPoint y
pueden colisionar con ficheros existentes al extraer. Sanea con
`os.path.basename` y escribe a un directorio fresco.

## 10. Slides ocultos

El autor los ocultó a propósito — backup del presentador, contenido
deprecated, o slides apartados para después. Por defecto, la
extracción debería **omitirlos**. Expón el conteo en el diagnóstico
para que el usuario sepa que existen.

Detecta:

```python
from pptx import Presentation

prs = Presentation("deck.pptx")
hidden = []
for idx, slide in enumerate(prs.slides, start=1):
    # python-pptx expone _element; los slides ocultos tienen show="0"
    if slide._element.get("show") == "0":
        hidden.append(idx)

print(f"Slides ocultos: {hidden}")
```

Si el usuario pide explícitamente el contenido oculto, re-ejecuta
con `--include-hidden` (modo rápido) o añade rama `if hidden` en
modo profundo.

## 11. Ficheros `.ppt` legacy

El formato binario `.ppt` (pre-Office 2007) no es un ZIP.
`python-pptx` no puede leerlo. Convierte con LibreOffice primero:

```bash
soffice --headless --convert-to pptx --outdir /tmp/ old.ppt
# → /tmp/old.pptx
```

Luego procesa como normal. `quick_extract.py` autodetecta el `.ppt`
legacy por la firma del fichero y convierte de forma transparente —
raramente necesitas ejecutar la conversión a mano.

Espera pérdida menor de fidelidad: animaciones, algunas shapes
custom y objetos Excel embebidos pueden llegar incompletos. Para
extracción de texto no importa; para análisis estructural sí.

## 12. Decks protegidos con contraseña

Si el PPTX abre pero revela XML cifrado dentro, `python-pptx`
lanzará `PackageNotFoundError`. El cifrado moderno de PPT usa OOXML
agile encryption (no OLECF como `.ppt` legacy).

```python
try:
    from pptx import Presentation
    prs = Presentation("locked.pptx")
except Exception as exc:
    print(f"No se puede abrir: {exc}")
```

No hay librería Python estable de descifrado de OOXML agile que
funcione sin la contraseña. Pide la contraseña al usuario y usa
`msoffcrypto-tool` para descifrar a un fichero temporal primero:

```bash
pip install msoffcrypto-tool
msoffcrypto-tool locked.pptx decrypted.pptx -p 'la-contraseña'
```

Luego procesa `decrypted.pptx` como normal. Nunca loguees ni
persistas la contraseña.

## 13. Cheat sheet de referencia rápida

| Tarea | Herramienta | Comando |
|---|---|---|
| Inspeccionar estructura | unzip | `unzip -l deck.pptx` |
| Conteo de slides | unzip + grep | `unzip -l deck.pptx \| grep -c 'ppt/slides/slide[0-9]'` |
| Slides ocultos | unzip + grep | `unzip -p deck.pptx ppt/presentation.xml \| grep -o 'show="0"' \| wc -l` |
| Texto por slide | python-pptx | `slide.shapes[*].text_frame.paragraphs[*]` |
| Tablas | python-pptx | `shape.has_table → shape.table.rows[*].cells[*]` |
| Notas del presentador | python-pptx | `slide.notes_slide.notes_text_frame.text` |
| Comentarios | lxml sobre XML | Parsea `ppt/comments/comment*.xml` |
| Datos de chart nativo | lxml sobre XML | Parsea `ppt/charts/chart*.xml` para `<c:ser>` |
| Extraer medios | unzip | `unzip deck.pptx 'ppt/media/*' -d /tmp/` |
| Metadatos | python-pptx | `prs.core_properties` |
| Rasterizar slides | soffice + pdftoppm | Ver `scripts/rasterize_slides.py` |
| Convertir `.ppt` legacy | soffice | `soffice --headless --convert-to pptx old.ppt` |

## 14. Cuándo cargar REFERENCE.md

- Heurísticas de detección de título (placeholder vs first-text-frame fallback)
- Herencia de tema (cómo fluyen los estilos de placeholder desde slide → layout → master)
- Detección de tipo de chart (bar / column / line / pie / scatter / radar desde XML)
- Transiciones y animaciones (expuestas pero raramente útiles)
- Custom XML parts (`customXml/item*.xml`, raro pero lleva metadatos)
- Manejo avanzado de ficheros cifrados / firmados
