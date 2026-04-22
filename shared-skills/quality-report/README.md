# quality-report

Shared skill that generates the formal data-quality coverage report in four output formats: chat (Markdown rendered in conversation), PDF, DOCX, and Markdown-on-disk. All formats consume the same `report-input.json` payload and the same underlying Python generator, keeping the four outputs aligned in content and translation.

Used by `data-analytics`, `data-analytics-light`, `data-quality` and `governance-officer`. Each agent picks the allowed formats: `data-analytics-light` is Chat-only, the rest have the full four.

## What it does

- Reads a validated `report-input.json` (executive summary, per-table coverage, gaps, priorities)
- Renders HTML via `jinja2` + `markdown` (for the chat and MD flows)
- Converts HTML→PDF via `weasyprint` (requires `libcairo2`, `libpango-1.0-0`, `libpangoft2-1.0-0`, `libgdk-pixbuf2.0-0`, `fonts-liberation`)
- Generates DOCX via `python-docx`
- Emits Markdown-on-disk with the same content surface
- Supports `--lang` for language-aware static headings and `--tone` for palette/type pairing (affects PDF and DOCX only)

## Python dependencies

- `weasyprint>=65`
- `jinja2>=3.1`
- `markdown>=3.7`
- `beautifulsoup4>=4.12`
- `python-docx>=1.1`

## System dependencies (apt)

- `libcairo2` — Cairo graphics for `weasyprint`
- `libpango-1.0-0` + `libpangoft2-1.0-0` — Pango text layout for `weasyprint`
- `libgdk-pixbuf2.0-0` — image backing
- `shared-mime-info` — MIME detection
- `fonts-liberation` — TrueType fonts for consistent rendering

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`)
