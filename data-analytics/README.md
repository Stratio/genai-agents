# data-analytics

Complete Business Intelligence and Business Analytics agent for Claude Code and OpenCode.

## Capabilities

- Querying governed data via MCP (Stratio SQL server)
- Advanced analysis with Python (pandas, numpy, scipy)
- Segmentation and clustering (scikit-learn)
- Professional visualizations (matplotlib, seaborn, plotly)
- Multi-format report generation: PDF, DOCX, interactive web, PowerPoint
- **Data quality coverage assessment and reporting** (read-only) — evaluate existing quality rules, identify coverage gaps, generate quality reports in Chat/PDF/DOCX/Markdown. Rule creation and scheduling remain in the Data Quality / Governance Officer agents.
- Reasoning documentation and output validation
- Persistent memory for analyses and preferences

## Requirements

- Python 3.10+ (dependencies in `requirements.txt`; install with `bash setup_env.sh`)
- Access to two Stratio MCP servers (configured in `.mcp.json` for Claude Code / claude.ai and in `opencode.json` for OpenCode):
  - **Data MCP** (`stratio_data`): via `MCP_SQL_URL` and `MCP_SQL_API_KEY` env vars — mandatory for analytical workflows
  - **Governance MCP** (`stratio_gov`): via `MCP_GOV_URL` and `MCP_GOV_API_KEY` env vars — needed for quality coverage assessment and reports. Only the read tool `get_quality_rule_dimensions` is allowed; write operations (rule creation/scheduling, AI metadata regeneration via `quality_rules_metadata`) are intentionally denied

## Packaging scripts

All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish). When `--lang` is used, output goes to `dist/<lang>/...` instead of `dist/...`.

Generic scripts at the monorepo root (from `../`):

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `claude_code/<name>/` | `bash ../pack_claude_code.sh --agent data-analytics` |
| `pack_opencode.sh` | OpenCode | `opencode/<name>/` | `bash ../pack_opencode.sh --agent data-analytics` |

## Compatibility

This agent works directly without packaging on:

- **Claude Code**: Package with `pack_claude_code.sh` to use with Claude Code.
- **OpenCode**: Package with `pack_opencode.sh` to use with OpenCode.

Pack scripts are only needed to distribute the agent outside the repository.

## Available skills

| Skill | Command | Origin | Description |
|-------|---------|--------|-------------|
| Analysis | `/analyze` | local | Full BI/BA data analysis: domain discovery, EDA, KPI planning, MCP queries, Python analysis, visualizations, and reports |
| Exploration | `/explore-data` | **shared** | Quick exploration of domains, tables, columns, and business terminology |
| Quality assessment | `/assess-quality` | **shared** | Assess quality coverage for a domain, table, or column; identify dimensions covered, gaps, and priorities |
| Quality report | `/quality-report` | **shared** | Generate a formal data quality coverage report (Chat / PDF / DOCX / Markdown) |
| Report | `/report` | local | Professional multi-format report generation (PDF, DOCX, web, PowerPoint) |
| Memory | `/update-memory` | local | Update persistent memory with preferences, patterns, and heuristics |
| Knowledge | `/propose-knowledge` | **shared** | Propose discovered business terms to Stratio Governance |
| PDF reading | `/pdf-reader` | **shared** | Extract text, tables, images and form data from PDF files |
| PDF writing | `/pdf-writer` | **shared** | Create designed PDFs, merge/split/rotate, watermark, encrypt, fill forms |

Skills marked as **shared** live in `shared-skills/` at the monorepo root and are shared with other agents. Local skills live in this agent's `skills/`.

## Generation tools

Reusable scripts in `tools/` for generating deliverables:

| Tool | Description |
|------|-------------|
| `css_builder.py` | 3-layer CSS assembler (tokens + theme + target) and palette extraction |
| `chart_layout.py` | Anti-overlap for matplotlib and Plotly charts (titles, legends, margins) |
| `pdf_generator.py` | PDF generator with Jinja2 + WeasyPrint (scaffold and free mode) |
| `docx_generator.py` | DOCX generator with styles and scaffold |
| `pptx_layout.py` | Layout helpers for PowerPoint (safe areas, positioning) |
| `dashboard_builder.py` | Interactive web dashboard generator (filters, KPI cards, sortable tables, Plotly) |
| `md_to_report.py` | Markdown to HTML/PDF/DOCX converter with styles and cover page |
| `image_utils.py` | Utilities for embedding images as base64 in HTML |

## Persistent memory

The agent maintains memory between sessions in two files:

- `output/MEMORY.md` — User preferences, known data patterns, learned heuristics
- `output/ANALYSIS_MEMORY.md` — Chronological index of completed analyses with domain, summary, and path to detail

Initial seed templates live under `templates/memory/` (versioned and translated). The agent's writing skills (`/update-memory` and `/analyze`) copy them into `output/` the first time they need to write, so the runtime `output/` stays out of git (`**/output/` is in `.gitignore`).
