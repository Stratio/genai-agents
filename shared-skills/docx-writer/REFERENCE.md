# docx-writer — REFERENCE

Copy-paste snippets for the document blocks and operations that
`SKILL.md` references but does not spell out inline. Load this when
you're about to build something beyond a basic heading+paragraph
document.

All snippets assume the `DESIGN` dict and `hex_to_rgb` helper from
the scaffold in `SKILL.md` §3.

---

## Palette reference

Six starting palettes aligned with the document taxonomy in §1. Copy
one verbatim into `DESIGN` or use it as a seed and tweak.

```python
PALETTES = {
    "editorial-serious": {
        "primary": "#0a2540", "ink": "#1f2937", "muted": "#6b7280",
        "rule":    "#d1d5db", "bg_alt": "#f3f4f6",
        "display": "Instrument Serif", "body": "Crimson Pro",
    },
    "corporate-formal": {
        "primary": "#1a365d", "ink": "#1f2937", "muted": "#6b7280",
        "rule":    "#e5e7eb", "bg_alt": "#f8fafc",
        "display": "Calibri",  "body": "Calibri",
    },
    "technical-minimal": {
        "primary": "#0369a1", "ink": "#111827", "muted": "#4b5563",
        "rule":    "#e5e7eb", "bg_alt": "#f9fafb",
        "display": "IBM Plex Sans", "body": "IBM Plex Sans",
    },
    "warm-magazine": {
        "primary": "#8a3324", "ink": "#1c1917", "muted": "#78716c",
        "rule":    "#e7e5e4", "bg_alt": "#fafaf9",
        "display": "Big Shoulders Display", "body": "Lora",
    },
    "restrained-legal": {
        "primary": "#1e1b4b", "ink": "#1f2937", "muted": "#6b7280",
        "rule":    "#d1d5db", "bg_alt": "#f9fafb",
        "display": "Libre Baskerville", "body": "Libre Baskerville",
    },
    "academic-sober": {
        "primary": "#312e81", "ink": "#1f2937", "muted": "#6b7280",
        "rule":    "#d4d4d8", "bg_alt": "#fafafa",
        "display": "Libre Baskerville", "body": "Libre Baskerville",
    },
}
```

Override inside `DESIGN` — merging keeps the size tokens, flips
palette + typography:

```python
DESIGN.update(PALETTES["editorial-serious"])
```

---

## Cover page

```python
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


def add_cover(doc, title, subtitle=None, metadata=None):
    # Thin accent rule on top of the cover.
    rule = doc.add_paragraph()
    pPr = rule._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "24")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), DESIGN["primary"].lstrip("#"))
    pBdr.append(bottom)
    pPr.append(pBdr)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(60)
    run = p.add_run(title)
    run.font.name = DESIGN["display"]
    run.font.size = Pt(DESIGN["size_h1"] + 12)
    run.font.bold = True
    run.font.color.rgb = hex_to_rgb(DESIGN["primary"])

    if subtitle:
        p = doc.add_paragraph()
        run = p.add_run(subtitle)
        run.font.name = DESIGN["body"]
        run.font.size = Pt(DESIGN["size_h2"])
        run.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    if metadata:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(36)
        for key, value in metadata.items():
            k_run = p.add_run(f"{key}: ")
            k_run.bold = True
            k_run.font.size = Pt(DESIGN["size_small"])
            v_run = p.add_run(f"{value}    ")
            v_run.font.size = Pt(DESIGN["size_small"])

    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
```

---

## Table with style override

Overrides the default Microsoft pastel style: primary header, no
vertical rules, alternating body bands, `cantSplit` rows, repeating
header on page break, safe `w:shd w:val="clear"` cell fills.

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


def _set_cell_shading(cell, hex_color: str) -> None:
    """Apply a background fill to a single cell using val='clear'."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")         # NEVER "solid"
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tc_pr.append(shd)


def _set_cell_borders(cell, *, bottom: str | None = None, sides: str = "none") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for edge in ("top", "start", "end"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), sides)
        tc_borders.append(border)
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single" if bottom else "none")
    bot.set(qn("w:sz"), "4")
    bot.set(qn("w:color"), (bottom or "FFFFFF").lstrip("#"))
    tc_borders.append(bot)
    tc_pr.append(tc_borders)


def _mark_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    tr_pr.append(header)
    # Prevent mid-row page breaks.
    cant = OxmlElement("w:cantSplit")
    tr_pr.append(cant)


def add_styled_table(doc, headers, rows, *, caption: str | None = None,
                    numeric_cols: set[int] | None = None):
    numeric_cols = numeric_cols or set()
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))

    # Header row.
    header_row = table.rows[0]
    _mark_repeat_header(header_row)
    for i, text in enumerate(headers):
        cell = header_row.cells[i]
        _set_cell_shading(cell, DESIGN["primary"])
        _set_cell_borders(cell)
        para = cell.paragraphs[0]
        para.alignment = (
            WD_ALIGN_PARAGRAPH.RIGHT if i in numeric_cols else WD_ALIGN_PARAGRAPH.LEFT
        )
        run = para.add_run(text)
        run.bold = True
        run.font.color.rgb = hex_to_rgb("#ffffff")
        run.font.size = Pt(DESIGN["size_body"])
        run.font.name = DESIGN["body"]

    # Body rows — alternating bands, subtle bottom rule.
    for r_idx, row_data in enumerate(rows):
        body_row = table.rows[r_idx + 1]
        cant = OxmlElement("w:cantSplit")
        body_row._tr.get_or_add_trPr().append(cant)
        for c_idx, text in enumerate(row_data):
            cell = body_row.cells[c_idx]
            if r_idx % 2 == 0:
                _set_cell_shading(cell, DESIGN["bg_alt"])
            _set_cell_borders(cell, bottom=DESIGN["rule"])
            para = cell.paragraphs[0]
            para.alignment = (
                WD_ALIGN_PARAGRAPH.RIGHT if c_idx in numeric_cols else WD_ALIGN_PARAGRAPH.LEFT
            )
            run = para.add_run(str(text))
            run.font.size = Pt(DESIGN["size_body"])
            run.font.name = DESIGN["body"]
            run.font.color.rgb = hex_to_rgb(DESIGN["ink"])

    if caption:
        cap = doc.add_paragraph(caption, style="Caption")
        for run in cap.runs:
            run.font.size = Pt(DESIGN["size_small"])
            run.font.color.rgb = hex_to_rgb(DESIGN["muted"])

    return table
```

---

## Figure with caption

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm


def add_figure(doc, image_path, caption: str | None = None,
               width_cm: float = 14.0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Pair figure + caption with keep_with_next.
    pPr = p._p.get_or_add_pPr()
    keep = OxmlElement("w:keepNext")
    pPr.append(keep)

    run = p.add_run()
    run.add_picture(str(image_path), width=Cm(width_cm))

    if caption:
        cap = doc.add_paragraph(caption, style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cap.runs:
            run.font.size = Pt(DESIGN["size_small"])
            run.font.color.rgb = hex_to_rgb(DESIGN["muted"])
            run.italic = True
```

---

## Callout box

Shaded paragraph with a coloured left rule. Kinds: `info` (primary),
`warning`, `danger`, `success`.

```python
CALLOUT_COLORS = {
    "info":    "primary",
    "warning": "state_warn",
    "danger":  "state_danger",
    "success": "state_ok",
}


def add_callout(doc, text: str, kind: str = "info"):
    colour_key = CALLOUT_COLORS.get(kind, "primary")
    hex_colour = DESIGN[colour_key]
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()

    # Left border (thick accent rule).
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "18")
    left.set(qn("w:space"), "6")
    left.set(qn("w:color"), hex_colour.lstrip("#"))
    pBdr.append(left)
    pPr.append(pBdr)

    # Background shading.
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), DESIGN["bg_alt"].lstrip("#"))
    pPr.append(shd)

    # Indentation so text doesn't kiss the rule.
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "300")
    ind.set(qn("w:right"), "100")
    pPr.append(ind)

    run = p.add_run(text)
    run.font.size = Pt(DESIGN["size_body"])
    run.font.color.rgb = hex_to_rgb(DESIGN["ink"])
    run.font.name = DESIGN["body"]
```

---

## Code block

Monospace, soft background, preserve whitespace (important: DOCX
collapses leading whitespace unless `xml:space="preserve"` is set on
each `<w:t>` — `add_run` does this automatically for strings starting
with whitespace, but only if the whole string survives as a single
run).

```python
def add_code_block(doc, text: str, language: str | None = None):
    lines = text.split("\n")
    for line in lines:
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        # Background shading.
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), DESIGN["bg_alt"].lstrip("#"))
        pPr.append(shd)
        # Tight spacing between code lines.
        spacing = OxmlElement("w:spacing")
        spacing.set(qn("w:before"), "20")
        spacing.set(qn("w:after"), "20")
        pPr.append(spacing)
        run = p.add_run(line or " ")
        run.font.name = DESIGN["mono"]
        run.font.size = Pt(DESIGN["size_small"] + 1)
        run.font.color.rgb = hex_to_rgb(DESIGN["ink"])
```

---

## Lists

Use Word's native numbering / bullet styles. **Never** paste Unicode
bullets (`•`) — they don't survive round-trips to Google Docs /
Office Web.

```python
for item in ["First point", "Second point", "Third point"]:
    doc.add_paragraph(item, style="List Bullet")

for item in ["Step one", "Step two", "Step three"]:
    doc.add_paragraph(item, style="List Number")
```

For a nested bullet, set the paragraph format level manually:

```python
p = doc.add_paragraph("Nested bullet", style="List Bullet")
p.paragraph_format.left_indent = Cm(1.5)
```

---

## Horizontal rule

Paragraph-level bottom border. Do **not** use a one-row table as a
rule — cells have minimum height and render visibly.

```python
def add_horizontal_rule(doc, colour_hex: str | None = None):
    colour_hex = (colour_hex or DESIGN["rule"]).lstrip("#")
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bot = OxmlElement("w:bottom")
    bot.set(qn("w:val"), "single")
    bot.set(qn("w:sz"), "6")
    bot.set(qn("w:space"), "1")
    bot.set(qn("w:color"), colour_hex)
    pBdr.append(bot)
    pPr.append(pBdr)
```

---

## Headers, footers, page numbers

### Centred page number in footer

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH


def add_footer_page_number(doc, labels: dict | None = None):
    labels = labels or {"page": "Page", "of": "of"}
    section = doc.sections[0]
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _field(instr: str):
        fld_begin = OxmlElement("w:fldChar")
        fld_begin.set(qn("w:fldCharType"), "begin")
        instr_el = OxmlElement("w:instrText")
        instr_el.text = instr
        fld_sep = OxmlElement("w:fldChar")
        fld_sep.set(qn("w:fldCharType"), "separate")
        fld_end = OxmlElement("w:fldChar")
        fld_end.set(qn("w:fldCharType"), "end")
        return fld_begin, instr_el, fld_sep, fld_end

    run = p.add_run(f"{labels['page']} ")
    run.font.size = Pt(DESIGN["size_small"])
    run = p.add_run()
    for el in _field("PAGE"):
        run._r.append(el)
    run.font.size = Pt(DESIGN["size_small"])

    run = p.add_run(f" {labels['of']} ")
    run.font.size = Pt(DESIGN["size_small"])
    run = p.add_run()
    for el in _field("NUMPAGES"):
        run._r.append(el)
    run.font.size = Pt(DESIGN["size_small"])
```

### Logo + running title in header

```python
from docx.shared import Inches


section = doc.sections[0]
header = section.header
p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = p.add_run()
run.add_picture("assets/logo.png", width=Inches(1.2))
run = p.add_run("    Retention Policy — Confidential")
run.bold = True
run.font.size = Pt(DESIGN["size_small"])
run.font.color.rgb = hex_to_rgb(DESIGN["muted"])
```

### Skip chrome on the cover page

```python
section = doc.sections[0]
section.different_first_page_header_footer = True
# Now section.first_page_header / section.first_page_footer exist and
# default to empty — which is what you want on the cover.
```

---

## Table of Contents

Insert a TOC field; Word fills it on first open.

```python
def add_toc(doc):
    toc_para = doc.add_paragraph()
    run = toc_para.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
```

Headings built via `doc.add_heading(text, level=N)` on a redefined
built-in style carry the correct `outlineLevel` so the TOC picks
them up automatically. Word prompts the user to update fields on
first open (or auto-updates depending on settings).

---

## Multi-section documents (mixed portrait / landscape)

```python
from docx.enum.section import WD_SECTION, WD_ORIENT

portrait = doc.sections[0]
# ... portrait content ...

landscape = doc.add_section(WD_SECTION.NEW_PAGE)
landscape.orientation = WD_ORIENT.LANDSCAPE
landscape.page_width = Cm(29.7)
landscape.page_height = Cm(21.0)
landscape.left_margin = landscape.right_margin = Cm(2.0)
doc.add_heading("Wide table", level=1)
# ... table content ...

# Back to portrait.
third = doc.add_section(WD_SECTION.NEW_PAGE)
third.orientation = WD_ORIENT.PORTRAIT
third.page_width = Cm(21.0)
third.page_height = Cm(29.7)
```

Each new section gets its own headers / footers by default. If you
want them to inherit from the previous section, set
`is_linked_to_previous = True` on the section's header / footer.

---

## Numbered headings (`1.`, `1.1`, `1.1.1`)

By default Word's H1–H3 styles have no numbering. Automatic multi-level
numbering requires editing `numbering.xml`, which `python-docx`
exposes only via low-level oxml. The pragmatic path:

1. Hand-craft a template DOCX with the desired numbering once (easier
   to do in Word itself or by editing the `numbering.xml` directly).
2. Load that template as the starting document.
3. Every `Heading 1` / `Heading 2` / `Heading 3` you add inherits the
   numbering.

```python
from docx import Document

doc = Document("templates/numbered_headings.docx")
# doc.add_heading(...) will now produce numbered entries.
```

If you need to craft the numbering definition from scratch in Python,
the pattern is to inject an `<w:abstractNum>` into
`doc.part.numbering_part.element` and bind H1–H3 styles to it via
`<w:numPr><w:numId w:val="..."/></w:numPr>`. That is reserved for
rare cases — prefer the template path.

---

## Font embedding

Word 2016+ on Windows / macOS honours fonts embedded inside
`word/fontTable.xml`. The procedure:

1. Build the DOCX normally with your display and body faces
   referenced by name.
2. Unzip the produced DOCX.
3. Add the TTF files into a new `word/fonts/` directory inside the
   ZIP.
4. Edit `word/fontTable.xml` so each embedded face has
   `<w:embedRegular r:id="..."/>` (plus bold / italic variants as
   applicable) pointing to the bundled files.
5. Register the relationships inside `word/_rels/fontTable.xml.rels`.
6. Repack the ZIP.

LibreOffice and Word Online ignore embeddings silently — they
substitute the nearest system match. Use embedding only when
delivery is guaranteed to be Word 2016+ Windows/macOS.

---

## Working with an existing DOCX as a starting point

For cases where "generate a DOCX" really means "fill a company
template":

```python
from docx import Document

template = Document("templates/company_letterhead.docx")
template.add_heading("Subject: Policy Update", level=1)
template.add_paragraph("Dear recipient, …")
template.save("output/letter.docx")
```

For fill-in-the-blank (`{{recipient_name}}` → real name), build the
template once with placeholder strings, then run `find_replace` from
`STRUCTURAL_OPS.md`:

```python
# See STRUCTURAL_OPS.md §Find-replace — the snippet reads the source
# DOCX, walks <w:t> nodes, and writes a new file with substitutions.
```

---

## Structural validation

Reopen the saved DOCX and emit a manifest of what it actually contains.
Catches corruption, missing runs, lost sections or broken OOXML
invariants *before* the file is delivered. Runs in ~100 ms; call it
immediately after `doc.save(...)` on every build.

```python
import zipfile
from pathlib import Path

from docx import Document
from lxml import etree


def validate_structure(docx_path) -> dict:
    """Reopen the DOCX and emit a structural manifest."""
    W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    PIC_NS = "http://schemas.openxmlformats.org/drawingml/2006/picture"
    SPACE_ATTR = "{http://www.w3.org/XML/1998/namespace}space"
    Q_T = f"{{{W_NS}}}t"
    Q_PIC = f"{{{PIC_NS}}}pic"

    path = Path(docx_path)
    manifest: dict = {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "reopens": False,
    }
    try:
        doc = Document(str(path))
        manifest["reopens"] = True
    except Exception as exc:
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        return manifest

    manifest["paragraphs"] = len(doc.paragraphs)
    manifest["tables"] = len(doc.tables)
    manifest["sections"] = len(doc.sections)

    headings = {"H1": 0, "H2": 0, "H3": 0}
    for p in doc.paragraphs:
        style_name = p.style.name if p.style else ""
        for level in (1, 2, 3):
            if style_name == f"Heading {level}":
                headings[f"H{level}"] += 1
    manifest["headings"] = headings

    # XML-level inspection — figures + OOXML invariants in one pass.
    figures = 0
    space_ok = True
    with zipfile.ZipFile(path) as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    for _ in root.iter(Q_PIC):
        figures += 1
    for t in root.iter(Q_T):
        txt = t.text or ""
        if txt != txt.strip() and t.get(SPACE_ATTR) != "preserve":
            space_ok = False
            break
    manifest["figures"] = figures
    manifest["xml_space_preserved"] = space_ok

    return manifest


# Usage
manifest = validate_structure("output/retention_policy.docx")
print(manifest)
# {"path": "output/retention_policy.docx", "size_bytes": 42381, "reopens": True,
#  "paragraphs": 12, "tables": 1, "sections": 1,
#  "headings": {"H1": 2, "H2": 1, "H3": 0}, "figures": 0,
#  "xml_space_preserved": True}
```

What to do with the manifest:

- `reopens: False` or `error` present — the file is corrupted. Fix the
  generator, don't deliver.
- `xml_space_preserved: False` — a leading/trailing whitespace run lost
  its `xml:space="preserve"` attribute; text will collapse on load. Fix
  the run emission (usually in `find_replace`-style code paths).
- Heading counts or section counts that don't match the brief
  ("I asked for 5 H1s, emitted 2") — regenerate, don't deliver.

---

## Visual validation pipeline

```bash
# 1. Convert DOCX to PDF with LibreOffice headless.
soffice --headless --convert-to pdf --outdir /tmp/preview output/doc.docx

# 2. Rasterize one PNG per page with poppler-utils.
pdftoppm -r 150 -png /tmp/preview/doc.pdf /tmp/preview/page
# → /tmp/preview/page-1.png, /tmp/preview/page-2.png, ...
```

Wrap in a small helper when iterating:

```python
import subprocess
from pathlib import Path


def visual_validate(docx_path, out_dir, dpi=150):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out), str(docx_path)],
        check=True,
    )
    pdf = out / (Path(docx_path).stem + ".pdf")
    subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png",
         str(pdf), str(out / Path(docx_path).stem)],
        check=True,
    )
    return sorted(out.glob(f"{Path(docx_path).stem}-*.png"))
```

Iterate: generate → rasterize at dpi=100 → inspect → adjust tokens →
regenerate. Bump to dpi=150–200 only for the final QA pass.

---

## Export PDF

One-liner when you need a PDF alongside the DOCX. Default is
**DOCX-only**; add the PDF when the user asks for it or the brief
clearly implies external distribution.

```python
import subprocess
from pathlib import Path


def export_pdf(docx_path, out_dir=None):
    out_dir = Path(out_dir or Path(docx_path).parent)
    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(docx_path)],
        check=True,
    )
    return out_dir / (Path(docx_path).stem + ".pdf")
```

---

## i18n labels

Minimal label catalogue for generated chrome (cover metadata, footer
counters). Extend as needed.

```python
LABELS = {
    "en": {
        "cover": {
            "author":       "Author",
            "domain":       "Domain",
            "date":         "Date",
            "version":      "Version",
            "ref":          "Ref",
            "default_title": "Untitled",
        },
        "page": {
            "page_label":    "Page",
            "of_label":      "of",
        },
    },
    "es": {
        "cover": {
            "author":       "Autor",
            "domain":       "Dominio",
            "date":         "Fecha",
            "version":      "Versión",
            "ref":          "Ref",
            "default_title": "Sin título",
        },
        "page": {
            "page_label":    "Página",
            "of_label":      "de",
        },
    },
}


def get_labels(lang: str | None, overrides: dict | None = None) -> dict:
    lang = (lang or "en").lower().split("-")[0]
    base = LABELS.get(lang, LABELS["en"])
    if overrides:
        merged = {k: {**v} for k, v in base.items()}
        for section, values in overrides.items():
            merged.setdefault(section, {}).update(values)
        return merged
    return base
```

Resolve the language from the caller's locale; the agent's guidance
about user language takes precedence over any heuristic.

---

## Sequence fields for figure / table numbering

Word's `SEQ` field auto-numbers figures, tables and equations.

```python
def add_seq_caption(doc, category: str, text: str):
    """Adds a caption like 'Figure 3 — <text>'."""
    p = doc.add_paragraph(style="Caption")
    p.add_run(f"{category} ").bold = True

    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = f'SEQ {category} \\* ARABIC'
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(fld_end)

    tail = p.add_run(f" — {text}")
    tail.italic = True
    for r in p.runs:
        r.font.size = Pt(DESIGN["size_small"])
        r.font.color.rgb = hex_to_rgb(DESIGN["muted"])
```

Word fills the counter when the user opens the file (or when `Update
Fields` is invoked). Call this once per figure / table.

---

## Content controls (`<w:sdt>`) — read-only inspection

`python-docx` does not expose writing or filling `<w:sdt>` content
controls. For read-only inspection:

```python
from docx.oxml.ns import qn

for sdt in doc.element.body.iter(qn("w:sdt")):
    tag = sdt.find(qn("w:sdtPr") + "/" + qn("w:tag"))
    content = sdt.find(qn("w:sdtContent"))
    if tag is not None:
        print("Tag:", tag.get(qn("w:val")))
    if content is not None:
        for t in content.iter(qn("w:t")):
            print("  Value:", t.text)
```

Writing `<w:sdtContent>` bodies requires hand-walking `document.xml`
and editing runs in place while preserving the `<w:sdtPr>` binding.
Out of scope for this skill.

---

## Batch generation

Each `Document` build is cheap (~20 ms for a simple letter on
commodity hardware). For N documents from a dataset, loop:

```python
from pathlib import Path

out_dir = Path("output/letters")
out_dir.mkdir(parents=True, exist_ok=True)

for row in rows:  # iterable of dicts
    doc = Document()
    # ... apply DESIGN styles, add_cover, content ...
    doc.save(out_dir / f"{row['id']}.docx")
```

Keep one module-level helper function per composition (cover, table,
figure, callout). Instantiate a fresh `Document` per row — there is
no shared state to worry about.

---

## Accessing the underlying python-docx primitives

Everything above is thin sugar over `python-docx`. When you need an
escape hatch (custom XML injection, a layout primitive not covered
here), drop down:

```python
section = doc.sections[0]
body = doc.element.body
# any python-docx operation works here
```

Walk the relevant part's XML tree via `lxml` selectors on `qn("w:...")`
when the Pythonic API does not cover what you need. The OOXML spec
(ECMA-376) is the authoritative reference for tag semantics.
