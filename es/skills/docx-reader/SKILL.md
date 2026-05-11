---
name: docx-reader
description: "Inspecciona, analiza y extrae contenido de documentos Word (.docx y .doc heredado) de forma inteligente. Usa esta skill siempre que necesites leer lo que hay dentro de un documento Word: extraer prosa, tablas, imágenes, metadatos, comentarios o cambios rastreados. Cubre documentos dominados por texto, informes con muchas tablas, documentos con imágenes inline y ficheros .doc binarios heredados. Ejecuta siempre un diagnóstico rápido antes de la extracción para elegir la estrategia adecuada."
argument-hint: "[ruta/al/fichero.docx]"
---

# Skill: DOCX Reader

Un enfoque disciplinado para sacar contenido útil de documentos Word. Cada fichero pide tácticas distintas: un informe limpio en prosa no se comporta como un documento muy revisado lleno de cambios rastreados, y ninguno se parece a un `.doc` heredado exportado desde Office 2003. Diagnostica primero, extrae después.

## 1. Dos modos: rápido y profundo

Dos formas de trabajar:

**Modo rápido — `scripts/quick_extract.py`**
Extracción de un solo paso que devuelve Markdown estructurado. Úsalo cuando:
- El documento es "normal" (dominado por prosa, sin mucho marcado)
- Quieres texto + tablas sin pensar qué librería usar
- Estás procesando muchos ficheros en lote
- Vas a alimentar la salida directamente a otro agente o LLM

**Modo profundo — el flujo de abajo**
Diagnóstico y extracción paso a paso. Úsalo cuando:
- El documento tiene cambios rastreados o comentarios que te importan
- Necesitas extraer imágenes o medios embebidos
- El modo rápido falló, devolvió basura o se saltó una región
- El fichero es un `.doc` binario heredado (necesita conversión primero)

Por defecto, modo rápido. Cae al modo profundo cuando el rápido no basta.

### Uso del modo rápido

```bash
# Extraer todo
python3 <raíz-skill>/scripts/quick_extract.py document.docx

# Dejar fuera las tablas y quedarse solo con prosa
python3 <raíz-skill>/scripts/quick_extract.py document.docx --no-tables

# Forzar un extractor concreto
python3 <raíz-skill>/scripts/quick_extract.py document.docx --tool pandoc

# Leer de stdin
cat document.docx | python3 <raíz-skill>/scripts/quick_extract.py -
```

El script:
- Devuelve Markdown por stdout (título, metadatos, prosa, tablas)
- Devuelve diagnósticos por stderr (qué herramienta se ejecutó, avisos)
- Sale con 0 si tiene éxito, 1 en fallo
- Autodetecta herramientas disponibles y cae en cadena
- Nunca contamina stdout: la salida se puede pipar con seguridad a otra herramienta

La cadena de extracción prueba, en orden: **pandoc → python-docx → recorrido XML crudo sobre zipfile**. La primera que produzca salida no vacía gana.

## 2. Regla de oro en modo profundo: diagnostica antes de extraer

Nunca ejecutes `python-docx` a ciegas sobre un documento desconocido. Un documento con cambios rastreados puede esconder párrafos que no ves. Uno generado por una herramienta vieja puede tener estilos rotos. Un `.doc` con extensión `.docx` fallará en `zipfile.ZipFile`. Un diagnóstico de dos segundos ahorra mucha depuración de basura.

Ejecuta este bloque de inspección primero:

```bash
# ¿Es realmente un .docx? La firma file(1) lo dice en una línea.
file target.docx

# Para un .docx, lista el contenido del ZIP. ¿Qué partes hay dentro?
unzip -l target.docx

# Muestra textual rápida: ¿pandoc lo parsea?
pandoc --from docx --to plain target.docx 2>/dev/null | head -30

# Metadatos core (título, autor, fechas, revisiones)
unzip -p target.docx docProps/core.xml | head -20

# ¿Hay cambios rastreados? La presencia de <w:ins> o <w:del> es la pista.
unzip -p target.docx word/document.xml | grep -cE '<w:(ins|del)\b' || true
```

Qué te dice cada salida:

- **`file`** — si reporta `Microsoft Word 2007+`, es un `.docx` (ZIP). Si reporta `Composite Document File V2 Document`, es un `.doc` binario heredado y debes convertirlo primero.
- **`unzip -l`** — el inventario de partes es tu mapa. Partes clave: `word/document.xml` (cuerpo principal), `word/comments.xml` (comentarios — normalmente ausente cuando no hay), `word/footnotes.xml`, `word/endnotes.xml`, `word/media/` (imágenes embebidas), `word/settings.xml`, `word/styles.xml`, `docProps/core.xml` (metadatos).
- **`pandoc … --to plain`** — si produce prosa legible, puedes confiar en el camino pandoc del modo rápido. Si da error o basura, cae a `python-docx`.
- **`docProps/core.xml`** — autor, creación/modificación, número de revisiones. Útil cuando el usuario pregunta "¿quién escribió esto?" y "¿cuántas rondas llevó?".
- **Conteo de cambios rastreados** — si es mayor que cero, una extracción de texto plano esconderá el "antes" o el "después"; decide cuál quieres y extráelo explícitamente.

## 3. Elige la estrategia según lo que contenga el documento

Clasifica mentalmente y aplica el flujo adecuado.

### Documentos dominados por prosa (cartas, memos, políticas, contratos, notas)

Herramienta principal: `pandoc`. Preserva listas, encabezados, notas al pie y ambos lados de cambios rastreados con un solo flag.

```bash
# Extracción limpia (acepta todos los cambios rastreados)
pandoc --from docx --to markdown document.docx --output document.md

# Muestra ambos lados de los cambios rastreados en línea
pandoc --from docx --to markdown --track-changes=all document.docx
```

Si `pandoc` no está disponible, usa `python-docx`:

```python
from docx import Document

doc = Document("document.docx")
paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
full_text = "\n\n".join(paragraphs)
```

### Documentos con cambios rastreados

Síntoma: el conteo `<w:ins>` / `<w:del>` del bloque de diagnóstico es distinto de cero.

`pandoc --track-changes=<modo>` da tres lentes:
- `accept` — conserva inserciones, elimina borrados (lo que obtendrías aceptando cada revisión)
- `reject` — elimina inserciones, conserva borrados (estado "antes")
- `all` — conserva ambos, anotados en línea

Elige explícitamente según lo que pidió el usuario. No asumas.

### Documentos con comentarios

Síntoma: `word/comments.xml` aparece en el listado de `unzip -l`.

`pandoc` preserva comentarios en markdown extendido. Para extracción estructurada (autor, anclaje, texto), lee el XML directamente:

```python
import zipfile
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

with zipfile.ZipFile("document.docx") as z:
    with z.open("word/comments.xml") as f:
        tree = etree.parse(f)

for c in tree.getroot().findall("w:comment", NS):
    author = c.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author")
    text = "".join(t.text or "" for t in c.iter(f"{{{NS['w']}}}t"))
    print(f"{author}: {text}")
```

### Documentos con muchas tablas (informes con datos, facturas, extractos)

`python-docx` da acceso a nivel de celda:

```python
from docx import Document

doc = Document("report.docx")
for ix, table in enumerate(doc.tables, 1):
    rows = []
    for row in table.rows:
        rows.append([cell.text.strip() for cell in row.cells])
    # rows[0] suele ser la fila de cabecera
    print(f"Tabla {ix}: {len(rows)-1} filas de datos")
```

Advertencia: las celdas fusionadas aparecen como el mismo objeto de celda en cada posición fusionada. Si estás reconstruyendo un DataFrame, deduplica por `id(cell)` por fila antes de tratar el valor como distinto.

### Documentos con imágenes embebidas

Las imágenes viven dentro del ZIP en `word/media/`. Extráelas directamente, sin librería:

```python
import zipfile
from pathlib import Path

out_dir = Path("/tmp/docx_media")
out_dir.mkdir(exist_ok=True)

with zipfile.ZipFile("document.docx") as z:
    for name in z.namelist():
        if name.startswith("word/media/"):
            data = z.read(name)
            (out_dir / Path(name).name).write_bytes(data)
```

Si además quieres posición y caption, recorre `document.xml` buscando elementos `<w:drawing>` y sus párrafos `<w:p>` vecinos.

### Ficheros `.doc` binarios heredados

Síntoma: `file` reporta `Composite Document File V2 Document`, o `zipfile.ZipFile` lanza `BadZipFile`.

Convierte con LibreOffice headless y trata el resultado como cualquier `.docx`:

```bash
soffice --headless --convert-to docx --outdir /tmp/docx_in target.doc
# /tmp/docx_in/target.docx ya es un .docx moderno
```

Sin LibreOffice, el `.doc` no es legible con librerías Python de la línea base. Instala `libreoffice` / `libreoffice-writer` — ya está en la imagen del sandbox.

### Documentos mixtos

Los ficheros reales suelen mezclar todo: prosa con tablas intercaladas, imágenes, comentarios, quizá un cambio rastreado en la página tres. No intentes extraer en un solo paso:

1. Extrae la prosa con `pandoc` (decide primero el modo de cambios rastreados).
2. Extrae las tablas con `python-docx` en un segundo paso.
3. Saca imágenes de `word/media/` con `zipfile` si las pidió el usuario.
4. Reporta los comentarios por separado: son metadatos, no cuerpo.
5. Une los hallazgos al final como un informe estructurado.

## 4. Conciencia de tokens al alimentar un LLM

Un .docx de 80 páginas de prosa produce aproximadamente 25.000 tokens de markdown. Si solo necesitas tres párrafos, localízalos primero y extrae solo esos:

```python
from docx import Document

doc = Document("long_doc.docx")
target_heading = "Política de retención"
capturing = False
collected = []
for p in doc.paragraphs:
    style = (p.style.name or "").lower()
    if "heading" in style:
        capturing = (p.text.strip() == target_heading)
    elif capturing:
        collected.append(p.text)
```

Coste aproximado en tokens:
- Extracción solo de prosa: ~200 tokens por página
- Prosa + tablas (como markdown): ~350–500 tokens por página
- Imágenes embebidas: cero tokens salvo que el agente las lea multimodalmente

## 5. Metadatos

`docProps/core.xml` y `docProps/app.xml` llevan los metadatos interesantes:

```python
import zipfile
from lxml import etree

NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}

with zipfile.ZipFile("document.docx") as z:
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

## 6. Limpieza de la salida extraída

La extracción cruda con `python-docx` suele necesitar un pequeño pase:
- Colapsar rachas de líneas en blanco a máximo dos
- Retirar caracteres de ancho cero (`\u200b`, `\ufeff`) que `pandoc` elimina pero `python-docx` preserva
- Normalizar comillas tipográficas a rectas si el consumidor downstream espera ASCII (solo cuando se pide explícitamente)

## 7. Cuándo cargar `REFERENCE.md`

`REFERENCE.md` cubre patrones avanzados: reconstrucción del árbol de encabezados, introspección de estilos, comentarios con réplicas resueltas, construcción de un índice desde los encabezados, inspección de `settings.xml` por defaults de vista/zoom, y recetas de procesamiento por lotes.

## 8. Resumen de dependencias

Python: `python-docx`, `lxml` (ya en la línea base).

Sistema: `pandoc` (recomendado), `libreoffice` / `libreoffice-writer` (para conversión de `.doc`).

Sin `pandoc`, la skill cae automáticamente a `python-docx`. Sin `libreoffice`, la skill no puede abrir `.doc` binarios heredados.
