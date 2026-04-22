# docx-reader

Shared skill that extracts text, tables, images, metadata and tracked-change markers from user-provided Word documents (`.docx` and legacy `.doc`). Used by agents that need to ingest DOCX inputs as part of an analysis, a governance workflow, or when building a semantic layer from business specifications.

Designed as a two-phase flow: quick mode (single-shot extraction with a multi-engine fallback chain) and deep mode (per-tool deterministic extraction with diagnostics first). The skill picks the phase based on what the document actually contains, never up-front.

## What it does

- Structural diagnosis (part inventory via `unzip -l`, detection of `word/comments.xml`, `word/media/`, `word/footnotes.xml`)
- Text extraction with multi-engine fallback: `pandoc` → `python-docx` → raw-XML walk over `zipfile`
- Table extraction with cell-level fidelity (`python-docx` `Document.tables`)
- Image extraction (ZIP walk into `word/media/*`)
- Core and extended metadata (author, title, created/modified dates, revision count, application)
- Tracked-change surfacing (read-only report of `<w:ins>` / `<w:del>` present in `document.xml`)
- Legacy `.doc` → `.docx` conversion (`soffice --headless --convert-to docx`)

## Python dependencies

- `python-docx>=1.1`
- `lxml` (transitive from `python-docx`)

Both are already part of the baseline `requirements.txt` of the Python agents that load this skill.

## System dependencies (apt)

- `pandoc` — primary extractor for prose-heavy documents (accurate footnotes, tracked changes, lists). Without it the skill falls back to `python-docx`.
- `libreoffice` (or `libreoffice-writer`) — legacy `.doc` → `.docx` conversion. Only needed when the input is a pre-2007 binary `.doc`.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section for install commands.

## Graceful degradation

The skill works with just `python-docx` + `lxml`. `pandoc` and `libreoffice` improve extraction quality and unlock legacy `.doc` support, but they are not mandatory.
