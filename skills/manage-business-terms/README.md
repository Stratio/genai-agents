# manage-business-terms

Creates business terms (single or batch) in the Stratio Governance dictionary with relationships to data assets. Includes a guided planning step to define name, description, type and related assets at the right granularity (collection / table / column).

Works against both **technical** and **semantic** (`semantic_*`) domains — business terms span the entire dictionary, not just one layer.

## What it does

- Resolves the target domain (technical or semantic) and asks the user what term(s) to create.
- Runs a guided planning step per term: proposes or asks for name and Markdown description, lists asset types via `list_business_asset_types`, and helps the user pick the related-asset granularity:
  - applies to specific columns → relate to columns;
  - applies to specific tables → relate to tables;
  - applies to more than ~2 tables of the same domain → relate to the collection.
- Presents the complete term for user approval and allows edits before execution.
- Supports **batch mode**: plan a list of terms, approve them together, create them sequentially, and report the results at the end.
- Retries failed creations with adjustments (max 2 retries per term).

## When to use it

- Document a KPI, concept or acronym surfaced during analysis.
- Link an existing business concept to concrete tables and columns in the dictionary.
- Register a term that spans several tables of the same domain (relate to the collection).
- Bulk-register a glossary of business terms for a new domain (batch mode).
- For automatic descriptions of views, prefer `create-semantic-terms` — that is the view-scoped equivalent.
- For proposing *candidate* business concepts during exploration, prefer `propose-knowledge`.

## Dependencies

### Other skills
- **Typical predecessors:** `explore-data` or `assess-quality` (surface the concepts to document).
- **Related:** `create-semantic-terms` (view-scoped descriptions), `propose-knowledge` (proposals before formal creation).

### Guides
None. MCP rules and parameters are inline in `SKILL.md`.

### MCPs
- **Governance (`gov`):** `list_business_asset_types`, `create_business_term`.
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`, `get_table_columns_details`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Terms are created in Draft state** and must be reviewed in the Governance UI before publication.
- **Granularity is the user's call.** The skill presents a recommendation based on how many assets the term applies to, but respects the user's final choice.
- **Both technical and semantic domains are accepted** — `domain_name` can be `my_collection` or `semantic_my_collection` depending on where the term should live.
- **Grouping vs. splitting** is a planning decision: the skill asks whether to merge related concepts into a single term or keep them separate.
