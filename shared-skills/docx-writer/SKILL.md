---
name: docx-writer
description: "Create Word documents (.docx) with intentional design, and perform structural operations on existing ones. Use this skill whenever you need to produce a polished Word document (letter, memo, contract, policy brief, multi-page report) or manipulate existing DOCX files (merge, split, find-replace, convert legacy .doc, render a visual preview). Do NOT use for: data-light or PDF outputs (pdf-writer), single-page visual artefacts (canvas-craft), interactive web (web-craft), or analytical reports generated inside /analyze (which has its own DOCXGenerator)."
argument-hint: "[brief describing what DOCX to build or modify]"
---

# Skill: DOCX Writer

Word is what many stakeholders open by default. A DOCX generated without design attention looks like a word-processor accident — Calibri everywhere, no hierarchy, grey-on-grey borders. This skill treats DOCX as an output surface that deserves the same deliberation as a PDF.

## 1. Design-first workflow

Make five decisions before touching the builder:

1. **What kind of document is this?** Letter, memo, contract, policy brief, newsletter, multi-page report, template. The answer decides tone, rhythm, weight.
2. **Which tone?** Editorial-serious, technical-minimal, warm-magazine, restrained-legal, friendly-modern. Commit to one. Uncommitted tone is the single biggest cause of generic output.
3. **Which typographic pairing?** Body face that reads at 10–11 pt, display face that earns attention on page 1. Because DOCX fonts do not travel unless embedded (§2), choose pairings that degrade gracefully: Calibri / Aptos / Arial are safe defaults; Crimson Pro + Instrument Sans or IBM Plex Serif + IBM Plex Mono require an embedded-font step.
4. **Palette.** One dominant accent (5–15% of surface), one deep neutral for body, one pale neutral for backgrounds, and state colours (success / warning / danger) kept sparingly. Declared in `palette.py` presets or overridden via `aesthetic_direction.palette_override`.
5. **Rhythm.** Margins (default 2.5 cm is ISO), section spacing, how much whitespace breathes between blocks. Cramped DOCX reads as a first draft; generous margins read as the final thing.

## 2. Fonts

DOCX uses the reader's installed fonts unless you embed yours inside `word/fontTable.xml`. Consequences:

- **Default path**: use widely-installed typefaces (Calibri, Aptos, Arial, Times New Roman, Georgia, Cambria). Works everywhere without extra steps.
- **Embed path**: pick any OFL display or body face, embed it via python-docx or by editing `fontTable.xml` after building. Increases file size (~80–150 KB per face) and only fully honoured by Word 2016+ on Windows/macOS. LibreOffice and Word Online may substitute.

`DOCXBuilder` wires the `font_main` key of the palette into `Normal` style and uses `aesthetic_direction.font_pair[0]` (when provided) for headings. That is the minimum contract.

## 3. Starting template

```python
import sys
sys.path.insert(0, "shared-skills/docx-writer/scripts")

from docx_builder import DOCXBuilder

b = DOCXBuilder(
    page_size="A4",
    aesthetic_direction={
        "tone": "corporate",
        "font_pair": ["Instrument Serif", "Crimson Pro"],  # display, body
        "palette_override": {"primary": "#0a2540"},
    },
    author="Compliance Team",
)

b.add_cover(
    title="Data Retention Policy",
    subtitle="Governing customer records under the 2026 framework",
    metadata={"Ref": "POL-042", "Version": "1.0"},
)

b.add_heading("Scope", level=1)
b.add_paragraph(
    "This document defines how customer records are retained, archived, "
    "and deleted across the governed data domains."
)

b.add_heading("Dimensions", level=2)
b.add_table(
    headers=["Dimension", "Commitment"],
    rows=[
        ["Retention window", "36 months rolling"],
        ["Encryption at rest", "AES-256"],
        ["Access audit", "Quarterly review"],
    ],
    caption="Summary of the top-level commitments.",
)

b.add_callout(
    "All clauses in this policy require explicit legal approval.",
    kind="warning",
)

b.set_footer_page_numbers(lang="en")
b.save("output/retention_policy.docx")
```

## 4. Tables that do not look like Excel

A DOCX table without design choices reads as a spreadsheet screenshot. The `shaded-header` style used by default applies:

- Header row filled with the primary colour, text in white, bold, 10 pt.
- Alternating body rows with a very light background.
- Single bottom rule per row in a subtle border colour.
- Monospaced column content when you pass numeric data (callers handle that inline via formatting on the strings).
- `cantSplit` on every row to prevent mid-row page breaks.
- The header row marked as repeat-on-page-break (`<w:tblHeader>`).

Prefer `style="minimal"` when a shaded header is too loud (legal / academic contexts).

## 5. Pitfalls

Reality-checked against `python-docx` and the ECMA-376 spec:

- **Set page size explicitly** — builder exposes it as the first constructor argument. A4 and Letter are not interchangeable; produce documents for the destination.
- **Pagination is the viewer's choice**. Do not try to force pixel-perfect breaks. Use `cantSplit` on atomic rows and `keep_with_next` / `keep_together` on figure + caption pairs (the builder already does this for figures).
- **Repeat the header row on long tables**: the builder does this by default via `<w:tblHeader>`. If you disable it, readers lose context on page two.
- **PNG only for images embedded in a DOCX**: `python-docx` does not accept SVG. Convert with `cairosvg` or `pillow` before calling `add_figure`.
- **Never insert Unicode bullet characters manually** (`•`, `\u2022`). Use `add_list(..., ordered=False)` which uses Word's native numbering — bullets survive round-trips to Google Docs and Word Online.
- **Page breaks must live inside a paragraph**. `add_page_break()` emits a paragraph containing `<w:br w:type="page"/>`.
- **Use `ShadingType.CLEAR` for cell backgrounds**. `SOLID` renders as a black fill on some viewers (this is the source of the "why is my cell black?" bug). The builder always uses `CLEAR`.
- **Do not use tables as horizontal rules**. Cells have minimum height and render as empty boxes in headers / footers. Call `add_horizontal_rule()` instead, which emits a paragraph-level bottom border.
- **Override built-in heading styles with their exact IDs** (`Heading 1`, `Heading 2`, `Heading 3`, `Normal`, `Caption`). Custom style names with alternative IDs break TOC generation and interoperability.
- **Include `outlineLevel`** on every heading style if you want automatic TOC generation. The builder emits this for H1-H3 (levels 0-2).
- **Figures need `keep_with_next`** so the caption never orphans on a new page. The builder sets this automatically inside `add_figure`.
- **`xml:space="preserve"` on `<w:t>` with leading/trailing whitespace**: relevant when using `find_replace_docx` on strings that start or end with a space. The builder sets it when needed inside the replace routine.

## 6. Structural operations

Merging multiple DOCX files, splitting one by section, find-replace with regex, converting legacy binary `.doc`. See `STRUCTURAL_OPS.md` for commands and examples.

## 7. Headers, footers, page numbers

```python
b.set_footer_page_numbers(lang="en")  # "Page N" centred in the footer
```

For richer headers (logos, running titles), access the underlying section:

```python
section = b.document.sections[0]
header = section.header
header.paragraphs[0].text = "Retention Policy — Confidential"
```

## 8. A4 vs Letter, landscape

Constructor arguments:

```python
DOCXBuilder(page_size="A4")              # default
DOCXBuilder(page_size="Letter")          # US
DOCXBuilder(page_size="A4", orientation="landscape")
```

Landscape does not swap `page_width` / `page_height` silently — the builder assigns them explicitly so `python-docx` emits the right XML regardless of the reader's default orientation resolution.

## 9. When NOT to use this skill

- **Analytical report DOCX inside `/analyze`**: use the analyse skill's own `DOCXGenerator` — it has an opinionated scaffold (executive summary → methodology → analysis → conclusions) this builder does not reproduce.
- **Multi-page typographic PDF** (invoice, contract, long prose report): `pdf-writer` is the right surface. PDFs preserve fonts and layout exactly; DOCX cannot match that fidelity.
- **Single-page visual piece** (poster, cover, certificate): `canvas-craft`.
- **Interactive frontend**: `web-craft`.
- **Quality coverage report**: `quality-report` skill has a fixed-layout generator tuned for that content.

## 10. Visual validation

After building, render a PNG-per-page preview and inspect it multimodally:

```bash
python3 shared-skills/docx-writer/scripts/visual_validate.py \
  output/retention_policy.docx \
  --out /tmp/preview --dpi 150
# stdout: list of PNG paths
```

If the output looks wrong (overflow, cramped margins, accent leaking), adjust `aesthetic_direction` and regenerate. Iterate until the preview matches the intent declared in the five design decisions.

## 11. Dependencies

Python: `python-docx`, `lxml`, `markdown`, `beautifulsoup4`, `pillow` — all in the baseline `requirements.txt` of the agents that load this skill.

System: `libreoffice` (optional — needed for `.doc` conversion and visual preview), `poppler-utils` (needed for the preview PDF → PNG step; already part of `pdf-reader`'s deps).

Without `libreoffice` you lose `.doc` conversion and visual preview; DOCX creation and structural operations still work.
