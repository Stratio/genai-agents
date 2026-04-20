# genai-agents

Collection of generative AI agents and skills that leverage the **Stratio Semantic Data Layer**, the semanticized data layer that **Stratio Governance** generates from its data domains, semantic layers, data quality rules and business terms, producing collections ready for analytical consumption. Thanks to **Stratio Virtualizer**, an Apache Spark-based engine, data access is independent of the underlying datastore and compatible with big data. The agents in this repository connect to Governance to query, analyze and generate reports on that governed data.

The repository is primarily oriented towards **OpenCode**, the open-source tool on which Stratio bases its Agent Builder in the GenAI platform. Some agents also include packages for other platforms such as **claude.ai Projects** or **Claude Desktop** (Claude Cowork).

## Agents

| Agent | Description | Platforms | Folder |
|-------|-------------|-----------|--------|
| **data-analytics** | Full BI/BA agent with advanced analysis, clustering, multi-format reports (PDF, DOCX, web, PowerPoint), read-only data quality coverage assessment and reporting, and reasoning documentation | Claude Code, OpenCode, Stratio Cowork | `data-analytics/` |
| **data-analytics-light** | Lightweight BI/BA agent oriented to chat-based analysis, with read-only data quality coverage assessment (chat-only summaries, no file generation). No formal report generation. Includes packaging scripts for multiple platforms | Claude Code, Claude Cowork, claude.ai, OpenCode | `data-analytics-light/` |
| **semantic-layer** | Agent specialized in building and maintaining semantic layers in Stratio Governance: creation of data collections (technical domains), technical terms, ontologies, business views, SQL mappings, view publishing, semantic terms and business terms | Claude Code, Claude Cowork, claude.ai, OpenCode, Stratio Cowork | `semantic-layer/` |
| **data-quality** | Data quality agent: coverage assessment, gap identification, quality rule creation with human-in-the-loop and coverage report generation | Claude Code, Claude Cowork, claude.ai, OpenCode, Stratio Cowork | `data-quality/` |
| **governance-officer** | Combined governance agent: full semantic layer building + data quality management in a single agent with unrestricted access to all governance tools | Claude Code, Claude Cowork, claude.ai, OpenCode, Stratio Cowork | `governance-officer/` |
| **skill-creator** | Agent for designing and generating AI agent skills (SKILL.md). Interactive requirements → design → generation → review → ZIP packaging | Claude Code, OpenCode, Stratio Cowork | `skill-creator/` |
| **agent-creator** | Agent for designing and generating complete AI agents for Stratio Cowork. Interactive requirements → architecture design → AGENTS.md generation → skill creation → review → agents/v1 ZIP packaging | Claude Code, OpenCode, Stratio Cowork | `agent-creator/` |

## Packaging

Scripts at the monorepo root to package any agent in the target platform format:

| Script | Target platform | Output |
|--------|----------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agent}/dist/claude_code/{name}/` |
| `pack_opencode.sh` | OpenCode | `{agent}/dist/opencode/{name}/` |
| `pack_stratio_cowork.sh` | Stratio Cowork (OpenCode) | `dist/{name}-stratio-cowork.zip` |
| `pack_shared_skills.sh` | All (standalone skills) | `dist/shared-skills.zip` or `dist/{skill}.zip` |

```bash
# Package data-analytics for Claude Code (English, default)
bash pack_claude_code.sh --agent data-analytics

# Package data-analytics for Claude Code in Spanish
bash pack_claude_code.sh --agent data-analytics --lang es

# Package data-analytics for OpenCode with a custom name
bash pack_opencode.sh --agent data-analytics --name my-agent

# Package semantic-layer for Stratio Cowork
bash pack_stratio_cowork.sh --agent semantic-layer
```

All pack scripts accept `--lang <code>` to generate output in a specific language. Without `--lang`, English is used. With `--lang es`, the output goes to `dist/es/{format}/{name}/` for traceability. The name must be kebab-case. If omitted, the basename of the agent directory is used. The generated directories are excluded from the repository (`.gitignore`).

`pack_stratio_cowork.sh` generates a composite ZIP with two sub-ZIPs designed for deployment in Stratio Cowork: one with the agent without its shared skills, and another with the shared skills separately (to distribute them independently from the agent). It also includes the agent's `mcps` file at the bundle root if it exists (see [Configure external tools](#4-configure-external-tools-mcps)).

`data-analytics-light`, `semantic-layer`, `data-quality` and `governance-officer` also include packaging scripts for the different Claude formats (AI Projects and Cowork). See [`data-analytics-light/README.md`](data-analytics-light/README.md) for detailed instructions on how to configure each format on the target platform.

### Output structure (`make package`)

All artifacts are generated under `dist/`, both at agent level (intermediates) and at root level (final versioned zips). `make package` generates artifacts for every language in the `languages` file:

```
genai-agents/
  dist/                                         # Final versioned ZIPs (EN + ES)
    data-analytics-claude-code-{v}.zip          # English
    data-analytics-claude-code-es-{v}.zip       # Spanish
    data-analytics-opencode-{v}.zip
    data-analytics-opencode-es-{v}.zip
    data-analytics-stratio-cowork-{v}.zip
    data-analytics-stratio-cowork-es-{v}.zip
    ...                                         # Same pattern for all agents
    shared-skills-{v}.zip
    shared-skills-es-{v}.zip
    shared-skill-explore-data-{v}.zip
    shared-skill-explore-data-es-{v}.zip
    ...                                         # Same pattern for all shared skills

  data-analytics/
    dist/                                       # Intermediate artifacts (EN)
      claude_code/data-analytics/
      opencode/data-analytics/
      es/                                       # Intermediate artifacts (ES)
        claude_code/data-analytics/
        opencode/data-analytics/

  data-analytics-light/
    dist/                                       # Intermediate artifacts (EN)
      claude_code/data-analytics-light/
      opencode/data-analytics-light/
      claude_cowork/data-analytics-light/
      claude_ai_projects/data-analytics-light/
      es/                                       # Intermediate artifacts (ES)
        claude_code/data-analytics-light/
        opencode/data-analytics-light/
        claude_cowork/data-analytics-light/
        claude_ai_projects/data-analytics-light/

  ...                                           # Same pattern for semantic-layer, data-quality, governance-officer
```

`make clean` removes all `dist/` directories (root + agents).

### Supported skill formats

The pack scripts recognize two skill definition formats:

| Format | Structure | Example |
|--------|-----------|---------|
| **Canonical** (recommended) | `skills/<name>/SKILL.md` | `skills/analyze/SKILL.md` |
| **Flat** | `skills/<name>.md` | `skills/analyze.md` |

The flat format is automatically normalized to canonical when packaging (`<name>.md` → `<name>/SKILL.md`).

Search locations (by priority order): `skills/` → `.claude/skills/` → `.opencode/skills/` → `.agents/skills/`.

### Memory templates

If an agent persists memory between sessions, its seed files live under `templates/memory/` (e.g. `templates/memory/MEMORY.md`). The agent's writing skills are responsible for copying the template into `output/` the first time they need to write — `**/output/` stays in `.gitignore` and pack scripts never create `output/` in the package. This keeps a single source of truth for the initial structure and avoids duplicating templates inline inside SKILL.md files.

## Shared skills

`shared-skills/` groups reusable skills across multiple agents in the monorepo. The pack scripts automatically include them in the output of each agent that declares them, without the need to duplicate code.

### Available skills

| Skill | Description | Agents that use it |
|-------|-------------|-------------------|
| `propose-knowledge` | Propose business terms and preferences to Stratio Governance after an analysis | data-analytics, data-analytics-light |
| `explore-data` | Quick exploration of domains, tables, columns and governed terminology | data-analytics, data-analytics-light |
| `stratio-data` | Stratio data MCPs reference: rules, usage patterns and best practices | (standalone) |
| `stratio-semantic-layer` | Stratio semantic layer MCPs reference: rules, usage patterns and best practices for governance tools | semantic-layer, governance-officer |
| `generate-technical-terms` | Generate or regenerate technical terms (table and column descriptions) for a domain | semantic-layer, governance-officer |
| `create-ontology` | Create or extend ontologies with interactive planning | semantic-layer, governance-officer |
| `create-business-views` | Create, regenerate or publish business views and SQL mappings from an ontology | semantic-layer, governance-officer |
| `create-sql-mappings` | Create or update SQL mappings for existing views | semantic-layer, governance-officer |
| `create-semantic-terms` | Generate or regenerate semantic business terms for views | semantic-layer, governance-officer |
| `manage-business-terms` | Create Business Terms in the dictionary with relationships to data assets | semantic-layer, governance-officer |
| `create-data-collection` | Search for tables and paths in the technical data dictionary and create a new collection (technical domain) | semantic-layer, governance-officer |
| `build-semantic-layer` | Full semantic layer pipeline: orchestrates technical terms, ontology, views, mappings and semantic terms creation | semantic-layer, governance-officer |
| `assess-quality` | Assess quality coverage by domain, table or column: dimensions covered, gaps and priorities | data-analytics, data-analytics-light, data-quality, governance-officer |
| `create-quality-rules` | Design and create quality rules to cover gaps, with mandatory human approval | data-quality, governance-officer |
| `create-quality-planification` | Create automatic execution schedules for quality rule folders | data-quality, governance-officer |
| `quality-report` | Generate a formal quality coverage report in PDF, DOCX or Markdown (in `data-analytics-light` only the Chat format is used) | data-analytics, data-analytics-light, data-quality, governance-officer |
| `pdf-reader` | Inspect, extract text, tables, images, form values and attachments from PDF files with diagnose-first strategy | data-analytics, data-quality, governance-officer |
| `pdf-writer` | Create designed PDFs, transform existing ones (merge, split, rotate, watermark, encrypt) and fill forms. Design-first workflow with custom typography | data-analytics, data-quality, governance-officer |

Shared guides (technical documentation that skills reference) live in `shared-skill-guides/`:

| Guide | Used by |
|-------|---------|
| `stratio-data-tools.md` | `explore-data`, `assess-quality`, `AGENTS.md` (data-analytics, data-analytics-light, data-quality, governance-officer) |
| `stratio-semantic-layer-tools.md` | `stratio-semantic-layer`, `build-semantic-layer`, `AGENTS.md` (semantic-layer, governance-officer) |
| `quality-exploration.md` | `assess-quality`, `create-quality-rules` (data-analytics, data-analytics-light, data-quality, governance-officer) |

### Using a shared skill in an agent

1. Create (if it doesn't exist) the `shared-skills` file in the agent folder with the skill name, one per line:

   ```
   propose-knowledge
   explore-data
   ```

2. If the agent's `AGENTS.md` directly references any guide from `shared-skill-guides/`, also declare it in `shared-guides`:

   ```
   stratio-data-tools.md
   ```

3. Package as normal — the generic pack scripts (`pack_claude_code.sh`, `pack_opencode.sh`) copy each guide declared in `skill-guides` **inside** the skill folder in the output and rewrite the references in `SKILL.md` to make them local (self-contained skill). Guides declared in the agent's `shared-guides` are also copied to `skills-guides/` so that `AGENTS.md`/`CLAUDE.md` can reference them:

   ```bash
   bash pack_claude_code.sh --agent my-agent
   ```

   Resulting output (example with `explore-data` which declares `stratio-data-tools.md`):
   ```
   .claude/
     skills/
       explore-data/
         SKILL.md                  # references "stratio-data-tools.md" (local)
         stratio-data-tools.md     # guide inside the skill
     skills-guides/
       stratio-data-tools.md       # for AGENTS.md (possible duplicate, ok)
   ```

If the agent has a skill in `skills/` with the same name, the local version takes priority over the shared one.

### Creating a new shared skill

1. Create the folder and `SKILL.md` (in English) in `shared-skills/`, and the Spanish translation in `es/`:

   ```
   shared-skills/
   └── my-skill/
       ├── SKILL.md       # Skill definition in English (self-contained or nearly so)
       └── skill-guides   # (Optional) List of shared-skill-guides it needs
   es/shared-skills/
   └── my-skill/
       └── SKILL.md       # Spanish translation
   ```

2. If the skill needs external guides, add the files in `shared-skill-guides/` (with their counterparts in `es/shared-skill-guides/`) and list them in `skill-guides`:

   ```
   # shared-skills/my-skill/skill-guides
   my-guide.md
   ```

3. Declare the skill in the agents that should include it (`shared-skills` file in each agent).

A shared skill should be as self-contained as possible: no dependencies on Python tools, styles or templates specific to an agent. If a skill depends heavily on artifacts from a specific agent, keep it as a local skill in that agent.

**SKILL.md content:** Do not reference `AGENTS.md` or `CLAUDE.md` directly — the pack scripts substitute these names depending on the platform, but a direct reference may not work correctly on some targets. Use generic phrasing such as "following the user question convention" or "according to the agent's instructions". Guide references must use the path `skills-guides/<file>` in the source — the generic pack scripts copy the guide inside the skill and rewrite the reference to make it local (self-contained).

## Internationalization (i18n)

The monorepo supports multiple languages. **English is the primary language** — files in the main tree contain English content. Translations live in a language overlay directory at the root (e.g., `es/` for Spanish) that mirrors the source tree structure:

```
genai-agents/
  shared-skills/explore-data/SKILL.md       # English (primary)
  es/shared-skills/explore-data/SKILL.md     # Spanish (overlay)
  data-analytics/AGENTS.md                   # English
  es/data-analytics/AGENTS.md                # Spanish
```

Supported languages are listed in the `languages` file at the root.

### What gets translated

All content files that the agent presents to the user or uses as instructions:

| File type | English (main tree) | Spanish (es/ overlay) | Translated? |
|-----------|--------------------|-----------------------|-------------|
| Agent instructions | `data-analytics/AGENTS.md` | `es/data-analytics/AGENTS.md` | Yes |
| Skills | `skills/analyze/SKILL.md` | `es/.../skills/analyze/SKILL.md` | Yes |
| Skill sub-guides | `analytical-patterns.md` | `es/.../analytical-patterns.md` | Yes |
| Shared skill guides | `shared-skill-guides/*.md` | `es/shared-skill-guides/*.md` | Yes |
| User READMEs | `USER_README.md` | `es/.../USER_README.md` | Yes |
| Developer READMEs | `README.md` (agents) | `es/.../README.md` | Yes |
| Cowork metadata | `cowork-metadata.yaml` | `es/.../cowork-metadata.yaml` | Yes |
| Memory templates | `templates/memory/*.md` | `es/.../templates/memory/*.md` | Yes |
| Python code, HTML, CSS | `tools/*.py`, `templates/` | — | No |
| Config files | `.mcp.json`, `opencode.json` | — | No |
| Manifests | `shared-skills`, `skill-guides` | — | No |
| Shell scripts | `pack_*.sh`, `bin/*.sh` | — | No |

Skill and folder names are **technical identifiers** and stay in English regardless of language.

### Packaging by language

All pack scripts accept `--lang <code>` to generate output in a specific language. Without `--lang`, English is used. For non-English languages, the script resolves content from the `es/` overlay via `bin/resolve-lang.sh` internally. Intermediate files go to `dist/es/...` for traceability.

```bash
# English (default)
bash pack_claude_code.sh --agent data-analytics
# → data-analytics/dist/claude_code/data-analytics/

# Spanish
bash pack_claude_code.sh --agent data-analytics --lang es
# → data-analytics/dist/es/claude_code/data-analytics/
```

`bin/package.sh` orchestrates all agents and languages, passing `--lang` to each pack script. Final versioned ZIPs go to `dist/`:

| Language | Pattern | Example |
|----------|---------|---------|
| English (primary) | `{agent}-{format}-{version}.zip` | `data-analytics-claude-code-0.1.0.zip` |
| Spanish | `{agent}-{format}-es-{version}.zip` | `data-analytics-claude-code-es-0.1.0.zip` |

### Translation workflow

When adding or modifying translatable content:

1. Write the primary file in English (e.g., `SKILL.md`)
2. Create or update the counterpart in `es/` (e.g., `es/.../SKILL.md`) with the Spanish translation
3. Run `bin/check-translations.sh` to verify completeness

### i18n helper scripts

| Script | Purpose |
|--------|---------|
| `bin/resolve-lang.sh` | Creates a temporary tree with the language overlay applied (called internally by pack scripts when `--lang` is passed) |
| `bin/check-translations.sh` | Verifies all translatable files have their counterpart in `es/` |

## Format and compatibility with development tools

The agents follow the `AGENTS.md` + `skills/` format, recognized by **OpenCode**, **Cursor**, **GitHub Copilot** plugins and other tools compatible with the agent instructions standard.

An agent is composed of:

- `AGENTS.md` (or `CLAUDE.md`) — agent instructions: role, workflow, rules (**required**)
- `skills/` — user-invocable skills (optional)
- `opencode.json` — MCP and permission configuration for OpenCode (optional)
- `.mcp.json` — MCP configuration for Claude Code / claude.ai (optional)

With these files, simply running the corresponding packaging script generates the package ready to use on the target platform.

The monorepo root includes a symlink `CLAUDE.md → AGENTS.md` so the project can be opened directly with **Claude Code** to develop new agents with its code assistant.

## Creating a new agent

This guide explains how to add an agent to the monorepo for use in **OpenCode**, **Claude Code** or the **Stratio GenAI agent framework**. An agent is composed of three pieces: **instructions** (`AGENTS.md`), **skills** (`skills/`) and **tool configuration**. By adding `opencode.json` and/or `.mcp.json` the agent can work on both platforms at once. The `pack_opencode.sh` and `pack_claude_code.sh` scripts handle packaging it for each target.

### 1. Folder structure

```
my-agent/
├── AGENTS.md              # Main instructions in English — role, workflow, rules
├── opencode.json          # OpenCode configuration (MCPs, permissions)
├── .mcp.json              # MCP configuration for Claude Code / claude.ai
├── mcps                   # (Optional) List of required MCPs for Stratio Cowork
├── skills/                # Agent-specific skills (user-invocable)
│   └── my-skill/
│       └── SKILL.md       # Skill definition (YAML frontmatter + body)
├── skills-guides/         # (Optional) Local technical guides shared between skills
├── shared-skills          # (Optional) List of shared skills from the monorepo to include
├── shared-guides          # (Optional) List of shared-skill-guides that AGENTS.md uses directly
└── templates/             # (Optional) Static templates used by the agent
    └── memory/            # (Optional) Persistent memory seed files (MEMORY.md, etc.)
```

The `skills-guides/` and `templates/memory/` directories are optional: use `skills-guides/` when multiple skills in the agent share extensive technical documentation; use `templates/memory/` only if the agent needs to persist memory between sessions (the writing skill copies the seed into `output/` on first write).

The `shared-skills` and `shared-guides` files (plain text, one entry per line) allow including skills and guides from the monorepo without duplicating them. See [Shared skills](#shared-skills) for details.

### 2. AGENTS.md — Agent instructions

Defines the agent's **role**, **workflow** and **cross-cutting rules**. Suggested structure:

```markdown
# [Agent Name]

## Role and Context
Description of the agent: what it does, who it serves, and what tools it operates with.

## Mandatory Workflow
Numbered execution phases. Example: triage → exploration → questions → plan → execution.
The more detailed, the more predictable the agent's behavior.

## Cross-cutting Rules
Rules that apply to every session (response language, mandatory validations,
tools it is forbidden to use, etc.).

## Available Skills
List of skills and when to activate each one.
```

### 3. Skills — Defining capabilities

Each skill encapsulates a specific workflow that the user can invoke (e.g.: `/analyze`, `/generate-report`). `SKILL.md` format:

```markdown
---
name: my-skill
description: Description of when to use this skill and what it does
argument-hint: [expected argument, e.g.: question or topic]
---

# Skill: My Skill

## 1. First Step
Detailed operational instructions...

## 2. Second Step
...
```

The YAML frontmatter is required: `name` is the identifier, `description` is used by the agent to decide when to activate it, `argument-hint` appears as a placeholder in the UI. The body sections are step-by-step instructions that the agent follows when executing the skill. If multiple skills share documentation, extract it to `skills-guides/` and reference it from the skill body.

To reuse skills already existing in the monorepo without duplicating them, see the [Shared skills](#shared-skills) section — the shared skills system avoids maintaining copies of identical skills in each agent.

### 4. Configure external tools (MCPs)

Each platform has its own configuration file. Both can be created so that the agent works on OpenCode and Claude Code simultaneously.

#### 4a. `opencode.json` — OpenCode

Declares the instructions, available MCPs and agent permissions:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": ["AGENTS.md"],
  "mcp": {
    "my-server": {
      "type": "remote",
      "url": "{env:MY_SERVER_URL}",
      "timeout": 90000,
      "headers": { "Authorization": "Bearer {env:MY_API_KEY}" }
    }
  },
  "permission": {
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "bash": { "*": "allow" }
  }
}
```

Environment variables are referenced with the `{env:VAR_NAME}` syntax. If the agent does not use external MCPs, omit the `mcp` block.

The `permission` block controls both bash/file commands and exposed MCP tools. For MCP tools the pattern is `{server-name}_*` (all tools from that server) or `*{tool-name}` (a specific tool on any server).

#### 4b. `.mcp.json` — Claude Code / claude.ai

Declares the MCP servers available for Claude Code:

```json
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "${MY_SERVER_URL:-http://127.0.0.1:8080/mcp}",
      "headers": { "Authorization": "Bearer ${MY_API_KEY:-}" },
      "allowedTools": ["tool_name_1", "tool_name_2"]
    }
  }
}
```

Environment variables use bash syntax `${VAR:-default_value}`. `allowedTools` restricts which tools from the MCP server are exposed to the agent. Bash and filesystem permissions are managed by Claude Code itself (outside this file).

#### 4c. `mcps` — Stratio Cowork

Plain text file (one line per MCP) that declares the MCP servers the agent needs. Only relevant for the **Stratio Cowork** bundle — `pack_stratio_cowork.sh` includes it at the root of the composite ZIP as a reference for the administrator configuring the installation.

```
Stratio_Data
Stratio_Gov
```

It has no effect on Claude Code or OpenCode packages (both scripts exclude it from their rsync). If the agent will not be distributed via Stratio Cowork, there is no need to create it.

### 5. Package

```bash
# Package for OpenCode (English, default)
bash pack_opencode.sh --agent my-agent

# Package for Claude Code
bash pack_claude_code.sh --agent my-agent

# Package for Claude Code in Spanish
bash pack_claude_code.sh --agent my-agent --lang es

# Package Stratio Cowork bundle (agent + separate shared skills + mcps)
bash pack_stratio_cowork.sh --agent my-agent

# With a custom name (kebab-case)
bash pack_opencode.sh --agent my-agent --name custom-name

# Package for all platforms and languages at once
make package
```

The output is generated in `my-agent/dist/opencode/my-agent/` (English) and `my-agent/dist/es/opencode/my-agent/` (Spanish) respectively (excluded from git by `.gitignore`).

### 6. Test

The `dist/` folder is overwritten on each packaging script run, so before opening the agent it is advisable to copy the generated package to a working path.

#### 6a. Test in OpenCode

```bash
cp -r my-agent/dist/opencode/my-agent ~/agents/my-agent
```

If `opencode.json` references environment variables for MCP servers, export them in the terminal before opening OpenCode:

```bash
export MY_SERVER_URL="https://my-server.example.com/mcp"
export MY_API_KEY="my-secret-token"
```

> **Note on TLS:** If the MCP servers use self-signed TLS certificates (common in development or pre-production environments), Node.js will reject the connection by default. To allow it, also export:
>
> ```bash
> export NODE_TLS_REJECT_UNAUTHORIZED=0
> ```
>
> This variable disables TLS certificate validation on all Node.js connections in the process. Use it **only in trusted environments** — never in production.

Then open OpenCode from the agent folder:

```bash
cd ~/agents/my-agent
opencode
```

On startup, OpenCode automatically loads `AGENTS.md` as the agent instructions, the available skills in `skills/` and connects to the MCP servers defined in `opencode.json`. Skills are invoked with `/skill-name` in the chat.

The `opencode.json` file can be manually edited at any time to add, remove or reconfigure MCP servers — just restart OpenCode for the changes to take effect.

#### 6b. Test in Claude Code

```bash
cp -r my-agent/dist/claude_code/my-agent ~/agents/my-agent-cc
export MY_SERVER_URL="https://my-server.example.com/mcp"
export MY_API_KEY="my-secret-token"
cd ~/agents/my-agent-cc
claude .
```

> **Note on TLS:** If the MCP servers use self-signed TLS certificates (common in development or pre-production environments), Node.js will reject the connection by default. To allow it, also export:
>
> ```bash
> export NODE_TLS_REJECT_UNAUTHORIZED=0
> ```
>
> This variable disables TLS certificate validation on all Node.js connections in the process. Use it **only in trusted environments** — never in production.

On startup, Claude Code loads `CLAUDE.md` as the agent instructions and the available skills in `.claude/skills/`. MCP servers are read from `.mcp.json`. Skills are invoked with `/skill-name` in the chat.

#### 6c. Test in Claude Desktop / Claude Cowork

Claude Cowork runs inside the Claude Desktop Electron process. Both share the same system-level configuration file: `claude_desktop_config.json`.

> **Important:** `claude_desktop_config.json` does **not** support `"type": "http"` for remote servers, nor the `${VAR:-default}` environment variable syntax used by Claude Code's `.mcp.json`. These are Claude Code CLI features only. See the differences below.

##### Claude Cowork (with plugins)

If you use Claude Cowork with the plugin generated by `pack_claude_cowork.sh`, the MCP servers are registered automatically when you install the plugin ZIP — no manual `claude_desktop_config.json` editing is needed.

> **Always package with `--url` / `--key`** (or `--sql-url`, `--gov-url`, etc.) to hardcode credentials into the plugin. Cowork does **not** expand `${VAR:-default}` templates in the plugin's `.mcp.json` — that syntax only works in Claude Code CLI.

##### Claude Desktop without Cowork (manual MCP configuration)

Desktop applications are not launched from a terminal, so `export` commands do not reach them. MCP servers must be configured in:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Local MCP servers** (`command` + `args`):

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"],
      "env": {
        "NODE_TLS_REJECT_UNAUTHORIZED": "0",
        "MY_SERVER_URL": "https://my-server.example.com/mcp"
      }
    }
  }
}
```

**Remote HTTP MCP servers** (via `mcp-remote` proxy):

Claude Desktop does not support remote HTTP servers natively. Use the [`mcp-remote`](https://www.npmjs.com/package/mcp-remote) npm package as a stdio-to-HTTP proxy:

```json
{
  "mcpServers": {
    "stratio_data": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://sql.example.com/mcp",
        "--header", "X-API-Key:${MCP_API_KEY}",
        "--header", "Authorization:${MCP_AUTH}"
      ],
      "env": {
        "MCP_API_KEY": "my-api-key",
        "MCP_AUTH": "Bearer my-api-key",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  }
}
```

> **Note:** Header values are placed in the `env` block and referenced in `args` without a space after the colon (e.g., `Authorization:${MCP_AUTH}` instead of `Authorization: ${MCP_AUTH}`). This works around a known bug in Claude Desktop on Windows where spaces inside args are not escaped properly. The `env` block passes environment variables to the `mcp-remote` child process, which expands `${VAR}` references from its environment. `NODE_TLS_REJECT_UNAUTHORIZED=0` disables TLS certificate validation — use only in trusted environments with self-signed certificates.

##### TLS for remote MCP servers (OS-level)

When using `mcp-remote` as shown above, the `NODE_TLS_REJECT_UNAUTHORIZED` variable in the `env` block is usually sufficient because `mcp-remote` is a Node.js child process that inherits it.

For other scenarios where there is no child process to configure (e.g., Custom Connectors configured through the Cowork UI), the Electron process itself makes the TLS connection. In that case, set the variable at the OS level:

##### macOS

**Option A — Launch from terminal (quick, non-persistent):**

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 open -a "Claude"
```

The environment variable is inherited by the Electron process. This must be done every time the app is opened.

**Option B — `launchctl setenv` (persistent for the GUI session):**

```bash
launchctl setenv NODE_TLS_REJECT_UNAUTHORIZED 0
```

Then restart Claude Desktop / Claude Cowork. The variable applies to **all** GUI applications in the session. To revert:

```bash
launchctl unsetenv NODE_TLS_REJECT_UNAUTHORIZED
```

##### Windows

**Option A — Launch from terminal (quick, non-persistent):**

CMD:

```cmd
set NODE_TLS_REJECT_UNAUTHORIZED=0 && start Claude
```

PowerShell:

```powershell
$env:NODE_TLS_REJECT_UNAUTHORIZED="0"; Start-Process Claude
```

This must be done every time the app is opened.

**Option B — User environment variable (persistent):**

PowerShell:

```powershell
[System.Environment]::SetEnvironmentVariable("NODE_TLS_REJECT_UNAUTHORIZED", "0", "User")
```

Or manually: **System Settings > Environment Variables > User variables > New** — name `NODE_TLS_REJECT_UNAUTHORIZED`, value `0`.

Then restart Claude Desktop / Claude Cowork. To revert:

```powershell
[System.Environment]::SetEnvironmentVariable("NODE_TLS_REJECT_UNAUTHORIZED", $null, "User")
```

> Both options disable TLS certificate validation on all Node.js connections in the process. Use them **only in trusted environments** — never in production.
