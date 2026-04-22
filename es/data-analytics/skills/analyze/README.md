# analyze

Skill local del agente `data-analytics`. Orquesta el flujo analítico completo: intake, preguntas de clarificación, plan, consulta de datos gobernados vía MCP, análisis Python, visualizaciones, testing opcional, iteración, documentación de razonamiento y validación, y generación de deliverables (PDF, DOCX, notebook, PPTX).

Es el único motor analítico del agente; cualquier otra skill (`update-memory`, sub-guides `report/`, `reasoning-guide.md`, `validation-guide.md`) se orquesta desde aquí.

## Qué hace

- Lee datos gobernados vía MCP (`query_data` con preguntas en lenguaje natural) — sin SQL manual
- Análisis con `pandas`/`numpy`/`scipy` en scripts bajo `output/[ANALISIS_DIR]/scripts/`
- Tests estadísticos, clustering, feature importance vía `scikit-learn` + `statsmodels`
- Tendencia / estacionalidad con `pymannkendall`
- Visualizaciones con `matplotlib`, `seaborn`, `plotly`
- Exportación PNG estática de gráficos Plotly vía `kaleido`
- Informes multi-formato (HTML → PDF vía `weasyprint`, DOCX vía `python-docx`, PPTX vía `python-pptx`, Markdown, notebook vía `nbconvert`)
- Testing opcional por script con `pytest`+`pytest-mock`

## Dependencias Python

- `pandas>=3.0`
- `numpy>=2.1`
- `scipy>=1.14`
- `pymannkendall>=1.4`
- `scikit-learn>=1.5`
- `statsmodels>=0.14.4`
- `matplotlib>=3.9`
- `seaborn>=0.13`
- `plotly>=6.0,<6.2` (upper-bound alineado con `kaleido 0.2.x`)
- `kaleido>=0.2,<1`
- `jinja2>=3.1`
- `markdown>=3.7`
- `weasyprint>=65`
- `beautifulsoup4>=4.12`
- `nbformat>=5.10`
- `nbclient>=0.10`
- `nbconvert>=7.16`
- `python-pptx>=1.0`
- `python-docx>=1.1`
- `openpyxl>=3.1`
- `tabulate>=0.9`

## Dependencias del sistema (apt)

- `libcairo2` + `libpango-1.0-0` + `libpangoft2-1.0-0` + `libgdk-pixbuf2.0-0` — soporte de `weasyprint`
- `shared-mime-info` + `fonts-liberation` — MIME y TrueType para rendering

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

## Sub-guides

- `report/report.md` — generación de deliverables multi-formato
- `reasoning-guide.md` — cómo y cuándo documentar el razonamiento
- `validation-guide.md` — bloques y formatos de validación
- `skills-guides/stratio-data-tools.md` — extracción de datos MCP-first (heredado del agente)
