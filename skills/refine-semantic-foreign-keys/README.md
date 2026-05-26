# refine-semantic-foreign-keys

Surgical add / modify / remove of foreign key relations between business views of a Stratio Governance domain. Sibling of `create-semantic-terms`, but for FK maintenance only — does NOT regenerate the semantic terms themselves.

## What it does

- Resolves the domain via `search_domains(domain_type='technical')`, falling back to `list_domains`. The tool accepts both the technical name (canonical, preferred in examples) and the `semantic_*` counterpart; if the user typed the semantic form the skill strips the prefix client-side and works on the technical equivalent, telling the user that both forms are accepted.
- Inspects candidates with `list_technical_domain_concepts`: business views with `has_semantic_terms: true` are refinable regardless of governance state (Draft / Pending Publish / Published); views with `has_semantic_terms: false` are surfaced separately and the user is pointed to `/create-semantic-terms` for those.
- Offers two scope options: all refinable views (default) or a specific subset.
- Asks the user for `user_instructions` (required) and guides them between the two productive intents — **TARGETED** (name a specific relation) or **DISCOVERY** (ask to detect missing FKs in named views); generic phrases without specifics waste a round trip and are warned against.
- Builds the final `user_instructions` through the **Glossary Instruction Enrichment Workflow** (`stratio-semantic-layer-tools.md` §11), scoped to the `semantic_terms` phase.
- Invokes `refine_semantic_foreign_keys` and forwards the tool's `message` field (a markdown summary covering per-domain totals plus a per-view bullet list with `fk_count`, persistence outcome, BT update status, columns enriched and any skip warning) verbatim to the user — no field parsing. Errors from the tool are also surfaced verbatim.

## When to use it

- An FK detected by `create-semantic-terms` points to the wrong target view.
- The create phase missed an FK between views that should exist (DISCOVERY mode).
- An FK is no longer applicable and must be removed.
- A targeted maintenance run that should not regenerate the whole semantic term (cheaper than `create_semantic_terms(regenerate=true)`).

## Dependencies

### Other skills
- **Hard prerequisite:** `create-semantic-terms` — every view the user wants to refine must already carry a semantic Business Term. The tool skips views without one with an explicit warning.
- **Reference (recommended to load first):** `stratio-semantic-layer` — the governance MCP rules.

### Guides
- `stratio-semantic-layer-tools.md` — full reference for the governance MCPs, including §11 Glossary Instruction Enrichment Workflow.

### MCPs
- **Governance (`gov`):** `refine_semantic_foreign_keys`, `list_technical_domain_concepts`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **`user_instructions` is required.** The tool rejects empty or whitespace-only input — no concrete instruction means no refine.
- **Not destructive by default.** An FK is removed only when the instruction names it explicitly or its target view disappeared from the domain; generic instructions preserve the current state.
- **Multi-FK columns are supported.** A single source column can participate in multiple FK relations and the chain renders one suffix per relation; the skill needs no special handling.
- **User-added content is preserved across refines.** Any content added to a view's Business Term outside the auto-generated `### Foreign Key Relations` section — additional headings, prose, lists, tables — is kept intact when the refine flow rewrites the section.
- **Views without a semantic Business Term are skipped.** The user is told to run `create_semantic_terms` first; no LLM calls happen for those views.
- **Publication is not required.** Any view with a semantic business term is refinable regardless of governance state (Draft / Pending Publish / Published).
- **Idempotent.** Re-running the same instruction yields an empty diff and `BT=unchanged` (no PUT).
- **Language support.** Only EN and ES are supported by the underlying tool. Other languages come back with an explicit error from the chain and are surfaced to the user without presupposing the cause.
- **Domain form tolerance.** The tool accepts both the technical name (canonical) and the `semantic_*` counterpart; the skill normalizes client-side to the technical form for discovery consistency.
- **Input names are normalized.** Leading and trailing whitespace and wrapping backticks in `view_names` are trimmed automatically.
- **Technical-table FKs are a different skill.** For FKs between physical tables of a technical domain use `refine-foreign-keys`. This skill never auto-routes between the two.
