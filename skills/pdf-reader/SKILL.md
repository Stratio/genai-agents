---
name: pdf-reader
description: "Inspect, analyze, and extract content from PDF files intelligently. Use this skill whenever you need to read what's inside a PDF — extracting text, tables, images, form field values, embedded attachments, or visually understanding page layout. Covers text PDFs, scanned documents, exported slide decks, fillable forms, and data-heavy reports. Always run a quick diagnostic before extraction to pick the right strategy."
argument-hint: "[path/to/file.pdf]"
---

# Skill: PDF Reader

A disciplined approach to getting useful content out of PDF files. Different
PDFs need different tactics — a scanned contract behaves nothing like a
slide export, and neither behaves like a financial report full of tables.
Diagnosis first, extraction second.

## 1. Two modes: quick and deep

This skill supports two ways of working:

**Quick mode — `scripts/quick_extract.py`**
One-shot extraction that returns structured Markdown. Use it when:
- The PDF is "normal" (text-based, not scanned, not exotic)
- You want text + tables without thinking about which library to use
- You're batch-processing many files
- You're feeding the output directly to another agent or LLM

**Deep mode — the workflow below**
Step-by-step diagnosis and extraction. Use it when:
- The PDF is complex, scanned, or misbehaving
- You need to extract figures, attachments, or form fields
- You care about layout, positioning, or vector graphics
- Quick mode failed or returned garbage

Default to quick mode. Fall back to deep mode when quick mode isn't enough.

### Quick mode usage

```bash
# Extract everything
python <skill-root>/scripts/quick_extract.py document.pdf

# Specific pages
python <skill-root>/scripts/quick_extract.py document.pdf --pages 1-5

# Text only, no tables
python <skill-root>/scripts/quick_extract.py document.pdf --no-tables

# Force a specific extractor
python <skill-root>/scripts/quick_extract.py document.pdf --tool pdfminer

# Read from stdin
cat document.pdf | python <skill-root>/scripts/quick_extract.py -

# If no Python extractor is installed, try to install one
python <skill-root>/scripts/quick_extract.py document.pdf --auto-install
```

The script:
- Returns Markdown on stdout (document metadata, per-page sections, tables)
- Returns diagnostics on stderr (which tool ran, warnings)
- Exits 0 on success, 1 on failure
- Auto-detects available tools and falls back through a chain
- Never pollutes stdout — the output is safe to pipe into another tool

The extractor chain tries, in order: **pdfplumber → pdfminer.six → pypdf →
pdftotext**. The first one that produces non-empty output wins.

## 2. Golden rule for deep mode: diagnose before you extract

Never run `pypdf` or `pdfplumber` blindly on an unknown PDF. A scanned PDF
will return empty strings. A PDF with broken font encoding will return
mojibake. A PDF with embedded attachments hides data that text extraction
never sees. A two-second diagnostic step saves ten minutes of debugging
garbage output.

Run this inspection block first:

```bash
# What are we dealing with? Pages, size, producer, creation date
pdfinfo target.pdf

# Is there actually extractable text, or is this a scan?
pdftotext -f 1 -l 2 target.pdf - | head -30

# Are there raster images worth extracting (photos, figures)?
pdfimages -list target.pdf | head -20

# Any embedded files (spreadsheets, data, sub-documents)?
pdfdetach -list target.pdf

# Are fonts embedded? Custom encodings often break text extraction.
pdffonts target.pdf | head -15
```

What each output tells you:

- **`pdfinfo`** — page count tells you the scale of the job. Producer tells
  you the origin (LaTeX, Word, InDesign, a scanner). File size per page
  hints at image content.
- **`pdftotext` sample** — if the first two pages return nothing or just
  whitespace, you have a scanned PDF. If they return readable prose,
  text extraction is viable. If they return gibberish, you probably have
  broken font encoding.
- **`pdfimages -list`** — columns show width, height, color space, and
  encoding. Thumbnails under ~50×50 are usually decoration; real figures
  are larger. Zero images doesn't mean zero figures — charts drawn as
  vector graphics don't appear here.
- **`pdfdetach -list`** — PDFs can embed other files (Excel spreadsheets,
  CSV data, other PDFs). Common in business reports and PDF/A-3.
- **`pdffonts`** — look at the "emb" column. If key fonts aren't embedded
  and use custom or Identity-H encoding, text extraction may produce
  wrong characters. That's your cue to rasterize instead.

## 3. Pick a strategy based on document type

Classify the PDF in your head, then apply the matching workflow.

### Text-heavy documents (reports, articles, books, papers)

Primary tool: `pdfplumber` for layout-aware extraction, or `pdftotext
-layout` from the command line.

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    full_text = []
    for page in pdf.pages:
        full_text.append(page.extract_text())
    text = "\n\n".join(full_text)
```

For multi-column layouts, `pdftotext -layout` often preserves columns
better than `pdfplumber`:

```bash
pdftotext -layout report.pdf report.txt
```

Only rasterize specific pages that contain figures you need to visually
inspect. Rasterizing the whole document is overkill and expensive.

### Scanned documents (no extractable text)

Symptom: `pdftotext` returns empty, or almost empty. Every page is
essentially an image of text.

Workflow: convert pages to images, run OCR.

```python
from pdf2image import convert_from_path
import pytesseract

pages = convert_from_path("scanned.pdf", dpi=300)
text_by_page = []
for i, img in enumerate(pages, 1):
    text = pytesseract.image_to_string(img, lang="eng")  # or "spa", "fra", etc.
    text_by_page.append(f"--- Page {i} ---\n{text}")

full_text = "\n\n".join(text_by_page)
```

DPI matters. 300 is a good default; 400+ for dense small type; 200 for
speed when quality is less critical. For non-English documents specify
`lang=` with the appropriate Tesseract language pack installed.

### Exported slide decks

Symptom: low page count (5–80), each page visually dense, `pdftotext`
returns bullet points without context, layout is lost.

Text extraction alone is rarely enough. Rasterize each slide you care
about and read it as an image.

```bash
# Render specific slides as images at screen-quality resolution
pdftoppm -jpeg -r 150 -f 3 -l 5 deck.pdf /tmp/slide
ls /tmp/slide-*.jpg
```

A note on filenames: `pdftoppm` zero-pads the suffix based on total page
count. A 50-page deck produces `slide-03.jpg`; a 200-page deck produces
`slide-003.jpg`. Don't hardcode the filename — list the directory.

### Fillable forms

PDFs with AcroForm fields (government forms, applications, contracts)
store the user's input as structured data. Extract it programmatically
instead of parsing the visual text.

```python
from pypdf import PdfReader

reader = PdfReader("application.pdf")

# All field types: text inputs, checkboxes, radio buttons, dropdowns
fields = reader.get_fields() or {}
for name, field in fields.items():
    value = field.get("/V", "")
    field_type = field.get("/FT", "")  # /Tx text, /Btn button, /Ch choice
    print(f"{name} ({field_type}): {value!r}")
```

**Warning**: `get_form_text_fields()` only returns text fields. If you
use it on a form with checkboxes or dropdowns, you'll silently miss data.
Always start with `get_fields()`.

For a thorough dump including options and defaults:

```bash
pdftk application.pdf dump_data_fields > fields.txt
```

### Data-heavy documents (tables, charts, dashboards)

Tables — try `pdfplumber` first:

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

If tables come out with merged cells, misaligned columns, or missing
data, `pdfplumber` has tuning knobs (`table_settings` with strategies
like `"lines"`, `"text"`, or explicit vertical/horizontal lines). See
`REFERENCE.md`.

Charts and figures drawn as vector graphics won't come out of
`pdfimages`. Rasterize the page that contains them:

```bash
pdftoppm -png -r 200 -f 4 -l 4 financials.pdf /tmp/chart
```

Then read `/tmp/chart-04.png` (or whatever it's named) as an image.

### Mixed documents

Many real-world PDFs are mixed: narrative text, some tables, a chart or
two, maybe a scanned appendix. Don't try to handle it in one pass.
Break it up:

1. Extract text from pages that have extractable text.
2. Rasterize pages with figures.
3. OCR any scanned sections separately.
4. Pull out attachments if present.
5. Merge findings at the end.

## 4. Token-awareness when consuming content into an LLM

If you're feeding PDF content to Claude or another LLM, cost matters.

| Approach | Approximate tokens per page |
|---|---|
| Plain text extraction | 200–500 |
| Rasterized page at 150 DPI | ~1,600 |
| Rasterized page at 300 DPI | ~2,800 |
| Text + rasterized image both | 2,000–3,300 |

A 100-page PDF rasterized at 150 DPI burns around 160K tokens. Text
extraction of the same document burns 20K–50K. Reserve rasterization for
pages where visual layout genuinely matters: charts, diagrams, form
layouts, complex tables, equations.

When precision matters for a specific page (e.g. a contract with a
signature block, a financial statement), sending both text and image
costs more but gives the LLM maximum context to cross-check.

## 5. Extracting embedded images

```bash
# Quick listing with metadata
pdfimages -list target.pdf

# Extract everything as PNG
pdfimages -png target.pdf /tmp/extracted

# Narrow to specific pages
pdfimages -png -f 3 -l 5 target.pdf /tmp/extracted

# Preserve original format (JPEG stays JPEG, PNG stays PNG)
pdfimages -all target.pdf /tmp/extracted
```

Expect noise: `pdfimages` produces a lot of transparency masks and
decorative elements along with real figures. Filter by file size to
find the substantive ones:

```bash
find /tmp -name "extracted-*.png" -size +10k
```

For images with their page coordinates (useful when you need to know
*where* on the page an image appears), use `pypdfium2`:

```python
import pypdfium2 as pdfium
from pypdfium2 import raw

pdf = pdfium.PdfDocument("target.pdf")
for page_num, page in enumerate(pdf, start=1):
    img_index = 0
    for obj in page.get_objects():
        if obj.type != raw.FPDF_PAGEOBJ_IMAGE:
            continue
        # Bounding box in page coordinates (points)
        left, bottom, right, top = obj.get_bounds()
        # extract() writes the image in its native format (jpg/png/etc.)
        obj.extract(f"/tmp/p{page_num}_i{img_index}_at_{int(left)}_{int(bottom)}")
        img_index += 1
pdf.close()
```

`pypdfium2` is Apache 2.0 / BSD licensed and covers positional image
extraction without the AGPL constraint of PyMuPDF. If you prefer to
work with PIL Images in memory instead of writing to disk, use
`obj.get_bitmap(render=False).to_pil()`.

## 6. Extracting embedded file attachments

PDFs can carry other files inside them — spreadsheets, CSVs, other PDFs.
Very common in regulated reports (PDF/A-3) and business portfolios.

```bash
pdfdetach -list target.pdf
mkdir -p /tmp/attachments
pdfdetach -saveall -o /tmp/attachments/ target.pdf
ls -la /tmp/attachments/
```

**Security note**: attachment filenames come from the PDF and can contain
path traversal sequences like `../../etc/passwd`. When using Python APIs
to extract attachments, always sanitize:

```python
import os
from pypdf import PdfReader

reader = PdfReader("target.pdf")
for raw_name, contents in (reader.attachments or {}).items():
    safe = os.path.basename(raw_name)  # strip any path components
    if not safe:
        continue
    for data in contents:
        with open(f"/tmp/attachments/{safe}", "wb") as f:
            f.write(data)
```

Two attachment mechanisms exist: page-level annotation attachments (the
paperclip icons you see in Acrobat) and document-level embedded files
(EmbeddedFiles name tree). Both `pdfdetach` and pypdf handle common
cases. Rich-media annotations (audio, video, 3D) rarely appear and
require inspecting the page's `/Annots` dictionary directly with
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
            # Inspect the /RichMediaContent dictionary for assets
            content = annot.get("/RichMediaContent", {})
            print(f"Page {page_num}: rich media annotation:", content)
```

Rich-media extraction is genuinely rare in practice — most "media
inside PDF" cases end up as regular embedded attachments that
`pdfdetach` already handles.

## 7. When text extraction is garbled

Symptoms: weird characters, missing letters, everything shifted by one
position, mojibake.

Run `pdffonts target.pdf` and look at:

- **emb column** — is the font actually embedded? If it says "no", the
  PDF is referencing a font by name and relying on the viewer to
  substitute. Extraction will likely fail.
- **enc column** — "Custom" or "Identity-H" without proper CIDToGID
  maps means character codes don't map back to readable Unicode.

When you hit this, stop fighting the text extraction. Rasterize the
page at 300 DPI and OCR it, or send the image to a vision model. The
visual output is the only truthful representation.

## 8. Password-protected PDFs

If the PDF is encrypted and you have the password:

```python
from pypdf import PdfReader

reader = PdfReader("locked.pdf")
if reader.is_encrypted:
    reader.decrypt("the-password-here")

for page in reader.pages:
    print(page.extract_text())
```

If there's an owner password preventing extraction (but no user password
preventing opening), `pypdf` will sometimes let you read without the
password. If not, creating an unlocked copy is a job for `pdf-writer`,
not this skill.

## 9. Quick-reference cheat sheet

| Task | Tool | Command |
|---|---|---|
| Inspect metadata | pdfinfo | `pdfinfo file.pdf` |
| Quick text sample | pdftotext | `pdftotext -f 1 -l 2 file.pdf -` |
| Layout-preserving text | pdftotext | `pdftotext -layout file.pdf out.txt` |
| Layout-aware text in Python | pdfplumber | `page.extract_text()` |
| Tables | pdfplumber | `page.extract_tables()` |
| Rasterize pages | pdftoppm | `pdftoppm -jpeg -r 150 -f N -l N file.pdf prefix` |
| Extract raster images | pdfimages | `pdfimages -png file.pdf prefix` |
| List attachments | pdfdetach | `pdfdetach -list file.pdf` |
| Extract attachments | pdfdetach | `pdfdetach -saveall -o dir/ file.pdf` |
| Font diagnostics | pdffonts | `pdffonts file.pdf` |
| Read form field values | pypdf | `reader.get_fields()` |
| OCR scanned pages | pytesseract + pdf2image | See scanned-documents section |

## 10. When to load REFERENCE.md

- Advanced `pdfplumber` table tuning
- Handling corrupted PDFs and recovery with `qpdf --fix-qdf`
- Batch processing pipelines
- Working with signed / certified PDFs
- Alternative Python libraries (`pypdfium2` for fast rasterization,
  `pdfminer.six` for unusual encodings)

## 11. Installation

This skill expects a standard PDF processing toolkit to be available.
For everyday use, install everything once and forget about it.

### One-shot install (Debian / Ubuntu)

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

### One-shot install (macOS)

```bash
brew install poppler qpdf pdftk-java tesseract tesseract-lang ghostscript

pip install \
    pypdf pdfplumber pdfminer.six pypdfium2 \
    pytesseract pdf2image pillow pandas ocrmypdf
```

### What each dependency provides

| Package | Used by | Purpose |
|---|---|---|
| `poppler-utils` | deep mode, quick mode fallback | `pdfinfo`, `pdftotext`, `pdftoppm`, `pdfimages`, `pdfdetach`, `pdffonts` |
| `qpdf` | `pdf-writer` | structural ops, repair of corrupted PDFs |
| `pdftk` | deep mode (forms inspection) | `dump_data_fields` |
| `tesseract-ocr` + language packs | OCR workflow | extracting text from scans |
| `ghostscript` | deep mode (corrupted PDFs) | last-resort repair / rasterization |
| `pypdf` | quick mode, forms | basic PDF reading, forms |
| `pdfplumber` | quick mode (primary) | layout-aware text + tables |
| `pdfminer.six` | quick mode (fallback) | pure-Python text extraction |
| `pypdfium2` | deep mode (rendering) | fast page rasterization, Apache 2.0 license |
| `pytesseract` + `pdf2image` | OCR workflow | Python wrapper over tesseract |
| `ocrmypdf` | deep mode | scanned → searchable PDF |

### Licensing note

Every package in the default install above is **permissively licensed**
(MIT, BSD, Apache 2.0, MPL, LGPL). None imposes copyleft obligations on
your project.

This skill deliberately does **not** include PyMuPDF (`fitz`). PyMuPDF
is feature-rich but ships under AGPL v3, which is incompatible with
most proprietary or source-available licenses. Everything this skill
documents is achievable with the permissive alternatives above.

### On-demand installation

The quick-mode script can install `pdfminer.six` on the fly when nothing
else is available:

```bash
python3 scripts/quick_extract.py document.pdf --auto-install
```

This is a safety net, not the normal path. For deep-mode workflows, the
skill assumes the packages above are already installed and will suggest
`pip install <pkg>` commands when something specific is missing.



Creation, merging, splitting, rotating, watermarking, encrypting,
filling forms, and OCR-flattening scanned documents into searchable
PDFs all live in the companion `pdf-writer` skill.
