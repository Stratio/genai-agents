# docx-writer

Shared skill that creates Word documents (`.docx`) with intentional design, and performs structural operations on existing ones. Covers two audiences: (1) generic prose-dominated documents (letters, memos, contracts, policy briefs, whitepapers, manuals, newsletters, multi-page reports) authored with a design-first workflow, and (2) structural operations on existing `.docx` files (merge, split, find-replace, convert `.doc` → `.docx`, visual preview).

The companion skill `docx-reader` covers ingestion of DOCX inputs. For analytical reports inside `data-analytics`, the `analyze` skill keeps its own opinionated `DOCXGenerator` with an analytical scaffold (executive summary / methodology / analysis / conclusions). `docx-writer` is the general-purpose authoring tool.

## What it does

- Design-first DOCX authoring via raw `python-docx` (no builder class): covers, headings, paragraphs, tables with style override, figures, callouts, lists, code blocks, markdown/HTML content via inline helpers
- Configurable page size (A4 / Letter) and orientation (portrait / landscape)
- Taxonomy of 7 document categories (policy brief, contract/legal, letter/memo, newsletter, manual, multi-page report, academic) as starting points — not enum-constrained
- Six reference palettes (editorial-serious, corporate-formal, technical-minimal, warm-magazine, restrained-legal, academic-sober) as inline `DESIGN` seeds
- Structural operations on existing DOCX files: merge, split by heading or page break, find-replace (run-aware), legacy `.doc` → `.docx` conversion
- Visual preview pipeline (DOCX → PDF → PNG per page) for pre-delivery layout inspection

## Python dependencies

- `python-docx>=1.1`
- `lxml` (transitive from `python-docx`)
- `pillow>=11.0` — figure embedding and image size inspection

All already part of the baseline `requirements.txt` of the Python agents that load this skill.

## System dependencies (apt)

- `libreoffice` (or `libreoffice-writer`) — legacy `.doc` → `.docx` conversion and visual preview rendering. Without it, creation and the pure-Python structural ops still work; only `.doc` conversion and PDF preview are disabled.
- `poppler-utils` — `pdftoppm` rasterises the visual preview PDF to per-page PNGs. Already part of `pdf-reader`'s system deps.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`)

## Bundled assets

None in this iteration. DOCX relies on fonts present on the reader's machine; the skill recommends Calibri / Aptos / Arial / Times New Roman as safe fallbacks and documents font-embedding in `REFERENCE.md` §Font embedding for cases where distribution requires exact fidelity.
