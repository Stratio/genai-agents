---
name: docx-writer
description: "Create Word documents (.docx) with intentional design, and perform structural operations on existing ones. Use this skill whenever you need to generate a polished Word document (letter, memo, contract, policy brief, whitepaper, newsletter, manual, multi-page report) or manipulate existing DOCX files (merge, split, find-replace, convert legacy .doc, render a visual preview). This skill treats design seriously — every document it produces has intentional typography, colour and rhythm, never the generic Calibri-everywhere default. Do NOT use for: data-heavy or single-visual outputs (pdf-writer / canvas-craft), interactive web (web-craft), or analytical reports generated inside /analyze (which has its own DOCXGenerator). For advanced patterns (TOC, font embedding, multi-section, numbered headings, batch), load REFERENCE.md. For merge / split / find-replace / legacy .doc conversion, load STRUCTURAL_OPS.md."
argument-hint: "[document type or description]"
---

# Skill: DOCX Writer

Word is the surface most stakeholders open by default. A DOCX generated
without design attention looks like a word-processor accident — Calibri
at every size, grey-on-grey borders, no hierarchy, the same 2.54 cm
margin on every side. That's the baseline this skill actively resists.

Before writing a single line of code, commit to a design direction.
The code serves the design, not the other way around.

## 1. Design-first workflow

Every DOCX generation task, regardless of size, follows five decisions:

1. **Classify the document** — what category is it? (See the taxonomy
   below.) This governs page size, margins, tone and weight downstream.
2. **Pick a visual tone** — editorial-serious, technical-minimal,
   warm-magazine, restrained-legal, corporate-formal, friendly-modern.
   Pick one and execute it confidently. An uncommitted "a bit of
   everything" document is the worst outcome.
3. **Select a type pairing** — one display face for headings, one
   body face for prose. Two typefaces is almost always enough. Because
   DOCX uses the reader's system fonts unless you embed (§5), choose
   pairings that degrade gracefully — Calibri / Aptos / Arial / Times
   New Roman / Georgia / Cambria are universal safe defaults.
4. **Define a palette** — one dominant accent colour (used for 5–15%
   of surface: headings, header rules, callouts), one deep neutral
   for body text (rarely pure black — a warm mid-slate reads better),
   one pale neutral for table bands or sidebars, plus state colours
   (success/warning/danger) used sparingly. Real saturation, not
   washed-out pastels by default. Concrete values come from the
   theme (§3), not from this skill.
5. **Set the rhythm** — margins (2.5 cm ISO default; 3 cm for generous
   editorial; 2 cm for dense reference manuals), paragraph spacing,
   heading air, line-height. Cramped DOCX reads as a first draft;
   generous whitespace reads as the final thing.

Only then open `python-docx`.

### Document taxonomy and starting points

| Category | Typical tone | Page size | Display face | Body face | Margins |
|---|---|---|---|---|---|
| Policy brief / whitepaper | Editorial-serious | A4 | Crimson Pro / IBM Plex Serif | Crimson Pro / Inter | 2.5 cm |
| Contract / legal | Restrained-precise | A4 / Letter | Libre Baskerville | Libre Baskerville | 2.5 cm |
| Letter / memo | Corporate-formal | A4 / Letter | Calibri / Aptos | Calibri / Aptos | 2.5 cm |
| Newsletter / internal briefing | Warm-magazine | A4 | Big Shoulders / Lora | Lora / Inter | 2.0 cm |
| Manual / how-to | Technical-minimal | A4 / Letter | IBM Plex Sans | IBM Plex Sans | 2.0 cm |
| Multi-page report | Editorial-serious | A4 | Instrument Serif / Crimson Pro | Crimson Pro / Inter | 2.5 cm |
| Academic / research | Academic-sober | A4 | Libre Baskerville | Libre Baskerville | 2.5 cm |

These are starting points, not mandates. Break them when the brief
calls for it. The point is **never default to python-docx's blank
Calibri 11 pt template**.

### When this skill is not the right fit

- **Analytical reports inside `/analyze`** — the `data-analytics`
  agent has its own opinionated DOCX pipeline at
  `skills/analyze/report/tools/docx_generator.py` with an analytical
  scaffold (executive summary → methodology → analysis → conclusions).
  Inside Phase 4 of `/analyze`, use that pipeline. This skill is for
  documents outside the analytical flow.
- **Multi-page typographic PDF** (invoice, contract to be delivered,
  long prose report where fidelity matters) — `pdf-writer` preserves
  fonts and layout exactly; DOCX cannot match that fidelity once the
  reader opens it on a different machine.
- **Single-page visual piece** (poster, cover, certificate, one-page
  flyer) — `canvas-craft`.
- **Interactive frontend** — `web-craft`.
- **Quality coverage report** — the `quality-report` skill has a
  fixed-layout generator tuned for that content.

## 2. Page size, margins, orientation

DOCX supports A4 (21 × 29.7 cm) and Letter (21.59 × 27.94 cm). Pick
based on the delivery geography — A4 for most of the world, Letter
for US-based readers. Do not silently ship A4 content to a Letter
printer: the last line of every page will drop off.

Landscape is legitimate for wide tables or dashboards embedded in a
mostly-portrait document. Use a dedicated section (§Multi-section
documents in `REFERENCE.md`) so the landscape pages live in their own
section and the portrait pages keep their own geometry.

Set margins by document intent, not by python-docx's 2.54 cm (1 inch)
default — that is a US-centric legacy that rarely suits intentional
design. Generous editorial: 3 cm. ISO default: 2.5 cm. Dense manual:
2 cm. Newsletter with sidebar: asymmetric (left 2 cm, right 4 cm).

## 3. Theme application

Design tokens (colors, typography, sizes) do not live in this skill —
they come from the theme chosen for the deliverable.

- If a centralized theming skill is available (brand-kit-style),
  run its workflow BEFORE authoring; it returns a token set that maps
  onto the `DESIGN` dict below.
- Otherwise, improvise tokens coherent with the deliverable following
  the tonal palette roles in `skills-guides/visual-craftsmanship.md`.

The `DESIGN` dict in the scaffold uses placeholders (`<hex>`,
`<font-family>`, `<pt>`) — fill them from the theme, don't hard-code.

## 4. A proper starting template

Instead of reaching for `Document()` and hoping, use this scaffold
and adapt:

```python
from pathlib import Path
from docx import Document
from docx.enum.text import WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# 1. Commit to the design tokens up front — they never change mid-doc.
#    Fill these from the chosen theme (see §3). Do not hard-code values
#    here; the skeleton is what stays stable, the values are branding.
DESIGN = {
    # Palette (hex strings — convert to RGBColor at use site)
    "primary":       "<hex>",   # headings, top rules, accents
    "ink":           "<hex>",   # body text (rarely pure black)
    "muted":         "<hex>",   # captions, metadata
    "rule":          "<hex>",   # dividers, table bottom rules
    "bg_alt":        "<hex>",   # pale neutral for table bands
    "state_danger":  "<hex>",
    "state_warn":    "<hex>",
    "state_ok":      "<hex>",
    # Typography
    "display":  "<font-family>",  # headings
    "body":     "<font-family>",  # prose
    "mono":     "<font-family>",  # code
    # Sizes (pt)
    "size_h1":    <pt>,
    "size_h2":    <pt>,
    "size_h3":    <pt>,
    "size_body":  <pt>,
    "size_small": <pt>,
    # Page (document decision, not theme)
    "page_size":  "A4",              # "A4" or "Letter"
    "margin_cm":  2.5,
}


def hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# 2. Build the document and set page geometry.
doc = Document()
section = doc.sections[0]
if DESIGN["page_size"] == "A4":
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
else:  # Letter
    section.page_width = Cm(21.59)
    section.page_height = Cm(27.94)
section.left_margin = section.right_margin = Cm(DESIGN["margin_cm"])
section.top_margin = section.bottom_margin = Cm(DESIGN["margin_cm"])


# 3. Redefine the built-in styles so every paragraph inherits the
#    design tokens. Never rename: Word looks up "Heading 1", "Normal"
#    and "Caption" by their exact IDs for TOC and interoperability.
styles = doc.styles
normal = styles["Normal"]
normal.font.name = DESIGN["body"]
normal.font.size = Pt(DESIGN["size_body"])
normal.font.color.rgb = hex_to_rgb(DESIGN["ink"])

for level, size_key in [(1, "size_h1"), (2, "size_h2"), (3, "size_h3")]:
    h = styles[f"Heading {level}"]
    h.font.name = DESIGN["display"]
    h.font.size = Pt(DESIGN[size_key])
    h.font.bold = True
    h.font.color.rgb = hex_to_rgb(DESIGN["primary"])


# 4. Small helpers for the compositions you'll repeat.
def add_cover(doc, title: str, subtitle: str | None = None,
              metadata: dict | None = None) -> None:
    # Accent rule above the title.
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
            run = p.add_run(f"{key}: ")
            run.bold = True
            run.font.size = Pt(DESIGN["size_small"])
            run = p.add_run(f"{value}    ")
            run.font.size = Pt(DESIGN["size_small"])

    # Force a page break after the cover.
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# 5. Compose the document.
add_cover(
    doc,
    title="Data Retention Policy",
    subtitle="Governing customer records under the 2026 framework",
    metadata={"Ref": "POL-042", "Version": "1.0", "Author": "Compliance Team"},
)

doc.add_heading("Scope", level=1)
doc.add_paragraph(
    "This document defines how customer records are retained, archived, "
    "and deleted across the governed data domains."
)

doc.add_heading("Dimensions", level=2)
# Tables, callouts, figures: see REFERENCE.md for ready-to-adapt snippets.

out_path = Path("output/retention_policy.docx")
out_path.parent.mkdir(parents=True, exist_ok=True)
doc.save(out_path)
```

Four rules the scaffold enforces:

- **Always redefine `Normal`, `Heading 1–3` and `Caption` styles by ID.**
  Don't invent new style names — Word's TOC, accessibility tooling and
  round-trips to Google Docs / LibreOffice all look up the exact IDs.
- **Always set page geometry explicitly.** python-docx defaults to
  Letter with 1-inch margins — rarely what you want.
- **Compute sizes and colours from design tokens**, never inline
  literals mid-document. If the accent colour changes, only `DESIGN`
  changes.
- **Compose with primitives + small helpers**. Reach for a small
  module-local helper the moment you repeat a pattern three times;
  don't build an abstraction up-front.

## 5. Fonts

DOCX uses the reader's installed fonts unless you embed them inside
`word/fontTable.xml`. Consequences:

- **Default path**: use widely-installed typefaces (Calibri, Aptos,
  Arial, Times New Roman, Georgia, Cambria, Courier New). Works
  everywhere without extra steps.
- **Embed path**: pick any OFL display or body face, embed it via the
  font-embedding procedure in `REFERENCE.md` §Font embedding. File
  size grows by 80–150 KB per face. Only fully honoured by Word 2016+
  on Windows/macOS; LibreOffice and Word Online substitute silently.

Recommendation: stick to safe defaults unless the document is only
going to be opened on Word 2016+ Windows/macOS. Inform the user if a
chosen pairing requires a non-standard face.

## 6. Palette guidance

A designed document has at most three colour families on any given
page: primary (one accent colour, saturated, used for 5–15% of
surface: headings, table header fill, accent rules), neutral (body
text and backgrounds), and state colours (success/warning/danger)
used sparingly for callouts.

Never mix two different blues, two different reds, or two different
accent saturations in the same document. Commit to concrete values up
front and apply them uniformly.

Where those concrete values come from depends on what the agent has:

- If a centralized theming skill is available, the chosen theme
  supplies a complete, coherent token set (primary, ink, muted, rule,
  bg_alt, accent, state colours, typography, sizes). Use it verbatim.
- Otherwise, improvise from the tonal palette roles in
  `skills-guides/visual-craftsmanship.md`. For a handful of editorial
  token seeds you can adapt, see `REFERENCE.md` §Palette guidance.

## 7. Document blocks you'll compose

These are the building blocks worth mastering. Snippets for each live
in `REFERENCE.md`; here is the menu.

- **Cover** — title, subtitle, metadata (ref, version, author, date),
  accent rule. Page-break after.
- **Heading** (levels 1–3) — styled via the redefined built-in styles.
  Use `outlineLevel` so automatic TOCs pick them up.
- **Paragraph** — prose body with justify or left alignment, inline
  bold / italic / inline code.
- **Table** — shaded header row, alternating body bands, no vertical
  rules, `cantSplit` per row so rows don't break mid-page.
- **Figure** — centred image with `keep_with_next` so the caption
  never orphans on the next page.
- **Callout** — a shaded box with a short block of text; `info`,
  `warning`, `success`, `danger` variants tint the left rule.
- **List** — native Word numbering for ordered, native bullet for
  unordered. Never insert `•` characters manually.
- **Code block** — monospace, soft background, preserve whitespace.
- **Horizontal rule** — paragraph-level bottom border, not an empty
  table.
- **Page break** — explicit `<w:br w:type="page"/>` inside a paragraph.

## 8. Tables

A DOCX table without design choices reads as a spreadsheet screenshot.
**Always override the default style.** The baseline override, in words:

- Header row: filled with the primary colour, text white, bold, body
  or display face at 10 pt, left-aligned for prose columns and
  right-aligned for numeric columns.
- Body rows: no vertical rules, a subtle horizontal rule between rows
  using `rule` colour, alternating band fill (`bg_alt` on even rows)
  for readability at a glance.
- Row height: slightly generous (2–3 mm of padding inside cells);
  cramped rows read as first-draft exports from Excel.
- `cantSplit="true"` on every row so rows never break mid-page.
- `<w:tblHeader/>` on the header row so it repeats on page-break.
- `<w:shd w:val="clear">` for cell fills — **never** `solid`, which
  renders as black on some viewers (the notorious "why is my cell
  black?" bug).

Full snippet in `REFERENCE.md` §Table with style override; copy it
verbatim for every table-producing document.

## 9. Figures

Embedded via `doc.add_picture(path, width=Cm(...))`. Two rules:

- **PNG only.** `python-docx` does not accept SVG. Convert with
  `cairosvg` or `pillow` before calling `add_picture`.
- **Pair figure + caption with `keep_with_next`** so the caption
  never orphans on a new page. Snippet in `REFERENCE.md` §Figure
  with caption.

For figure numbering ("Figure 3 — Retention cohort curve") use a
module-local counter or hand-crafted sequence fields. Auto-numbered
fields require `seq` in `document.xml` — see `REFERENCE.md`
§Sequence fields for figure numbering.

## 10. Headers, footers, page numbers

Every page-long document benefits from running chrome — a title
header, a page counter in the footer, occasionally a logo. The
baseline:

```python
from docx.enum.text import WD_ALIGN_PARAGRAPH

section = doc.sections[0]
header = section.header
p = header.paragraphs[0]
p.text = "Data Retention Policy — Confidential"
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
for run in p.runs:
    run.font.size = Pt(DESIGN["size_small"])
    run.font.color.rgb = hex_to_rgb(DESIGN["muted"])
```

For centred `Page N of M`, and logo-plus-title headers, see
`REFERENCE.md` §Headers, footers, page numbers.

Skip running chrome on the cover page by marking the first section
`different_first_page_header_footer = True` and leaving its header /
footer paragraphs empty (snippet also in REFERENCE.md).

## 11. Post-build validation and PDF export

After building, always verify the result. Three snippets in
`REFERENCE.md`:

- **Structural validation** (§Structural validation): reopen the saved
  DOCX and emit a manifest — pages, paragraphs, tables, figures,
  heading counts by level, OOXML invariants (`xml:space="preserve"`
  on whitespace-leading runs). Catches corruption, lost sections or
  broken invariants *before* the file is delivered. Runs in ~100 ms;
  do it on every build.
- **Visual validation** (§Visual validation pipeline): convert to PDF
  via LibreOffice and rasterize per-page PNGs with `pdftoppm`.
  Inspect each PNG for overflow, awkward contrast, cramped spacing,
  broken figures. Regenerate and re-validate; 2–3 iterations is
  normal.
- **PDF export** (§Export PDF): one-liner via
  `soffice --headless --convert-to pdf`. Default deliverable is the
  DOCX on its own. Only add a sibling PDF when the user explicitly
  asks for it or when the brief clearly implies distribution outside
  Word (external share, email attachment, audience without Office,
  "I'll send it around", publication). If you're not sure, deliver
  only the DOCX — the user can ask for the PDF afterwards.

Visual validation and PDF export require `libreoffice` and
`poppler-utils`. Structural validation only needs `python-docx` and
`lxml`.

## 12. User-provided templates

When a user provides a corporate template — with their logo, letterhead,
styles and colour palette — ignore the scaffold in §4 and load their
file:

```python
from docx import Document

doc = Document("templates/company_letterhead.docx")
# Inspect the styles the template provides.
for style in doc.styles:
    if style.type is not None:
        print(style.name, style.type)

# Use the template's built-in styles by name — don't redefine them.
doc.add_heading("Subject: Policy Update", level=1)
doc.add_paragraph("Dear recipient, ...")
doc.save("output/letter.docx")
```

When using a client template:

- **Do not redefine `Normal` or `Heading 1–3`.** The template's
  designer picked those fonts and colours for a reason.
- **Do reuse the template's custom styles** if they exist
  (`Quote`, `Sidebar`, `Signature Block`). Look them up by name.
- **Still validate visually** — a template can be out-of-date or
  partially broken; you'll catch it only by rendering and inspecting.

For a fill-in-the-blank pattern (`{{recipient}}` → real name), see
`REFERENCE.md` §Working with an existing DOCX as a starting point.

## 13. Structural operations

For manipulating existing documents (merge several DOCX files, split
by heading level or page break, find-replace with regex across body /
headers / footers, convert legacy binary `.doc` to `.docx`), see
`STRUCTURAL_OPS.md`. Those are copy-paste snippets; run them from a
small script, don't try to import them as a module.

## 14. Pitfalls

Reality-checked against `python-docx` 1.1 and the ECMA-376 spec:

- **Set page size explicitly.** python-docx defaults to Letter with
  1-inch margins. A4 ≠ Letter — produce documents for the destination
  geography.
- **Pagination is the viewer's choice.** Do not try to force
  pixel-perfect breaks. Use `cantSplit` on atomic rows and
  `keep_with_next` / `keep_together` on figure + caption pairs.
- **Repeat the header row on long tables** via `<w:tblHeader/>`. Without
  it, readers lose context on page two.
- **PNG only for embedded images.** `python-docx` does not accept
  SVG. Convert beforehand with `cairosvg` or `pillow`.
- **Never insert Unicode bullet characters manually** (`•`, `\u2022`).
  Use `doc.add_paragraph(..., style="List Bullet")`. Bullets survive
  round-trips only through Word's native numbering.
- **Page breaks must live inside a paragraph.** Emit them as
  `paragraph.add_run().add_break(WD_BREAK.PAGE)`.
- **Use `w:shd w:val="clear"` for cell fills.** `solid` renders as
  black on some viewers. This is the source of the "why is my cell
  black?" bug.
- **Do not use tables as horizontal rules.** Cells have a minimum
  height and render as visible boxes inside headers / footers. Use a
  paragraph-level bottom border instead (snippet in REFERENCE.md).
- **Override built-in heading styles by their exact IDs**
  (`Heading 1`, `Heading 2`, `Heading 3`, `Normal`, `Caption`). Custom
  style names break TOC generation.
- **Include `outlineLevel`** on every heading style if you want
  automatic TOC generation. H1 → `outlineLevel="0"`, H2 → `"1"`,
  H3 → `"2"`.
- **Figures need `keep_with_next`** so the caption never orphans. Set
  it on the paragraph that contains the image, not on the caption.
- **`xml:space="preserve"` on `<w:t>` with leading/trailing whitespace**
  matters when using find-replace on strings that start or end with a
  space; without it the whitespace collapses.

## 15. Known limitations

`python-docx` covers ~85% of real-world document authoring cleanly.
The remaining 15% either needs raw OOXML manipulation or is not
supported at all:

- **Comments and tracked changes** — not supported. Insert them with
  Word or LibreOffice after the fact.
- **Content controls (`<w:sdt>`)** — read-only. Filling form templates
  requires XML-level work; see REFERENCE.md §Content controls for the
  pattern.
- **Equations** — not supported natively. Render as PNG via LaTeX or
  Mathpix and embed as a figure.
- **Charts** — `python-docx` does not expose chart creation. Render
  with matplotlib / plotly, export to PNG at `dpi=200`, and embed as
  a figure.
- **Automatic TOC with numbered entries and page numbers** — the TOC
  field is inserted correctly, but Word fills it only when the user
  opens the file (or accepts the "update fields" dialog). Show the
  user how to trigger it.
- **Exact-font rendering on every machine** — see §5.

Document the limitation in a short appendix or in a call-out when it
affects the deliverable.

## 16. Quick-reference cheat sheet

| Task | Approach |
|---|---|
| Create document | `Document()` then set page geometry on `doc.sections[0]` |
| Redefine built-in styles | by exact ID: `styles["Normal"]`, `"Heading 1"` |
| Cover page | see `REFERENCE.md` §Cover page |
| Heading | `doc.add_heading(text, level=N)` where styles are pre-defined |
| Paragraph | `doc.add_paragraph(text)` with inline runs for formatting |
| Bullet / numbered list | `add_paragraph(..., style="List Bullet")` / `"List Number"` |
| Table with design override | see `REFERENCE.md` §Table with style override |
| Figure with caption | see `REFERENCE.md` §Figure with caption |
| Callout box | see `REFERENCE.md` §Callout box |
| Code block | see `REFERENCE.md` §Code block |
| Horizontal rule | paragraph-level bottom border; see REFERENCE.md |
| Headers / footers / page numbers | see `REFERENCE.md` §Headers, footers, page numbers |
| TOC | see `REFERENCE.md` §Table of Contents |
| Landscape pages mid-document | see `REFERENCE.md` §Multi-section documents |
| Visual preview | `soffice --convert-to pdf` + `pdftoppm -r 150` |
| Export PDF | `soffice --headless --convert-to pdf out.docx` |
| Merge / split / find-replace | see `STRUCTURAL_OPS.md` |
| Convert `.doc` legacy | `soffice --headless --convert-to docx old.doc` |
| User-provided template | load `.docx` / `.dotx` directly; reuse its styles |

## 17. When to load REFERENCE.md

- Full snippets for each document block (cover, headings, paragraphs,
  tables with overrides, figures, callouts, lists, code blocks,
  horizontal rules)
- Palette reference (editorial-serious, corporate-formal,
  technical-minimal, warm-magazine, restrained-legal,
  academic-sober)
- Table of Contents field
- Headers / footers / page numbers (centred, logo+title, skip-first-page)
- Multi-section documents (mixed portrait / landscape)
- Numbered headings (`1.`, `1.1`, `1.1.1`)
- Font embedding procedure (for pixel-exact Word 2016+ delivery)
- Working with an existing DOCX as a starting point
- Visual validation pipeline (DOCX → PDF → PNG per page)
- PDF export one-liner
- i18n labels (English / Spanish) for cover / footer labels
- Sequence fields for figure / table numbering
- Content controls (read-only inspection)
- Batch generation (N documents from a dataset)
