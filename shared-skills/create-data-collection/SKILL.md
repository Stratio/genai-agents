---
name: create-data-collection
description: "Search for tables and paths in the technical data dictionary and create a new data collection (technical domain) in Stratio Governance."
argument-hint: "[collection name or search terms (optional)]"
---

# Skill: Create Data Collection

Searches for tables and paths in the technical data dictionary and creates a new data collection (technical domain) in Stratio Governance. Phase 0 of the semantic layer pipeline — allows creating new domains before building their semantic layer.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_data_dictionary(search_text, search_type?)` | sql | Search for tables and paths in the dictionary. `search_type`: `'tables'`, `'paths'` or `'both'` (default). Results ordered by relevance. Each result: `metadata_path`, `name`, `subtype` (Table/Path), `alias?`, `data_store?`, `description?` |
| `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | gov | Create collection + associate tables/paths + refresh technical view. `collection_name` without spaces (use underscores). At least one of the two lists required. The `metadata_path` values come from `search_data_dictionary` results |
| `list_domains(domain_type='technical', refresh?)` | sql | Verify that the name does not already exist. After creating the collection, call with `refresh=true` to warm the cache |

**Key rules**: `collection_name` without spaces or special characters (use underscores) — same convention as ontologies. At least one `table_metadata_paths` or `path_metadata_paths` required. The `metadata_path` values are obtained from `search_data_dictionary` results. Explicit confirmation before creating. Search is read-only and idempotent; creation is not idempotent.

## Workflow

### 1. Determine intent

If `$ARGUMENTS` contains text, use it as the initial search seed and proceed directly to step 2. If there is no argument, ask the user what type of data they are looking for or what collection they want to create, following the user question convention.

### 2. Iterative dictionary search

Execute `search_data_dictionary(search_text, search_type?)` with the provided term. `search_type` defaults to `'both'`.

**Keyword search**: The tool works best with short terms or individual keywords rather than long phrases or multiple words. If the user describes what they are looking for in natural language, extract the most relevant terms and search them separately (e.g.: "customer tables with their contracts" → search first "customers", then "contracts"). Avoid sending complete phrases as search_text.

Present results in a table:

```
| # | Type | Name | metadata_path | data_store | Description |
|---|------|------|---------------|------------|-------------|
| 1 | Table | customers | /path/to/customers | PostgreSQL | Customers table |
```

- **No results**: Offer options: refine search term, change `search_type` (`'tables'`, `'paths'` or `'both'`), or cancel
- **Refinement loop**: The user can search as many times as needed. Accumulate selections between iterations

### 3. Table/path selection

The user selects elements from the table by number (multiple selection: numbers separated by comma). Mix of Table and Path allowed.

Show accumulated summary after each selection:
```
Current selection: Tables: N, Paths: M
```

Offer options: search for more elements or proceed with creation.

### 4. Request name and description

- **Name**: Ask the user what name they want for the collection (`collection_name` without spaces, use underscores — same convention as ontologies). If the user has no preference, a name derived solely from the actual search terms used can be suggested (e.g.: searched "customers" → suggest `customers`). Do not infer themes or business purposes not mentioned by the user.
- **Description**: Ask the user what description they want for the collection. Do not invent a description. If the user has no preference, present the available names and descriptions of the selected tables/paths as context for them to decide, but do not fabricate business context or themes.

**Rule**: Do not invent business context, themes or purposes that have not been provided by the user or derived from the actual metadata of the selected tables (names, descriptions returned by `search_data_dictionary`).

Verify that the proposed name does not match an existing domain by executing `search_domains(name, domain_type='technical')` or `list_domains(domain_type='technical')`. If it already exists, inform and request an alternative name.

### 5. Confirmation and execution

Present the complete final summary before creating:
```
## Create Data Collection
- Name: my_collection
- Description: ...
- Tables (N): [list of metadata_paths]
- Paths (M): [list of metadata_paths]
```

Request explicit user confirmation (write operation).

Separate the selection by `subtype`:
- Results with subtype `Table` → parameter `table_metadata_paths`
- Results with subtype `Path` → parameter `path_metadata_paths`

Invoke `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)`.

Present result: `tables_inserted`, `tables_failed`, `message`.

If there are failures: report which ones and offer to retry only the failed ones (maximum 2 retries).

### 6. Warm cache

After a successful creation, execute `list_domains(domain_type='technical', refresh=true)` to force a cache refresh. No need to wait or retry — the goal is that when the user invokes `/build-semantic-layer` next, the domain is already visible without delays. If the call fails, ignore the error (not critical).

### 7. Summary and next step

Present a summary of the created collection with the final result.

Suggest next step: "You can build its semantic layer with `/build-semantic-layer [name]`"
