# data-analytics

Agente completo de Business Intelligence y Business Analytics para Claude Code y OpenCode.

## Capacidades

- Consulta de datos gobernados vía MCP (servidor SQL de Stratio)
- Análisis avanzado con Python (pandas, numpy, scipy)
- Segmentación y clustering (scikit-learn)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Generación de informes multi-formato: PDF, DOCX, web interactiva, PowerPoint
- **Evaluación y reporte de cobertura de calidad de datos** (solo lectura) — evaluar reglas de calidad existentes, identificar gaps de cobertura, generar informes de calidad en Chat/PDF/DOCX/Markdown. La creación y planificación de reglas queda reservada a los agentes Data Quality / Governance Officer.
- Documentación del razonamiento y validación de output
- Memoria persistente de análisis y preferencias

## Requisitos

- Python 3.10+ (dependencias en `requirements.txt`; instalar con `bash setup_env.sh`)
- Acceso a dos servidores MCP de Stratio (configurados en `.mcp.json` para Claude Code / claude.ai y en `opencode.json` para OpenCode):
  - **MCP de datos** (`stratio_data`): vía variables de entorno `MCP_SQL_URL` y `MCP_SQL_API_KEY` — obligatorio para flujos analíticos
  - **MCP de gobernanza** (`stratio_gov`): vía variables de entorno `MCP_GOV_URL` y `MCP_GOV_API_KEY` — necesario para la evaluación e informes de cobertura de calidad. Solo se permite la tool de lectura `get_quality_rule_dimensions`; las operaciones de escritura (creación/planificación de reglas, regeneración de metadata IA vía `quality_rules_metadata`) están intencionadamente denegadas

## Scripts de empaquetado

Todos los scripts aceptan `--lang <código>` para generar output en un idioma específico (ej: `--lang es` para español). Cuando se usa `--lang`, el output va a `dist/<lang>/...` en lugar de `dist/...`.

Scripts genéricos en la raíz del monorepo (desde `../`):

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics` |
| `pack_opencode.sh` | OpenCode | `opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics` |

## Compatibilidad

Este agente funciona directamente sin empaquetar en:

- **Claude Code**: Empaquetar con `pack_claude_code.sh` para usar con Claude Code.
- **OpenCode**: Empaquetar con `pack_opencode.sh` para usar con OpenCode.

Los pack scripts solo son necesarios para distribuir el agente fuera del repositorio.

## Skills disponibles

| Skill | Comando | Origen | Descripción |
|-------|---------|--------|-------------|
| Análisis | `/analyze` | local | Análisis completo de datos BI/BA: descubrimiento de dominio, EDA, planificación de KPIs, queries MCP, análisis Python, visualizaciones e informes |
| Exploración | `/explore-data` | **shared** | Exploración rápida de dominios, tablas, columnas y terminología de negocio |
| Evaluación de calidad | `/assess-quality` | **shared** | Evaluación de cobertura de calidad para un dominio, tabla o columna; identifica dimensiones cubiertas, gaps y prioridades |
| Informe de calidad | `/quality-report` | **shared** | Generar un informe formal de cobertura de calidad de datos (Chat / PDF / DOCX / Markdown) |
| Informe | `/report` | local | Generación de informes profesionales multi-formato (PDF, DOCX, web, PowerPoint) |
| Memoria | `/update-memory` | local | Actualizar memoria persistente con preferencias, patrones y heurísticas |
| Conocimiento | `/propose-knowledge` | **shared** | Proponer términos de negocio descubiertos a Stratio Governance |

Las skills marcadas como **shared** viven en `shared-skills/` en la raíz del monorepo y se comparten con otros agentes. Las locales viven en `skills/` de este agente.

## Herramientas de generación

Scripts reutilizables en `tools/` para generar deliverables:

| Herramienta | Descripción |
|-------------|-------------|
| `css_builder.py` | Ensamblador CSS de 3 capas (tokens + theme + target) y extraccion de paleta |
| `chart_layout.py` | Anti-overlap para gráficas matplotlib y Plotly (títulos, leyendas, márgenes) |
| `pdf_generator.py` | Generador de PDFs con Jinja2 + WeasyPrint (scaffold y modo libre) |
| `docx_generator.py` | Generador de DOCX con estilos y scaffold |
| `pptx_layout.py` | Helpers de layout para PowerPoint (safe areas, posicionamiento) |
| `dashboard_builder.py` | Generador de dashboards web interactivos (filtros, KPI cards, tablas ordenables, Plotly) |
| `md_to_report.py` | Conversor Markdown a HTML/PDF/DOCX con estilos y portada |
| `image_utils.py` | Utilidades para embeber imágenes como base64 en HTML |

## Memoria persistente

El agente mantiene memoria entre sesiones en dos ficheros:

- `output/MEMORY.md` — Preferencias del usuario, patrones de datos conocidos, heurísticas aprendidas
- `output/ANALYSIS_MEMORY.md` — Índice cronológico de análisis realizados con dominio, resumen y ruta al detalle

Las plantillas iniciales (semilla) viven en `templates/memory/` (versionadas y traducidas). Las skills de escritura del agente (`/update-memory` y `/analyze`) las copian a `output/` la primera vez que necesitan escribir, así el `output/` de runtime queda fuera de git (`**/output/` está en `.gitignore`).
