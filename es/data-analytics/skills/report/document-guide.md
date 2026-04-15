# Guía de Generación de Documento (PDF + DOCX)

Referencia operativa para el pipeline de documento dentro de `/report`.

> **Idioma**: Todos los ejemplos de código omiten los argumentos `lang=` y `labels=` por brevedad. En invocaciones reales, **pasar siempre `lang="<código_idioma_usuario>"` a cada generador** (`PDFGenerator.render_scaffold`, `PDFGenerator.render_from_html`, `DOCXGenerator.render_scaffold`, `DOCXGenerator.render_from_markdown`). Ver sec 3.1 de `SKILL.md` para las reglas de resolución y las claves del catálogo disponibles.

## Pipeline

1. Usar `tools/pdf_generator.py` (`PDFGenerator`) con el estilo visual elegido por el usuario
2. Si estructura **scaffold**: usar `render_scaffold()` con KPIs, tablas, figuras y secciones estructuradas. Usa templates Jinja2 de `templates/pdf/`
3. Si estructura **al vuelo**: usar `render_from_html()` con HTML libre generado en el script. Solo envuelve con CSS, portada opcional, base64 y metadata
4. Ambos modos generan portada automática, numeracion de paginas, headers, e imágenes embebidas en base64
5. Generar script: `output/[ANALISIS_DIR]/scripts/generate_pdf.py` que importe y use `PDFGenerator`
6. Guardar en `output/[ANALISIS_DIR]/report.pdf`
7. `save()` por defecto no guarda el HTML (artefacto intermedio de build). Pasar `also_save_html=True` solo si se necesita una versión web estática del documento además del PDF
8. Generar DOCX: instanciar `DOCXGenerator(style=estilo)` con los MISMOS datos que el PDF. Si scaffold → `render_scaffold()` con los mismos parámetros. Si al vuelo → `render_from_markdown()` con el markdown source
9. Guardar en `output/[ANALISIS_DIR]/report.docx`

## Pitfalls DOCX

- Imágenes DEBEN ser PNG (no SVG) — python-docx no soporta SVG
- Tablas muy anchas (>7 columnas) pueden desbordarse — dividir o transponer
- No hay paginacion controlable — Word decide los saltos de pagina
- Fuentes: usar fallback Arial/Calibri si la fuente del tema no está instalada
- **Imágenes inline**: Las secciones HTML (`executive_summary`, `analysis`, etc.) renderizan `<figure>`, `<img>`, `<table>`, `<h3>`, `<ul>`, `<ol>`, `<div class="callout">` y `<blockquote>` en su posición correcta dentro del texto. Las imágenes base64 (`data:image/png;base64,...`) se decodifican automáticamente
- **No duplicar imágenes**: Si una imagen ya está embebida en el HTML de una sección (ej. `<figure><img src="data:..."/></figure>`), NO pasarla también en el parámetro `figures=` — se duplicaría en el documento
- Las tablas, listas y subheadings dentro de secciones HTML también se renderizan inline en su posición correcta
