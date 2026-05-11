# pdf-reader — Advanced Reference

Load this file only when the base SKILL.md isn't enough: tricky tables,
corrupted files, batch pipelines, or alternative libraries.

## Table of contents

1. Advanced table extraction with `pdfplumber`
2. Alternative libraries and when to use them
3. Corrupted and non-compliant PDFs
4. Batch processing patterns
5. Signed and certified PDFs
6. Language support for OCR
7. Performance tips

---

## 1. Advanced table extraction with `pdfplumber`

Default `page.extract_tables()` works when tables have visible ruling
lines. When it fails, you usually need to help `pdfplumber` understand
where the table boundaries are.

### Strategy parameter

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

Strategies available:
- `"lines"` — use detected ruling lines (best for classic bordered tables)
- `"lines_strict"` — same but only lines that form rectangles
- `"text"` — infer boundaries from text alignment (best for borderless tables)
- `"explicit"` — you provide the x/y coordinates yourself

### Explicit column boundaries

When `pdfplumber` keeps merging two columns or splitting one, define the
boundaries yourself:

```python
page = pdf.pages[0]
tables = page.extract_tables(table_settings={
    "vertical_strategy": "explicit",
    "explicit_vertical_lines": [50, 180, 310, 440, 560],  # page x-coordinates
    "horizontal_strategy": "text",
})
```

Find the right x-coordinates by visualizing:

```python
im = page.to_image(resolution=150)
im.debug_tablefinder().save("/tmp/debug.png")
```

Open the image and inspect where `pdfplumber` thinks the lines are.

### Tables that span multiple pages

Manually stitch them:

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

## 2. Alternative libraries and when to use them

### `pypdfium2` — Google's PDFium bindings

Fast rendering and generally the best engine for rasterization quality.
Good when `pdftoppm` isn't available or when you want to stay in Python.

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("target.pdf")
page = pdf[0]
bitmap = page.render(scale=2.0)  # 2x = ~144 DPI; 4x = ~288 DPI
pil_image = bitmap.to_pil()
pil_image.save("/tmp/page-01.png")
pdf.close()
```

### `pypdfium2` — advanced usage (text + positions)

For word-level coordinates without needing PyMuPDF, use `pypdfium2`'s
text page API:

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

Key concepts:
- **Rects** are logical text chunks (typically words or lines).
- **Charbox** gives per-character bounding boxes.
- **Search** returns `(char_index, char_count)` tuples — convert to
  bounding boxes via `get_charbox` on the first and last character.

This covers most real use cases for "which text is where on the page"
without pulling in AGPL-licensed libraries.

### `pdfminer.six` — the oldest, still useful for character-level work

```python
from pdfminer.high_level import extract_text
text = extract_text("target.pdf")
```

Slower than `pdfplumber` but handles some edge cases (unusual encodings)
better. For character-level layout details:

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

### Decision matrix

| Need | Best choice |
|---|---|
| Text + simple tables | pdfplumber |
| Fast rendering | pypdfium2 |
| Text with word/char positions | pypdfium2 (text page API) or pdfplumber |
| Maximum encoding tolerance | pdfminer.six |
| Per-character font info | pdfminer.six |
| Just a text dump | pdftotext CLI |

All options above are permissively licensed. If you ever need
annotation-iteration or rich-media features that only PyMuPDF provides,
verify your project can accept AGPL v3 before installing it.

---

## 3. Corrupted and non-compliant PDFs

Symptoms: "EOF marker not found", "xref table not found", "invalid
object", parsers crash or hang.

### Repair with `qpdf`

`qpdf` can rebuild the cross-reference table and rewrite the file in
a clean format:

```bash
qpdf --qdf --object-streams=disable broken.pdf fixed.pdf
# Then retry your extraction against fixed.pdf
```

### Repair with Ghostscript (heavier but thorough)

```bash
gs -o repaired.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress broken.pdf
```

This actually re-parses and re-renders, so formatting may shift slightly
but the file becomes readable.

### Partial recovery when even repair fails

Rasterize the entire document and OCR. You lose structure but recover
content:

```python
from pdf2image import convert_from_path
import pytesseract

pages = convert_from_path("damaged.pdf", dpi=300, strict=False)
text = "\n\n".join(pytesseract.image_to_string(p) for p in pages)
```

---

## 4. Batch processing patterns

### Parallel extraction of many PDFs

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

Processes, not threads — pdfplumber holds the GIL during parsing.

### Streaming mode for very large PDFs

Don't hold all pages in memory:

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

## 5. Signed and certified PDFs

Signed PDFs embed cryptographic signatures in an Adobe PKCS#7 blob.

### Detect signatures

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

### Inspect signature details with `pyhanko`

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

Verifying signatures against a trust anchor is a full topic — consult
`pyhanko`'s documentation. For simple reading, just detecting that a
document is signed and noting the signer is usually enough.

---

## 6. Language support for OCR

Tesseract uses three-letter ISO codes:

| Language | Code | Package (Debian/Ubuntu) |
|---|---|---|
| English | `eng` | default |
| Spanish | `spa` | `tesseract-ocr-spa` |
| French | `fra` | `tesseract-ocr-fra` |
| German | `deu` | `tesseract-ocr-deu` |
| Italian | `ita` | `tesseract-ocr-ita` |
| Portuguese | `por` | `tesseract-ocr-por` |
| Catalan | `cat` | `tesseract-ocr-cat` |
| Arabic | `ara` | `tesseract-ocr-ara` |
| Chinese simplified | `chi_sim` | `tesseract-ocr-chi-sim` |
| Japanese | `jpn` | `tesseract-ocr-jpn` |

Multiple languages at once (useful for multilingual contracts):

```python
text = pytesseract.image_to_string(image, lang="spa+eng")
```

List installed languages:

```bash
tesseract --list-langs
```

Install missing ones:

```bash
sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra
```

---

## 7. Performance tips

### Text extraction is I/O bound at scale

For thousands of PDFs, bottleneck is disk reads, not CPU. SSDs matter
more than core count.

### Rasterization is CPU-bound

`pdftoppm` and `pypdfium2` both scale well with cores. Use
`ProcessPoolExecutor` across files, not pages within a file.

### Cache aggressively

Text extraction is deterministic. If you're iterating on analysis
logic, cache extracted text to disk once and load from cache:

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

### Avoid double work

If your pipeline both extracts text and rasterizes pages, open the PDF
once and do both in a single pass with `pypdfium2`:

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

For an even simpler approach (two passes but no extra dependencies),
use `pdfplumber` for text and `pdftoppm` for images. The single-pass
version shown above is only worth it at high volumes.
