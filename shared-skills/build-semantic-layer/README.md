# build-semantic-layer

End-to-end orchestrator that builds the full semantic layer of a technical domain in Stratio Governance. Runs the **five phases of the pipeline in sequence** (technical terms → ontology → business views → SQL mappings → semantic terms), with an optional publication step between phases 4 and 5.

The skill calls the governance MCP tools inline — it does **not** delegate to the individual `create-*` skills (skills cannot programmatically invoke other skills). The `create-*` skills remain available for users who want to run a single phase independently.

## What it does

- Resolves the technical domain and runs a **full diagnosis in parallel**: collection description, technical terms coverage, existing ontologies, business views, mappings and semantic terms — including their governance state.
- Presents a per-phase status dashboard and proposes an execution plan, flagging what is complete, partial or pending, and dependencies between phases.
- Collects **global user context** once: reference files (ontologies, specs, glossaries), business definitions, naming rules. That context is passed as `user_instructions` into every phase that accepts it.
- Executes each phase in strict order, reporting progress and the tool summary after each one. Phase 2 (ontology) runs the same interactive planning loop as `create-ontology`.
- Offers optional publication of the views between phase 4 and phase 5.
- On failure, offers three recovery paths per phase: retry with improved instructions, skip (with a dependency warning), or abort.

## When to use it

- Build the semantic layer of a freshly created collection from scratch.
- Complete a partially built semantic layer (pick up where a previous run stopped).
- Audit an existing semantic layer (the diagnosis dashboard alone is useful even if no phase is executed).
- For a single-phase change, prefer the matching `create-*` skill instead.

## Dependencies

### Other skills
- **Hard prerequisite:** `create-data-collection` (the technical domain must exist).
- **Reference (recommended to load first):** `stratio-semantic-layer` — the governance MCP rules.
- **Delegated in spirit (not in code):** `create-technical-terms`, `create-ontology`, `create-business-views`, `create-sql-mappings`, `create-semantic-terms`.
- **Typical next step:** `manage-business-terms` to enrich the dictionary with cross-asset business terms.

### Guides
- `stratio-semantic-layer-tools.md` — complete reference for the governance MCPs: tool list, immutability of `domain_name`, `user_instructions` contract, destructive-operation protocol, ADD+DELETE ontology rules, state-detection table for idempotency, and the OpenSearch-availability fallback.

### MCPs
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `create_ontology`, `update_ontology`, `delete_ontology_classes`, `create_technical_terms`, `list_technical_domain_concepts`, `create_business_views`, `delete_business_views`, `publish_business_views`, `create_sql_mappings`, `create_semantic_terms`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Destructive operations** (ontology class deletion, view regeneration with `regenerate=true`, semantic-term regeneration) always require explicit user confirmation — the pipeline never auto-regenerates existing artefacts.
- **Cache propagation:** when the domain does not appear after `search_domains`, the skill retries with `refresh=true` and waits up to ~60 seconds before giving up.
- **Phase skipping warns about dependencies:** skipping the ontology phase means no views can be created in phase 3.
- **Publication is never automatic** — the user is asked between phase 4 and phase 5 whether to publish the views (moves them from Draft to Pending Publish).
- **Semantic layer becomes the `semantic_*` domain** once published to the virtualizer; before that, it lives inside the technical domain.
