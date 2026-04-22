# docx-writer

Shared skill that creates Word documents (`.docx`) with intentional design, and performs structural operations on existing ones. Covers two audiences: (1) generic prose-dominated documents (letters, memos, contracts, policy briefs, multi-page reports) authored with a design-first workflow, and (2) structural operations on existing `.docx` files (merge, split, find-replace, convert `.doc` → `.docx`, visual preview).

The companion skill `docx-reader` covers ingestion of DOCX inputs. For analytical reports inside `data-analytics`, the `analyze` skill keeps its own opinionated `DOCXGenerator` with an analytical scaffold (executive summary / methodology / analysis / conclusions). `docx-writer` is the general-purpose authoring tool.

## What it does

- Design-first DOCX authoring with a primitives-oriented `DOCXBuilder` class (covers, headings, paragraphs, tables, figures, callouts, lists, code blocks, markdown blocks)
- Configurable page size (A4 / Letter) and orientation (portrait / landscape)
- Style application via `aesthetic_direction` (tone, palette override, font pair)
- Table composition with proper DXA widths, cell margins and `ShadingType.CLEAR` to avoid cross-viewer breakage
- Structural operations on existing DOCX files: merge, split, find-replace (run-aware)
- Legacy `.doc` → `.docx` conversion via `libreoffice --headless --convert-to docx`
- Visual preview pipeline (DOCX → PDF → PNG per page) to let the agent inspect layout before delivery

## Python dependencies

- `python-docx>=1.1`
- `lxml` (transitive from `python-docx`)
- `markdown>=3.6` — used by `add_markdown_block` to fold markdown into docx primitives
- `beautifulsoup4>=4.12` — parse inline HTML produced by markdown for faithful docx rendering
- `pillow>=11.0` — figure embedding and image size inspection

All already part of the baseline `requirements.txt` of the Python agents that load this skill.

## System dependencies (apt)

- `libreoffice` (or `libreoffice-writer`) — legacy `.doc` → `.docx` conversion and visual preview rendering. Without it, creation and all pure-Python structural ops still work; only `.doc` conversion and preview are disabled.
- `poppler-utils` — `pdftoppm` rasterises the visual preview PDF to per-page PNGs. Already part of `pdf-reader`'s system deps.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`)

## Bundled assets

None in this iteration. DOCX relies on fonts present on the reader's machine; the skill recommends Calibri / Aptos / Arial as safe fallbacks and documents font-embedding for the cases where distribution requires it.
