# Guides

Shared technical guides referenced from skills and agent instructions across the monorepo. They are not skills themselves — they are reference documents that one or more skills (or an agent's `AGENTS.md`) load to share a common body of rules, patterns or contracts without duplicating them.

A guide is consumed in one of two ways:

- **From a skill** — the skill lists the guide in its `guides` manifest. At packaging time, the pack scripts copy the guide flat into the skill folder and rewrite every `guides/<file>` reference inside the skill so the prefix disappears (e.g. `See guides/stratio-data-tools.md` becomes `See stratio-data-tools.md`). The result is a skill folder that resolves its references locally and can be packaged standalone.
- **From an agent's `AGENTS.md`** — the agent lists the guide in its top-level `guides` manifest. The pack scripts copy it into `<bundle>/guides/` and leave the literal `guides/<file>` reference untouched, because at agent level that folder physically exists.

## Available guides

| Guide | What it covers | Used by |
|---|---|---|
| [external-api-calls.md](external-api-calls.md) | How to make outbound HTTP/HTTPS calls from inside the Stratio Cowork sandbox: auth modes, proxy behaviour, timeouts, error handling, retries. | `cowork-api` skill. |
| [quality-exploration.md](quality-exploration.md) | Patterns for exploring data quality coverage: how to interpret dimensions, gaps and priorities, and how to phrase findings back to the user. | `assess-quality`, `create-quality-rules` (skills); `data-analytics-officer`, `data-governance-officer`, `data-quality` (agents). |
| [stratio-data-tools.md](stratio-data-tools.md) | Mandatory usage rules for the Stratio data MCPs (`query_data`, `list_domains`, `search_domains`, `generate_sql`, `profile_data`, `get_tables_details`, …): call order, parameter contracts, anti-patterns. | `assess-quality`, `build-semantic-layer`, `create-sql-mappings`, `explore-data`, `stratio-data` (skills); `data-analytics-officer`, `data-governance-officer`, `data-quality`, `semantic-layer` (agents). |
| [stratio-mcp-response-patterns.md](stratio-mcp-response-patterns.md) | Common response shapes returned by Stratio MCP tools and how to interpret them (success, partial, error, paginated, governed-vs-raw). Shared low-level reference for both data and governance flows. | `assess-quality`, `build-semantic-layer`, `create-sql-mappings`, `explore-data`, `stratio-data`, `stratio-semantic-layer` (skills); `data-analytics-officer`, `data-governance-officer`, `data-quality`, `semantic-layer` (agents). |
| [stratio-semantic-layer-tools.md](stratio-semantic-layer-tools.md) | Mandatory usage rules for the Stratio Governance MCPs (`create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms`, `create_business_term`, `refine_foreign_keys`, …) — sister document of `stratio-data-tools.md` for the governance side. | `build-semantic-layer`, `create-sql-mappings`, `stratio-semantic-layer` (skills); `data-governance-officer`, `semantic-layer` (agents). |
| [visual-craftsmanship.md](visual-craftsmanship.md) | Visual design principles shared by every writer skill (PDF, DOCX, PPTX, XLSX, web, canvas): typography, palette, composition, when to delegate to which writer. Contains the disambiguation table for `web-craft` vs `canvas-craft` vs `pdf-writer`. | `brand-kit`, `canvas-craft`, `docx-writer`, `pdf-writer`, `pptx-writer`, `web-craft`, `xlsx-writer` (skills); `data-analytics-officer`, `data-governance-officer`, `data-quality` (agents). |

## Adding a new guide

1. **Place the file.** `guides/<my-guide>.md`. Write it in English (this is the primary language for the monorepo).
2. **Translate.** Create the Spanish counterpart at `es/guides/<my-guide>.md`. Run `bash bin/check-translations.sh` to verify the pair is detected. When a pack script runs with `--lang es`, it resolves content from the `es/` overlay automatically; both versions must exist if you want the guide to be available in both languages.
3. **Declare consumers.**
   - Each shared skill that needs the guide lists it in its `guides` manifest at `skills/<skill>/guides` (one filename per line).
   - Each agent whose `AGENTS.md` references the guide directly lists it in `agents/<agent>/guides`.
4. **Reference it.** Inside any `.md` file (skill body, agent instructions, sub-guide), use the path `guides/<my-guide>.md`. The pack scripts rewrite this path at packaging time so it works regardless of the final bundle layout.
5. **Keep it generic.** A guide should be reusable by at least two skills, or by an agent's `AGENTS.md` plus at least one skill. If only one skill needs it, it belongs as a sub-file of that skill (e.g. `skills/<skill>/REFERENCE.md`), not in this folder.

## Path conventions

- **Source path (everywhere in `.md` files):** `guides/<file>.md` — never an absolute path, never a different prefix.
- **Inside a skill bundle:** the pack scripts copy the guide flat into the skill directory (sibling of `SKILL.md`, not inside a nested `guides/` folder) and run a recursive `sed 's|guides/||g'` over every `.md` in the skill, so `guides/<file>.md` becomes `<file>.md` after packaging. This keeps the skill self-contained and packable standalone.
- **Inside an agent bundle:** the guide is copied to `<bundle>/guides/` (the folder is preserved) and the literal `guides/<file>.md` reference in `AGENTS.md` is **not** rewritten — it still resolves because the folder physically exists at agent level.
- **Inspect it yourself:** the substitution happens in `pack_opencode.sh` (the `find … -exec sed -i 's|guides/||g' {} \;` step) and is duplicated by `pack_stratio_cowork.sh` and `pack_skills.sh`. The agent-level `guides/` folder is created by the agent-bundling step of the same scripts.

## See also

- [`skills/README.md`](../skills/README.md) — how shared skills declare and consume guides.
- [`agents/README.md`](../agents/README.md) — how agents declare guides from this folder via their `guides` manifest.
- Repository root [`README.md`](../README.md) — packaging scripts and the i18n overlay model.
