# docx-writer — Reference

Advanced patterns that extend the `DOCXBuilder` primitives. Loaded on demand; you do not need any of this for standard document creation.

## Accessing the underlying `python-docx` Document

Everything `DOCXBuilder` does is thin sugar over `python-docx`. When you need an escape hatch (say, custom XML injection, or a layout primitive the builder does not cover), read through it:

```python
b = DOCXBuilder()
doc = b.document              # python-docx Document
section = doc.sections[0]
# any python-docx operation works here
```

## Table of Contents

DOCX uses a field code for automatic TOC generation. The headings in a document built with `DOCXBuilder` already carry the correct `outlineLevel` (0 for H1, 1 for H2, 2 for H3), so a TOC field picks them up on first open:

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def add_toc_field(paragraph):
    run = paragraph.add_run()
    fld_char_begin = OxmlElement("w:fldChar")
    fld_char_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld_char_separate = OxmlElement("w:fldChar")
    fld_char_separate.set(qn("w:fldCharType"), "separate")
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char_begin)
    run._r.append(instr)
    run._r.append(fld_char_separate)
    run._r.append(fld_char_end)

toc_para = b.document.add_paragraph()
add_toc_field(toc_para)
b.add_page_break()
```

Word prompts the user to update the TOC on first open (or auto-updates it depending on the user's settings). Generated TOCs are empty until the reader accepts the update.

## Custom headers

The `set_footer_page_numbers` helper configures a simple centred footer. For a logo-plus-title header:

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

section = b.document.sections[0]
header = section.header
para = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
para.alignment = WD_ALIGN_PARAGRAPH.LEFT
run = para.add_run()
run.add_picture("assets/logo.png", width=Inches(1.2))
run = para.add_run("    Retention Policy — Confidential")
run.bold = True
```

## Font embedding

Word 2016+ on Windows / macOS honours fonts embedded inside `word/fontTable.xml`. The workflow:

1. Build the DOCX normally with your display and body faces referenced by name.
2. Unzip the produced DOCX.
3. Add the TTF files to a new `word/fonts/` directory inside the ZIP.
4. Edit `word/fontTable.xml` so each embedded face has `<w:embedRegular r:id="..."/>` (and bold / italic variants as applicable) pointing to the bundled files.
5. Register the relationships inside `word/_rels/fontTable.xml.rels`.
6. Repack the ZIP.

LibreOffice and Word Online ignore these embeddings (they substitute the best system match), so embedding is mostly for pixel-exact Windows / macOS delivery.

## Multi-section documents

A single DOCX can have multiple sections with independent page sizes, orientations and headers. Useful for documents where a landscape table sits inside a mostly-portrait report:

```python
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.shared import Cm

section_portrait = b.document.sections[0]
b.add_paragraph("Portrait content...")
new_section = b.document.add_section(WD_SECTION.NEW_PAGE)
new_section.orientation = WD_ORIENT.LANDSCAPE
new_section.page_width = Cm(29.7)
new_section.page_height = Cm(21.0)
b.add_heading("Wide table section", level=1)
b.add_table(headers=[...], rows=[...])
# Switch back to portrait for the rest if needed
third = b.document.add_section(WD_SECTION.NEW_PAGE)
third.orientation = WD_ORIENT.PORTRAIT
third.page_width = Cm(21.0)
third.page_height = Cm(29.7)
```

## Numbered headings ("1.", "1.1", ...)

By default Word's H1–H3 styles have no numbering. To get "1. Scope", "1.1 Subscope" you need a numbering definition:

```python
# In numbering.xml: define an abstractNum with multilevel numbering,
# then bind it to Heading 1 / Heading 2 / Heading 3 via pStyle references.
```

Because this requires editing `numbering.xml` (which `python-docx` exposes via low-level oxml), it is easier to hand-craft an abstract numbering once, write it to a template DOCX, and open the template as the starting document:

```python
from docx import Document as _Document

template = _Document("shared-skills/docx-writer/templates/numbered_headings.docx")
# Then feed `template` into DOCXBuilder by substituting `self._doc` manually,
# or keep two docs open and copy content across.
```

(There is no template bundled in Fase 1. If you need this, create the template once, commit it to your agent's local `skills/`, and load from there.)

## Comments and tracked changes

Not in scope for this skill in Fase 1. Modify with care at the XML level if needed, or use Word / LibreOffice to insert them after the fact.

## Working with an existing DOCX as a starting point

For cases where "generate a DOCX" really means "fill a company template":

```python
from docx import Document as _Document

template = _Document("templates/company_letterhead.docx")
# Insert content into the existing document
template.add_heading("Subject: Policy Update", level=1)
template.add_paragraph("Dear recipient, ...")
template.save("output/letter.docx")
```

In that case `DOCXBuilder`'s value is mostly the styled-primitives layer; adapt by building into a temporary document and copying its body elements into your template. Alternatively: build with `DOCXBuilder`, then use `find_replace_docx` on a template-style placeholder (`{{recipient_name}}`) to fill in values.

## Validation rounds

Regenerate and inspect in a tight loop when iterating on design:

```python
# loop: adjust aesthetic, regenerate, look at pages
b = DOCXBuilder(aesthetic_direction={"tone": "corporate",
                                     "font_pair": ["Instrument Serif", "Crimson Pro"]})
# ... build ...
b.save("iter_1.docx")
# shell: visual_validate.py iter_1.docx --out /tmp/preview_1 --dpi 100
# Inspect PNG, adjust palette_override, try again.
```

Keep the DPI at 100 during iteration (faster rasterisation) and bump to 150–200 only for the final preview.

## Batch generation

For generating N documents from a dataset:

```python
from pathlib import Path

out_dir = Path("output/letters")
out_dir.mkdir(parents=True, exist_ok=True)

for row in rows:  # iterable of dicts
    b = DOCXBuilder(aesthetic_direction={"tone": "corporate"})
    b.add_cover(title=row["title"], subtitle=row["subtitle"],
                author=row["author"])
    b.add_paragraph(row["body"])
    b.save(out_dir / f"{row['id']}.docx")
```

Each DOCXBuilder is independent; building them in a loop is cheap (~20 ms per simple document on commodity hardware).
