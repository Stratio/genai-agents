# pdf-writer

Shared skill that creates, transforms and hardens PDF documents. Covers two audiences: (1) multi-page typographic documents and prose-dominated single pages (analytical reports, invoices, contracts, zines), and (2) structural operations (merge, split, rotate, watermark, encrypt, flatten, fill forms).

The companion skill `canvas-craft` covers single-page static artefacts (posters, covers, certificates); `web-craft` covers interactive HTML/JS output; `quality-report` covers the fixed-template data-quality report. `pdf-writer` is the general-purpose PDF authoring tool.

## What it does

- Multi-page PDF authoring with `reportlab` (body text, tables, figures, flow)
- SVG-to-PDF conversion with `svglib` (kept below 1.6 to avoid pulling `pycairo`, which has no manylinux wheels)
- Image embedding and manipulation with `pillow`
- Page merging, splitting, rotation, extraction via `pypdf` (library) or `qpdf` (CLI, structural repair)
- Form-field filling, inspection and flattening via `pdftk-java`
- Watermarking, encryption, PDF/A-1 conversion via `ghostscript`

## Python dependencies

- `reportlab>=4.4`
- `svglib>=1.5,<1.6` — pin below 1.6 because 1.6+ pulls `rlPyCairo` → `pycairo`, and `pycairo` has no manylinux wheels on PyPI; compiling from source would require `libcairo2-dev` + a C toolchain that the sandbox purges after build.
- `pillow>=11.0`
- `pypdf>=5.0`

## System dependencies (apt)

- `qpdf` — structural operations and repair used as CLI fallback
- `pdftk-java` — form-field inspection and flattening (`pdftk`, via update-alternatives)
- `ghostscript` — PDF/A conversion and last-resort flattening

In Stratio Cowork the sandbox image (`genai-agents-sandbox`) provides all of the above. In dev local, see the monorepo `README.md` "System dependencies" section.

## Shared guides

- `visual-craftsmanship.md` (via `skill-guides`)

## Bundled assets

Ships a 14-family OFL display-and-body font bundle under `fonts/` so the generated PDFs look consistent across environments without relying on system font discovery.
