# genai-agents — Monorepo

Monorepo with generative AI agents for business data analysis.

## Structure

```
genai-agents/
  shared-skills/           # Shared skills across agents (self-contained or nearly so)
    propose-knowledge/
    explore-data/
    stratio-data/
    stratio-semantic-layer/
    generate-technical-terms/
    create-ontology/
    create-business-views/
    create-sql-mappings/
    create-semantic-terms/
    manage-business-terms/
    create-data-collection/
    build-semantic-layer/
    assess-quality/
    create-quality-rules/
    create-quality-planification/
    quality-report/
    pdf-reader/
    pdf-writer/
    skill-creator/
  shared-skill-guides/     # Shared guides (not skills; copied to skills-guides/ in the output)
    stratio-data-tools.md
    stratio-semantic-layer-tools.md
    quality-exploration.md
  es/                      # Spanish translations (overlay directory, mirrors main tree)
    shared-skills/
    shared-skill-guides/
    data-analytics/
    data-analytics-light/
    semantic-layer/
    data-quality/
    governance-officer/
    skill-creator/
    agent-creator/
  data-analytics/          # Full agent (analysis + multi-format reports)
    shared-skills          # List of shared skills included by this agent
    shared-guides          # List of shared-skill-guides that AGENTS.md references directly
  data-analytics-light/    # Lightweight agent (chat-based analysis)
    shared-skills
    shared-guides
  semantic-layer/          # Semantic layer construction agent
    shared-skills
    shared-guides
  data-quality/            # Data quality agent (assessment, rules, reports)
    shared-skills
    shared-guides
  governance-officer/      # Governance officer: semantic layer + data quality combined
    shared-skills
    shared-guides
  skill-creator/           # Skill creation agent
    shared-skills
  agent-creator/           # Agent creation agent
    shared-skills
```

## Development instructions

- Each agent has its own `AGENTS.md` with specific instructions. Always work from the corresponding agent folder
- Agent-specific skills live in `skills/`; shared skills live in `shared-skills/` (monorepo root)
- Shared guides live in `shared-skill-guides/` (monorepo root); local guides in the agent's `skills-guides/`
- Each agent declares which shared skills it needs in `shared-skills` (one line per skill) and which direct guides in `shared-guides`
- Each shared skill can declare which guides from `shared-skill-guides/` it needs in a `skill-guides` file inside its folder
- If an agent has a skill in `skills/` with the same name as a shared skill, the local version takes priority
- Generic packaging scripts at the monorepo root: `pack_claude_code.sh` and `pack_opencode.sh` (any agent)
- Platform-specific packaging scripts in `data-analytics-light/`, `semantic-layer/`, `data-quality/` and `governance-officer/` (`pack_claude_ai_project.sh`, `pack_claude_cowork.sh`)
- The root `.gitignore` covers all agents

## Agent summary

### data-analytics
Full BI/BA agent: queries governed data via MCP, analysis with Python (pandas, scipy, scikit-learn), visualizations (matplotlib, seaborn, plotly), report generation (PDF, DOCX, web, PowerPoint), PDF reading and extraction (`pdf-reader`), ad-hoc PDF creation and manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms), read-only data quality coverage assessment and reporting (uses shared skills `assess-quality` and `quality-report`; does not create rules), reasoning documentation, validation, cross-session memory management.

### data-analytics-light
Lightweight BI/BA agent: same analytical engine but chat-oriented. Includes read-only data quality coverage assessment with chat-only summaries (uses `assess-quality` and `quality-report` forcing the Chat format; no file generation, no rule creation). No formal report generation — the primary output is the chat. Includes packaging scripts for Claude AI Projects and Claude Cowork.

### semantic-layer
Agent specialized in building and maintaining semantic layers in Stratio Governance. Orchestrates the creation of data collections (technical domains), technical terms, ontologies, business views, SQL mappings, view publishing, semantic terms and business terms via governance MCPs. Does not execute data queries or generate files — its output is MCP tool interaction + chat summaries. Can read local user files to enrich planning.

### data-quality
Agent specialized in data governance and quality. Evaluates quality coverage by domain, collection, table or column, identifies gaps (uncovered dimensions), proposes and creates quality rules with mandatory human approval, and generates coverage reports in multiple formats (PDF, DOCX, Markdown). Includes PDF reading (`pdf-reader`) and ad-hoc PDF manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms). Operates on governed data via SQL and governance MCPs.

### governance-officer
Combined governance agent with the full capabilities of both semantic-layer and data-quality. Builds and maintains semantic layers (ontologies, views, mappings, terms) AND manages data quality (assessment, rule creation, scheduling, reports). Includes PDF reading (`pdf-reader`) and ad-hoc PDF creation and manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms, ontology documentation). Has full access to all governance and data MCP tools with no restrictions.

### skill-creator
Agent for designing and generating AI agent skills (SKILL.md files). Interactive workflow: requirements gathering, skill design following proven principles, SKILL.md generation with supporting files, quality review with checklist, and ZIP packaging for download. No MCPs — works purely with conversation and file generation.

### agent-creator
Agent for designing and generating complete AI agents for Stratio Cowork. Interactive workflow: requirements gathering, architecture design (workflow phases, triage tables, skill decomposition), AGENTS.md generation following proven patterns, skill creation via shared skill-creator, supporting files (README.md, opencode.json), quality review with 26-point checklist, and agents/v1 ZIP packaging. No MCPs — works purely with conversation and file generation.

## Packaging scripts (root)

Generic scripts that work with any agent in the monorepo:

| Script | Target platform | Output |
|--------|----------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agent}/claude_code/{name}/` |
| `pack_opencode.sh` | OpenCode | `{agent}/opencode/{name}/` |
| `pack_shared_skills.sh` | All (standalone skills) | `dist/shared-skills.zip` or `dist/{skill}.zip` |

Usage: `bash pack_claude_code.sh --agent <agent-path> [--name <kebab-case-name>] [--lang <code>]`

All pack scripts accept `--lang <code>` to generate output in a specific language. Without `--lang` (or with `--lang en`), English is used. With `--lang es`, the script resolves Spanish content from the `es/` overlay and generates the output in `dist/es/...` for traceability.

## Shared skills

### Creating a shared skill

1. Create `shared-skills/<name>/SKILL.md` with the skill content (in English)
2. Create the Spanish translation at `es/shared-skills/<name>/SKILL.md`
3. If the skill needs external guides, create the files in `shared-skill-guides/` (with their counterparts in `es/shared-skill-guides/`) and list them in `shared-skills/<name>/skill-guides` (plain text, one line per file)
4. Declare the skill in the agents that use it by adding its name to the `<agent>/shared-skills` file
5. If the agent's AGENTS.md references the guide directly, also add it to `<agent>/shared-guides`

**SKILL.md content rules:**
- Do not reference `AGENTS.md` or `CLAUDE.md` directly — use generic phrasing such as "according to the agent's instructions" or "following the user question convention". The pack scripts substitute these names depending on the target platform, but a direct reference may not work correctly on some platforms
- Do not depend on Python tools, styles, templates or paths specific to a particular agent — if the skill needs those, it should be local
- References to `output/MEMORY.md` are acceptable if conditioned on the file's existence (`if it exists`) — agents without memory simply ignore it
- Guide references in the SKILL.md must use the path `skills-guides/<file>` (without platform prefix) — the generic pack scripts copy each guide **inside** the skill folder and rewrite the references to make them local (self-contained). Guides declared in the agent's `shared-guides` are also copied to `skills-guides/` so that `AGENTS.md` can reference them

### Using a shared skill in an agent

Add the skill name to the `<agent>/shared-skills` file (one line per skill). If AGENTS.md directly references any guide from `shared-skill-guides/`, add it to `<agent>/shared-guides`. All pack scripts read these manifests automatically.

If the agent already has a skill in `skills/` with the same name, the local version takes priority and the shared one is skipped.

## Internationalization (i18n)

The monorepo supports multiple languages. **English is the primary language** — files in the main tree contain English content. Translations live in a language overlay directory at the root (e.g., `es/` for Spanish) that mirrors the source tree structure:

```
genai-agents/
  shared-skills/explore-data/SKILL.md          # English (primary)
  es/shared-skills/explore-data/SKILL.md        # Spanish (overlay)
  data-analytics/AGENTS.md                      # English
  es/data-analytics/AGENTS.md                   # Spanish
```

Supported languages are listed in the `languages` file at the monorepo root.

**What gets translated:** `AGENTS.md`, `SKILL.md`, sub-guides (`*.md` inside `skills/`), `skills-guides/*.md`, `shared-skill-guides/*.md`, `USER_README.md`, `README.md`, `cowork-metadata.yaml`, `templates/memory/*.md`.

**What stays language-neutral (not translated):** Python code, HTML templates, CSS, shell scripts, JSON configs (`.mcp.json`, `opencode.json`), manifests (`shared-skills`, `shared-guides`, `skill-guides`), `Makefile`, `Jenkinsfile`, `VERSION`.

**Skill and folder names are technical identifiers** — they stay in English regardless of language (`explore-data`, not `explorar-datos`).

### Packaging by language

Each pack script accepts `--lang <code>` to package in a specific language. When `--lang es` is passed, the script internally resolves the Spanish content from `es/` and generates output in `dist/es/{format}/{name}/` (intermediate files available for inspection). `bin/package.sh` orchestrates this for all agents and languages, producing final versioned ZIPs in `dist/`:

- English (primary): `data-analytics-claude-code-0.1.0.zip` (no suffix)
- Spanish: `data-analytics-claude-code-es-0.1.0.zip`

Individual pack script usage:

```bash
# English (default)
bash pack_claude_code.sh --agent data-analytics
# → data-analytics/dist/claude_code/data-analytics/

# Spanish
bash pack_claude_code.sh --agent data-analytics --lang es
# → data-analytics/dist/es/claude_code/data-analytics/
```

### Translation workflow

When adding or modifying translatable content:

1. Edit the primary file (e.g., `SKILL.md`) with English content
2. Create or update the counterpart in `es/` (e.g., `es/.../SKILL.md`) with the Spanish translation
3. Run `bin/check-translations.sh` to verify no translations are missing

## Adding a new agent

The complete creation guide is in `README.md` (section "Creating a new agent"). Monorepo integration checklist:

1. Create a `my-agent/` folder with the minimum structure:
   - `AGENTS.md` — role, workflow, agent rules
   - `opencode.json` — MCPs and permissions for OpenCode (if it uses OpenCode)
   - `skills/` — optional; if the agent has its own skills, canonical format `skills/<name>/SKILL.md`
   - `shared-skills` — optional; list of shared skills from the monorepo to include (one line per skill)
   - `shared-guides` — optional; list of shared-skill-guides that AGENTS.md references directly
2. Add `my-agent` to the `release-modules` file (one line per agent) so that `make package` includes it
3. Update the agents table in `README.md`
4. Create counterparts in `es/<agent>/` for all translatable files (see [Internationalization](#internationalization-i18n))
