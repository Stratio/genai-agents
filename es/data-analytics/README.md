# data-analytics

Agente completo de Business Intelligence y Business Analytics para Claude Code y OpenCode.

## Capacidades

- Consulta de datos gobernados vía MCP (servidor SQL de Stratio)
- Análisis avanzado con Python (pandas, numpy, scipy)
- Segmentación y clustering (scikit-learn)
- Visualizaciones profesionales (matplotlib, seaborn, plotly)
- **Entregables analíticos** (multi-formato) — PDF, DOCX, dashboard web interactivo, PowerPoint, póster/infografía, generados por `/analyze` Fase 4 vía las skills writer (`pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`) + `brand-kit` para los tokens de diseño
- **Entregables visuales ligeros sin análisis** — pósteres / infografías / portadas de una sola página (`canvas-craft`), dashboards interactivos standalone (`web-craft`), PDFs ligeros con ≤3 KPIs o documentos tipográficos como facturas y cartas (`pdf-writer`)
- **Lectura de PDF** — extraer texto, tablas, imágenes y datos de formulario de PDFs (`pdf-reader`)
- **Evaluación y reporte de cobertura de calidad de datos** (solo lectura) — evaluar reglas de calidad existentes, identificar gaps de cobertura, generar informes de calidad en Chat/PDF/DOCX/Markdown. La creación y planificación de reglas queda reservada a los agentes Data Quality / Governance Officer.
- Documentación del razonamiento y validación de output
- Memoria persistente de análisis y preferencias

## Requisitos

- Python 3.10+ con las dependencias listadas en `requirements.txt`. En Stratio Cowork la imagen del sandbox las provee; en dev local, `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. Paquetes del sistema (poppler-utils, tesseract-ocr, ghostscript, qpdf, pdftk-java, libcairo2, libpango-1.0-0, libpangoft2-1.0-0) — ver la sección "System dependencies" del `README.md` del monorepo
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
| Análisis | `/analyze` | local | Análisis completo de datos BI/BA: descubrimiento de dominio, EDA, planificación de KPIs, queries MCP, análisis Python, visualizaciones y entregables multi-formato (PDF, DOCX, dashboard web, PowerPoint, póster) — delega en las skills writer según el contrato formato→skill en `AGENTS.md §8` |
| Exploración | `/explore-data` | **shared** | Exploración rápida de dominios, tablas, columnas y terminología de negocio |
| Evaluación de calidad | `/assess-quality` | **shared** | Evaluación de cobertura de calidad para un dominio, tabla o columna; identifica dimensiones cubiertas, gaps y prioridades |
| Informe de calidad | `/quality-report` | **shared** | Generar un informe formal de cobertura de calidad de datos (Chat / PDF / DOCX / Markdown) |
| Memoria | `/update-memory` | local | Actualizar memoria persistente con preferencias, patrones y heurísticas |
| Conocimiento | `/propose-knowledge` | **shared** | Proponer términos de negocio descubiertos a Stratio Governance |
| Lectura de PDF | `/pdf-reader` | **shared** | Extraer texto, tablas, imágenes y datos de formulario de archivos PDF |
| Escritura de PDF | `/pdf-writer` | **shared** | PDFs multi-página o dominados por prosa (informes ligeros con ≤3 KPIs, facturas, cartas, newsletters, certificados). También combinar/dividir/rotar, marca de agua, cifrar, rellenar formularios |
| Lectura de DOCX | `/docx-reader` | **shared** | Extraer texto, tablas, imágenes, metadatos y cambios rastreados de ficheros `.docx` (o `.doc` heredado vía conversión con LibreOffice) |
| Escritura de DOCX | `/docx-writer` | **shared** | Documentos Word genéricos (cartas, memos, contratos, notas de política, informes multipágina en prosa). También combinar/dividir, find-replace, convertir `.doc` a `.docx`, preview visual |
| Lectura de PPTX | `/pptx-reader` | **shared** | Extraer texto, notas del presentador, datos de chart de ficheros `.pptx` (o `.ppt` heredado vía conversión con LibreOffice) |
| Escritura de PPTX | `/pptx-writer` | **shared** | Decks PowerPoint diseñados (pitch, ventas, briefing ejecutivo, formación, académico). También combinar/dividir/reordenar, find-replace en slides y notas, conversión legacy `.ppt` |
| Artefacto visual | `/canvas-craft` | **shared** | Visuales de una sola página dominados por composición: pósteres, infografías, portadas, one-pagers (PDF o PNG) |
| Artefacto web | `/web-craft` | **shared** | HTML interactivo standalone: dashboards, componentes UI, landing pages |
| Tokens de marca | `/brand-kit` | **shared** | Catálogo centralizado de temas de identidad visual (colores, tipografía, paletas de gráficos). Se invoca antes de cualquier entregable visual. Ver AGENTS.md §8.3 para la cascada de decisión |

Las skills marcadas como **shared** viven en `shared-skills/` en la raíz del monorepo y se comparten con otros agentes. Las locales viven en `skills/` de este agente.

## Herramientas de generación

Este agente delega la generación de deliverables en las skills writer (`pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` + `brand-kit`) según el contrato formato→skill en `AGENTS.md §8`. La única utilidad local es `skills/analyze/chart_layout.py` (helpers anti-solapamiento para gráficas matplotlib y Plotly generadas durante el análisis — títulos, subtítulos, leyendas, márgenes, más conversión hex/RGB a `rgba()` compatible con Plotly).

## Memoria persistente

El agente mantiene memoria entre sesiones en dos ficheros:

- `output/MEMORY.md` — Preferencias del usuario, patrones de datos conocidos, heurísticas aprendidas
- `output/ANALYSIS_MEMORY.md` — Índice cronológico de análisis realizados con dominio, resumen y ruta al detalle

Las plantillas iniciales (semilla) viven en `templates/memory/` (versionadas y traducidas). Las skills de escritura del agente (`/update-memory` y `/analyze`) las copian a `output/` la primera vez que necesitan escribir, así el `output/` de runtime queda fuera de git (`**/output/` está en `.gitignore`).
