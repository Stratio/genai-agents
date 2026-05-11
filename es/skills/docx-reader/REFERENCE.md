# docx-reader — Referencia

Patrones avanzados para casos donde el modo rápido o las recetas directas del modo profundo no bastan.

## Reconstrucción del árbol de encabezados

Cuando necesites una estructura tipo índice a partir de un documento arbitrario:

```python
from docx import Document

doc = Document("report.docx")

def heading_level(paragraph):
    name = (paragraph.style.name or "").lower()
    for level in range(1, 10):
        if name == f"heading {level}":
            return level
    return None

tree = []
for p in doc.paragraphs:
    level = heading_level(p)
    if level is not None and p.text.strip():
        tree.append((level, p.text.strip()))

# tree es una lista plana; conviértela en anidada recorriendo con una pila.
```

## Comentarios con réplicas resueltas

En `.docx` modernos, los comentarios pueden tener réplicas (en hilos vía `word/commentsExtended.xml`). El `word/comments.xml` base tiene el texto; el extendido tiene la paternidad. Lector mínimo:

```python
import zipfile
from lxml import etree

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
}

with zipfile.ZipFile("document.docx") as z:
    with z.open("word/comments.xml") as f:
        base = etree.parse(f).getroot()
    try:
        with z.open("word/commentsExtended.xml") as f:
            ext = etree.parse(f).getroot()
    except KeyError:
        ext = None

comments = {}
for c in base.findall("w:comment", NS):
    cid = c.get(f"{{{NS['w']}}}id")
    author = c.get(f"{{{NS['w']}}}author")
    text = "".join(t.text or "" for t in c.iter(f"{{{NS['w']}}}t"))
    comments[cid] = {"author": author, "text": text, "parent": None}
```

## Introspección de estilos

Antes de fiarte de la detección de encabezados, lista los estilos realmente definidos:

```python
from docx import Document

doc = Document("document.docx")
for style in doc.styles:
    print(f"{style.type}  {style.name}  builtin={style.builtin}")
```

Un estilo custom "Heading 1 Alt" no es `Heading 1`. Construye una tabla de mapeo para los documentos que ingestes habitualmente.

## Inspección de settings.xml

Defaults de vista / zoom, fuentes por defecto, configuración de rastreado:

```python
import zipfile
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

with zipfile.ZipFile("document.docx") as z:
    with z.open("word/settings.xml") as f:
        root = etree.parse(f).getroot()

track = root.find("w:trackChanges", NS)
print("Rastreado activo al guardar:", track is not None)
```

## Notas al pie y notas finales

```python
import zipfile
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

def read_notes(zpath, part):
    try:
        with zpath.open(part) as f:
            tree = etree.parse(f).getroot()
    except KeyError:
        return []
    out = []
    for n in tree.findall("w:footnote", NS) + tree.findall("w:endnote", NS):
        nid = n.get(f"{{{NS['w']}}}id")
        if nid in ("0", "-1"):  # saltar marcadores separadores
            continue
        text = "".join(t.text or "" for t in n.iter(f"{{{NS['w']}}}t"))
        out.append((nid, text))
    return out

with zipfile.ZipFile("document.docx") as z:
    footnotes = read_notes(z, "word/footnotes.xml")
    endnotes = read_notes(z, "word/endnotes.xml")
```

## Procesamiento por lotes

Para un directorio de ficheros DOCX, lanza la extracción rápida en paralelo:

```bash
ls *.docx | xargs -n1 -P4 -I{} python3 <raíz-skill>/scripts/quick_extract.py {} > {}.md
```

Cada extracción es independiente; mantén el paralelismo en 4–8 trabajadores para evitar que pandoc se sature.

## Manejo de `.doc` binarios en lote

LibreOffice headless convierte un fichero a la vez por proceso, pero admite llamada con comodín:

```bash
soffice --headless --convert-to docx --outdir /tmp/docx_out /ruta/*.doc
```

Lanza una única instancia de LibreOffice y convierte cada coincidencia secuencialmente. Atento a bloqueos de fichero si ya hay otro `soffice` corriendo.

## Extracción de objetos embebidos (Excel, PowerPoint)

DOCX puede embeber objetos OLE. Viven en `word/embeddings/` como `.xlsx`, `.pptx`, `.bin`:

```python
import zipfile
from pathlib import Path

out = Path("/tmp/docx_embeddings")
out.mkdir(exist_ok=True)

with zipfile.ZipFile("document.docx") as z:
    for name in z.namelist():
        if name.startswith("word/embeddings/"):
            (out / Path(name).name).write_bytes(z.read(name))
```

## DOCX corruptos

Si `zipfile.ZipFile` lanza `BadZipFile`, prueba el round-trip de conversión de LibreOffice para normalizar:

```bash
soffice --headless --convert-to docx --outdir /tmp/reparado possiblemente_corrupto.docx
```

LibreOffice repara en silencio pequeños problemas estructurales. Daños mayores (fichero truncado) son irrecuperables.
