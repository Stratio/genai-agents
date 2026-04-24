# pptx-writer

Shared skill that creates PowerPoint (`.pptx`) decks with intentional design, and performs structural operations on existing ones. Covers: (1) decks authored with a design-first workflow (pitches, executive briefings, training, academic, sales, town-hall, analytical decks), and (2) structural operations on existing `.pptx` files (merge, split, reorder, delete slides, find-replace across slides and speaker notes, convert legacy `.ppt` → `.pptx`, rasterize slides, export to PDF).

The companion skill `pptx-reader` covers ingestion of PPTX inputs.

## What it does

- Design-first PPT authoring following a 5-step workflow (classify → tone → type pairing → palette → rhythm), with a deck taxonomy and canonical scaffold snippet in `SKILL.md`
- 16:9 default aspect ratio (10 × 5.625 inches) via bundled blank scaffold (`assets/blank.pptx`); 4:3 available by loading a user-provided template
- Slide primitives as copy-paste snippets in `REFERENCE.md`: cover, agenda, section divider, title+content, bullets, two-column, image-with-text, KPI, table with style override, native OOXML charts, quote, conclusion
- Native OOXML chart authoring (bar / column / line / pie / area / scatter / radar / bubble) so the user can edit the underlying data in PowerPoint
- Structural operations on existing PPT files: merge, split (by section or by N slides), reorder, delete, find-replace (in slide text and / or speaker notes), legacy `.ppt` → `.pptx` conversion via LibreOffice
- Visual preview pipeline (PPTX → PDF → per-slide PNG) for the model to inspect layout before delivery
- One-liner PDF export via LibreOffice headless

## Python dependencies

- `python-pptx>=1.0`
- `lxml` (transitive from `python-pptx`) — used by structural operation snippets for XML manipulation (`_sldIdLst`, find-replace across slides)
- `pillow>=11.0` — only when snippets post-process images before embedding (resize, composite)

All already part of the baseline `requirements.txt` of the Python agents that load this skill.

## System dependencies (apt)

- `libreoffice` (or `libreoffice-impress`) — required for (a) legacy `.ppt` → `.pptx` conversion, (b) the visual preview pipeline, (c) PDF export. Without it, deck creation and all pure-Python structural ops still work; only those three features are disabled.
- `poppler-utils` — `pdftoppm` rasterises the visual preview PDF to per-slide PNGs. Already part of `pptx-reader`'s and `pdf-reader`'s system deps.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides both pre-installed (same pattern as `docx-writer` and `pdf-writer`). In dev local, see the monorepo `README.md` "System dependencies" section.

### Install on Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y libreoffice-impress poppler-utils
```

### Install on macOS

```bash
brew install --cask libreoffice
brew install poppler
```

## Companion skills

- `pptx-reader` — the ingestion counterpart (text / bullets / tables / notes / comments / chart data). Shares the `python-pptx` + LibreOffice stack.

## MCPs

None — the skill operates purely on local files.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`) — shared design principles across the visual-craftsmanship family (`web-craft`, `canvas-craft`, `pdf-writer`, `docx-writer`, `pptx-writer`).

## Bundled assets

- `assets/blank.pptx` — a clean 16:9 scaffold (10 × 5.625 inches) with a single Blank layout and a neutral theme. About 30 KB. Load it with `Presentation(path_to_blank_pptx)` as the starting point for every new deck, unless the user provides a corporate template.

No shipped fonts. PPT uses the reader's system fonts unless explicitly embedded, and embedding is unreliable across Office / LibreOffice / Web Office renderers. The skill recommends Calibri / Aptos / Inter / Arial as safe defaults and documents the trade-off in `SKILL.md` §Fonts.
