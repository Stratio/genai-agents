# explore-data

Quick exploration of governed data through the Stratio data MCPs: find domains, understand tables and columns, read existing business terminology, and optionally run lightweight statistical profiling and governance-quality checks before a deeper analysis.

## What it does

- Resolves the target domain by name or topic (`search_domains` with `prefer_semantic` by default; falls back to `list_domains`).
- Lists tables, pulls business descriptions, column metadata and domain knowledge, and surfaces business terminology relevant to the user's question.
- On focused scope (single domain or a small subset of tables), runs `profile_data` and `get_tables_quality_details` in parallel to add a statistical + governance-coverage layer without turning exploration into a full analysis.
- Reads `output/MEMORY.md` (when present) for known data patterns and warns about recurring issues before profiling.
- Produces a structured summary and 3–5 concrete analytical suggestions tailored to the tables and columns found (time trend, Pareto, segmentation, funnel, cohort, etc.).

## When to use it

- The user asks "what data do we have on X", "show me the tables of domain Y", or wants to understand a domain before choosing an analysis.
- Before analyses that require knowing table relationships and column semantics.
- As a launchpad for other skills: `assess-quality`, `propose-knowledge`, or the agent's analytical workflow.
- Do **not** use it as a replacement for a full quality assessment (use `assess-quality`) or for building a semantic layer (use `build-semantic-layer`).

## Dependencies

### Other skills
- **Companion reference:** `stratio-data` (MCP rules and patterns — loaded before any data interaction).
- **Typical next steps:** `assess-quality`, `propose-knowledge`, or the agent's analysis workflow.

### Guides
- `stratio-data-tools.md` — flow for the data MCPs: `search_domains` → `list_domain_tables` → `get_tables_details` → `query_data`. Rule of thumb: never write SQL manually; always delegate to `generate_sql`. Also covers `profile_data` thresholds and `get_tables_quality_details` usage.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`, `generate_sql`, `profile_data`, `get_tables_quality_details`.

### Python
None — this is a prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Profiling is costly.** The skill restricts `profile_data` to focused scopes (single domain or short list of tables) and uses adaptive sampling thresholds (100k / 1M rows) defined in `stratio-data-tools.md` section 5.1.
- **Semantic vs. technical domains:** by default the skill prefers the semantic layer (`prefer_semantic=true`) — the user's bare domain name resolves to the `semantic_*` entry when one exists. Switches to technical only on explicit user phrasing.
- **MEMORY.md integration:** when `output/MEMORY.md` exists, known data patterns are surfaced up-front so the user does not re-discover them.
