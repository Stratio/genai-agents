# refine-semantic-foreign-keys

Surgical add / modify / remove of foreign key relations between business views in a semantic Stratio Governance domain. Sibling of `create-semantic-terms`, but for FK maintenance only — does NOT regenerate the semantic terms themselves.

## What it does

- Resolves the semantic domain (`search_domains` with `domain_type='business'`, falling back to `list_domains`). Disambiguates bare names (e.g. `sakila` could mean the technical domain or the published `semantic_sakila`) by asking the user explicitly; never auto-routes between the technical and the semantic skill.
- Reports candidates: every view in a published semantic domain carries a semantic Business Term by construction. If the underlying tool later reports a skip warning for a view, the skill surfaces it verbatim and suggests `/create-semantic-terms` for the missing one.
- Offers two scope options: all eligible views (default) or a specific subset.
- Asks the user for `user_instructions` (required) and guides them between the two productive intents — **TARGETED** (name a specific relation) or **DISCOVERY** (ask to detect missing FKs in named views); generic phrases without specifics waste a round trip and are warned against.
- Builds the final `user_instructions` through the **Glossary Instruction Enrichment Workflow** (`stratio-semantic-layer-tools.md` §11), scoped to the `semantic_terms` phase.
- Invokes `refine_semantic_foreign_keys` and forwards the tool's `message` field (a markdown summary covering per-domain totals plus a per-view bullet list with `fk_count`, persistence outcome, BT update status, columns enriched and any skip warning) verbatim to the user — no field parsing.

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
- **Governance (`gov`):** `refine_semantic_foreign_keys`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.

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
- **Idempotent.** Re-running the same instruction yields an empty diff and `BT=unchanged` (no PUT).
- **Language support.** Only EN and ES are supported by the underlying tool. Other languages come back with an explicit error from the chain and are surfaced to the user without presupposing the cause.
- **Technical vs semantic.** This skill operates only on semantic domains (`semantic_<x>`). Technical domains are rejected by the tool with an error that points to `refine_foreign_keys`; the skill surfaces the message verbatim and never auto-routes between the two.
