# data-analytics-light

Lightweight Business Intelligence and Business Analytics agent. Same analytical engine as `data-analytics`, but oriented to conversation: the primary output is the chat, without formal report generation.

## Capabilities

- Querying governed data via MCP (Stratio SQL server)
- Advanced analysis with Python (pandas, numpy, scipy)
- Professional visualizations (matplotlib, seaborn, plotly)
- Direct chat output with actionable insights
- **Data quality coverage assessment** and quality summaries in chat (read-only, no file generation, no rule creation). `/quality-report` produces file formats by delegating to the writer skills (pdf-writer, docx-writer, pptx-writer, web-craft, canvas-craft). This agent declares only `quality-report` (not writers), so only Chat format is available. For PDF / DOCX / PPTX / Dashboard / Poster quality reports, use the full `data-analytics` agent.

## Requirements

- Python 3.10+ with the dependencies listed in `requirements.txt`. Install with `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`. No system packages needed (this agent has no PDF/OCR stack)
- Access to two Stratio MCP servers (configured in `.mcp.json` for Claude Code / claude.ai and in `opencode.json` for OpenCode):
  - **Data MCP** (`stratio_data`): via `MCP_SQL_URL` and `MCP_SQL_API_KEY` env vars — mandatory for analytical workflows
  - **Governance MCP** (`stratio_gov`): via `MCP_GOV_URL` and `MCP_GOV_API_KEY` env vars — needed for quality coverage assessment (chat only). Only the read tool `get_quality_rule_dimensions` is allowed; write operations (rule creation/scheduling, AI metadata regeneration via `quality_rules_metadata`) are intentionally denied

## Packaging scripts

All scripts are non-interactive (CI/CD-friendly). If `--name` is not provided, they default to `data-analytics-light`. All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish). When `--lang` is used, output goes to `dist/<lang>/...` instead of `dist/...`.

### Specific scripts (from this folder)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<name>/` | `bash pack_claude_ai_project.sh --name data-analytics-light` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<name>/` | `bash pack_claude_cowork.sh --name data-analytics-light` |

The cowork script also accepts `--url <MCP_URL>` and `--key <API_KEY>`. If omitted, they remain as environment variable templates to be configured later.

### Generic scripts (from the monorepo root)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent data-analytics-light` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent data-analytics-light` |

### Files included per package

| Source file | `claude_ai_project` | `claude_cowork` | `claude_code` | `opencode` |
|---|---|---|---|---|
| `AGENTS.md` | ✅ → `CLAUDE.md` | ✅ → `CLAUDE.md`¹ | ✅ → `CLAUDE.md` | ✅ → `AGENTS.md` |
| `requirements.txt` | ✅ | ❌ | ✅ | ✅ |
| `skills/` | ✅² | ✅ (in ZIP) | ✅ (in `.claude/skills/`) | ✅ (in `.opencode/skills/`) |
| `skills-guides/` | ✅³ | ✅ (in ZIP) | ✅⁴ | ✅⁴ |
| `.mcp.json` | ❌ | ✅ (in ZIP) | ✅ | ❌ |
| `opencode.json` | ❌ | ❌ | ❌ | ✅ |
| `plugin.json` | ❌ | ✅ (in ZIP) | ❌ | ❌ |
| `.claude/settings.local.json` | ❌ | ❌ | ✅ | ❌ |

¹ Generated (not a direct copy): `skills-guides/` references → `skills/analyze/`, placeholder `{{TOOL_QUESTIONS}}` resolved.
² Flattened to root: `analyze.md`, `analyze_*.md`, `explore-data.md`, `propose-knowledge.md`; guides prefixed: `skills-guides_stratio-data-tools.md`.
³ Guides renamed with prefix: `skills-guides_stratio-data-tools.md`.
⁴ Guides inside each skill (self-contained) + in `skills-guides/` for references from `CLAUDE.md`/`AGENTS.md`.

### Packaging as Claude Cowork

Generates a package to configure the agent in Claude Cowork without replacing the orchestrator. The script builds the plugin internally (skills + MCP, without agent) and combines it with the agent instructions. It produces two files:

| File | What it is | What it is for |
|------|-----------|----------------|
| `CLAUDE.md` | Folder instructions (generated from AGENTS.md) | Agent instructions — Cowork reads them automatically from the working directory |
| `<name>.zip` | Plugin ZIP (skills + MCP only, without agent) | Installed as a plugin in Cowork; provides the skills and MCP connection |

> **Note:** Claude plugins do not include agent instructions (CLAUDE.md) — only skills, MCP, and hooks. That is why the `CLAUDE.md` goes separately, as a file in the working directory.

```bash
bash pack_claude_cowork.sh --name data-analytics-light --url https://mcp.example.com --key my-api-key
```

The result is located in `dist/claude_cowork/data-analytics-light/`.

**How to use it in Cowork:**

1. Copy `CLAUDE.md` to the working directory of the project in Cowork — Cowork reads it automatically as folder instructions
3. Install `<name>.zip` as a plugin in Cowork (provides the skills `/analyze`, `/explore-data`, `/propose-knowledge` and the MCP connection)
4. The Cowork orchestrator reads the instructions from `CLAUDE.md` and delegates to the plugin skills when appropriate

> **MCP configuration:** The plugin ZIP includes a `.mcp.json` that registers the MCP servers automatically when installed in Cowork. Always package with `--url` and `--key` to hardcode credentials — Cowork (which runs inside Claude Desktop) does **not** expand `${VAR:-default}` templates; that syntax only works in Claude Code CLI. If you need to use the agent in Claude Desktop without Cowork (no plugin support), configure the MCP servers manually in `claude_desktop_config.json` using the `mcp-remote` proxy — see section [6c of the root README](../README.md#6c-test-in-claude-desktop--claude-cowork) for the format.

### Packaging as Claude AI Project (claude.ai)

Generates the flattened files (skills, guides, requirements):

```bash
bash pack_claude_ai_project.sh --name data-analytics-light
```

To configure it in claude.ai:

1. Create a new **Project** in [claude.ai](https://claude.ai)
2. Open `dist/claude_ai_projects/data-analytics-light/` and upload **all files** (except `CLAUDE.md`) to the project's files section
3. Open `CLAUDE.md` from the generated package, copy **all its content** and paste it into the project's **Instructions** field
4. Save the project — the agent will be ready to use

## Compatibility

To use with any platform, package with the corresponding script:

- **Claude Code**: Package with `pack_claude_code.sh` to use with Claude Code.
- **OpenCode**: Package with `pack_opencode.sh` to use with OpenCode.

The pack scripts generate the correct format for each platform (renaming files, relocating skills, etc.).

## Available skills

| Skill | Command | Origin | Description |
|-------|---------|--------|-------------|
| Analysis | `/analyze` | local | BI/BA data analysis: domain discovery, EDA, KPI planning, MCP queries, Python analysis, and visualizations |
| Exploration | `/explore-data` | **shared** | Quick exploration of domains, tables, columns, and business terminology |
| Quality assessment | `/assess-quality` | **shared** | Assess quality coverage for a domain, table, or column; identify dimensions covered, gaps, and priorities |
| Quality report | `/quality-report` | **shared** | Generate a quality coverage report. In this lightweight agent, **only the `Chat` format** is used (no file generation) |
| Knowledge | `/propose-knowledge` | **shared** | Propose discovered business terms to Stratio Governance |

Skills marked as **shared** live in `shared-skills/` at the monorepo root and are shared with `data-analytics`. Local skills live in this agent's `skills/`.

**Note**: This agent does not use persistent file-based memory — the primary output is the chat.
