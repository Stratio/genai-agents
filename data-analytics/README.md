# data-analytics

Agente completo de Business Intelligence y Business Analytics para Claude Code y OpenCode.

## Capacidades

- Consulta de datos gobernados via MCP (servidor SQL de Stratio)
- Analisis avanzado con Python (pandas, numpy, scipy)
- Segmentacion y clustering (scikit-learn)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- Generacion de informes multi-formato: PDF, DOCX, web interactiva, PowerPoint
- Documentacion del razonamiento y validacion de output
- Memoria persistente de analisis y preferencias

## Scripts de empaquetado

Scripts genericos en la raiz del monorepo (desde `../`):

| Script | Plataforma destino | Output | Ejemplo |
|--------|-------------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `claude_code/<nombre>/` | `bash ../pack_claude_code.sh --agent data-analytics` |
| `pack_opencode.sh` | OpenCode | `opencode/<nombre>/` | `bash ../pack_opencode.sh --agent data-analytics` |

## Compatibilidad

Este agente funciona directamente sin empaquetar en:

- **Claude Code**: `claude .` desde esta carpeta. Lee `CLAUDE.md` y carga skills de `.claude/skills/` automaticamente.
- **OpenCode**: Abrir desde esta carpeta. `opencode.json` apunta a `CLAUDE.md` y reconoce `.claude/skills/`.

Los pack scripts solo son necesarios para distribuir el agente fuera del repositorio.

## Skills disponibles

| Skill | Comando | Descripcion |
|-------|---------|-------------|
| Analisis | `/analyze` | Analisis completo de datos BI/BA: descubrimiento de dominio, EDA, planificacion de KPIs, queries MCP, analisis Python, visualizaciones e informes |
| Exploracion | `/explore-data` | Exploracion rapida de dominios, tablas, columnas y terminologia de negocio |
| Informe | `/report` | Generacion de informes profesionales multi-formato (PDF, DOCX, web, PowerPoint) |
| Memoria | `/update-memory` | Actualizar memoria persistente con preferencias, patrones y heuristicas |
| Conocimiento | `/propose-knowledge` | Proponer terminos de negocio descubiertos a Stratio Governance |

## Herramientas de generacion

Scripts reutilizables en `tools/` para generar deliverables:

| Herramienta | Descripcion |
|-------------|-------------|
| `css_builder.py` | Ensamblador CSS de 3 capas (tokens + theme + target) y extraccion de paleta |
| `chart_layout.py` | Anti-overlap para graficas matplotlib y Plotly (titulos, leyendas, margenes) |
| `pdf_generator.py` | Generador de PDFs con Jinja2 + WeasyPrint (scaffold y modo libre) |
| `docx_generator.py` | Generador de DOCX con estilos y scaffold |
| `pptx_layout.py` | Helpers de layout para PowerPoint (safe areas, posicionamiento) |
| `dashboard_builder.py` | Generador de dashboards web interactivos (filtros, KPI cards, tablas ordenables, Plotly) |
| `md_to_report.py` | Conversor Markdown a HTML/PDF/DOCX con estilos y portada |
| `image_utils.py` | Utilidades para embeber imagenes como base64 en HTML |

## Memoria persistente

El agente mantiene memoria entre sesiones en dos ficheros:

- `output/MEMORY.md` — Preferencias del usuario, patrones de datos conocidos, heuristicas aprendidas
- `output/ANALYSIS_MEMORY.md` — Indice cronologico de analisis realizados con dominio, resumen y ruta al detalle

Las plantillas iniciales (semilla) estan versionadas en `output-templates/`. Los pack scripts las copian a `output/` al empaquetar. En uso directo, el agente las crea en `output/` automaticamente.

## Setup

```bash
bash setup_env.sh
```

## Uso

```bash
claude .
```
