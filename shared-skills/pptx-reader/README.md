# pptx-reader

Shared skill that ingests PowerPoint presentations (`.pptx`, and legacy `.ppt` via LibreOffice conversion). Covers text, bullets, tables, speaker notes, comments, native OOXML chart data, embedded media and metadata extraction. Supports two modes: a one-shot `quick_extract.py` that returns structured Markdown, and a deep workflow documented in `SKILL.md` for complex decks (data-heavy dashboards, hidden slides, encrypted files, mixed content).

The companion skill `pptx-writer` covers authoring and structural operations on PPT files.

## What it does

- One-shot text + bullets + tables + speaker notes extraction via `scripts/quick_extract.py`, emitting Markdown
- Per-slide rasterization via `scripts/rasterize_slides.py` (PPTX → PDF → PNG) for feeding a vision model
- Native OOXML chart data extraction from `ppt/charts/chart*.xml` without OCR
- Speaker notes extraction from `ppt/notesSlides/notesSlide*.xml`
- Reviewer comments extraction from `ppt/comments/comment*.xml`
- Hidden-slide detection and optional inclusion
- Legacy `.ppt` conversion via `libreoffice --headless --convert-to pptx`
- Metadata (author, title, created/modified, revision) via `python-pptx`

## Python dependencies

- `python-pptx>=1.0`
- `lxml` (transitive from `python-pptx`) — needed for the XML walk fallback and chart-data parsing

Both are already part of the baseline `requirements.txt` of the Python agents that load this skill.

Optional:
- `msoffcrypto-tool` — required only for decrypting password-protected `.pptx`. Install on demand when the user provides a password.
- `Pillow` — only if you want to post-process rasterized slide PNGs (resize, composite). Already part of the baseline.

## System dependencies (apt)

- `libreoffice` (or `libreoffice-impress`) — required for (a) converting legacy `.ppt` to `.pptx`, (b) the rasterization pipeline (PPTX → PDF). Without it, modern `.pptx` text extraction still works; only conversion and rasterization are disabled.
- `poppler-utils` — `pdftoppm` rasterises the intermediate PDF to per-slide PNGs. Already part of `pdf-reader`'s system deps, so usually already present.

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides both pre-installed. In dev local, see the monorepo `README.md` "System dependencies" section.

### Install on Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y libreoffice-impress poppler-utils
```

### Install on macOS

```bash
brew install --cask libreoffice
brew install poppler
```

## Shared guides

None in this iteration.

## MCPs

None — the skill operates purely on user-provided PPTX files.

## Bundled assets

None. The skill relies on `python-pptx` and the system LibreOffice; no fonts or templates are shipped.
