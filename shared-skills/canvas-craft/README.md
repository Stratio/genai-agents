# canvas-craft

Shared skill that produces single-page static artefacts as PDF or PNG: posters, covers, certificates, marketing one-pagers, infographics, visual summaries. Complementary to `pdf-writer` (multi-page typographic documents) and `web-craft` (interactive HTML/JS). Shares the `visual-craftsmanship.md` guide with both.

## What it does

- Single-page PDF authoring with `reportlab` (full control of coordinates, flow not required)
- PNG rasterization from the generated PDF via `pdf2image` (requires `poppler-utils`)
- Raster manipulation, resizing, colour transforms with `pillow`
- Colour palette, type pairing and margin heuristics tuned for display pieces (see `visual-craftsmanship.md`)

## Python dependencies

- `reportlab>=4.4`
- `pdf2image>=1.17` (requires `poppler-utils`)
- `pillow>=11.0`

## System dependencies (apt)

- `poppler-utils` — backing `pdf2image` for PDF→PNG rasterization

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`)

## MCPs

None — the skill produces visual artefacts from a brief plus theme tokens.

## Bundled assets

Ships **3 OFL display-font families** under `fonts/` so display typography is available out of the box:

- **Fraunces** — variable weight, serif with optional italic variable axis (display + body duty).
- **Instrument Serif** — regular + italic, refined editorial serif.
- **Archivo Black** — regular + italic, high-impact display sans for posters and covers.

Each family ships with its OFL licence text. The bundle is intentionally smaller than `pdf-writer`'s (which ships 14 families) because canvas-craft focuses on single-page display pieces where a handful of idiosyncratic faces go further than a broad library.
