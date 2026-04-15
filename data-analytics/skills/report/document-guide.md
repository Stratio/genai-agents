# Document Generation Guide (PDF + DOCX)

Operational reference for the document pipeline within `/report`.

> **Language**: All code snippets below omit `lang=` and `labels=` arguments for brevity. In real invocations, **always pass `lang="<user_language_code>"` to every generator** (`PDFGenerator.render_scaffold`, `PDFGenerator.render_from_html`, `DOCXGenerator.render_scaffold`, `DOCXGenerator.render_from_markdown`). See sec 3.1 of `SKILL.md` for the full resolution rules and the available catalogue keys.

## Pipeline

1. Use `tools/pdf_generator.py` (`PDFGenerator`) with the visual style chosen by the user
2. If structure is **scaffold**: use `render_scaffold()` with KPIs, tables, figures, and structured sections. Uses Jinja2 templates from `templates/pdf/`
3. If structure is **on the fly**: use `render_from_html()` with free HTML generated in the script. Only wraps with CSS, optional cover, base64, and metadata
4. Both modes generate automatic cover page, page numbering, headers, and base64-embedded images
5. Generate script: `output/[ANALYSIS_DIR]/scripts/generate_pdf.py` that imports and uses `PDFGenerator`
6. Save in `output/[ANALYSIS_DIR]/report.pdf`
7. `save()` by default does not save the HTML (intermediate build artifact). Pass `also_save_html=True` only if a static web version of the document is needed in addition to the PDF
8. Generate DOCX: instantiate `DOCXGenerator(style=style)` with the SAME data as the PDF. If scaffold → `render_scaffold()` with the same parameters. If on the fly → `render_from_markdown()` with the markdown source
9. Save in `output/[ANALYSIS_DIR]/report.docx`

## DOCX Pitfalls

- Images MUST be PNG (not SVG) — python-docx does not support SVG
- Very wide tables (>7 columns) may overflow — split or transpose
- There is no controllable pagination — Word decides page breaks
- Fonts: use Arial/Calibri fallback if the theme font is not installed
- **Inline images**: HTML sections (`executive_summary`, `analysis`, etc.) render `<figure>`, `<img>`, `<table>`, `<h3>`, `<ul>`, `<ol>`, `<div class="callout">`, and `<blockquote>` in their correct position within the text. Base64 images (`data:image/png;base64,...`) are decoded automatically
- **Do not duplicate images**: If an image is already embedded in a section's HTML (e.g., `<figure><img src="data:..."/></figure>`), do NOT also pass it in the `figures=` parameter — it would be duplicated in the document
- Tables, lists, and subheadings within HTML sections are also rendered inline in their correct position
