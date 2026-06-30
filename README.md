# genai-agents

Collection of generative AI agents and skills that leverage the **Stratio Semantic Data Layer**, the semanticized data layer that **Stratio Governance** generates from its data domains, semantic layers, data quality rules and business terms, producing collections ready for analytical consumption. Thanks to **Stratio Virtualizer**, an Apache Spark-based engine, data access is independent of the underlying datastore and compatible with big data. The agents in this repository connect to Governance to query, analyze and generate reports on that governed data.

The repository is oriented towards **OpenCode**, the open-source tool on which Stratio bases its Agent Builder in the GenAI platform, and **Stratio Cowork** (`agents/v1` deployable bundles).

## Agents

The monorepo currently ships six agents (BI/BA analytics, semantic-layer construction, data quality, combined governance, plus authoring agents for skills and full agents). The full catalogue with a one-line description per agent, the per-agent folder structure and the workflow to add a new agent lives in [`agents/README.md`](agents/).

## Functional plugins

A **functional plugin** bundles one or more agents and/or shared skills into a single deployable unit that solves a vertical of business (e.g. data governance, document productivity, data storytelling). Plugins are an additive packaging layer on top of the per-agent and per-skill artifacts: the individual ZIPs are still produced, and a plugin can include any subset of them.

Plugins live in `plugins/<name>/` with two files:

- `plugin.yaml` — declarative manifest (name, description, tags, contents, MCPs, platforms).
- `README.md` — user-facing documentation (purpose, contents, install instructions).

Each plugin is packaged for two targets: a **Stratio Cowork** wrapper bundle (deployable via `genai-api`) and a **Claude marketplace plugin** (`.claude-plugin/plugin.json`).

The catalogue of available plugins, platform rules, output structure, install workflow and the workflow to add a new one live in [`plugins/README.md`](plugins/).

## Packaging

Scripts at the monorepo root to package agents, skills and plugins:

| Script | Target | Output |
|--------|--------|--------|
| `pack_opencode.sh` | OpenCode (developer testing) | `{agent}/dist/[{lang}/]opencode/{name}/` |
| `pack_stratio_cowork.sh` | Stratio Cowork (`agents/v1` deployable bundle) | `dist/{name}-stratio-cowork.zip` |
| `pack_skills.sh` | Bulk skills ZIP and individual skill ZIPs | `dist/skills.zip` or `dist/{skill}.zip` |
| `pack_plugin.sh` | Functional plugins (`stratio-cowork` wrapper or `claude` marketplace) | `dist/{plugin}-{platform}.zip` |

```bash
# Package data-analytics-officer for OpenCode (English, default)
bash pack_opencode.sh --agent data-analytics-officer

# Package data-analytics-officer for OpenCode in Spanish
bash pack_opencode.sh --agent data-analytics-officer --lang es

# Package semantic-layer for Stratio Cowork
bash pack_stratio_cowork.sh --agent semantic-layer

# Package the stratio-governance plugin
bash pack_plugin.sh --plugin stratio-governance --platform stratio-cowork
```

All pack scripts accept `--lang <code>` to generate output in a specific language. Without `--lang`, English is used. With `--lang es`, the output goes to `dist/es/{format}/{name}/` for traceability. The name must be kebab-case. If omitted, the basename of the agent directory is used. The generated directories are excluded from the repository (`.gitignore`).

`pack_stratio_cowork.sh` generates a composite ZIP with two sub-ZIPs designed for deployment in Stratio Cowork: one with the agent without its shared skills, and another with the shared skills separately (to distribute them independently from the agent). It also includes the agent's `mcps` file at the bundle root if it exists (see [Configure external tools](#4-configure-external-tools-mcps)).

### Output structure (`make package`)

All artifacts are generated under `dist/`, both at agent level (intermediates) and at root level (final versioned zips). `make package` generates artifacts for every language in the `languages` file:

```
genai-agents/
  dist/                                                # Final versioned ZIPs (EN + ES)
    agent-data-analytics-officer-opencode-{v}.zip              # Per-agent OpenCode bundles
    agent-data-analytics-officer-opencode-es-{v}.zip
    agent-data-analytics-officer-stratio-cowork-{v}.zip        # Per-agent Stratio Cowork bundles
    agent-data-analytics-officer-stratio-cowork-es-{v}.zip
    ...                                                # Same pattern for all 6 agents
    skills-{v}.zip                                     # Bulk skills bundle
    skills-es-{v}.zip
    skill-explore-data-{v}.zip                         # Individual skill bundles
    skill-explore-data-es-{v}.zip
    ...                                                # Same pattern for all skills
    plugin-stratio-governance-stratio-cowork-{v}.zip   # Functional plugins (verticals)
    plugin-stratio-productivity-claude-{v}.zip
    ...                                                # Same pattern for each plugin × platform

  agents/
    data-analytics-officer/
      dist/                                     # Intermediate artifacts (EN)
        opencode/data-analytics-officer/
        es/                                     # Intermediate artifacts (ES)
          opencode/data-analytics-officer/
    ...                                         # Same pattern for the other 5 agents
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

## System dependencies

Several skills and Python libraries require OS-level packages that `pip` cannot install. The table below is the single source of truth. Each agent's `README.md` and each skill's `README.md` references this section instead of duplicating the list.

**In Stratio Cowork**, the sandbox image (`genai-agents-sandbox`) provides all of these plus the Python stack. No action is needed.

**In dev local**, install them yourself with the commands below.

| System package | Provides | Python libs that depend on it | Agents that need it |
|---|---|---|---|
| `poppler-utils` (Debian/Ubuntu) / `poppler` (Homebrew) | `pdfinfo`, `pdftotext`, `pdftoppm`, `pdfimages`, `pdfdetach`, `pdffonts` | `pdf2image`, `ocrmypdf`; diagnostic commands used directly by `pdf-reader` | `data-analytics-officer`, `data-quality`, `data-governance-officer` |
| `qpdf` | CLI merge/split/rotate, repair | — (used as CLI fallback by `pdf-writer` and `pdf-reader`) | `data-analytics-officer`, `data-quality`, `data-governance-officer` |
| `pdftk-java` (Debian/Ubuntu, provides `pdftk` via update-alternatives) / `pdftk-java` (Homebrew) | Form-field inspection, robust flattening | — (used directly by `pdf-writer/FORMS.md` and `pdf-reader` forms flow) | `data-analytics-officer`, `data-quality`, `data-governance-officer` |
| `tesseract-ocr` + language packs (`tesseract-ocr-eng`, `tesseract-ocr-spa`, `-fra`, `-deu`, …) | OCR engine | `pytesseract`, `ocrmypdf` | `data-analytics-officer`, `data-quality`, `data-governance-officer` |
| `ghostscript` | PDF/A conversion, repair, last-resort flattening | `ocrmypdf`; also used directly by `pdf-writer` | `data-analytics-officer`, `data-quality`, `data-governance-officer` |
| `libcairo2` + `libpango-1.0-0` + `libpangoft2-1.0-0` (Debian/Ubuntu) / `cairo` + `pango` (Homebrew) | Cairo graphics + Pango text layout | `weasyprint` | `data-analytics-officer`, `data-quality`, `data-governance-officer` |

Install everything on Debian/Ubuntu (24.04):

```bash
sudo apt update && sudo apt install -y \
    poppler-utils qpdf pdftk-java ghostscript \
    tesseract-ocr tesseract-ocr-eng tesseract-ocr-spa tesseract-ocr-fra tesseract-ocr-deu \
    libcairo2 libpango-1.0-0 libpangoft2-1.0-0
```

Install on macOS (Homebrew):

```bash
brew install poppler qpdf pdftk-java ghostscript tesseract tesseract-lang cairo pango
```

Install Python stack (dev local, Ubuntu 24.04 — use a venv, PEP 668 rejects system-wide installs):

```bash
cd <agent-dir>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Notes:

- `semantic-layer`, `skill-creator` and `agent-creator` do not require any of these system packages — they do not declare `pdf-reader`, `pdf-writer`, `canvas-craft` or the WeasyPrint-based report skills.
- `web-craft` emits HTML/CSS/JS only; it needs no system or Python dependencies at runtime.
- For digital-signature inspection in `pdf-reader`, install `pyhanko` on demand (`pip install pyhanko`). It is not part of the baseline `requirements.txt`.
- Each skill's `README.md` lists its own Python and system dependencies — useful when declaring a new agent as a subset.

## Shared skills

`skills/` groups skills imported by more than one agent. The pack scripts inline a shared skill into each agent's bundle at packaging time, so there is no need to duplicate copies in every agent folder.

The full catalogue (skills grouped by family — Stratio MCPs, semantic-layer pipeline, data quality, office document I/O, visual craftsmanship, platform/meta), the rules for adding a new shared skill and the import workflow for agents live in [`skills/README.md`](skills/). The shared technical guides referenced by both skills and agents live in [`guides/`](guides/) — see [`guides/README.md`](guides/) for the catalogue and the path conventions used by the pack scripts.

## Internationalization (i18n)

The monorepo supports multiple languages. **English is the primary language** — files in the main tree contain English content. Translations live in a language overlay directory at the root (e.g., `es/` for Spanish) that mirrors the source tree structure:

```
genai-agents/
  skills/explore-data/SKILL.md       # English (primary)
  es/skills/explore-data/SKILL.md     # Spanish (overlay)
  agents/data-analytics-officer/AGENTS.md            # English
  es/agents/data-analytics-officer/AGENTS.md         # Spanish
```

Supported languages are listed in the `languages` file at the root.

### What gets translated

All content files that the agent presents to the user or uses as instructions:

| File type | English (main tree) | Spanish (es/ overlay) | Translated? |
|-----------|--------------------|-----------------------|-------------|
| Agent instructions | `agents/data-analytics-officer/AGENTS.md` | `es/agents/data-analytics-officer/AGENTS.md` | Yes |
| Skills | `skills/analyze/SKILL.md` | `es/.../skills/analyze/SKILL.md` | Yes |
| Skill sub-guides | `analytical-patterns.md` | `es/.../analytical-patterns.md` | Yes |
| Shared skill guides | `guides/*.md` | `es/guides/*.md` | Yes |
| User READMEs | `USER_README.md` | `es/.../USER_README.md` | Yes |
| Per-artifact developer READMEs | `agents/<name>/README.md`, `plugins/<name>/README.md`, `skills/<name>/README.md` | `es/.../README.md` | Yes |
| Top-level folder READMEs | `agents/README.md`, `guides/README.md`, `plugins/README.md`, `skills/README.md` | — | **No** — they are repo-only metadocumentation, never bundled |
| Repository root README | `README.md` | — | **No** — same reason as above |
| Cowork metadata | `cowork-metadata.yaml` | `es/.../cowork-metadata.yaml` | Yes |
| Python code, HTML, CSS | `tools/*.py`, `templates/` | — | No |
| Config files | `.mcp.json`, `opencode.json` | — | No |
| Manifests | `imported-skills`, `guides`, `plugin.yaml` | — | No |
| Shell scripts | `pack_*.sh`, `bin/*.sh` | — | No |

Skill and folder names are **technical identifiers** and stay in English regardless of language.

The distinction between *per-artifact* and *top-level folder* READMEs matters: per-artifact READMEs (one per agent / plugin / shared skill) end up inside the packaged ZIPs that ship to users, so they need a Spanish overlay. Top-level folder READMEs are catalogue / how-to pages whose only consumer is someone browsing the repository on GitHub — they never enter any bundle, so they are kept English-only to avoid pointless translation churn.

### Packaging by language

All pack scripts accept `--lang <code>` to generate output in a specific language. Without `--lang`, English is used. For non-English languages, the script resolves content from the `es/` overlay via `bin/resolve-lang.sh` internally. Intermediate files go to `dist/es/...` for traceability.

```bash
# English (default)
bash pack_opencode.sh --agent data-analytics-officer
# → data-analytics-officer/dist/opencode/data-analytics-officer/

# Spanish
bash pack_opencode.sh --agent data-analytics-officer --lang es
# → data-analytics-officer/dist/es/opencode/data-analytics-officer/
```

`bin/package.sh` orchestrates all agents and languages, passing `--lang` to each pack script. Final versioned ZIPs go to `dist/`:

| Type | Pattern | Example |
|----------|---------|---------|
| Agent (English) | `agent-{name}-{format}-{version}.zip` | `agent-data-analytics-officer-opencode-0.2.0.zip` |
| Agent (Spanish) | `agent-{name}-{format}-es-{version}.zip` | `agent-data-analytics-officer-opencode-es-0.2.0.zip` |
| Skill | `skill-{name}-[es-]{version}.zip` | `skill-stratio-data-0.2.0.zip` |
| Bulk skills | `skills-[es-]{version}.zip` | `skills-0.2.0.zip` |
| Plugin | `plugin-{name}-{platform}-[es-]{version}.zip` | `plugin-stratio-governance-stratio-cowork-0.2.0.zip` |

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
- `mcps` — list of MCP names required by this agent on Stratio Cowork (optional, one name per line)

With these files, simply running the corresponding packaging script generates the package ready to use on the target platform.

The monorepo root includes a symlink `CLAUDE.md → AGENTS.md` so the project can be opened with **Claude Code** to develop new agents with its code assistant.

## Creating a new agent

This guide explains how to add an agent to the monorepo for use in **OpenCode** or the **Stratio GenAI agent framework**. An agent is composed of three pieces: **instructions** (`AGENTS.md`), **skills** (`skills/`) and **tool configuration**. The `pack_opencode.sh` script handles packaging it for OpenCode; `pack_stratio_cowork.sh` produces the `agents/v1` bundle deployable to Stratio Cowork via the `cowork-api` shared skill.

### 1. Folder structure

```
my-agent/
├── AGENTS.md              # Main instructions in English — role, workflow, rules
├── opencode.json          # OpenCode configuration (MCPs, permissions)
├── mcps                   # (Optional) List of required MCPs for Stratio Cowork
├── skills/                # Agent-specific skills (user-invocable)
│   └── my-skill/
│       └── SKILL.md       # Skill definition (YAML frontmatter + body)
├── imported-skills        # (Optional) List of shared skills imported from the monorepo
├── guides                 # (Optional) List of root-level guides that AGENTS.md uses directly
└── templates/             # (Optional) Static templates used by the agent
```

The `imported-skills` and `guides` files (plain text, one entry per line) allow including skills and guides from the monorepo without duplicating them. See [Shared skills](#shared-skills) for details.

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

The YAML frontmatter is required: `name` is the identifier, `description` is used by the agent to decide when to activate it, `argument-hint` appears as a placeholder in the UI. The body sections are step-by-step instructions that the agent follows when executing the skill. If multiple skills share documentation, extract it to `guides/` and reference it from the skill body.

To reuse skills already existing in the monorepo without duplicating them, see the [Shared skills](#shared-skills) section — the shared skills system avoids maintaining copies of identical skills in each agent.

### 4. Configure external tools (MCPs)

There are two configuration files: `opencode.json` for the OpenCode runtime (testing and Stratio Cowork deployment) and `mcps` for Stratio Cowork's `agents/v1` bundle metadata.

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

#### 4b. `mcps` — Stratio Cowork

Plain text file (one line per MCP) that declares the MCP servers the agent needs. Only relevant for the **Stratio Cowork** bundle — `pack_stratio_cowork.sh` includes it at the root of the composite ZIP as a reference for the administrator configuring the installation.

```
Stratio_Data
Stratio_Gov
```

It has no effect on the OpenCode package (`pack_opencode.sh` excludes it from its rsync). If the agent will not be distributed via Stratio Cowork, there is no need to create it.

### 5. Package

```bash
# Package for OpenCode (English, default)
bash pack_opencode.sh --agent my-agent

# Package for OpenCode in Spanish
bash pack_opencode.sh --agent my-agent --lang es

# Package Stratio Cowork bundle (agent + separate shared skills + mcps)
bash pack_stratio_cowork.sh --agent my-agent

# With a custom name (kebab-case)
bash pack_opencode.sh --agent my-agent --name custom-name

# Package for all platforms and languages at once
make package
```

The output is generated in `my-agent/dist/opencode/my-agent/` (English) and `my-agent/dist/es/opencode/my-agent/` (Spanish) respectively (excluded from git by `.gitignore`).

### 6. Test in OpenCode

The `dist/` folder is overwritten on each packaging script run, so before opening the agent it is advisable to copy the generated package to a working path.

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


### 7. Deploy to Stratio Cowork

To register the agent (or a plugin that bundles it) into a Stratio Cowork tenant, use the [`cowork-api`](skills/cowork-api/) shared skill from inside the sandbox. It calls `/v1/agents/bundle/import` (single-agent bundles) or `/v1/agents/skills/bundle/import` (skills) and orchestrates plugin uploads via the `upload-plugin` task. See the skill's tasks for endpoint, conflict-strategy and authentication details.
