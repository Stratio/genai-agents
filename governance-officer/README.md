# governance-officer

Governance officer agent combining semantic layer building and data quality management. Orchestrates the full lifecycle of governance artifacts: ontologies, views, mappings, terms, quality rules, and coverage reports.

## Capabilities

### Semantic layer
- Building and maintaining semantic layers via governance MCPs
- Publishing business views (Draft → Pending Publish)
- Exploring technical domains and published semantic layers
- Interactive ontology planning with local file reading
- Creating data collections from data dictionary searches
- Managing business terms in the governance dictionary

### Data quality
- Quality coverage assessment by domain, collection, table, or column
- Gap identification: uncovered quality dimensions
- Reasoned quality rule proposals based on semantic context and real data
- Quality rule creation with mandatory human approval
- Automatic execution scheduling for quality rules
- Coverage report generation (chat, PDF, DOCX, Markdown)

## Requirements

- Python 3.10+ (dependencies in `requirements.txt`; install with `bash setup_env.sh`)
- Access to two Stratio MCP servers:
  - `gov` (governance): semantic layer tools, quality dimensions, rule creation
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
| Full pipeline | `/build-semantic-layer` | Build complete semantic layer: terms, ontology, views, mappings, semantic terms |
| Technical terms | `/generate-technical-terms` | Generate technical descriptions for tables and columns |
| Ontology | `/create-ontology` | Create, extend, or delete ontology classes |
| Business views | `/create-business-views` | Create, regenerate, or delete business views |
| SQL mappings | `/create-sql-mappings` | Create or update SQL mappings for views |
| Semantic terms | `/create-semantic-terms` | Generate business semantic terms |
| Business terms | `/manage-business-terms` | Create business terms in the governance dictionary |
| Data collection | `/create-data-collection` | Search and create new technical domains |
| Quality assessment | `/assess-quality` | Assess quality coverage by domain or table |
| Rule creation | `/create-quality-rules` | Design and create quality rules with human approval |
| Quality scheduling | `/create-quality-planification` | Create automatic execution schedules |
| Quality report | `/quality-report` | Generate formal coverage report (PDF, DOCX, Markdown) |

## Packaging scripts

All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish). When `--lang` is used, output goes to `dist/<lang>/...` instead of `dist/...`.

### Specific scripts (from this folder)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<name>/` | `bash pack_claude_ai_project.sh --name governance-officer` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<name>/` | `bash pack_claude_cowork.sh --name governance-officer` |

The cowork script also accepts `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>`, and `--sql-key <KEY>` to configure the two MCP servers. If omitted, they remain as environment variable templates to configure later.

### Generic scripts (from the monorepo root)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent governance-officer` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent governance-officer` |

## Quick start

```bash
# 1. Configure environment variables
export MCP_SQL_URL="https://my-sql-server.example.com/mcp"
export MCP_SQL_API_KEY="my-sql-api-key"
export MCP_GOV_URL="https://my-governance-server.example.com/mcp"
export MCP_GOV_API_KEY="my-governance-api-key"

# 2. Install dependencies (for PDF/DOCX report generation)
bash setup_env.sh

# 3. Package for the desired platform
bash ../pack_opencode.sh --agent governance-officer
# or
bash ../pack_claude_code.sh --agent governance-officer
```
