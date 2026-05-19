# genai-agents

Collection of generative AI agents and skills that leverage the **Stratio Semantic Data Layer**, the semanticized data layer that **Stratio Governance** generates from its data domains, semantic layers, data quality rules and business terms, producing collections ready for analytical consumption. Thanks to **Stratio Virtualizer**, an Apache Spark-based engine, data access is independent of the underlying datastore and compatible with big data. The agents in this repository connect to Governance to query, analyze and generate reports on that governed data.

The repository is oriented towards **OpenCode**, the open-source tool on which Stratio bases its Agent Builder in the GenAI platform, and **Stratio Cowork** (`agents/v1` deployable bundles).

## Agents

| Agent | Description | Platforms | Folder |
|-------|-------------|-----------|--------|
| **data-analytics-officer** | Full BI/BA agent with advanced analysis, clustering, multi-format reports (PDF, DOCX, web, PowerPoint), read-only data quality coverage assessment and reporting, and reasoning documentation | OpenCode, Stratio Cowork | `agents/data-analytics-officer/` |
| **semantic-layer** | Agent specialized in building and maintaining semantic layers in Stratio Governance: creation of data collections (technical domains), technical terms, ontologies, business views, SQL mappings, view publishing, semantic terms and business terms | OpenCode, Stratio Cowork | `agents/semantic-layer/` |
| **data-quality** | Data quality agent: coverage assessment, gap identification, quality rule creation with human-in-the-loop and coverage report generation | OpenCode, Stratio Cowork | `agents/data-quality/` |
| **data-governance-officer** | Combined governance agent: full semantic layer building + data quality management in a single agent with unrestricted access to all governance tools | OpenCode, Stratio Cowork | `agents/data-governance-officer/` |
| **skill-creator** | Agent for designing and generating AI agent skills (SKILL.md). Interactive requirements → design → generation → review → ZIP packaging | OpenCode, Stratio Cowork | `agents/skill-creator/` |
| **agent-creator** | Agent for designing and generating complete AI agents for Stratio Cowork. Interactive requirements → architecture design → AGENTS.md generation → skill creation → review → agents/v1 ZIP packaging | OpenCode, Stratio Cowork | `agents/agent-creator/` |

## Functional plugins

A **functional plugin** bundles one or more agents and/or shared skills into a single deployable unit that solves a vertical of business (e.g. data governance, document productivity, data storytelling). Plugins are an additive packaging layer on top of the per-agent and per-skill artifacts: the individual ZIPs are still produced, and a plugin can include any subset of them.

Plugins live in `plugins/<name>/` with two files:

- `plugin.yaml` — declarative manifest (name, description, tags, contents, MCPs, platforms).
- `README.md` — user-facing documentation (purpose, contents, install instructions).

Each plugin is packaged for two targets: a **Stratio Cowork** wrapper bundle (deployable via `genai-api`) and a **Claude marketplace plugin** (`.claude-plugin/plugin.json`).

### Available plugins

| Plugin | Description | Contents | Platforms |
|--------|-------------|----------|-----------|
| **stratio-governance** | Data governance: semantic layers and data quality coverage end-to-end. | data-governance-officer + data-quality + semantic-layer (agents) | Stratio Cowork |
| **stratio-data** | Senior BI/BA analyst that turns business questions into actionable analyses on governed data. | data-analytics-officer (agent) | Stratio Cowork |
| **stratio-cowork-development** | Build AI agents and skills interactively from a guided workflow. | agent-creator + skill-creator (agents) | Stratio Cowork |
| **stratio-productivity** | Productivity skills: office documents, visual outputs and brand identity. | pdf/docx/pptx/xlsx readers+writers, web-craft, canvas-craft, brand-kit (skills-only) | Stratio Cowork, Claude |
| **stratio-data-toolkit** | Pluggable Stratio data skills (query patterns, exploration, knowledge contributions, quality assessment). | stratio-data, explore-data, propose-knowledge, assess-quality (skills-only) | Claude |

### Platform rules

| Plugin contents | Stratio Cowork | Claude |
|---|---|---|
| Has agents | yes (`agents/v1` wrapper bundle) | **no** — Claude does not support agents in plugins |
| Skills-only | yes (skills bundle compatible with `/v1/agents/skills/bundle/import`) | yes (`.claude-plugin/plugin.json`) |

The validator (`bin/validate-plugins.py`) enforces these rules: a plugin with agents that explicitly declares `claude` in `platforms:` aborts the build with a clear error.

### Output artifacts

`make package` produces, in addition to the per-agent and per-skill ZIPs:

```
dist/
├── plugin-stratio-governance-stratio-cowork-{version}.zip            # wrapper of 3 agent sub-zips
├── plugin-stratio-governance-stratio-cowork-es-{version}.zip
├── plugin-stratio-data-stratio-cowork-{version}.zip                  # wrapper of the data-analytics-officer agent
├── plugin-stratio-data-stratio-cowork-es-{version}.zip
├── plugin-stratio-cowork-development-stratio-cowork-{version}.zip    # wrapper of agent-creator + skill-creator
├── plugin-stratio-cowork-development-stratio-cowork-es-{version}.zip
├── plugin-stratio-productivity-stratio-cowork-{version}.zip          # wrapper with one skills sub-zip
├── plugin-stratio-productivity-stratio-cowork-es-{version}.zip
├── plugin-stratio-productivity-claude-{version}.zip                  # .claude-plugin marketplace zip
├── plugin-stratio-productivity-claude-es-{version}.zip
├── plugin-stratio-data-toolkit-claude-{version}.zip                  # Claude-only data skills bundle
└── plugin-stratio-data-toolkit-claude-es-{version}.zip
```

### Installing a plugin

For the Stratio Cowork variant, use the `upload-plugin` task of the [`cowork-api`](skills/cowork-api/) shared skill. The task opens the wrapper, reads the aggregated `plugin.yaml`, and dispatches each sub-ZIP to the correct `genai-api` endpoint (`/v1/agents/bundle/import` for agents, `/v1/agents/skills/bundle/import` for skills). It returns an aggregated report of imported, conflicted and failed artifacts.

For the Claude variant, follow the standard Claude Code plugin install flow (`/plugin install` from a marketplace).

### Adding a new plugin

See [CLAUDE.md](CLAUDE.md) section "Plugins funcionales" for the dev-facing how-to (manifest schema, validation rules, how the build picks it up).

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

### Memory templates

If an agent persists memory between sessions, its seed files live under `templates/memory/` (e.g. `templates/memory/MEMORY.md`). The agent's writing skills are responsible for copying the template into `output/` the first time they need to write — `**/output/` stays in `.gitignore` and pack scripts never create `output/` in the package. This keeps a single source of truth for the initial structure and avoids duplicating templates inline inside SKILL.md files.

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

`skills/` groups reusable skills across multiple agents in the monorepo. The pack scripts automatically include them in the output of each agent that declares them, without the need to duplicate code.

### Available skills

| Skill | Description | Agents that use it |
|-------|-------------|-------------------|
| `propose-knowledge` | Propose business terms and preferences to Stratio Governance after an analysis | data-analytics-officer |
| `explore-data` | Quick exploration of domains, tables, columns and governed terminology | data-analytics-officer |
| `stratio-data` | Stratio data MCPs reference: rules, usage patterns and best practices | (standalone) |
| `stratio-semantic-layer` | Stratio semantic layer MCPs reference: rules, usage patterns and best practices for governance tools | semantic-layer, data-governance-officer |
| `create-technical-terms` | Create or regenerate technical terms (table and column descriptions) for a domain | semantic-layer, data-governance-officer |
| `create-ontology` | Create or extend ontologies with interactive planning | semantic-layer, data-governance-officer |
| `create-business-views` | Create, regenerate or publish business views and SQL mappings from an ontology | semantic-layer, data-governance-officer |
| `create-sql-mappings` | Create or update SQL mappings for existing views | semantic-layer, data-governance-officer |
| `create-semantic-terms` | Generate or regenerate semantic business terms for views | semantic-layer, data-governance-officer |
| `manage-business-terms` | Create Business Terms in the dictionary with relationships to data assets | semantic-layer, data-governance-officer |
| `create-data-collection` | Search for tables and paths in the technical data dictionary and create a new collection (technical domain) | semantic-layer, data-governance-officer |
| `build-semantic-layer` | Full semantic layer pipeline: orchestrates technical terms, ontology, views, mappings and semantic terms creation | semantic-layer, data-governance-officer |
| `assess-quality` | Assess quality coverage by domain, table or column: dimensions covered, gaps and priorities | data-analytics-officer, data-quality, data-governance-officer |
| `create-quality-rules` | Design and create quality rules to cover gaps, with mandatory human approval | data-quality, data-governance-officer |
| `create-quality-schedule` | Create automatic execution schedules for quality rule folders | data-quality, data-governance-officer |
| `quality-report` | Generate a formal quality coverage report in PDF, DOCX or Markdown | data-analytics-officer, data-quality, data-governance-officer |
| `pdf-reader` | Inspect, extract text, tables, images, form values and attachments from PDF files with diagnose-first strategy | data-analytics-officer, data-quality, data-governance-officer |
| `pdf-writer` | Create designed PDFs, transform existing ones (merge, split, rotate, watermark, encrypt) and fill forms. Design-first workflow with custom typography | data-analytics-officer, data-quality, data-governance-officer |
| `xlsx-reader` | Extract cell values, tables, formulas, images and metadata from `.xlsx`/`.xlsm` files (or legacy `.xls`/`.xlsb` via LibreOffice). Diagnose-first strategy | data-analytics-officer, data-quality, data-governance-officer |
| `xlsx-writer` | Create designed Excel workbooks (analytical cover/KPI + detail sheets, coverage matrices, pivot tables, tabular exports, catalogs, quantitative models). Merge/split, find-replace, legacy `.xls` conversion, formula refresh via LibreOffice | data-analytics-officer, data-quality, data-governance-officer |
| `brand-kit` | Centralized catalog of visual identity themes (colors, typography, chart palettes, sizes, tone). Ships 10 curated themes and is extensible — clients add their own | data-analytics-officer, data-quality, data-governance-officer |

Shared guides (technical documentation that skills reference) live in `guides/`:

| Guide | Used by |
|-------|---------|
| `stratio-data-tools.md` | `explore-data`, `assess-quality`, `AGENTS.md` (data-analytics-officer, data-quality, data-governance-officer) |
| `stratio-semantic-layer-tools.md` | `stratio-semantic-layer`, `build-semantic-layer`, `AGENTS.md` (semantic-layer, data-governance-officer) |
| `quality-exploration.md` | `assess-quality`, `create-quality-rules` (data-analytics-officer, data-quality, data-governance-officer) |

### Using a shared skill in an agent

1. Create (if it doesn't exist) the `imported-skills` file in the agent folder with the skill name, one per line:

   ```
   propose-knowledge
   explore-data
   ```

2. If the agent's `AGENTS.md` directly references any guide from `guides/`, also declare it in `guides`:

   ```
   stratio-data-tools.md
   ```

3. Package as normal — the generic pack scripts (`pack_opencode.sh`, `pack_stratio_cowork.sh`) copy each guide declared in `guides` **inside** the skill folder in the output and rewrite the references in `SKILL.md` to make them local (self-contained skill). Guides declared in the agent's `guides` are also copied to `guides/` so that `AGENTS.md` can reference them:

   ```bash
   bash pack_opencode.sh --agent my-agent
   ```

   Resulting output (example with `explore-data` which declares `stratio-data-tools.md`):
   ```
   .claude/
     skills/
       explore-data/
         SKILL.md                  # references "stratio-data-tools.md" (local)
         stratio-data-tools.md     # guide inside the skill
     guides/
       stratio-data-tools.md       # for AGENTS.md (possible duplicate, ok)
   ```

If the agent has a skill in `skills/` with the same name, the local version takes priority over the shared one.

### Creating a new shared skill

1. Create the folder and `SKILL.md` (in English) in `skills/`, and the Spanish translation in `es/`:

   ```
   skills/
   └── my-skill/
       ├── SKILL.md       # Skill definition in English (self-contained or nearly so)
       └── guides         # (Optional) List of root-level guides it needs
   es/skills/
   └── my-skill/
       └── SKILL.md       # Spanish translation
   ```

2. If the skill needs external guides, add the files in `guides/` (with their counterparts in `es/guides/`) and list them in `guides`:

   ```
   # skills/my-skill/guides
   my-guide.md
   ```

3. Declare the skill in the agents that should include it (`imported-skills` file in each agent).

A shared skill should be as self-contained as possible: no dependencies on Python tools, styles or templates specific to an agent. If a skill depends heavily on artifacts from a specific agent, keep it as a local skill in that agent.

**SKILL.md content:** Do not reference `AGENTS.md` or `CLAUDE.md` directly — the pack scripts substitute these names depending on the platform, but a direct reference may not work correctly on some targets. Use generic phrasing such as "following the user question convention" or "according to the agent's instructions". Guide references must use the path `guides/<file>` in the source — the generic pack scripts copy the guide inside the skill and rewrite the reference to make it local (self-contained).

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
| Developer READMEs | `README.md` (agents) | `es/.../README.md` | Yes |
| Cowork metadata | `cowork-metadata.yaml` | `es/.../cowork-metadata.yaml` | Yes |
| Memory templates | `templates/memory/*.md` | `es/.../templates/memory/*.md` | Yes |
| Python code, HTML, CSS | `tools/*.py`, `templates/` | — | No |
| Config files | `.mcp.json`, `opencode.json` | — | No |
| Manifests | `imported-skills`, `guides` | — | No |
| Shell scripts | `pack_*.sh`, `bin/*.sh` | — | No |

Skill and folder names are **technical identifiers** and stay in English regardless of language.

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
    └── memory/            # (Optional) Persistent memory seed files (MEMORY.md, etc.)
```

The `templates/memory/` directory is optional: use it only if the agent needs to persist memory between sessions (the writing skill copies the seed into `output/` on first write).

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
