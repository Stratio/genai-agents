# create-technical-terms

Creates or regenerates technical descriptions (tables and columns) for a technical domain in Stratio Governance. **Phase 1 of the semantic-layer pipeline.** Also seeds the collection description when missing — no need to call `create_collection_description` separately.

## What it does

- Resolves the technical domain (`search_domains` with `domain_type='technical'`, falling back to `list_domains`).
- Reports the current state: total tables, tables already documented, tables pending, and whether the collection has a description.
- Offers four scope options: all pending tables (idempotent), a specific subset, full regeneration (destructive), or regeneration of specific tables (destructive).
- Offers the user the chance to provide `user_instructions` before the call — including reading local files (data dictionaries, specs, glossaries) to feed definitions into the generator.
- Invokes `create_technical_terms` and reports the tool summary directly; retries failed entities up to twice with improved instructions.

## When to use it

- Bulk-generate technical terms for a freshly created collection.
- Refresh terms after a schema change adds new tables or columns.
- Recover missing technical terms after a partial run.
- Document an existing collection that has been imported but never described.
- For the full semantic-layer pipeline end-to-end, prefer `build-semantic-layer` — it includes Phase 1 as its first step.

## Dependencies

### Other skills
- **Prerequisite:** `create-data-collection` (the technical domain must exist).
- **Typical next step:** `create-ontology`.

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Governance (`gov`):** `create_technical_terms`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **`regenerate=true` is destructive.** Explicit confirmation is mandatory; existing descriptions are deleted and recreated.
- **Idempotent by default:** the tool skips tables that already have a description unless `regenerate=true` is passed.
- **Collection description is generated automatically** the first time, so there is no dedicated step for it.
- **`user_instructions`** never asks about language or output format (those are controlled internally) — only about domain context, business definitions and naming rules.
