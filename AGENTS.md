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
  shared-skill-guides/     # Shared guides (not skills; copied to skills-guides/ in the output)
    stratio-data-tools.md
    visual-craftsmanship.md
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
Full BI/BA agent: queries governed data via MCP, analysis with Python (pandas, scipy, scikit-learn), visualizations (matplotlib, seaborn, plotly), report generation (PDF, DOCX, web, PowerPoint, Excel/XLSX), PDF reading and extraction (`pdf-reader`), ad-hoc PDF creation and manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms), DOCX reading (`docx-reader`) and ad-hoc DOCX authoring / manipulation (`docx-writer`: merge, split, find-replace, convert `.doc` to `.docx`), PPTX reading (`pptx-reader`) and ad-hoc PPTX authoring / manipulation (`pptx-writer`: merge, split, reorder, find-replace in slides and notes, convert `.ppt` to `.pptx`) for decks outside the analytical pipeline, XLSX reading (`xlsx-reader`) and ad-hoc XLSX authoring / manipulation (`xlsx-writer`: analytical workbooks with cover/KPI + detail sheets, pivot matrices, tabular exports, merge/split/find-replace, convert `.xls` to `.xlsx`, formula refresh), read-only data quality coverage assessment and reporting (uses shared skills `assess-quality` and `quality-report`; does not create rules), reasoning documentation, validation, cross-session memory management.

### data-analytics-light
Lightweight BI/BA agent: same analytical engine but chat-oriented. Includes read-only data quality coverage assessment with chat-only summaries (uses `assess-quality` and `quality-report` forcing the Chat format; no file generation, no rule creation). No formal report generation — the primary output is the chat. Includes packaging scripts for Claude AI Projects and Claude Cowork.

### semantic-layer
Agent specialized in building and maintaining semantic layers in Stratio Governance. Orchestrates the creation of data collections (technical domains), technical terms, ontologies, business views, SQL mappings, view publishing, semantic terms and business terms via governance MCPs. Does not execute data queries or generate files — its output is MCP tool interaction + chat summaries. Can read local user files to enrich planning, including DOCX specifications via `docx-reader` and PPTX specification decks via `pptx-reader`.

### data-quality
Agent specialized in data governance and quality. Evaluates quality coverage by domain, collection, table or column, identifies gaps (uncovered dimensions), proposes and creates quality rules with mandatory human approval, and generates coverage reports in multiple formats (PDF, DOCX, PPTX, Dashboard web, Web article / Narrative report, Poster/Infographic, XLSX, Markdown). Includes PDF reading (`pdf-reader`) and ad-hoc PDF manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms), DOCX reading (`docx-reader`) and ad-hoc DOCX authoring / manipulation (`docx-writer`: merge, split, find-replace, `.doc` conversion), PPTX reading (`pptx-reader`) and ad-hoc PPTX authoring (`pptx-writer`) for executive quality summary decks and training decks on rules, plus XLSX reading (`xlsx-reader`) for rule-spec workbooks and table catalogs and XLSX authoring (`xlsx-writer`) for multi-sheet coverage workbooks (materialises the Excel option of `quality-report`) and ad-hoc XLSX (rule-spec templates, term catalog exports). Operates on governed data via SQL and governance MCPs.

### governance-officer
Combined governance agent with the full capabilities of both semantic-layer and data-quality. Builds and maintains semantic layers (ontologies, views, mappings, terms) AND manages data quality (assessment, rule creation, scheduling, reports in PDF, DOCX, PPTX, Dashboard web, Web article / Narrative report, Poster/Infographic, XLSX, Markdown). Includes PDF reading (`pdf-reader`) and ad-hoc PDF creation and manipulation (`pdf-writer`: merge, split, watermark, encrypt, forms, ontology documentation), DOCX reading (`docx-reader`) and ad-hoc DOCX authoring / manipulation (`docx-writer`: merge, split, find-replace, `.doc` conversion) for policy briefs, compliance reports and ontology documentation, PPTX reading (`pptx-reader`) and PPTX authoring (`pptx-writer`) for compliance briefings, policy presentations, ontology walkthroughs and steering-committee decks, plus XLSX reading (`xlsx-reader`) for data dictionaries, term catalogs and rule-spec workbooks, and XLSX authoring (`xlsx-writer`) for multi-sheet quality-coverage workbooks, ontology exports, term catalogs, compliance matrices and policy checklist workbooks. Has full access to all governance and data MCP tools with no restrictions.

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

## Claude Code test skills (OpenCode)

Repo-local Claude Code skills under `.claude/skills/` automate the test deployment of an agent into the team's shared OpenCode test directory `~/genai-agents-tests/opencode/<agent>/`. The naming convention `test-opencode-<agent>` makes the target platform explicit (we may add `test-claude-code-<agent>` siblings later for the Claude Code packaging). They are committed to the repo so any teammate gets them on clone.

| Skill | Slash form | Packs |
|-------|-----------|-------|
| `test-opencode-data-analytics` | `/test-opencode-data-analytics` | data-analytics opencode-es |
| `test-opencode-data-quality` | `/test-opencode-data-quality` | data-quality opencode-es |
| `test-opencode-governance-officer` | `/test-opencode-governance-officer` | governance-officer opencode-es |

Each skill runs `pack_opencode.sh --agent <agent> --lang es` and `rsync -a` (no `--delete`) the output into the test folder, so existing extra content in the destination (notably an `output/` folder with previous run artifacts) is preserved. Paths use `git rev-parse --show-toplevel` for the source and `~/genai-agents-tests/opencode/...` for the destination so the skills work regardless of where the repo is cloned.

To add a new test skill for another agent, copy one of the existing folders under `.claude/skills/test-opencode-*/` and adjust the agent name in three places (frontmatter `name`/`description`, `pack_opencode.sh --agent <name>`, and the rsync source/destination paths).

## Shared skills

### Reference rules

Shared-skills **should** stay self-contained when practical — most SKILL.md files in `shared-skills/` do not reference another shared-skill by name, so they can be packaged standalone and consumed in isolation by third-party agents. This is the preferred default.

Cross-referencing other shared-skills by name from inside a shared SKILL.md is **permitted** when the skill's workflow genuinely depends on delegating to others and inlining their logic would duplicate thousands of lines. Examples already in the repo:

- `pdf-reader` ↔ `pdf-writer`, `docx-reader` ↔ `docx-writer`, `pptx-reader` ↔ `pptx-writer` (companion skills that reference each other for round-trip flows).
- `visual-craftsmanship.md` guide (the only place where `web-craft`, `canvas-craft` and `pdf-writer` are compared side by side so an agent can disambiguate).
- `quality-report` (delegates file-format generation to `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` and `brand-kit`).

**Trade-off**: a cross-referencing shared-skill is not perfectly self-contained anymore. It is no longer safe to package standalone — at runtime it needs the skills it names. Two consequences:

1. Any agent that declares a cross-referencing shared-skill in its `shared-skills` manifest must also declare the skills it depends on. Without that, the references inside the SKILL.md point to skills the agent cannot load.
2. The skill's own `README.md` documents the dependency explicitly, so the next developer (or agent author) knows what to bundle.

A chat-oriented agent may intentionally omit some of the dependent skills — in that case the cross-referencing skill should detect the absence at the beginning of its workflow and restrict itself to the features that do not require the missing skills (e.g. offering only the Chat format). This "graceful degradation" is a valid configuration and should be stated in both the skill's SKILL.md (pre-check) and the host agent's AGENTS.md.

Skills inside `<agent>/skills/` and any `AGENTS.md` may reference directly any skill the agent declares (local or shared). Prefer `load /skill-x and follow its §Y` over duplicating instructions.

### Visual-craftsmanship family

Three shared skills cover the visual output of the monorepo. They share the guide `shared-skill-guides/visual-craftsmanship.md` but do not reference each other in runtime. The disambiguation table in that guide is the only place where the three names live together.

- `web-craft` — interactive frontend (HTML/CSS/JS, React, Vue). Components, pages, dashboards.
- `canvas-craft` — single-page static artifacts (PDF/PNG). Posters, covers, certificates, marketing one-pagers, infographics. Ships a small set of OFL display fonts.
- `pdf-writer` — multi-page typographic documents or prose-dominated single pages. Analytical reports, invoices, contracts, zines.

Agents that produce visual output declare the family members they need in `<agent>/shared-skills` and add `visual-craftsmanship.md` to `<agent>/shared-guides`. `data-analytics`, `governance-officer` and `data-quality` all declare the full family (pdf-writer, docx-writer, pptx-writer, web-craft, canvas-craft) so they can offer every output format through both the analytical pipeline and `quality-report`.

### Brand-kit / centralized theming

`brand-kit` is the shared skill that centralizes visual identity tokens (colors, typography, chart palettes, sizes, tone). It ships ten curated themes and is extensible — clients add their own themes directly inside the skill or provide an alternative theming skill. Agents that generate visual deliverables declare `brand-kit` in `<agent>/shared-skills`.

Output skills (`docx-writer`, `pptx-writer`, `pdf-writer`, `xlsx-writer`, `web-craft`, `canvas-craft`) reference the concept "centralized theming skill" **generically**, not by name — they never mention `brand-kit` literally. This keeps self-containment intact: a client can substitute `brand-kit` with their own skill without editing any output skill, and a standalone pack of (for example) `docx-writer` or `xlsx-writer` still works by improvising tokens from `visual-craftsmanship.md`.

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
   - `shared-skills` — optional; list of shared skills from the monorepo to include (one line per skill)
   - `shared-guides` — optional; list of shared-skill-guides that AGENTS.md references directly
2. Add `my-agent` to the `release-modules` file (one line per agent) so that `make package` includes it
3. Update the agents table in `README.md`
4. Create counterparts in `es/<agent>/` for all translatable files (see [Internationalization](#internationalization-i18n))
