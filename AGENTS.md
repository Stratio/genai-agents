# genai-agents — Monorepo

Monorepo with generative AI agents for business data analysis.

## Structure

```
genai-agents/
  skills/           # Shared skills across agents (self-contained or nearly so)
    propose-knowledge/
    explore-data/
    stratio-data/
    stratio-semantic-layer/
    create-technical-terms/
    create-ontology/
    create-business-views/
    create-sql-mappings/
    create-semantic-terms/
    manage-business-terms/
    create-data-collection/
    build-semantic-layer/
    assess-quality/
    create-quality-rules/
    create-quality-schedule/
    quality-report/
    pdf-reader/
    pdf-writer/
    docx-reader/
    docx-writer/
    pptx-reader/
    pptx-writer/
    xlsx-reader/
    xlsx-writer/
    web-craft/
    canvas-craft/
    brand-kit/
    skill-creator/
  guides/     # Shared guides (not skills; copied to guides/ in the output)
    stratio-data-tools.md
    visual-craftsmanship.md
    stratio-semantic-layer-tools.md
    quality-exploration.md
  es/                      # Spanish translations (overlay directory, mirrors main tree)
    skills/
    guides/
    agents/
      data-analytics-officer/
      semantic-layer/
      data-quality/
      data-governance-officer/
      skill-creator/
      agent-creator/
  agents/                  # All agents live under agents/<name>/
    data-analytics-officer/        # Full agent (analysis + multi-format reports)
      imported-skills      # List of skills imported from monorepo skills/
      guides               # List of root-level guides this agent uses directly
    semantic-layer/        # Semantic layer construction agent
      imported-skills
      guides
    data-quality/          # Data quality agent (assessment, rules, reports)
      imported-skills
      guides
    data-governance-officer/    # Governance officer: semantic layer + data quality combined
      imported-skills
      guides
    skill-creator/         # Skill creation agent
      imported-skills
    agent-creator/         # Agent creation agent
      imported-skills
  plugins/                 # Functional plugins (verticals): see "Plugins funcionales"
    stratio-governance/    # plugin.yaml + README.md
    stratio-data/
    stratio-cowork-development/
    stratio-productivity/
    stratio-data-toolkit/
```

## Development instructions

- Each agent has its own `AGENTS.md` with specific instructions. Always work from the corresponding agent folder
- Agent-specific skills live in `<agent>/skills/`; shared skills live in the root-level `skills/` directory
- Shared guides live in `guides/` (monorepo root); local guides in the agent's `guides/`
- Each agent declares which shared skills it imports in `imported-skills` (one line per skill) and which direct guides in `guides`
- Each shared skill can declare which guides from `guides/` it needs in a `guides` file inside its folder
- If an agent has a skill in `skills/` with the same name as a shared skill, the local version takes priority
- Generic packaging script at the monorepo root: `pack_opencode.sh` (any agent), plus `pack_stratio_cowork.sh` (agents/v1 bundles), `pack_skills.sh` (skill ZIPs) and `pack_plugin.sh` (functional plugins)
- The root `.gitignore` covers all agents

## Agent summary

### data-analytics-officer
Full BI/BA agent: queries governed data via MCP, analysis with Python (pandas, scipy, scikit-learn), visualizations (matplotlib, seaborn, plotly), report generation (PDF, DOCX, web, PowerPoint, Excel/XLSX), PDF reading and extraction (`pdf-reader`), ad-hoc PDF creation and manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms), DOCX reading (`docx-reader`) and ad-hoc DOCX authoring / manipulation (`docx-writer`: merge, split, find-replace, convert `.doc` to `.docx`), PPTX reading (`pptx-reader`) and ad-hoc PPTX authoring / manipulation (`pptx-writer`: merge, split, reorder, find-replace in slides and notes, convert `.ppt` to `.pptx`) for decks outside the analytical pipeline, XLSX reading (`xlsx-reader`) and ad-hoc XLSX authoring / manipulation (`xlsx-writer`: analytical workbooks with cover/KPI + detail sheets, pivot matrices, tabular exports, merge/split/find-replace, convert `.xls` to `.xlsx`, formula refresh), read-only data quality coverage assessment and reporting (uses shared skills `assess-quality` and `quality-report`; does not create rules), reasoning documentation, validation, cross-session memory management.

### semantic-layer
Agent specialized in building and maintaining semantic layers in Stratio Governance. Orchestrates the creation of data collections (technical domains), technical terms, ontologies, business views, SQL mappings, view publishing, semantic terms and business terms via governance MCPs. Does not execute data queries or generate files — its output is MCP tool interaction + chat summaries. Can read local user files to enrich planning, including DOCX specifications via `docx-reader` and PPTX specification decks via `pptx-reader`.

### data-quality
Agent specialized in data governance and quality. Evaluates quality coverage by domain, collection, table or column, identifies gaps (uncovered dimensions), proposes and creates quality rules with mandatory human approval, and generates coverage reports in multiple formats (PDF, DOCX, PPTX, Dashboard web, Web article / Narrative report, Poster/Infographic, XLSX, Markdown). Includes PDF reading (`pdf-reader`) and ad-hoc PDF manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms), DOCX reading (`docx-reader`) and ad-hoc DOCX authoring / manipulation (`docx-writer`: merge, split, find-replace, `.doc` conversion), PPTX reading (`pptx-reader`) and ad-hoc PPTX authoring (`pptx-writer`) for executive quality summary decks and training decks on rules, plus XLSX reading (`xlsx-reader`) for rule-spec workbooks and table catalogs and XLSX authoring (`xlsx-writer`) for multi-sheet coverage workbooks (materialises the Excel option of `quality-report`) and ad-hoc XLSX (rule-spec templates, term catalog exports). Operates on governed data via SQL and governance MCPs.

### data-governance-officer
Combined governance agent with the full capabilities of both semantic-layer and data-quality. Builds and maintains semantic layers (ontologies, views, mappings, terms) AND manages data quality (assessment, rule creation, scheduling, reports in PDF, DOCX, PPTX, Dashboard web, Web article / Narrative report, Poster/Infographic, XLSX, Markdown). Includes PDF reading (`pdf-reader`) and ad-hoc PDF creation and manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms, ontology documentation), DOCX reading (`docx-reader`) and ad-hoc DOCX authoring / manipulation (`docx-writer`: merge, split, find-replace, `.doc` conversion) for policy briefs, compliance reports and ontology documentation, PPTX reading (`pptx-reader`) and PPTX authoring (`pptx-writer`) for compliance briefings, policy presentations, ontology walkthroughs and steering-committee decks, plus XLSX reading (`xlsx-reader`) for data dictionaries, term catalogs and rule-spec workbooks, and XLSX authoring (`xlsx-writer`) for multi-sheet quality-coverage workbooks, ontology exports, term catalogs, compliance matrices and policy checklist workbooks. Has full access to all governance and data MCP tools with no restrictions.

### skill-creator
Agent for designing and generating AI agent skills (SKILL.md files). Interactive workflow: requirements gathering, skill design following proven principles, SKILL.md generation with supporting files, quality review with checklist, and ZIP packaging for download. No MCPs — works purely with conversation and file generation.

### agent-creator
Agent for designing and generating complete AI agents for Stratio Cowork. Interactive workflow: requirements gathering, architecture design (workflow phases, triage tables, skill decomposition), AGENTS.md generation following proven patterns, skill creation via shared skill-creator, supporting files (README.md, opencode.json), quality review with 26-point checklist, and agents/v1 ZIP packaging. No MCPs — works purely with conversation and file generation.

## Packaging scripts (root)

Generic scripts that work with any agent in the monorepo:

| Script | Target | Output |
|--------|--------|--------|
| `pack_opencode.sh` | OpenCode (developer testing in `~/genai-agents-tests/opencode/`) | `{agent}/dist/[{lang}/]opencode/{name}/` |
| `pack_stratio_cowork.sh` | Stratio Cowork (`agents/v1` deployable bundle) | `dist/{name}-stratio-cowork.zip` |
| `pack_skills.sh` | All — bulk skills ZIP and individual skill ZIPs | `dist/skills.zip` or `dist/{skill}.zip` |
| `pack_plugin.sh` | Functional plugins (`stratio-cowork` wrapper or `claude` marketplace) | `dist/{plugin}-{platform}.zip` |

Usage: `bash pack_opencode.sh --agent <agent-path> [--name <kebab-case-name>] [--lang <code>]`

All pack scripts accept `--lang <code>` to generate output in a specific language. Without `--lang` (or with `--lang en`), English is used. With `--lang es`, the script resolves Spanish content from the `es/` overlay and generates the output in `dist/es/...` for traceability.

## OpenCode test skills

Repo-local Claude Code skills under `.claude/skills/` automate the test deployment of an agent into the team's shared OpenCode test directory `~/genai-agents-tests/opencode/<agent>/`. The naming convention `test-opencode-<agent>` makes the target platform explicit. They are committed to the repo so any teammate gets them on clone.

| Skill | Slash form | Packs |
|-------|-----------|-------|
| `test-opencode-data-analytics-officer` | `/test-opencode-data-analytics-officer` | data-analytics-officer opencode-es |
| `test-opencode-data-quality` | `/test-opencode-data-quality` | data-quality opencode-es |
| `test-opencode-data-governance-officer` | `/test-opencode-data-governance-officer` | data-governance-officer opencode-es |

Each skill runs `pack_opencode.sh --agent <agent> --lang es` and `rsync -a` (no `--delete`) the output into the test folder, so existing extra content in the destination (notably an `output/` folder with previous run artifacts) is preserved. Paths use `git rev-parse --show-toplevel` for the source and `~/genai-agents-tests/opencode/...` for the destination so the skills work regardless of where the repo is cloned.

To add a new test skill for another agent, copy one of the existing folders under `.claude/skills/test-opencode-*/` and adjust the agent name in three places (frontmatter `name`/`description`, `pack_opencode.sh --agent <name>`, and the rsync source/destination paths).

## Shared skills

### Reference rules

Shared-skills **should** stay self-contained when practical — most SKILL.md files in `skills/` do not reference another shared-skill by name, so they can be packaged standalone and consumed in isolation by third-party agents. This is the preferred default.

Cross-referencing other shared-skills by name from inside a shared SKILL.md is **permitted** when the skill's workflow genuinely depends on delegating to others and inlining their logic would duplicate thousands of lines. Examples already in the repo:

- `pdf-reader` ↔ `pdf-writer`, `docx-reader` ↔ `docx-writer`, `pptx-reader` ↔ `pptx-writer` (companion skills that reference each other for round-trip flows).
- `visual-craftsmanship.md` guide (the only place where `web-craft`, `canvas-craft` and `pdf-writer` are compared side by side so an agent can disambiguate).
- `quality-report` (delegates file-format generation to `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` and `brand-kit`).

**Trade-off**: a cross-referencing shared-skill is not perfectly self-contained anymore. It is no longer safe to package standalone — at runtime it needs the skills it names. Two consequences:

1. Any agent that declares a cross-referencing shared-skill in its `imported-skills` manifest must also declare the skills it depends on. Without that, the references inside the SKILL.md point to skills the agent cannot load.
2. The skill's own `README.md` documents the dependency explicitly, so the next developer (or agent author) knows what to bundle.

A chat-oriented agent may intentionally omit some of the dependent skills — in that case the cross-referencing skill should detect the absence at the beginning of its workflow and restrict itself to the features that do not require the missing skills (e.g. offering only the Chat format). This "graceful degradation" is a valid configuration and should be stated in both the skill's SKILL.md (pre-check) and the host agent's AGENTS.md.

Skills inside `<agent>/skills/` and any `AGENTS.md` may reference directly any skill the agent declares (local or shared). Prefer `load /skill-x and follow its §Y` over duplicating instructions.

### Visual-craftsmanship family

Three shared skills cover the visual output of the monorepo. They share the guide `guides/visual-craftsmanship.md` but do not reference each other in runtime. The disambiguation table in that guide is the only place where the three names live together.

- `web-craft` — interactive frontend (HTML/CSS/JS, React, Vue). Components, pages, dashboards.
- `canvas-craft` — single-page static artifacts (PDF/PNG). Posters, covers, certificates, marketing one-pagers, infographics. Ships a small set of OFL display fonts.
- `pdf-writer` — multi-page typographic documents or prose-dominated single pages. Analytical reports, invoices, contracts, zines.

Agents that produce visual output declare the family members they need in `<agent>/imported-skills` and add `visual-craftsmanship.md` to `<agent>/guides`. `data-analytics-officer`, `data-governance-officer` and `data-quality` all declare the full family (pdf-writer, docx-writer, pptx-writer, web-craft, canvas-craft) so they can offer every output format through both the analytical pipeline and `quality-report`.

### Brand-kit / centralized theming

`brand-kit` is the shared skill that centralizes visual identity tokens (colors, typography, chart palettes, sizes, tone). It ships ten curated themes and is extensible — clients add their own themes directly inside the skill or provide an alternative theming skill. Agents that generate visual deliverables declare `brand-kit` in `<agent>/imported-skills`.

Output skills (`docx-writer`, `pptx-writer`, `pdf-writer`, `xlsx-writer`, `web-craft`, `canvas-craft`) reference the concept "centralized theming skill" **generically**, not by name — they never mention `brand-kit` literally. This keeps self-containment intact: a client can substitute `brand-kit` with their own skill without editing any output skill, and a standalone pack of (for example) `docx-writer` or `xlsx-writer` still works by improvising tokens from `visual-craftsmanship.md`.

### Creating a shared skill

1. Create `skills/<name>/SKILL.md` with the skill content (in English)
2. Create the Spanish translation at `es/skills/<name>/SKILL.md`
3. If the skill needs external guides, create the files in `guides/` (with their counterparts in `es/guides/`) and list them in `skills/<name>/guides` (plain text, one line per file)
4. Declare the skill in the agents that use it by adding its name to the `<agent>/imported-skills` file
5. If the agent's AGENTS.md references the guide directly, also add it to `<agent>/guides`

**SKILL.md content rules:**
- Do not reference `AGENTS.md` or `CLAUDE.md` directly — use generic phrasing such as "according to the agent's instructions" or "following the user question convention". The pack scripts substitute these names depending on the target platform, but a direct reference may not work correctly on some platforms
- Do not depend on Python tools, styles, templates or paths specific to a particular agent — if the skill needs those, it should be local
- References to `output/MEMORY.md` are acceptable if conditioned on the file's existence (`if it exists`) — agents without memory simply ignore it
- Guide references in any `.md` file inside a skill (SKILL.md or any nested file) must always use the path `guides/<file>` — independently of how deep the referencing file lives. The pack scripts:
  - Copy each declared guide **flat into the skill root** (sibling of SKILL.md, not into a nested `guides/` folder).
  - Run a recursive `sed 's|guides/||g'` over every `.md` in the skill, so all references become flat filenames after packing.
  - Resolution at runtime is by context, not by filesystem path — the LLM has the skill loaded and finds `<file>.md` regardless of where the referencing file sits within the skill.
- Guides declared at the agent level (in `<agent>/guides`) are copied to `<agent>/guides/` so that `AGENTS.md` can reference them with the same `guides/<file>` path. `AGENTS.md` is **not** rewritten by the pack — the path stays literal because the folder physically exists at agent level.

**SKILL.md frontmatter limits (enforced by Anthropic / OpenCode / GitHub Copilot Code at runtime):**

- `name`: 1–64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`, must equal the parent directory name, must not contain reserved words `anthropic` or `claude`, no XML/HTML tags
- `description`: 1–1024 chars, no XML/HTML tags (only the first ~250 are shown in `/skills` UI listings)
- File must be named exactly `SKILL.md` (case-sensitive); frontmatter must be valid YAML between `---` markers
- Soft recommendation: SKILL.md body under ~500 lines (Anthropic best practice — beyond that, extract to supporting files)

The `pack_opencode.sh` script re-validates `description` length in its integrity-check phase and aborts with a clear error if any `SKILL.md` exceeds 1024 chars. Use the `skill-creator` shared-skill (`skills/skill-creator/SKILL.md`) as the authoring guide — it covers anatomy, progressive disclosure, writing patterns, and the full quality checklist.

### Using a shared skill in an agent

Add the skill name to the `<agent>/imported-skills` file (one line per skill). If AGENTS.md directly references any guide from `guides/`, add it to `<agent>/guides`. All pack scripts read these manifests automatically.

If the agent already has a skill in `skills/` with the same name, the local version takes priority and the shared one is skipped.

## Plugins funcionales

A **functional plugin** (`plugins/<name>/`) is a top-down composition unit that bundles agents and/or shared skills into a single deployable artifact for a business vertical. Plugins are additive — the per-agent and per-skill ZIPs keep being produced; plugins reference them by name and produce extra ZIPs in `dist/`.

### Layout

```
plugins/
  <plugin-name>/
    plugin.yaml          # required, declarative manifest
    README.md            # required, user-facing documentation
es/
  plugins/
    <plugin-name>/
      README.md          # i18n overlay of the README (plugin.yaml is not translated)
```

### `plugin.yaml` schema

```yaml
name: <plugin-name>           # kebab-case, must match parent directory name
version: 0.1.0                # optional — inherits VERSION when omitted
description: "..."            # ≤1024 chars
tags:                         # optional list of strings
  - <tag>
contents:
  agents:                     # optional — names of agent directories at the monorepo root
    - <agent-name>
  skills:                     # optional — names of shared skills (under skills/<name>/)
    - <skill-name>
mcps:                         # optional — ONLY in skills-only plugins (no agents declared)
  - <MCP_NAME>                # surfaced in the README; phase 2 will use it server-side
platforms:                    # optional — defaults derived from contents
  - stratio-cowork
  - claude
```

### Validation rules (`bin/validate-plugins.py`)

- `name` must be kebab-case and equal to the parent directory.
- `description` is required and ≤1024 chars.
- At least one of `agents:` / `skills:` must be non-empty.
- Every `agents:` entry must be a top-level directory with `AGENTS.md`.
- Every `skills:` entry must exist as `skills/<name>/SKILL.md`.
- `mcps:` is only allowed in skills-only plugins (declaring it together with `agents:` is a fatal error).
- `claude` in `platforms:` together with non-empty `agents:` is a fatal error — Claude does not support agents in plugins. The validator emits a clear message.
- `mcps:` entries that don't appear in any `<agent>/mcps` file in the monorepo emit a warning (likely typo).

Run it manually with:

```bash
python3 bin/validate-plugins.py             # all plugins
python3 bin/validate-plugins.py --plugin <name>
python3 bin/validate-plugins.py --strict    # warnings count as errors
```

`bin/package.sh` runs the validator once per language pass before iterating the plugins, so a malformed manifest fails the build early.

### Platform rules

| Plugin contents | Stratio Cowork | Claude |
|---|---|---|
| Has `agents:` | yes — wrapper with `agents/v1` sub-ZIPs | **no** |
| Skills-only | yes — wrapper with one skills sub-ZIP (compatible with `/v1/agents/skills/bundle/import`) | yes — `.claude-plugin/plugin.json` |

If a plugin's effective platforms exclude the requested target, `pack_plugin.sh` skips silently (no error). The orchestrator in `bin/package.sh` calls it once per `(plugin, platform)` combination.

### How a plugin is packaged

`pack_plugin.sh --plugin <name> --platform {stratio-cowork|claude} [--version <semver>] [--lang <code>]` produces, in `<repo_root>/dist/`:

- `<plugin>-stratio-cowork.zip` — wrapper containing `plugin.yaml` (with `bundles[]` catalogue and SHA-256s), `README.md`, `agents/<agent>-stratio-cowork.zip` (one per agent, regenerated by reusing `pack_stratio_cowork.sh`), and optionally `skills/<plugin>-skills.zip` (one bundle with the explicitly-listed skills).
- `<plugin>-claude.zip` — `.claude-plugin/plugin.json` derived from `plugin.yaml`, `README.md`, and `skills/<skill>/` for every skill in `skills:` (with their guides resolved like `pack_skills.sh` does).

`bin/package.sh` runs `pack_plugin.sh` after the per-agent pass for each language, then renames the unsuffixed output to `dist/<plugin>-<platform>[-<lang>]-<version>.zip`.

### How a plugin is deployed (Stratio Cowork)

The deployment is orchestrated by the `upload-plugin` task of the [`cowork-api`](skills/cowork-api/) shared skill. It opens the wrapper, reads `plugin.yaml`, validates SHA-256 per sub-bundle, and dispatches each one to the matching `genai-api` endpoint. The aggregated report covers all sub-bundles. Atomicity is best-effort in phase 1 (no server-side rollback); the future `plugins/v1` API will improve this.

### Adding a new plugin

1. `mkdir plugins/<name>` and write `plugin.yaml` + `README.md`.
2. `mkdir -p es/plugins/<name>` with the Spanish `README.md` overlay.
3. Run `python3 bin/validate-plugins.py --plugin <name>` until it returns OK.
4. Run `bash pack_plugin.sh --plugin <name> --platform stratio-cowork` (and `--platform claude` if applicable) to produce the artifacts.
5. The full release pipeline (`make package`) picks the plugin up automatically — nothing extra to register.

Use the plugins under `plugins/` as templates: `stratio-governance` and `stratio-cowork-development` for multi-agent verticals, `stratio-data` for a single-agent vertical, `stratio-productivity` for a skills-only plugin published to both platforms, and `stratio-data-toolkit` for a skills-only plugin restricted to Claude only.

## Internationalization (i18n)

The monorepo supports multiple languages. **English is the primary language** — files in the main tree contain English content. Translations live in a language overlay directory at the root (e.g., `es/` for Spanish) that mirrors the source tree structure:

```
genai-agents/
  skills/explore-data/SKILL.md          # English (primary)
  es/skills/explore-data/SKILL.md        # Spanish (overlay)
  agents/data-analytics-officer/AGENTS.md               # English
  es/agents/data-analytics-officer/AGENTS.md            # Spanish
```

Supported languages are listed in the `languages` file at the monorepo root.

**What gets translated:** `AGENTS.md`, `SKILL.md`, sub-guides (`*.md` inside `skills/`), `guides/*.md` (root-level and per-agent), `USER_README.md`, per-artifact `README.md` (one per agent / plugin / shared skill — i.e. `agents/<name>/README.md`, `plugins/<name>/README.md`, `skills/<name>/README.md`), `cowork-metadata.yaml`, `templates/memory/*.md`.

**What stays language-neutral (not translated):** Python code, HTML templates, CSS, shell scripts, JSON configs (`.mcp.json`, `opencode.json`), manifests (`imported-skills`, `guides`, `plugin.yaml`), `Makefile`, `Jenkinsfile`, `VERSION`, the repository root `README.md`, and the top-level folder READMEs `agents/README.md`, `guides/README.md`, `plugins/README.md`, `skills/README.md`. The folder READMEs are catalogue / how-to pages whose only consumer is someone browsing the repository on GitHub — they never enter any packaged bundle, so they are kept English-only.

**Skill and folder names are technical identifiers** — they stay in English regardless of language (`explore-data`, not `explorar-datos`).

### Packaging by language

Each pack script accepts `--lang <code>` to package in a specific language. When `--lang es` is passed, the script internally resolves the Spanish content from `es/` and generates output in `dist/es/{format}/{name}/` (intermediate files available for inspection). `bin/package.sh` orchestrates this for all agents and languages, producing final versioned ZIPs in `dist/` with consistent type prefixes:

- Agent: `agent-data-analytics-officer-opencode-0.2.0.zip` / `agent-data-analytics-officer-opencode-es-0.2.0.zip`
- Skill: `skill-stratio-data-0.2.0.zip` / `skill-stratio-data-es-0.2.0.zip`
- Bulk skills: `skills-0.2.0.zip` / `skills-es-0.2.0.zip`
- Plugin: `plugin-stratio-governance-stratio-cowork-0.2.0.zip` / `plugin-stratio-governance-stratio-cowork-es-0.2.0.zip`

Individual pack script usage:

```bash
# English (default)
bash pack_opencode.sh --agent data-analytics-officer
# → data-analytics-officer/dist/opencode/data-analytics-officer/

# Spanish
bash pack_opencode.sh --agent data-analytics-officer --lang es
# → data-analytics-officer/dist/es/opencode/data-analytics-officer/
```

### Translation workflow

When adding or modifying translatable content:

1. Edit the primary file (e.g., `SKILL.md`) with English content
2. Create or update the counterpart in `es/` (e.g., `es/.../SKILL.md`) with the Spanish translation
3. Run `bin/check-translations.sh` to verify no translations are missing

## Changelog

`CHANGELOG.md` tracks user-facing milestones per release: new agents, new shared skills, architectural changes, breaking changes, and structural refactors that change how the monorepo is consumed. Each release section aggregates those milestones at a summary level, not the incremental PRs that built them. **The changelog is always written in English**, regardless of the conversation language — it is part of the repository's public surface and is not translated into the `es/` overlay.

**Do not add to the changelog:** small bug fixes, documentation tweaks, internal renames, test adjustments, dependency bumps without user impact, and intermediate work inside a feature that has not shipped yet. If the entry would read as "fix typo", "small improvement" or "minor refactor", it belongs in the commit / PR — which is already the source of truth at that level of detail.

Practical rule: before adding an entry, ask whether an external consumer of this repo would care about it. If the answer is no, the entry does not belong here.

When preparing a release, collapse incremental PR-level entries accumulated in the upcoming section into a handful of high-level bullets (by agent, shared-skill family, packaging, i18n, CI/CD). Keep the released section short — the git log carries the detail.

## Adding a new agent

The complete creation guide is in `README.md` (section "Creating a new agent"). Monorepo integration checklist:

1. Create a `my-agent/` folder with the minimum structure:
   - `AGENTS.md` — role, workflow, agent rules
   - `opencode.json` — MCPs and permissions for OpenCode (if it uses OpenCode)
   - `skills/` — optional; if the agent has its own skills, canonical format `skills/<name>/SKILL.md`
   - `imported-skills` — optional; list of shared skills from the monorepo to include (one line per skill)
   - `guides` — optional; list of guides that AGENTS.md references directly
2. Add `my-agent` to the `release-modules` file (one line per agent) so that `make package` includes it
3. Update the agents table in `README.md`
4. Create counterparts in `es/<agent>/` for all translatable files (see [Internationalization](#internationalization-i18n))
