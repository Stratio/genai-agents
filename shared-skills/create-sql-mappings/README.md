# create-sql-mappings

Creates or updates the SQL mappings of existing business views in Stratio Governance **without recreating the views** (and without losing their semantic terms). **Phase 4 of the semantic-layer pipeline.** Optionally publishes the affected Draft views afterwards.

## What it does

- Resolves the technical domain and inspects existing views (`list_technical_domain_concepts`) with their governance state and mapping presence.
- Offers three scopes: all views without mapping (safe), specific views (can include views that already have a mapping, to update it), or an explicit "update existing mappings" path.
- Offers the user the chance to provide `user_instructions` — including reading local files (ER diagrams, integration specs, reference SQL) to feed JOIN rules, transformations and exclusion filters into the generator.
- Invokes `create_sql_mappings` and reports the tool summary; retries failed views up to twice with improved instructions.
- After updating, offers optional publication of the affected Draft views.

## When to use it

- Correct a mapping that does not reflect the expected SQL.
- Add a missing column to a mapping or fix JOIN logic without rebuilding the view.
- Recover from a partial mapping generation (views that were created without their mapping).
- For end-to-end view + mapping regeneration, prefer `create-business-views` with `regenerate=true`.
- For the full pipeline, prefer `build-semantic-layer`.

## Dependencies

### Other skills
- **Prerequisites:** `create-data-collection`, `create-ontology`, `create-business-views` (the views must already exist).
- **Typical next step:** `create-semantic-terms`.

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Governance (`gov`):** `list_technical_domain_concepts`, `create_sql_mappings`, `publish_business_views`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Not destructive at the view level:** `create_sql_mappings` replaces only the SQL mapping. The view and its semantic terms are preserved.
- **Overwrites existing mappings** when a view is re-run — this is expected and intentional.
- **Publication** is optional and only suggested for views that ended up in Draft state after the update.
