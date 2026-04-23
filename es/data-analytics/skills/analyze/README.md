# analyze

Skill local del agente `data-analytics`. Orquesta el flujo analítico completo: intake, preguntas de clarificación, plan, consulta de datos gobernados vía MCP, análisis Python, visualizaciones, testing opcional, iteración, documentación de razonamiento y validación, y orquestación de la generación de deliverables a través de las skills writer declaradas en `AGENTS.md §8`.

Es el único motor analítico del agente; cualquier otra skill local (`update-memory`) se orquesta desde aquí. La generación de deliverables se delega a `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` + `brand-kit`.

## Qué hace

- Lee datos gobernados vía MCP (`query_data` con preguntas en lenguaje natural) — sin SQL manual
- Análisis con `pandas`/`numpy`/`scipy` en scripts bajo `output/[ANALISIS_DIR]/scripts/`
- Tests estadísticos, clustering, feature importance vía `scikit-learn` + `statsmodels`
- Tendencia / estacionalidad con `pymannkendall`
- Visualizaciones con `matplotlib`, `seaborn`, `plotly`
- Exportación PNG estática de gráficos Plotly vía `kaleido`
- Escribe el markdown analítico interno (`report.md`) y delega en las skills writer la generación de cada formato seleccionado
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
- `openpyxl>=3.1`
- `tabulate>=0.9`

Las skills writer (`pdf-writer`, `docx-writer`, `pptx-writer`) aportan su propio stack Python cuando se invocan.

## Dependencias del sistema (apt)

Ninguna específica de `/analyze`. Las skills writer declaran sus propias dependencias de sistema.

## Sub-guides

- `visualization.md` — selección de tipo de gráfica, storytelling, principios anti-solapamiento
- `analytical-dashboard.md` — patrones de composición para dashboards analíticos (la carga `web-craft` cuando el formato es Dashboard web)
- `reasoning-guide.md` — cómo y cuándo documentar el razonamiento
- `validation-guide.md` — bloques y formatos de validación
- `analytical-patterns.md` — patrones operacionalizados (Pareto, cohortes, funnel, RFM, etc.)
- `advanced-analytics.md` — rigor estadístico, análisis prospectivo, detección de anomalías, root cause
- `clustering-guide.md` — segmentación, clustering, feature importance
- `chart_layout.py` — utilidad Python para layout anti-solapamiento en gráficos matplotlib/Plotly
- `skills-guides/stratio-data-tools.md` — extracción de datos MCP-first (heredado del agente)
