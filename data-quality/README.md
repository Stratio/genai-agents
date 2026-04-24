# data-quality

Expert agent in Data Governance and Data Quality. Assesses quality coverage of governed data, identifies gaps, proposes and creates quality rules with human approval, and generates coverage reports.

## Capabilities

- Quality coverage assessment by domain, collection, or table
- Gap identification: uncovered quality dimensions or tables without coverage
- Reasoned quality rule proposals based on semantic context and real data
- Quality rule creation with mandatory human approval
- Automatic execution scheduling for quality rules
- Coverage report generation (chat, PDF, DOCX, PPTX, Dashboard web, Poster/Infographic, XLSX, Markdown)

## Requirements

- Python 3.10+ with the dependencies listed in `requirements.txt`. In Stratio Cowork the sandbox image provides them; in dev local, `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. System packages (poppler-utils, tesseract-ocr, ghostscript, qpdf, pdftk-java, libcairo2, libpango-1.0-0, libpangoft2-1.0-0) — see the monorepo `README.md` "System dependencies" section
- Access to two Stratio MCP servers:
  - `gov` (governance): quality dimensions, rule creation
  - `sql` (exploration): discovery, SQL generation, profiling, execution

MCP configuration is in `.mcp.json` (Claude Code / claude.ai) and in `opencode.json` (OpenCode), both preconfigured to read URL and credentials from environment variables.

## Environment variables

| Variable | Description |
|----------|-------------|
| `MCP_SQL_URL` | Stratio SQL MCP server URL |
| `MCP_SQL_API_KEY` | SQL MCP server API key |
| `MCP_GOV_URL` | Stratio Governance MCP server URL |
| `MCP_GOV_API_KEY` | Governance MCP server API key |

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Quality assessment | `/assess-quality` | Assess quality coverage by domain or table: covered dimensions, gaps, and priorities |
| Rule creation | `/create-quality-rules` | Design and create quality rules to cover gaps, with mandatory human approval |
| Quality scheduling | `/create-quality-schedule` | Create automatic execution schedules for quality rules by domain/collection |
| Quality report | `/quality-report` | Generate a formal coverage report in chat, PDF, DOCX, PPTX, Dashboard web, Poster/Infographic, XLSX or Markdown |
| PDF reading | `/pdf-reader` | Extract text, tables and data from user-provided PDF files |
| PDF writing | `/pdf-writer` | Create custom PDFs, merge/split, watermark, encrypt, fill forms |
| DOCX reading | `/docx-reader` | Extract text, tables, images, metadata and tracked changes from `.docx` (or legacy `.doc`) files |
| DOCX writing | `/docx-writer` | Generic DOCX (letters, memos, contracts, policy briefs). Merge/split, find-replace, convert `.doc` to `.docx`, visual preview |
| XLSX reading | `/xlsx-reader` | Extract cell values, tables, formulas, images and metadata from `.xlsx`/`.xlsm` files (or legacy `.xls`/`.xlsb` via LibreOffice conversion) |
| XLSX writing | `/xlsx-writer` | Multi-sheet quality-coverage workbooks + ad-hoc XLSX (rule-specs templates, term catalog exports). Merge/split, find-replace, legacy `.xls` conversion, formula refresh |

## Packaging scripts

All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish). When `--lang` is used, output goes to `dist/<lang>/...` instead of `dist/...`.

### Specific scripts (from this folder)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<name>/` | `bash pack_claude_ai_project.sh --name data-quality` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<name>/` | `bash pack_claude_cowork.sh --name data-quality` |

The cowork script also accepts `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>`, and `--sql-key <KEY>` to configure the two MCP servers. If omitted, they remain as environment variable templates to configure later.

### Generic scripts (from the monorepo root)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent data-quality` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent data-quality` |

## Quick start

```bash
# 1. Configure environment variables
export MCP_SQL_URL="https://my-sql-server.example.com/mcp"
export MCP_SQL_API_KEY="my-sql-api-key"
export MCP_GOV_URL="https://my-governance-server.example.com/mcp"
export MCP_GOV_API_KEY="my-governance-api-key"

# 2. Install dependencies (for PDF/DOCX report generation) — dev local only
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# 3. Package for the desired platform
bash ../pack_opencode.sh --agent data-quality
# or
bash ../pack_claude_code.sh --agent data-quality
```
