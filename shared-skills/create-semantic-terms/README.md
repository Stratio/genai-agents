# create-semantic-terms

Generates or regenerates **semantic terms** (business-facing descriptions of views and their columns) in the Stratio Governance glossary. **Phase 5 of the semantic-layer pipeline** — the final step before the semantic layer is ready for review.

## What it does

- Resolves the technical domain and inspects existing views with their state, mappings and semantic terms (`list_technical_domain_concepts`).
- Enforces the prerequisite: **views must have a SQL mapping** to produce semantic terms. Views without mapping are surfaced and excluded, with a pointer to `create-sql-mappings` or `create-business-views`.
- Offers four scope options: create for views without terms (idempotent), a specific subset, full regeneration (destructive), or regeneration of selected views (destructive).
- Offers the user the chance to provide `user_instructions` — including reading local files (business glossaries, functional docs, terminology style guides) to guide the generator.
- Invokes `create_semantic_terms` and reports the tool summary; retries failed views up to twice with improved instructions.

## When to use it

- Populate semantic terms for the first time after the semantic-layer pipeline reaches Phase 4.
- Refresh terms after the ontology or the views change.
- Recover missing terms after a partial generation.
- For business-dictionary entries (KPIs, concepts, acronyms) that span multiple assets, prefer `manage-business-terms` — that is a different governance artefact.

## Dependencies

### Other skills
- **Prerequisites:** the full semantic-layer stack up to Phase 4 (`create-data-collection` → `create-technical-terms` → `create-ontology` → `create-business-views` → `create-sql-mappings`).
- **Optional next step:** `manage-business-terms` to enrich the dictionary with cross-asset concepts.

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Governance (`gov`):** `list_technical_domain_concepts`, `create_semantic_terms`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **`regenerate=true` is destructive.** Explicit confirmation is mandatory; the existing terms of the targeted views are deleted and recreated.
- **Hard prerequisite: mapping must exist.** The skill refuses to run on views without SQL mapping and points to the remediation skill.
- **The semantic layer is considered complete** once this phase succeeds. If the views are still Draft, the user can publish them via the Governance UI or by asking the agent.
