# pdf-writer — Advanced Reference

Load this when SKILL.md's scaffold isn't enough: multi-column layouts,
bookmarks, embedded vectors, TOC generation, batch rendering, or
conditional typography.

## Table of contents

1. Multi-column layouts
2. Bookmarks and document outline
3. Tables of contents (auto-generated)
4. Embedding SVG vector graphics
5. Drawing charts directly into PDFs
6. Headers, footers, and running titles
7. Two-sided print layouts (mirrored margins)
8. Batch generation patterns
9. PDF/A compliance and archival output
10. Attaching files inside a PDF
11. Merging while preserving bookmarks

---

## 1. Multi-column layouts

Use `BaseDocTemplate` with multiple `Frame` objects per page:

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

Content flows into `frame_left` first; when it fills, it continues in
`frame_right`, then onto the next page.

### Mixing layouts (cover page + two-column body)

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
    # ... body content
]
```

## 2. Bookmarks and document outline

Bookmarks show up in the sidebar of every PDF viewer. Essential for
long documents.

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

## 3. Tables of contents (auto-generated)

reportlab has a built-in `TableOfContents` that collects entries as
it goes:

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
    # Feed TOC
    doc.notify("TOCEntry", (level, text, doc.page))

# Build requires multiBuild to resolve page numbers
doc.multiBuild(story)
```

Note: `multiBuild` runs two passes — the first collects entries, the
second places them with correct page numbers.

## 4. Embedding SVG vector graphics

SVGs scale losslessly at any size. Install `svglib`:

```python
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF

drawing = svg2rlg("/path/to/logo.svg")
# Scale it
scale = 0.6
drawing.width  *= scale
drawing.height *= scale
drawing.scale(scale, scale)

# Insert in a Platypus story
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

## 5. Drawing charts directly into PDFs

reportlab has native chart primitives. For anything beyond bar/line,
use matplotlib and embed the output as SVG or PNG:

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

For crisp output at any zoom level, save as SVG and embed via `svglib`.

## 6. Headers, footers, and running titles

Use the `onPage` callback of `PageTemplate`. Conditional logic based on
page number goes inside the callback:

```python
def draw_header(canvas, doc):
    canvas.saveState()

    # First page: no header
    if doc.page == 1:
        canvas.restoreState()
        return

    # Odd pages: doc title on left
    # Even pages: chapter on right
    canvas.setFont("Body", 8)
    canvas.setFillColor(MUTED)
    if doc.page % 2 == 1:
        canvas.drawString(MARGIN_X, A4[1] - 12*mm, "Annual Report — 2026")
    else:
        canvas.drawRightString(A4[0] - MARGIN_X, A4[1] - 12*mm,
                               getattr(doc, "current_chapter", ""))

    canvas.restoreState()
```

Update `doc.current_chapter` as you encounter chapter headings.

## 7. Two-sided print layouts (mirrored margins)

For booklets and books, alternate inner/outer margins:

```python
INNER, OUTER = 28 * mm, 18 * mm

def frame_for(page_num):
    if page_num % 2 == 1:  # recto (right-hand page)
        left, right = INNER, OUTER
    else:                   # verso (left-hand page)
        left, right = OUTER, INNER
    return Frame(left, my,
                 page_w - left - right, page_h - 2*my,
                 id=f"f{page_num}")
```

Or define two `PageTemplate` objects, one per parity, and switch with
`NextPageTemplate`.

## 8. Batch generation patterns

Generating hundreds of invoices, certificates, or letters from a dataset:

```python
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import csv

def render_one(record):
    # record is a dict from one CSV row
    out_path = Path(f"/tmp/invoices/INV-{record['id']}.pdf")
    # Build document for this record
    build_invoice(out_path, record)
    return out_path

def build_invoice(out_path, record):
    # your existing builder — parametrized by record
    ...

with open("customers.csv") as f:
    records = list(csv.DictReader(f))

Path("/tmp/invoices").mkdir(exist_ok=True)
with ProcessPoolExecutor(max_workers=8) as ex:
    for path in ex.map(render_one, records):
        print("done:", path)
```

Important: **register fonts inside the worker function**, not in the
main process. TTF registrations don't always survive the fork/spawn
boundary.

## 9. PDF/A compliance and archival output

PDF/A is the ISO standard for long-term archival. Key requirements:
fonts must be embedded, no transparency, no encryption, no external
references, standard color spaces.

reportlab doesn't directly produce PDF/A. The practical workflow:

```bash
# Generate with reportlab normally, then convert
gs -dPDFA=2 -dBATCH -dNOPAUSE -sProcessColorModel=DeviceRGB \
   -sDEVICE=pdfwrite -sPDFACompatibilityPolicy=1 \
   -o output_pdfa.pdf input.pdf
```

Or use a dedicated library like `pikepdf` + manual metadata injection.

## 10. Attaching files inside a PDF

Useful for delivering a polished PDF with its raw data (CSV, Excel)
embedded:

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

Readers will show a paperclip icon; users can extract the attachment
from the document.

## 11. Merging while preserving bookmarks

`PdfWriter.append` preserves outline entries (bookmarks) from each
source:

```python
from pypdf import PdfWriter

out = PdfWriter()
out.append("part_1.pdf", outline_item="Part 1 — Background")
out.append("part_2.pdf", outline_item="Part 2 — Analysis")
out.append("part_3.pdf", outline_item="Part 3 — Conclusions")

with open("/tmp/combined.pdf", "wb") as f:
    out.write(f)
```

Each source's own bookmarks become children of the top-level outline
entry you specify.

## Quick font-pairing cheat sheet

When the document category isn't in the main SKILL.md taxonomy:

| Mood | Display | Body | Mono |
|---|---|---|---|
| Serious / editorial | Instrument Serif | Crimson Pro | IBM Plex Mono |
| Corporate / clean | Instrument Sans (bold) | Work Sans | JetBrains Mono |
| Warm / book-like | Young Serif | Lora | DM Mono |
| Technical / docs | Outfit (bold) | IBM Plex Serif | IBM Plex Mono |
| Quirky / creative | Boldonse | Crimson Pro | Red Hat Mono |
| Brutal / posterish | Big Shoulders | Work Sans | JetBrains Mono |
| Ceremonial | Italiana | Libre Baskerville | — |
| Retro / techy | Tektur | Outfit | JetBrains Mono |

Always embed; never rely on viewer substitution.
