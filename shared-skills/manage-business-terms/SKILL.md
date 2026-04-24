---
name: manage-business-terms
description: "Create business terms in the Stratio Governance dictionary, single or batch, with relationships to data assets, via guided planning (name, description, type, relationships). Use when the user wants to add, link or document business terms (KPIs, concepts, acronyms) in the dictionary, or connect an existing term to specific tables and columns. For bulk semantic terms of views, prefer create-semantic-terms."
argument-hint: "[domain (optional)]"
---

# Skill: Manage Business Terms

Creates Business Terms in the Stratio Governance dictionary with relationships to data assets. Includes guided planning to define name, description, type and related assets.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type?, refresh?)` | sql | **Prefer**. Search domains by free text (accepts technical and semantic). Results by relevance |
| `list_domains(domain_type?, refresh?)` | sql | List available domains (accepts technical and semantic). `refresh=true` for cache bypass |
| `list_domain_tables(domain)` | sql | Discover domain tables for relationships |
| `get_table_columns_details(domain, table)` | sql | Discover columns for column-level relationships |
| `list_business_asset_types()` | gov | Available asset types for business terms |
| `create_business_term(domain, name, description, type, related_assets)` | gov | Create business term in the dictionary |

**Key rules**: `domain_name` immutable. Business terms accept both technical and semantic domains (`semantic_*`). Related assets follow a granularity hierarchy.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS)` (accepts both technical and semantic domains). If it does not match, retry with `search_domains($ARGUMENTS, refresh=true)` in case it is a recently created or published domain. If it now matches, continue. If it does not match or there is no argument, list domains with `list_domains()` and ask the user following the user question convention.

### 2. Guided planning

For each business term, plan these fields:

**Term name**: Propose based on context or ask the user.

**Description**: Markdown text with the complete definition of the term. Propose a description based on the domain context, or ask the user to provide it.

**Asset type**: Execute `list_business_asset_types()` and present available types to the user for selection.

**Related assets** — Explain the hierarchy to the user:
- Format: `collection.table.column`, `collection.table`, or `collection`
- **Granularity rule**:
  - If the term applies to **specific columns** → relate to the columns (do not add table or collection redundantly)
  - If it applies to **specific tables** → relate to the tables (do not add collection)
  - If it applies to **more than 2 tables** in the same domain → relate to the collection directly
- The user decides the final granularity — present the recommendation but respect their criteria

To discover available assets:
- `list_domain_tables(domain)` → domain tables
- `get_table_columns_details(domain, table)` → columns of specific tables

**Grouping**: The user may want to group several concepts into a single business term or create separate terms. Ask if applicable — this is the user's decision.

### 3. Approval

Show the complete term before creating:
```
## Business Term: [name]
- **Type**: [selected type]
- **Description**: [Markdown description]
- **Related assets**:
  - collection.table.column1
  - collection.table.column2
```

Allow the user to edit any field before confirming.

### 4. Execution

Invoke `create_business_term(domain, name, description, type, related_assets)` with the approved data.

If there is an error, analyze the cause and offer to retry with adjustments (max 2 retries per term).

### 5. Batch mode

If the user wants to create multiple business terms:
1. Plan all terms in a list
2. Present complete list for approval
3. Create sequentially
4. Present final summary:
   - Terms created successfully
   - Errors if any
   - Note: "Business terms are created in Draft state. They will be reviewed in the Governance UI"
