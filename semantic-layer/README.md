# semantic-layer

Agent specialized in building and maintaining semantic layers in Stratio Data Governance.

## Capabilities

- Building semantic layers via governance MCPs (`stratio_gov` server)
- Exploring technical domains and published semantic layers (`stratio_data` server)
- Complete 5-phase pipeline: technical terms → ontology → business views → SQL mappings → semantic terms
- Interactive ontology planning (with reading of local files .owl/.ttl, CSVs, business documents)
- Diagnosing the status of a domain's semantic layer
- Managing business terms in the governance dictionary
- Creating data collections (technical domains) from data dictionary searches

This agent does not execute data queries, does not generate files on disk, and does not analyze data — its output is interaction with governance MCP tools + summaries in chat.

## Requirements

- Access to two Stratio MCP servers:
  - `stratio_gov` (governance): creation and management of semantic artifacts
  - `stratio_data` (exploration): domain and data dictionary queries
- Environment variables: `MCP_GOV_URL`, `MCP_GOV_API_KEY`, `MCP_SQL_URL`, `MCP_SQL_API_KEY`
- Preconfigured setup in `.mcp.json` (Claude Code / claude.ai) and in `opencode.json` (OpenCode), both preconfigured to read the URL and credentials from environment variables

## Packaging scripts

All scripts are non-interactive (CI/CD-friendly). If `--name` is not provided, they default to `semantic-layer`. All scripts accept `--lang <code>` to generate output in a specific language (e.g., `--lang es` for Spanish). When `--lang` is used, output goes to `dist/<lang>/...` instead of `dist/...`.

### Specific scripts (from this folder)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_ai_project.sh` | claude.ai (Projects) | `dist/claude_ai_projects/<name>/` | `bash pack_claude_ai_project.sh --name semantic-layer` |
| `pack_claude_cowork.sh` | Claude Cowork | `dist/claude_cowork/<name>/` | `bash pack_claude_cowork.sh --name semantic-layer` |

The cowork script also accepts `--gov-url <URL>`, `--gov-key <KEY>`, `--sql-url <URL>`, and `--sql-key <KEY>` to configure the two MCP servers. If omitted, they remain as environment variable templates for later configuration.

### Generic scripts (from the monorepo root)

| Script | Target platform | Output | Example |
|--------|----------------|--------|---------|
| `pack_claude_code.sh` | Claude Code CLI | `dist/claude_code/<name>/` | `bash ../pack_claude_code.sh --agent semantic-layer` |
| `pack_opencode.sh` | OpenCode | `dist/opencode/<name>/` | `bash ../pack_opencode.sh --agent semantic-layer` |

### Files included per package

| Source file | `claude_ai_project` | `claude_cowork` | `claude_code` | `opencode` |
|---|---|---|---|---|
| `AGENTS.md` | ✅ → `CLAUDE.md` | ✅ → `CLAUDE.md`¹ | ✅ → `CLAUDE.md` | ✅ → `AGENTS.md` |
| `skills/` | ✅² | ✅ (in ZIP) | ✅ (in `.claude/skills/`) | ✅ (in `.opencode/skills/`) |
| `skills-guides/` | ✅³ | ✅ (in ZIP) | ✅⁴ | ✅⁴ |
| `.mcp.json` | ❌ | ✅ (in ZIP) | ✅ | ❌ |
| `opencode.json` | ❌ | ❌ | ❌ | ✅ |
| `plugin.json` | ❌ | ✅ (in ZIP) | ❌ | ❌ |
| `.claude/settings.local.json` | ❌ | ❌ | ✅ | ❌ |

¹ Generated (not a direct copy): `skills-guides/` references → `skills/stratio-semantic-layer/`, placeholder `{{TOOL_PREGUNTAS}}` resolved.
² Flattened at root: `build-semantic-layer.md`, `stratio-semantic-layer.md`, `generate-technical-terms.md`, etc.; guides prefixed: `skills-guides_stratio-semantic-layer-tools.md`.
³ Guides renamed with prefix: `skills-guides_stratio-semantic-layer-tools.md`.
⁴ Guides inside each skill (self-contained) + in `skills-guides/` for references from `CLAUDE.md`/`AGENTS.md`.

### Packaging as Claude Cowork

Generates a package to configure the agent in Claude Cowork without replacing the orchestrator. The script builds the plugin internally (skills + MCP, without agent) and combines it with the agent instructions. It produces two files:

| File | What it is | What it is for |
|------|-----------|----------------|
| `CLAUDE.md` | Folder instructions (generated from AGENTS.md) | Agent instructions — Cowork reads them automatically from the working directory |
| `<name>.zip` | Plugin ZIP (only skills + MCP, without agent) | Installed as a plugin in Cowork; provides the skills and the MCP connection |

> **Note:** Claude plugins do not include agent instructions (CLAUDE.md) — only skills, MCP, and hooks. That is why `CLAUDE.md` goes separately, as a file in the working directory.

```bash
bash pack_claude_cowork.sh --name semantic-layer --gov-url https://gov.example.com --sql-url https://sql.example.com
```

The result is located in `dist/claude_cowork/semantic-layer/`.

**How to use it in Cowork:**

1. Copy `CLAUDE.md` to the project's working directory in Cowork — Cowork reads it automatically as folder instructions
3. Install `<name>.zip` as a plugin in Cowork (provides the skills `/build-semantic-layer`, `/stratio-semantic-layer`, `/generate-technical-terms`, `/create-ontology`, `/create-business-views`, `/create-sql-mappings`, `/create-semantic-terms`, `/manage-business-terms`, `/create-data-collection` and the MCP connection)
4. The Cowork orchestrator reads the instructions from `CLAUDE.md` and delegates to the plugin skills when appropriate

### Packaging as Claude AI Project (claude.ai)

Generates the flattened files (skills, guides):

```bash
bash pack_claude_ai_project.sh --name semantic-layer
```

To configure it in claude.ai:

1. Create a new **Project** in [claude.ai](https://claude.ai)
2. Open `dist/claude_ai_projects/semantic-layer/` and upload **all files** (except `CLAUDE.md`) to the project's files section
3. Open the generated `CLAUDE.md` from the package, copy **all its content**, and paste it into the project's **Instructions** field
4. Save the project — the agent will be ready to use

## Compatibility

To use with any platform, package with the corresponding script:

- **Claude Code**: Package with `pack_claude_code.sh` for use with Claude Code.
- **OpenCode**: Package with `pack_opencode.sh` for use with OpenCode.

The pack scripts generate the correct format for each platform (renaming files, relocating skills, etc.).

## Available skills

| Skill | Command | Description |
|-------|---------|-------------|
| Full pipeline | `/build-semantic-layer` | 5-phase pipeline to build the semantic layer of a domain |
| Semantic MCP reference | `/stratio-semantic-layer` | Governance MCP tools reference: rules, patterns, and best practices |
| Technical terms | `/generate-technical-terms` | Generate technical descriptions of tables and columns |
| Ontology | `/create-ontology` | Create, extend, or delete ontology classes with interactive planning |
| Business views | `/create-business-views` | Create, regenerate, or delete business views from an ontology |
| SQL Mappings | `/create-sql-mappings` | Create or update SQL mappings for existing views |
| Semantic terms | `/create-semantic-terms` | Generate business semantic terms for the views of a domain |
| Business Terms | `/manage-business-terms` | Create Business Terms with relationships to data assets |
| Data collection | `/create-data-collection` | Search tables in the dictionary and create a new data collection |

All skills live in `shared-skills/` at the monorepo root and are shared with the governance-officer agent.

**Note**: This agent does not use persistent memory in files nor generates files on disk — the main output is interaction with MCP tools + summaries in chat.
