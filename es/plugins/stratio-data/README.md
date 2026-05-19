# Plugin Stratio Data

Vertical de análisis de datos para Stratio Cowork. Empaqueta el agente `data-analytics-officer`: un analista senior BI/BA que convierte preguntas de negocio en análisis accionables con datos reales de dominios gobernados.

## Qué incluye

| Agente | Propósito |
|---|---|
| [data-analytics-officer](../../agents/data-analytics-officer/) | Flujo BI/BA completo: descubrimiento de datos sobre dominios gobernados, EDA y profiling, análisis dirigido por hipótesis con Python (pandas, scipy, scikit-learn), visualizaciones (matplotlib, seaborn, plotly), y generación de entregables multi-formato (PDF, DOCX, PPTX, Dashboard web, Artículo web, Póster/Infografía, XLSX). |

El agente importa las skills que necesita (`stratio-data`, `quality-report`, `pdf-writer`, `docx-writer`, `pptx-writer`, `xlsx-writer`, `web-craft`, `canvas-craft`, `brand-kit`, …) vía su manifest `imported-skills`. Viajan dentro del bundle del agente y se enlazan al agente cuando se instala en Cowork.

## Plataformas soportadas

| Plataforma | Soportada | Notas |
|---|---|---|
| Stratio Cowork | sí | Desplegable como bundle envoltorio `agents/v1`. |
| Claude (claude-plugin) | **no** | Los plugins del marketplace de Claude no soportan agentes. |

## Instalación

El plugin produce un artefacto:

- `dist/stratio-data-stratio-cowork-{version}.zip` — Bundle envoltorio para Stratio Cowork.

Usa la task `upload-plugin` de la shared-skill [`cowork-api`](../../skills/cowork-api/) para desplegarlo.
