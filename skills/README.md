# Shared skills

Reusable skills that more than one agent in the monorepo declares via its `imported-skills` manifest. Sharing avoids maintaining identical copies of the same skill inside every agent — the pack scripts inline the shared content at packaging time so each agent bundle is still self-contained.

A shared skill should be **as self-contained as possible**: no dependencies on Python tools, styles or templates owned by a specific agent. If a skill depends heavily on artifacts of one agent only, keep it as a local skill inside `agents/<agent>/skills/` instead.

## Catalogue

The catalogue is grouped by family. The *Used by* column lists the agents in this monorepo that import the skill via their `imported-skills` manifest. A blank cell means the skill is currently used only through a functional plugin (see [`plugins/README.md`](../plugins/README.md)) or as a standalone bundle for third-party consumers.

### Stratio MCP wrappers and data exploration

| Skill | Purpose | Used by |
|---|---|---|
| [explore-data](explore-data/) | Quick exploration of data domains, tables, columns, statistical profiling, governance quality coverage and business terminology via the governed-data MCPs. | data-analytics-officer |
| [propose-knowledge](propose-knowledge/) | Propose business terms, definitions and preferences discovered during an analysis to the Stratio Governance layer of a domain. | data-analytics-officer |
| [refine-foreign-keys](refine-foreign-keys/) | Add, modify or remove virtual foreign keys of tables in a technical domain, after `create-technical-terms`. | data-governance-officer, semantic-layer |
| [refine-semantic-foreign-keys](refine-semantic-foreign-keys/) | Add, modify or remove the foreign key relations persisted in the business term of semantic views in a `semantic_<x>` domain, after `create-semantic-terms`. | data-governance-officer, semantic-layer |
| [stratio-data](stratio-data/) | Mandatory rules, usage patterns and best practices for the Stratio data MCP tools (`query_data`, `list_domains`, `generate_sql`, `profile_data`, …). | standalone (stratio-data-toolkit plugin) |
| [stratio-semantic-layer](stratio-semantic-layer/) | Mandatory rules, usage patterns and best practices for the Stratio Governance MCP tools (`create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms`, …). | data-governance-officer, semantic-layer |

### Semantic-layer pipeline

| Skill | Purpose | Used by |
|---|---|---|
| [build-semantic-layer](build-semantic-layer/) | Full end-to-end pipeline orchestrator: technical terms → ontology → business views → SQL mappings → semantic terms, with optional view publishing. | data-governance-officer, semantic-layer |
| [create-business-views](create-business-views/) | Create, regenerate, delete or publish business views and their SQL mappings from an existing ontology. | data-governance-officer, semantic-layer |
| [create-data-collection](create-data-collection/) | Create a new data collection (technical domain) and search the technical dictionary for tables and paths to include. | data-governance-officer, semantic-layer |
| [create-ontology](create-ontology/) | Create, extend or delete ontology classes with interactive planning from reference files (`.owl`, `.ttl`, CSVs, business docs). | data-governance-officer, semantic-layer |
| [create-semantic-terms](create-semantic-terms/) | Generate or regenerate semantic terms for the business views of a domain. | data-governance-officer, semantic-layer |
| [create-sql-mappings](create-sql-mappings/) | Create or update SQL mappings for existing views, without recreating the views, with optional publish step. | data-governance-officer, semantic-layer |
| [create-technical-terms](create-technical-terms/) | Create or regenerate technical terms (table and column descriptions) for an entire domain. Seeds the collection description when missing. | data-governance-officer, semantic-layer |
| [manage-business-terms](manage-business-terms/) | Create business terms in the dictionary, single or batch, with relationships to data assets via guided planning. | data-governance-officer, semantic-layer |
| [manage-critical-data-elements](manage-critical-data-elements/) | Consult or define Critical Data Elements (CDEs) for a domain. Mandatory approval pause before any tagging operation. | data-governance-officer, data-quality |

### Data quality

| Skill | Purpose | Used by |
|---|---|---|
| [assess-quality](assess-quality/) | Assess quality coverage for a domain, table or column: dimensions covered, gaps, columns prioritised for new rules. | data-analytics-officer, data-governance-officer, data-quality |
| [create-quality-rules](create-quality-rules/) | Design and create data quality rules with mandatory human confirmation before execution. Covers gap-driven (Flow A) and ad-hoc (Flow B) creation. | data-governance-officer, data-quality |
| [create-quality-schedule](create-quality-schedule/) | Create a schedule (at folder/collection level) that runs all quality rules in one or more folders automatically. | data-governance-officer, data-quality |
| [update-quality-rules](update-quality-rules/) | Modify existing rules: fix SQL, change thresholds, update descriptions, add/remove scheduling. Requires the rule UUID and human confirmation. | data-governance-officer, data-quality |
| [update-quality-scheduler](update-quality-scheduler/) | Modify an existing quality scheduler: change cron, update collections/filters, rename, activate/deactivate, resize execution. Requires the scheduler UUID and human confirmation. | data-governance-officer, data-quality |
| [quality-report](quality-report/) | Generate a formal quality coverage report in the format chosen by the user — chat, PDF, DOCX, PPTX, web dashboard, web article, poster or XLSX. Delegates file rendering to the writer skills. | data-analytics-officer, data-governance-officer, data-quality |

### Office document I/O

| Skill | Purpose | Used by |
|---|---|---|
| [docx-reader](docx-reader/) | Read Word documents (`.docx` and legacy `.doc`). Prose, tables, images, comments, tracked changes — with a diagnose-first strategy. | data-analytics-officer, data-governance-officer, data-quality, semantic-layer |
| [docx-writer](docx-writer/) | Create polished Word documents and perform structural ops on existing ones (merge, split, find-replace, `.doc` conversion). Intentional design — no Calibri-everywhere defaults. | data-analytics-officer, data-governance-officer, data-quality |
| [pdf-reader](pdf-reader/) | Read PDFs of any kind (text, scanned, exported decks, forms, data-heavy). Text, tables, images, form-field values, attachments, layout — diagnose-first. | data-analytics-officer, data-governance-officer, data-quality |
| [pdf-writer](pdf-writer/) | Create designed PDFs (reports, invoices, certificates, newsletters, booklets, …) and transform existing ones (merge, split, rotate, watermark, encrypt, flatten, forms). | data-analytics-officer, data-governance-officer, data-quality |
| [pptx-reader](pptx-reader/) | Read PowerPoint decks (`.pptx` and legacy `.ppt`). Slide text, bullets, tables, notes, images, charts, comments — diagnose-first. | data-analytics-officer, data-governance-officer, data-quality, semantic-layer |
| [pptx-writer](pptx-writer/) | Create polished decks and transform existing ones (merge, split, reorder, find-replace in text and speaker notes, `.ppt` conversion, rasterise, export to PDF). | data-analytics-officer, data-governance-officer, data-quality |
| [xlsx-reader](xlsx-reader/) | Read Excel workbooks (`.xlsx`, `.xlsm` and legacy `.xls`). Cells, tables, formulas, chart data, hidden sheets — diagnose-first. | data-analytics-officer, data-governance-officer, data-quality |
| [xlsx-writer](xlsx-writer/) | Create analytical workbooks (cover/KPI, pivot, coverage matrix, catalog, quantitative model) and perform structural ops on existing files (merge, split, find-replace, `.xls` conversion, formula refresh). | data-analytics-officer, data-governance-officer, data-quality |

### Visual craftsmanship

These three skills cover every visual output of the monorepo. They share [`guides/visual-craftsmanship.md`](../guides/visual-craftsmanship.md) — the disambiguation table for picking between them lives there.

| Skill | Purpose | Used by |
|---|---|---|
| [brand-kit](brand-kit/) | Centralised catalogue of visual identity themes (colours, typography, chart palettes, sizes, tone). Ships ten curated themes, extensible by clients. Every writer skill consumes it via a generic "centralised theming skill" reference. | data-analytics-officer, data-governance-officer, data-quality |
| [canvas-craft](canvas-craft/) | Single-page visual artifacts (posters, covers, certificates, marketing one-pagers, infographics) as PDF or PNG. Composition dominates over prose. | data-analytics-officer, data-governance-officer, data-quality |
| [web-craft](web-craft/) | Distinctive, production-grade interactive frontends (HTML/CSS/JS, React, Vue). Components, pages, landings, dashboards. | data-analytics-officer, data-governance-officer, data-quality |

### Platform and meta-tools

| Skill | Purpose | Used by |
|---|---|---|
| [cowork-api](cowork-api/) | Upload, import, deploy or register packaged agent/skill/plugin bundles to Stratio Cowork via `genai-api`. Calls `/v1/agents/bundle/import` and `/v1/agents/skills/bundle/import`; plugins dispatch to both. | agent-creator, skill-creator |
| [skill-creator](skill-creator/) | Authoring guide for creating high-quality SKILL.md files. Anatomy, frontmatter, progressive disclosure, writing patterns, quality checklist. | agent-creator, skill-creator |

## Anatomy of a shared skill

```
skills/<name>/
├── SKILL.md       # Skill definition (YAML frontmatter + body), required
├── README.md      # Developer-facing documentation, required
├── guides         # Optional plain-text manifest listing root-level guides this skill needs (one filename per line — NOT a folder)
└── ...            # Optional supporting files (REFERENCE.md, sub-templates, helpers)
```

**SKILL.md frontmatter limits** (enforced by Anthropic / OpenCode / GitHub Copilot at runtime):

- `name` — 1–64 chars, regex `^[a-z0-9]+(-[a-z0-9]+)*$`, must equal the parent directory name, must not contain reserved words `anthropic` or `claude`.
- `description` — 1–1024 chars (only the first ~250 are shown in `/skills` UI listings).
- File name must be exactly `SKILL.md`, frontmatter must be valid YAML between `---` markers.

Soft recommendation: keep the SKILL.md body under ~500 lines. Beyond that, extract supporting material into sibling files (e.g. `REFERENCE.md`, `FORMS.md`, `STRUCTURAL_OPS.md`) and load them on demand via progressive disclosure.

## Using a shared skill in an agent

1. **Import it.** Add the skill name to `agents/<agent>/imported-skills`, one per line:

   ```
   explore-data
   propose-knowledge
   ```

2. **Declare guides if needed.** If the agent's `AGENTS.md` references a root-level guide directly, add it to `agents/<agent>/guides`:

   ```
   stratio-data-tools.md
   ```

3. **Package as normal.** The pack scripts (`pack_opencode.sh`, `pack_stratio_cowork.sh`) copy each guide declared in the skill's own `guides` manifest into the skill folder in the output and rewrite the references in `SKILL.md` so it stays self-contained:

   ```bash
   bash pack_opencode.sh --agent <agent>
   ```

   Example output for an agent that imports `explore-data` (which declares `stratio-data-tools.md`):

   ```
   .claude/
     skills/
       explore-data/
         SKILL.md                  # references "stratio-data-tools.md" (flat, local)
         stratio-data-tools.md     # guide inlined inside the skill
     guides/
       stratio-data-tools.md       # also at agent level for AGENTS.md (possible duplicate, ok)
   ```

If the agent has a local skill in `agents/<agent>/skills/` with the same name as a shared one, the local version takes priority and the shared one is skipped.

## Cross-referencing other shared skills

Most skills here stay fully self-contained so they can be packaged standalone for third-party consumers. Cross-referencing another shared skill by name from inside a `SKILL.md` is **permitted** only when the workflow genuinely depends on delegating (e.g. `quality-report` delegates file rendering to `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` and `brand-kit`).

When a skill cross-references another:

- Any agent that imports the cross-referencing skill **must also import** every skill named inside it. Without that, the references at runtime point to skills the agent cannot load.
- The skill's own `README.md` documents the dependency explicitly.
- The skill may detect missing dependencies at the start of its workflow and **gracefully degrade** to the features that still work. Concrete example: `quality-report` offers the Chat format standalone, but the PDF, DOCX, PPTX, web-dashboard, web-article, poster and XLSX formats only when the host agent declares the matching writer skill. A chat-only agent imports `quality-report` without any writer and still gets a working subset.

### Centralised theming — a special case of decoupled cross-reference

For visual output, the rule is one level subtler: every writer skill (`docx-writer`, `pptx-writer`, `pdf-writer`, `xlsx-writer`, `web-craft`, `canvas-craft`) refers to a **"centralised theming skill" generically** — it never names `brand-kit` literally. The disambiguation lives in [`guides/visual-craftsmanship.md`](../guides/visual-craftsmanship.md). Why this matters:

- A client can replace `brand-kit` with their own theming skill (different palette, different tokens) without editing any writer.
- A standalone pack of any single writer (e.g. only `docx-writer`) still works by improvising tokens from `visual-craftsmanship.md` when no theming skill is present.

In short: writers depend on the **role** ("centralised theming skill"), not on the implementation (`brand-kit`). Treat any future visual-output skill the same way.

## Adding a new shared skill

1. **Create the folder and `SKILL.md`** in English under `skills/<name>/`. Pick a kebab-case name. The directory name must match the `name:` value in the frontmatter.
2. **Write `README.md`** for developers. Same expectations as every other shared skill.
3. **Declare guides** if you depend on any from the [`guides/`](../guides/) folder by listing them in `skills/<name>/guides` (one filename per line).
4. **Translate.** Create the Spanish counterpart at `es/skills/<name>/SKILL.md` (and any sub-guide or `README.md` of the skill). Run `bash bin/check-translations.sh` afterwards — it scans every `.md` under `skills/<name>/` and reports missing Spanish counterparts.
5. **Import it from agents.** Add the skill name to `agents/<agent>/imported-skills` for every agent that should ship it.
6. **Update this catalogue.** Add a row to the appropriate family table above. The repository root README only points here — no table to update there.

When writing the SKILL.md body, follow the rules at the top of this file (self-containment, no Python/template assumptions specific to one agent) and respect a couple of platform-portability conventions:

- **Do not reference `AGENTS.md` or `CLAUDE.md` by name.** Use generic phrasing such as "according to the agent's instructions" or "following the user question convention". The pack scripts substitute the agent-instructions filename depending on the target platform (OpenCode uses `AGENTS.md`, Claude Code uses `CLAUDE.md`); a literal reference would silently break on the other platform.
- **Reference guides as `guides/<file>.md`** regardless of how deep the referencing file lives inside the skill. The pack scripts copy the guide flat next to `SKILL.md` and run a recursive `sed 's|guides/||g'` over every `.md` in the skill at packaging time, so all references become flat filenames in the bundle and the skill stays packable standalone.

## See also

- [`agents/README.md`](../agents/README.md) — agents that import these skills.
- [`guides/README.md`](../guides/README.md) — technical guides skills can reference.
- [`plugins/README.md`](../plugins/README.md) — functional plugins that bundle skills together (e.g. `stratio-productivity`, `stratio-data-toolkit`).
- Repository root [`README.md`](../README.md) — packaging scripts, output structure and the i18n overlay model.
