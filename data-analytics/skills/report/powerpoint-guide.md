# PowerPoint Generation Guide

Operational reference for the PowerPoint pipeline within `/report`.

## Pipeline

1. Generated scripts MUST import helpers from `tools/pptx_layout.py`. NEVER define `add_slide_header`, `add_text`, `add_kpi_box`, `add_paragraph`, `fill_shape`, `add_rect`, etc. inline — import them from the module
2. NEVER hardcode content positions — use `content_area()`, `chart_area()`, `footer_area()` to get safe coordinates
3. For charts: use `add_image_safe()` which automatically calculates position within the safe area
4. For footnotes: use `add_footer_note()` which positions in the safe zone
5. Initialization: use `create_presentation(style)` which returns `(prs, palette)` with standard dimensions (10x7.5")
6. Headers: `add_slide_header(slide, title, subtitle, palette)` returns `CONTENT_TOP` — use that value as the starting point for content
7. Colors: use `rgb_color(palette["primary"])` to convert RGB tuples to `RGBColor`
8. Slide design:
   - Cover: analysis title, date, domain
   - Executive summary: 3-5 bullets with key findings (large numbers 60-72pt for KPIs via `add_kpi_box`)
   - Data slides: one main chart per slide (from `output/[ANALYSIS_DIR]/assets/`), with title as insight
   - Tables: key data in tabular format when charts are not sufficient
   - Conclusions and recommendations: actionable bullets
9. Design principles:
   - Color palette from the chosen theme (via `get_palette`), no hardcoded colors
   - Layout variety: do not repeat the same layout on consecutive slides
   - Each slide needs at least one visual element (chart, table, diagram, highlighted number)
   - Typography: titles 36-44pt bold, body 14-16pt
   - Indicative number of slides: 8-12 for executive, 15-20 for detailed
10. Generate script: `output/[ANALYSIS_DIR]/scripts/generate_pptx.py --style corporate`
11. Save in `output/[ANALYSIS_DIR]/presentation.pptx`

## Slides with Image + Side Panel

- Use `add_image_with_aspect(slide, img_path, left, top, max_width, max_height)` which returns `(actual_w, actual_h)` actual dimensions after preserving aspect ratio
- Use the constant `PANEL_GAP` (0.3") as standard separation between image and side panel
- Calculate panel position: `panel_left = left + actual_w + PANEL_GAP`

## Common Pitfalls

- **Aspect ratio**: NEVER pass width AND height to `slide.shapes.add_picture()` directly — always use `add_image_with_aspect()` or `add_image_safe()` which preserve proportions. Landscape matplotlib charts (18x7) get distorted if forced into square areas
- Images must be **PNG** (not SVG) — python-pptx does not support SVG. Save charts as PNG in `output/[ANALYSIS_DIR]/assets/`
- python-pptx does not support markdown — text must be formatted with `runs` (bold, italic, color via `run.font`)
- Use `get_palette(style)` for shape and font colors, never hardcode RGB values
- Overflow: NEVER place elements below CONTENT_BOTTOM (7.3"). Use `check_bounds()` to validate custom positions. For charts use `add_image_safe()` which calculates automatically
- Header clearance: Content ALWAYS starts at CONTENT_TOP (1.3"), never higher. `add_slide_header()` returns this value
- Inline helpers: NEVER redefine `add_slide_header`, `add_text`, `add_kpi_box`, etc. in the script. Import from `tools/pptx_layout`
