# data-analytics

Agente completo de Business Intelligence y Business Analytics para Claude Code y OpenCode.

## Capacidades

- Consulta de datos gobernados vía MCP (servidor SQL de Stratio)
- Análisis avanzado con Python (pandas, numpy, scipy)
- Segmentación y clustering (scikit-learn)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Generación de informes multi-formato: PDF, DOCX, web interactiva, PowerPoint
- Documentación del razonamiento y validación de output
- Memoria persistente de análisis y preferencias

## Requisitos

- Python 3.10+ (dependencias en `requirements.txt`; instalar con `bash setup_env.sh`)
- Acceso a un servidor MCP de Stratio. La configuración está en `.mcp.json` (Claude Code / claude.ai) y en `opencode.json` (OpenCode), ambos preconfigurados para leer la URL y credenciales desde variables de entorno

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

Las plantillas iniciales (semilla) están versionadas en `output-templates/`. Los pack scripts las copian a `output/` al empaquetar. En uso directo, el agente las crea en `output/` automáticamente.
