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

## Bundled assets

Ships the same OFL display-font bundle as `pdf-writer` so display typography is available out of the box.
