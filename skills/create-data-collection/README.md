# create-data-collection

Searches the technical data dictionary for tables and paths, then creates a new **data collection** (technical domain) in Stratio Governance grouping the selected assets. **Phase 0 of the semantic-layer pipeline** — the container that every subsequent phase (`create-technical-terms`, `create-ontology`, `create-business-views`, `create-sql-mappings`, `create-semantic-terms`, `build-semantic-layer`) works on.

## What it does

- Takes a search seed from `$ARGUMENTS` or asks the user for the kind of data they are looking for.
- Runs `search_data_dictionary` iteratively — short keywords work better than full phrases; the user can refine and accumulate selections across iterations.
- Allows mixed selection of `Table` and `Path` entries by number; keeps a running summary of the chosen assets.
- Asks for a collection name (underscores, no special characters) and description, using only what the user provides or the actual metadata of the selected assets — no invented business context.
- Verifies the name is not already in use (`search_domains` / `list_domains` with `domain_type='technical'`).
- Confirms with the user and invokes `create_data_collection`, splitting the selection by `subtype` into `table_metadata_paths` and `path_metadata_paths`.
- Warms the cache (`list_domains(domain_type='technical', refresh=true)`) so the collection is visible immediately to the next skill.

## When to use it

- The user wants to register a new technical domain in Governance to group a set of tables and paths.
- The user needs the container in place before calling `build-semantic-layer` or any `create-*` skill.
- Do **not** use this to build the semantic layer itself — for that, chain with `build-semantic-layer` (or the individual `create-*` skills).

## Dependencies

### Other skills
- **Typical next step:** `build-semantic-layer` (recommended) or `create-technical-terms` directly.

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Data (`sql`):** `search_data_dictionary`, `search_domains`, `list_domains`.
- **Governance (`gov`):** `create_data_collection`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Naming convention:** no spaces, no special characters (use underscores). Same rule as ontology names.
- **Keyword search:** `search_data_dictionary` works best with short terms. Split natural-language phrases into separate searches and accumulate selections.
- **Creation is not idempotent** — running the skill twice with the same name produces a conflict. The skill checks for pre-existence before calling the MCP.
- **Cache warming is best-effort.** If the refresh call fails, it is ignored; the collection may take 1–2 minutes to propagate and the next skill will retry with `refresh=true`.
- **Do not invent business context.** Descriptions and names come from the user or from the actual metadata of the selected tables — never from inferred themes.
