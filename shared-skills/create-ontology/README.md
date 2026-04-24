# create-ontology

Interactive skill to create, extend or delete classes of an ontology in Stratio Governance. Phase 2 of the semantic-layer pipeline: it takes a technical domain (and optionally reference files from the user) and produces a reviewed Markdown plan that becomes an ontology through the governance MCPs.

## What it does

- Discovers the technical domain (`search_domains` / `list_domains`) and the ontologies that may already exist for it.
- Reads local reference files the user provides (`.owl`, `.ttl`, CSVs, business docs) to seed class proposals.
- Runs an interactive planning loop: proposes classes, data properties, relationships and source tables; iterates with the user up to three times until the plan is approved.
- Creates a new ontology, extends an existing one with new classes, or deletes specific classes (the destructive path is always confirmed, and classes bound to Published business views are automatically skipped).
- Verifies the result with `get_ontology_info` and reports what was created versus what was planned.

## When to use it

- The user wants to model a new domain as an ontology before building business views.
- An existing ontology needs new classes (extension is ADD-only).
- Obsolete classes need to be removed (with the usual Published-views protection).
- Before running this skill: the technical collection must exist (`create-data-collection`). Phase 1 (`create-technical-terms`) is recommended but not strictly required.
- Do not use this to generate business views or SQL mappings — that is `create-business-views` and `create-sql-mappings`.

## Dependencies

### Other skills
- **Prerequisite:** `create-data-collection` (the technical domain must exist).
- **Recommended before:** `create-technical-terms` (table descriptions improve the ontology plan).
- **Typical next step:** `create-business-views`.

### Guides
- None. The skill carries its MCP reference inline in `SKILL.md`.

### MCPs
- **Governance (`gov`):** `search_ontologies`, `list_ontologies`, `get_ontology_info`, `create_ontology`, `update_ontology`, `delete_ontology_classes`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_tables_details`, `get_table_columns_details`, `search_domain_knowledge`.

### Python
None — this is a prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Destructive operation:** `delete_ontology_classes` requires explicit user confirmation. Classes with dependent Published business views are automatically skipped (reported as `skipped_locked`).
- **Immutable classes:** existing classes cannot be modified. To change a class you must delete it and re-create it (allowed only if no Published view depends on it).
- **Naming:** no spaces (use underscores), no special characters. Same convention as collections.
- **`user_instructions`:** the skill always offers the user a chance to provide extra context (glossaries, business docs) before calling the creation tool; if the user provides file paths, the skill reads them and feeds the content into the plan.
