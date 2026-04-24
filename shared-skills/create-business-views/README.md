# create-business-views

Creates, regenerates, deletes and optionally publishes business views (with their SQL mappings) in Stratio Governance, from an existing ontology. **Phase 3 of the semantic-layer pipeline.** SQL mappings are generated automatically together with each view.

## What it does

- Resolves the technical domain and the target ontology (`search_ontologies` or `list_ontologies`).
- Reports the current state in parallel: classes in the ontology (`get_ontology_info`) vs. views already created (`list_technical_domain_concepts`), with their governance state, mapping and semantic terms.
- Offers five operations: create views for classes without view (idempotent), create for specific classes, regenerate all (destructive), regenerate selected views (destructive), or delete specific views without recreating.
- After creating or regenerating, offers an optional publication step (`publish_business_views`) to move views from Draft to Pending Publish.

## When to use it

- Generate business views for the first time from a reviewed ontology.
- Rebuild views after the ontology has been extended with new classes.
- Remove obsolete views (Published views are automatically skipped).
- Publish a batch of Draft views after creation.
- For SQL-only tweaks without recreating the view, prefer `create-sql-mappings`.
- For the end-to-end pipeline, prefer `build-semantic-layer`.

## Dependencies

### Other skills
- **Prerequisites:** `create-data-collection` and `create-ontology`.
- **Typical next steps:** `create-sql-mappings` (to refine the mappings) or `create-semantic-terms`.

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `list_technical_domain_concepts`, `create_business_views`, `delete_business_views`, `publish_business_views`.
- **Data (`sql`):** `search_domains`, `list_domains`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Mappings are auto-generated** with the views. Use `create-sql-mappings` afterwards only if a mapping needs manual adjustment.
- **`regenerate=true` is destructive** and also drops the associated semantic terms. Explicit confirmation is mandatory.
- **Published views are protected** — `delete_business_views` reports them as `skipped_published`.
- **`user_instructions` is pending tool-side implementation** at the time of writing; the skill already supports the parameter for when it becomes available.
- **Publishing is a governance state change** (not destructive) but still requires explicit user approval and reports `published` / `failed` / `not_found`.
