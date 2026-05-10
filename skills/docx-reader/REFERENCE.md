# docx-reader — Reference

Advanced patterns for cases where quick mode or the straightforward deep-mode recipes are not enough.

## Heading tree reconstruction

When you need a table-of-contents-like structure from an arbitrary document:

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

# tree is a flat list; turn it into nested structure by walking with a stack
```

## Comments with resolved replies

In modern `.docx`, comments can have replies (threaded via `word/commentsExtended.xml`). The base `word/comments.xml` has the text; the extended file has the parenthood. Minimal reader:

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

if ext is not None:
    # commentEx elements bind replies to their parent via paraIdParent
    for ce in ext.findall("w15:commentEx", NS):
        pid = ce.get(f"{{{NS['w15']}}}paraId")
        parent = ce.get(f"{{{NS['w15']}}}paraIdParent")
        # Map paraIds back to comment ids via a scan; omitted here for brevity.
```

## Styles introspection

Before trusting heading detection, list what styles are actually defined:

```python
from docx import Document

doc = Document("document.docx")
for style in doc.styles:
    print(f"{style.type}  {style.name}  builtin={style.builtin}")
```

Custom "Heading 1 Alt" style is not `Heading 1`. Build a mapping table for the documents you commonly ingest.

## Inspecting settings.xml

View / zoom defaults, default fonts, tracking settings:

```python
import zipfile
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

with zipfile.ZipFile("document.docx") as z:
    with z.open("word/settings.xml") as f:
        root = etree.parse(f).getroot()

track = root.find("w:trackChanges", NS)
print("Track-changes enabled at save time:", track is not None)
```

## Finding footnotes and endnotes

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
        if nid in ("0", "-1"):  # skip separator placeholders
            continue
        text = "".join(t.text or "" for t in n.iter(f"{{{NS['w']}}}t"))
        out.append((nid, text))
    return out

with zipfile.ZipFile("document.docx") as z:
    footnotes = read_notes(z, "word/footnotes.xml")
    endnotes = read_notes(z, "word/endnotes.xml")
```

## Batch processing

For a directory of DOCX files, run quick extraction in parallel:

```bash
ls *.docx | xargs -n1 -P4 -I{} python3 <skill-root>/scripts/quick_extract.py {} > {}.md
```

Each file's extraction is independent; keep parallelism at 4–8 workers to avoid pandoc thrashing.

## Handling `.doc` binaries in bulk

LibreOffice headless converts one file at a time per process, but supports a wildcard call:

```bash
soffice --headless --convert-to docx --outdir /tmp/docx_out /path/*.doc
```

This launches a single LibreOffice instance and converts every match in sequence. Watch for file lock issues if another soffice process is already running.

## Extracting embedded objects (Excel, PowerPoint)

DOCX can embed `ole` objects. They live under `word/embeddings/` as `.xlsx`, `.pptx`, `.bin`:

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

## Dealing with corrupted DOCX

If `zipfile.ZipFile` raises `BadZipFile`, try the LibreOffice convert round-trip to normalise:

```bash
soffice --headless --convert-to docx --outdir /tmp/repaired possibly_corrupt.docx
```

LibreOffice will silently repair minor structural issues. Major damage (truncated file) is unrecoverable.
