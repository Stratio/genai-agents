---
name: pdf-writer
description: "Create, manipulate, and produce beautiful PDF files. Use this skill whenever the user wants to generate a new PDF (reports, invoices, certificates, newsletters, booklets, receipts, letters), or transform existing PDFs (merge, split, rotate, watermark, encrypt, flatten, add pages). This skill takes design seriously — every PDF it produces has intentional typography, color, and layout, not the generic defaults. For filling interactive form fields in existing PDFs, load FORMS.md."
argument-hint: "[document type or description]"
---

# Skill: PDF Writer

This skill produces PDFs that look designed, not generated. Most automated
PDF output is visually dead: Helvetica body, black on white, 1-inch margins
everywhere, a blue heading if you're lucky. That's the baseline this skill
actively resists.

Before writing a single line of code, commit to a design direction. The
code serves the design, not the other way around.

## 1. Design-first workflow

Every PDF generation task, regardless of size, follows five steps:

1. **Classify the document** — what category is it? (See the taxonomy
   below.) This governs everything downstream.
2. **Pick a visual tone** — editorial, technical-minimal, corporate-formal,
   warm-magazine, brutalist, playful, luxury-refined. Pick one and execute
   it confidently. A timid "a bit of everything" PDF is the worst outcome.
3. **Select a type pairing** — one display face for titles and headings,
   one body face for prose. Two typefaces is almost always enough; three
   is the maximum.
4. **Define a palette** — one dominant accent color, one deep neutral for
   text (rarely pure black), one pale neutral for backgrounds or rules.
   Use colors with real saturation, not washed-out pastels by default.
5. **Set the grid** — margins, column count, baseline spacing. Generous
   margins communicate confidence; cramped margins look like a Word doc.

Only then open reportlab.

### Document taxonomy and starting points

| Category | Typical tone | Page size | Suggested pairing |
|---|---|---|---|
| Analytical report | Editorial-serious | A4 / Letter | Crimson Pro (body) + Instrument Sans (display) |
| Financial statement | Technical-minimal | A4 / Letter | IBM Plex Serif (body) + IBM Plex Mono (data) |
| Invoice / receipt | Clean-utilitarian | A4 / Letter | Instrument Sans (everything) + JetBrains Mono (figures) |
| Newsletter | Warm-magazine | Letter | Lora (body) + Big Shoulders (display) |
| Contract / legal | Restrained-precise | A4 / Letter | Libre Baskerville (body) + Instrument Sans (captions) |
| Booklet / zine | Editorial-playful | A5 | Crimson Pro (body) + Italiana or Erica One (display) |

These are starting points, not mandates. Break them when the brief calls
for it. The point is **never default to reportlab's built-in Helvetica**.

### When this skill is not the right fit

This skill produces multi-page typographic documents where prose, tables
or structured data carry the meaning. Some briefs look similar but belong
to a different tool:

- **Single-page artifacts where composition dominates** — posters,
  certificates, marketing one-pagers, infographics. In those pieces,
  roughly seventy per cent or more of the surface is visual composition
  rather than prose or data. Typography becomes a visual element. A
  different skill handles that medium; see
  `skills-guides/visual-craftsmanship.md` for the selection criterion.
- **Interactive web interfaces** — components, pages, dashboards that live
  in a browser. PDF is static; those briefs call for HTML/CSS.

For a report that needs a designed cover, produce the cover with the
dedicated visual-artifact skill, assemble the multi-page body here, and
merge the two with `pypdf` as a final step. Keep the cover's last-page
margins consistent with the body's first-page margins for a clean seam.

## 2. Registering custom fonts (do this first)

reportlab ships with Type 1 built-ins (Helvetica, Times, Courier).
Those produce ugly PDFs. This skill bundles a curated set of OFL fonts
in the `fonts/` directory — register them at the top of every script.

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
    # ... register the families you'll actually use

    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    registerFontFamily(
        "CrimsonPro",
        normal="CrimsonPro",
        bold="CrimsonPro-Bold",
        italic="CrimsonPro-It",
    )

register_fonts()
```

Only register what you'll use — each registration embeds the font in the
output PDF and adds roughly 80–150 KB to file size.

## 3. Theme application

Design tokens (colors, typography, sizes) do not live in this skill —
they come from the theme chosen for the PDF.

- If a centralized theming skill is available (brand-kit-style),
  run its workflow BEFORE authoring; it returns a token set that maps
  onto the `HexColor` tokens below.
- Otherwise, improvise tokens coherent with the deliverable following
  the tonal palette roles in `skills-guides/visual-craftsmanship.md`.

### Print-specific sensibilities

Themes are written to serve multiple media. If the chosen theme
declares a `## Print variant` block, use it verbatim — the author
already tuned paper-vs-screen. Otherwise adapt when mapping screen
tokens to the PDF:

- `PAPER` should not be pure `#FFFFFF` — prefer a slightly warm
  off-white (bone, paper, cream).
- `INK` should not be pure `#000000` — a warm near-black reads kinder.
- `RULE` thinner and warmer than a web theme would use.

The template below uses placeholders — fill them from the theme
(adjusted for print per the notes above). See §2 for font registration.

## 4. A proper starting template

Instead of reaching for reportlab defaults, use this as a scaffold and
adapt:

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
# The theme names the families; match each family to a bundled TTF.
FONTS = Path(__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Body",        FONTS / "<body-regular>.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold",   FONTS / "<body-bold>.ttf"))
pdfmetrics.registerFont(TTFont("Display",     FONTS / "<display-bold>.ttf"))
pdfmetrics.registerFont(TTFont("Mono",        FONTS / "<mono-regular>.ttf"))

# === DESIGN TOKENS ===
# Fill from the chosen theme (see §3). Do not hard-code values here.
INK    = HexColor("<hex>")   # body text (rarely pure black)
ACCENT = HexColor("<hex>")   # accent color, CTAs, highlights
MUTED  = HexColor("<hex>")   # captions, metadata
RULE   = HexColor("<hex>")   # hairlines, subtle dividers
PAPER  = HexColor("<hex>")   # page background (often maps to bg or bg_alt)

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
    """Runs on every page — use for header, footer, page number, rules."""
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
    # For "Page X of Y" totals, see REFERENCE.md §7 (NumberedCanvas).
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
    doc._pdfVersion = (1, 4)  # reportlab defaults to 1.3; bump so alpha/ExtGState render
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

This scaffold already gives you:
- Custom typography (no Helvetica)
- Intentional color palette with an accent and muted neutrals
- Generous margins that breathe
- Chrome that draws a rule and page number on every page
- Metadata (title, author) for proper PDF properties

Adapt the scaffold; don't fight it.

## 5. Tables that don't look like Excel screenshots

reportlab's default tables are hideous. A designed table needs:

- No vertical grid lines (modern tables use horizontal rules only)
- Tight row padding, not the default cavernous spacing
- Right-aligned numerics, left-aligned strings
- A subtly shaded or bold header row
- Mono font for figures (JetBrainsMono, IBMPlexMono, DMMono)

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

## 6. Common gotchas with reportlab

### Unicode subscripts and superscripts

Never paste characters like ₂ or ⁵ directly into reportlab output. The
built-in Type 1 fonts don't contain those glyphs and you'll get black
rectangles in the PDF. Use the `<sub>` and `<super>` tags inside
Paragraph objects:

```python
Paragraph("Water is H<sub>2</sub>O, and E = mc<super>2</super>", body)
```

If you use a custom TTF that does include those glyphs (most modern
fonts do), direct Unicode works — but it's safer to stick with tags.

### Emojis and non-Latin scripts

Built-in fonts cover Latin only. For any non-ASCII text, register a
font that actually contains the glyphs you need. For emoji, use a font
like Noto Color Emoji — but be aware reportlab's color emoji support
is limited.

### Pixelated images

If you pass a small raster image to `Image()` without specifying size,
reportlab draws it at its native pixel dimensions. For high-quality
print output, size your source images at 300 DPI for the target print
size. Vector alternatives (SVG via `svglib`) scale cleanly.

### Very long tables

`Table` doesn't split across pages by default. Use `LongTable` for
tables that may exceed one page:

```python
from reportlab.platypus import LongTable
tbl = LongTable(data, colWidths=[...], repeatRows=1)
```

`repeatRows=1` keeps the header row at the top of every page.

## 7. Merging, splitting, and rotating PDFs

For structural operations, `pypdf` is the tool. Don't reach for
reportlab — that's for creating content, not rearranging it.

### Merge

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

### Split (one file per page)

```python
from pypdf import PdfReader, PdfWriter

src = PdfReader("/tmp/merged.pdf")
for i, page in enumerate(src.pages, 1):
    out = PdfWriter()
    out.add_page(page)
    with open(f"/tmp/page_{i:03d}.pdf", "wb") as f:
        out.write(f)
```

### Extract a page range

```python
src = PdfReader("/tmp/merged.pdf")
out = PdfWriter()
for page in src.pages[4:9]:  # pages 5–9 (0-indexed)
    out.add_page(page)
with open("/tmp/section.pdf", "wb") as f:
    out.write(f)
```

### Rotate

```python
src = PdfReader("/tmp/scanned.pdf")
out = PdfWriter()
for page in src.pages:
    page.rotate(90)  # 90, 180, or 270
    out.add_page(page)
with open("/tmp/rotated.pdf", "wb") as f:
    out.write(f)
```

### Command-line equivalents with `qpdf`

When you're in a shell and don't need Python:

```bash
# Merge
qpdf --empty --pages cover.pdf body.pdf appendix.pdf -- merged.pdf

# Extract pages 5–9
qpdf input.pdf --pages . 5-9 -- section.pdf

# Rotate page 1 by 90°
qpdf input.pdf --rotate=+90:1 rotated.pdf
```

## 8. Watermarks

A watermark is a PDF drawn on top of another PDF, page by page. Easiest
approach: create the watermark with reportlab, then merge.

```python
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from pypdf import PdfReader, PdfWriter

# 1. Generate watermark
c = rl_canvas.Canvas("/tmp/watermark.pdf", pagesize=A4)
c.saveState()
c.translate(A4[0] / 2, A4[1] / 2)
c.rotate(35)
c.setFont("Display", 84)
c.setFillColor(Color(0.85, 0.15, 0.15, alpha=0.15))  # translucent red
c.drawCentredString(0, 0, "CONFIDENTIAL")
c.restoreState()
c.save()

# 2. Apply over source
watermark = PdfReader("/tmp/watermark.pdf").pages[0]
src = PdfReader("/tmp/report.pdf")
out = PdfWriter()
for page in src.pages:
    page.merge_page(watermark)
    out.add_page(page)

with open("/tmp/report_watermarked.pdf", "wb") as f:
    out.write(f)
```

For a visible-but-less-distracting watermark, lower the alpha to 0.06–0.10.

## 9. Encryption and permissions

```python
from pypdf import PdfReader, PdfWriter

src = PdfReader("/tmp/report.pdf")
out = PdfWriter()
for page in src.pages:
    out.add_page(page)

out.encrypt(
    user_password="readonly",    # required to open
    owner_password="fullaccess", # required to print / copy / modify
    use_128bit=True,
)

with open("/tmp/report_encrypted.pdf", "wb") as f:
    out.write(f)
```

Note: PDF encryption is not a security boundary. Anyone can remove it
with the right tool. It's a polite barrier, not a vault.

## 10. Converting scanned PDFs to searchable PDFs

Use OCRmyPDF when available — it preserves the original scan and adds
an invisible text layer:

```bash
ocrmypdf --language spa+eng scanned.pdf scanned_searchable.pdf
```

Python equivalent by hand: rasterize + OCR + rebuild is possible but
fiddly. OCRmyPDF handles all the edge cases.

## 11. Post-build validation

After building, always verify the result. Two snippets in
`REFERENCE.md`:

- **Structural validation** (§Structural validation): reopen the
  saved PDF and emit a manifest — pages, extracted text length,
  images, tables, outline entries, metadata. Catches corruption,
  pages that render blank, or a missing TOC *before* the file is
  delivered. Runs in ~100–300 ms (longer on big PDFs); do it on
  every build.
- **Visual validation** (§Visual validation pipeline): rasterize
  per-page PNGs with `pdftoppm`. Inspect each PNG for overflow,
  cramped spacing, broken figures, font substitution. Regenerate and
  re-validate; 2–3 iterations is normal.

Structural validation only needs `pypdf` (and optionally `pdfplumber`
for image / table counts). Visual validation requires `poppler-utils`
for `pdftoppm`.

## 12. When to load additional files

- **`FORMS.md`** — filling interactive AcroForm fields in existing PDFs
- **`REFERENCE.md`** — advanced reportlab patterns, SVG embedding,
  TOC generation, bookmarks, page numbering, batch rendering
- **`fonts/`** — the TTF files themselves, with OFL license notices

## 13. Bundled fonts

The `fonts/` directory ships with TTF files under the SIL Open Font License. Register them directly from that directory when you build a PDF — no system-wide install needed. See `fonts/README.md` for the complete list, available weights and licensing notes.



Extracting text, reading tables, rasterizing pages for inspection, OCR
of existing scans, pulling out attachments, and font diagnostics all
live in the companion `pdf-reader` skill.
