# quality-report

Skill compartida que genera el informe formal de cobertura de calidad de datos en cuatro formatos: chat (Markdown renderizado en la conversación), PDF, DOCX y Markdown en disco. Los cuatro formatos consumen el mismo payload `report-input.json` y el mismo generador Python subyacente, manteniendo contenido y traducción alineados.

La usan `data-analytics`, `data-analytics-light`, `data-quality` y `governance-officer`. Cada agente elige los formatos permitidos: `data-analytics-light` es sólo Chat, el resto tiene los cuatro.

## Qué hace

- Lee un `report-input.json` validado (resumen ejecutivo, cobertura por tabla, gaps, prioridades)
- Renderiza HTML vía `jinja2` + `markdown` (para los flujos chat y MD)
- Convierte HTML→PDF vía `weasyprint` (requiere `libcairo2`, `libpango-1.0-0`, `libpangoft2-1.0-0`, `libgdk-pixbuf2.0-0`, `fonts-liberation`)
- Genera DOCX vía `python-docx`
- Emite Markdown en disco con la misma superficie de contenido
- Soporta `--lang` para headings estáticos conscientes del idioma y `--tone` para paleta/pareado tipográfico (afecta sólo a PDF y DOCX)

## Dependencias Python

- `weasyprint>=65`
- `jinja2>=3.1`
- `markdown>=3.7`
- `beautifulsoup4>=4.12`
- `python-docx>=1.1`

## Dependencias del sistema (apt)

- `libcairo2` — Cairo graphics para `weasyprint`
- `libpango-1.0-0` + `libpangoft2-1.0-0` — layout de texto Pango para `weasyprint`
- `libgdk-pixbuf2.0-0` — soporte de imágenes
- `shared-mime-info` — detección MIME
- `fonts-liberation` — fuentes TrueType para rendering consistente

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

## Guides compartidos

- `visual-craftsmanship.md` (declarado en `skill-guides`)
