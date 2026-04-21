# Stratio Semantic Layer MCP Usage Guide

## 1. Fundamental Rule

**The agent never modifies the data model directly.** It operates through governance MCP tools that use internal AI to generate content (descriptions, ontologies, SQL mappings, semantic terms). The agent orchestrates, plans, validates, and provides context — the tools do the generation work.

## 2. Available MCP Tools

### `gov` Server (governance)

| Category | MCP Tool | Purpose |
|----------|----------|---------|
| **Ontology** | `search_ontologies(search_text)` | Search ontologies by free text (name or description). Results by relevance. Use when part of the name is known |
| | `list_ontologies` | List all existing ontologies |
| | `get_ontology_info(name)` | Structure of classes, data properties, and relationships of an ontology |
| | `create_ontology(domain, name, ontology_plan)` | Create a new ontology with a Markdown plan |
| | `update_ontology(domain, name, update_plan)` | Add new classes to an existing ontology |
| | `delete_ontology_classes(ontology_name, class_names)` | DESTRUCTIVE: delete specific classes (protected by Published) |
| **Technical terms** | `create_technical_terms(domain, table_names?, user_instructions?, regenerate?)` | Generate table and column descriptions. Skips existing ones. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |
| **Business views** | `create_business_views(domain, ontology, class_names?, regenerate?)` | Create views + mappings. Skips existing ones. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |
| | `delete_business_views(domain, view_names)` | DESTRUCTIVE: delete specific views without recreating (protected by Published) |
| | `publish_business_views(domain, view_names?)` | Publish views (Draft -> Pending Publish). Without `view_names`, publishes all. Returns `published`, `failed` (transition not allowed), and `not_found`. Idempotent |
| **SQL Mappings** | `create_sql_mappings(domain, view_names?, user_instructions?)` | Create or update SQL mappings for existing views |
| **Semantic terms** | `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | Generate semantic terms. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |
| **Business terms** | `create_business_term(domain, name, description, type, related_assets)` | Create a business term in the dictionary with asset relationships |
| | `list_business_asset_types()` | List available asset types for business terms |
| **Collections** | `create_data_collection(collection_name, description, table_metadata_paths?, path_metadata_paths?)` | Create a data collection (technical domain) with tables and paths. `collection_name` without spaces (use underscores). Automatically refreshes the technical view |
| **Utility** | `list_technical_domain_concepts(domain)` | List existing business views with governance status (Draft/Pending Publish/Published), mappings, and semantic terms |
| | `create_collection_description(domain, user_instructions?)` | Generate ONLY the domain/collection description (without touching tables) |
| | `get_mcp_task_result(task_id)` | Retrieve the result of a long-running tool that continues executing in the background on the `gov` server (see section 9) |

### `sql` Server (domain exploration)

| MCP Tool | Purpose |
|----------|---------|
| `search_domains(search_text, domain_type?, refresh?)` | **Prefer over `list_domains`**. Search domains by free text (name or description). For technical domains: `domain_type='technical'`. For published semantic domains: `domain_type='business'`. Results sorted by relevance. Use when part of the name or topic is known |
| `list_domains(domain_type?, refresh?)` | List available domains. For technical domains: `domain_type='technical'` (includes description if it exists). For published semantic domains: `domain_type='business'` (prefix `semantic_`). `refresh` (boolean, default false): cache bypass — use after creating/deleting collections or when a recently published domain does not appear. Use only when you need to see all domains without filtering |
| `list_domain_tables(domain)` | List tables of a domain with their descriptions (indicates whether they have technical terms) |
| `get_tables_details(domain, tables)` | Table details: business rules, context |
| `get_table_columns_details(domain, table)` | Table columns: names, types, business descriptions |
| `search_domain_knowledge(question, domain)` | Search knowledge in technical and semantic domains |
| `search_data_dictionary(search_text, search_type?)` | Search tables and paths in the technical data dictionary. `search_type`: `'tables'`, `'paths'`, or `'both'` (default). Results sorted by relevance, with `metadata_path`, `name`, `subtype` (Table/Path), `alias`, `data_store`, `description` |
| `get_mcp_task_result(task_id)` | Retrieve the result of a long-running tool that continues executing in the background on the `sql` server (see section 9) |

## 3. Strict Rules

- **IMMUTABILITY of `domain_name`**: The `domain_name` parameter in ALL MCP calls must be **exactly** the value returned by `list_domains` or `search_domains`. NEVER translate, interpret, paraphrase, or infer it. If the domain is called `AnaliticaBanca`, use `"AnaliticaBanca"` — not `"Banca Particulares"`, not `"Analítica Banca"`, not `"banca"`. If in doubt about the exact name, call `search_domains` or `list_domains` again to confirm
- **Technical domains for creation and publishing**: Creation tools (`create_technical_terms`, `create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms`) and publishing (`publish_business_views`) use technical domains. Discover them with `list_domains(domain_type='technical')` or `search_domains(text, domain_type='technical')`. Semantic domains (`semantic_*`) are the RESULT of the process, not the input
- **Semantic domains for exploration**: `list_domains(domain_type='business')`, `search_domains(text, domain_type='business')`, and `search_domain_knowledge` allow exploring already-published semantic layers
- **`user_instructions` always offered**: Before invoking any tool that accepts `user_instructions`, offer the user the opportunity to provide additional context. The agent can **read local files** from the user (documentation, glossaries, specifications, CSVs, ontologies .owl/.ttl) to extract relevant information and pass it as context. Ask if they have files or domain context they want to contribute. This is not blocking — if the user does not contribute, continue without the parameter. **Do not suggest options that the tool controls internally** (language, output format) — focus on domain context, business definitions, and specific rules
- **Destructive operations (`regenerate=true`, `delete_*`)**: ALWAYS require explicit user confirmation with a clear warning of what will be lost. Pattern: detect existence -> inform what will be lost -> ask (skip/execute/cancel) -> additional confirmation for the destructive action
- **View publishing (`publish_business_views`)**: Confirm with the user by listing the views that will be published. Verify prior state with `list_technical_domain_concepts`. This is not destructive and does not require "destructive-type" confirmation, but it is a governance state change that the user must approve. Present the result: published views + failed + not found
- **Ontologies are ADD+DELETE**: `update_ontology` adds new classes. `delete_ontology_classes` deletes specific classes (protected: classes with dependent Published views are automatically skipped). Existing classes cannot be modified
- **Ontology naming**: No spaces (use underscores), no special characters
- **Collection naming**: No spaces (use underscores), no special characters — same convention as ontologies

## 4. Technical Domain Discovery Workflow

Steps to explore a technical domain before building its semantic layer.

### 4.1 Discover Technical Domains

**Prefer searching over listing** — `search_domains` returns relevant results without loading the full list (which can be very large).

If the user provides a domain or gives hints about the topic:
- Execute `search_domains(name_or_hint, domain_type='technical')` to search for matches
- If it matches a result -> use it directly and go to step 4.2
- If there are no matches -> execute `list_domains(domain_type='technical')` as a fallback and ask the user

If there is no clear domain, ask the user which one they are interested in. If the user gives no hints, execute `list_domains(domain_type='technical')` to show all available technical domains (present as selectable options).

If the user indicates they just created a collection and the domain does not appear, retry with `refresh=true` (cache bypass) before concluding it does not exist.

### 4.2 Explore Tables

`list_domain_tables(domain)` to list all tables in the domain. Tables with descriptions already have generated technical terms.

### 4.3 Table Details

For the tables of interest:
1. `get_tables_details(domain, table_names)` to obtain business rules and context
2. `get_table_columns_details(domain, table)` for columns, types, and descriptions

Launch 4.3 in parallel when dealing with independent tables.

### 4.4 Existing Knowledge

- `list_technical_domain_concepts(domain)` -> existing business views with mapping and semantic term status
- `search_ontologies(text)` or `list_ontologies` + `get_ontology_info` -> existing ontologies and their structure. Prefer `search_ontologies` if searching for a specific ontology
- `search_domain_knowledge(question, domain)` -> search terminology and definitions

## 5. Exploring Published Semantic Layers

When a generated semantic layer is approved in the Stratio Governance UI, it is published as a new business domain with the prefix `semantic_` (e.g., `semantic_mi_dominio`).

- `search_domains(text, domain_type='business')` -> **prefer**: search published semantic domains by name or description
- `list_domains(domain_type='business')` -> list all published semantic domains (fallback if search yields no results). If a recently published domain does not appear, retry with `refresh=true`
- `list_domain_tables(domain)` -> tables of the published semantic domain
- `search_domain_knowledge(question, domain)` -> search knowledge in technical or semantic domain

Useful for: ontology planning (see what has been done before), verifying the final result, helping the user understand the current state.

## 6. State Detection (Idempotency)

Before any operation, verify it does not already exist:

| Artifact | How to detect | If it already exists |
|----------|--------------|---------------------|
| Data collection | `list_domains(domain_type='technical')` or `search_domains(name, domain_type='technical')` -> verify if the domain already exists. If just created and not appearing, use `refresh=true` | If it exists, inform. Options: use existing / create new with a different name |
| Technical terms | `list_domain_tables(domain)` -> tables with descriptions | Inform. Options: skip / regenerate (destructive) / cancel |
| Domain description | `list_domains(domain_type='technical')` -> whether the domain has a description | Inform. Options: skip / regenerate (destructive) / cancel |
| Ontology | `search_ontologies(name)` or `list_ontologies` + `get_ontology_info` | Options: extend (`update_ontology`) / delete classes (`delete_ontology_classes`) / create new |
| Business views | `list_technical_domain_concepts(domain)` | Inform of existing views. Options: skip / delete specific ones (`delete_business_views`) / regenerate (`create_business_views(regenerate=true)`) |
| View publishing | `list_technical_domain_concepts(domain)` -> status of each view | If already Pending Publish or Published, inform. Only Draft views can be published |
| SQL Mappings | `list_technical_domain_concepts(domain)` -> mapping status per view | `create_sql_mappings` overwrites existing mappings |
| Semantic terms | `list_technical_domain_concepts(domain)` -> term status per view | Inform. Options: skip / regenerate (destructive) / cancel |

> When any `search_*` tool above is unavailable (not empty, but failing), substitute per §10 and continue.

## 7. Error Handling and Recovery

- Analyze the error -> try to diagnose the cause
- If the agent can resolve it -> retry with improved `user_instructions` (reformulate, add specific context)
- If it cannot -> ask the user what additional context to provide -> pass it as `user_instructions` in the retry
- Retry ONLY the failed entity (specific table, class, or view), not the entire batch
- Maximum 2 retries per entity. If it persists -> document in the summary and continue with the rest

## 8. Parallel Execution

- **Read tools** (`list_*`, `get_*`, `search_*`): Launch in parallel whenever they are independent
- **Creation**: Sequential within the same phase
- **Between phases**: Strict mandatory sequence: technical terms -> ontology -> business views -> SQL mappings -> (optional publishing) -> semantic terms. Each phase depends on the artifacts from the previous one. Publishing can be done after completing mappings or at any later point

## 9. Long-Running Task Polling

Any MCP tool may take longer than expected to complete. When this happens, instead of the normal response, the tool returns a response containing only a `task_id` field. This is not an error — the operation continues running in the background on the server and the result can be retrieved later.

**Protocol — follow strictly when a response contains a `task_id`:**
1. Wait **5 seconds**
2. Call `get_mcp_task_result(task_id=<the received task_id>)` — **use the same server** where the original tool was called (`gov` server tools → `gov` server's `get_mcp_task_result`, `sql` server tools → `sql` server's `get_mcp_task_result`)
3. Inspect the `status` field in the response:
   - `"pending"` — the task is still running. Wait **10 seconds** and call `get_mcp_task_result` again. Repeat until the status changes
   - `"done"` — the `result` field contains the original tool response. Parse and use it as if the tool had returned it directly
   - `"error"` — the task failed. Read the `error` field for details. Apply the error handling strategy from section 7 or inform the user
   - `"not_found"` — the task_id expired or is unknown. Retry the original tool call from scratch

This applies to ALL MCP tools on both servers. Always check the response for a `task_id` field before processing the result normally.

## 10. OpenSearch Availability Fallback

`search_domains`, `search_ontologies` and `search_data_dictionary` consult OpenSearch internally. OpenSearch may not be available in every environment. This section defines the fallback when any of these tools is unavailable — distinct from the *empty result* fallback already described in §4.1 and §5.

### 10.1 Case detection

| Situation | Indicator | Fallback path |
|-----------|-----------|---------------|
| Empty result (already documented) | Tool returns a well-formed response with zero matches | §4.1 / §5 — call the corresponding `list_*` and ask the user |
| Unavailability (new) | Error response mentioning OpenSearch / index / connection / timeout, **or** two successive retries per §7 still fail (not a `task_id` pending per §9) | §10.2 |

### 10.2 Deterministic fallback

| OpenSearch tool | Deterministic alternative | Coverage |
|-----------------|---------------------------|----------|
| `search_domains(search_text, domain_type?)` | `list_domains(domain_type?)` + local substring filter over `name` and `description` | Complete |
| `search_ontologies(search_text)` | `list_ontologies()` + local substring filter over `name` and `description` | Complete |
| `search_data_dictionary(search_text, search_type?)` | With a domain hint: `list_domain_tables(domain)` + `get_tables_details(domain, tables)`. Without a domain hint: `list_domains(domain_type='technical')` → ask the user to pick one → continue | Partial — no cross-domain free-text search without OpenSearch |

### 10.3 Procedure

1. On first detected unavailability in the session, announce the degradation to the user once — per tool, not per call.
2. Invoke the deterministic alternative.
3. Continue the workflow (non-blocking). The §6 state-detection checks still apply: if `search_ontologies(name)` is used for idempotency, substitute with `list_ontologies` + local filter. The §7 retry budget is consumed before declaring unavailability.
4. Stop only if the alternative cannot cover the user's need — typically `search_data_dictionary` without a domain hint when the user cannot narrow the scope. In that case, inform the user and halt this sub-task.
5. Note the degradation in the summary at the end of the phase.
