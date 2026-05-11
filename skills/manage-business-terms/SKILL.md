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

## Domain selection — STRONG default: semantic

> *Scope: this domain-selection rule is specific to `create_business_term` and the workflow of this skill. It does NOT generalize to other governance tools — `create_technical_terms`, `create_ontology`, `create_business_views`, `create_sql_mappings`, `create_semantic_terms` and `publish_business_views` continue to use the technical domain.*

`create_business_term` is a **post-publication** operation: it runs after the semantic layer is built and published, not as part of the construction pipeline. **Default: prefer the semantic / business domain (`semantic_<x>`)**. Business terms describe business concepts; they belong under "Semantic Knowledge". If `semantic_<x>` exists, use it as `domain` — do not ask the user. The technical domain is the **exception**, not the default.

**When to choose the technical domain** (legitimate, supported edge cases — proceed without push back):

- The term describes a *physical-model artifact* with no semantic-layer representation: a specific column, a data type, a load rule, an operational constraint that only makes sense to a data engineer.
- The technical domain has **no published semantic layer** (`semantic_<x>` does not exist) and the user wants to document the term anyway.
- The user **explicitly asks** to attach the term to the technical domain (e.g. "document this in the raw layer"). User intent overrides the default; briefly confirm in one line if `semantic_<x>` also exists.

**Prefix consistency**: every entry in `related_assets` must start with the **same** value as `domain` — the chain rejects mixed prefixes. If `domain="semantic_finance"`, all related assets must start with `semantic_finance.`.

**`domain_name` immutability**: the value passed to the tool must be **exactly** the one returned by `list_domains` / `search_domains` — never translate, paraphrase, or reformat it.

**Examples**:
- *Semantic (default)* — KPI "Customer Lifetime Value" on a published semantic layer: `domain="semantic_finance"`, `related_assets=["semantic_finance.card.clv"]`. No question to user.
- *Technical — no semantic layer published* — column `tx_id` in `raw_finance` with no `semantic_raw_finance`: `domain="raw_finance"`, `related_assets=["raw_finance.transactions.tx_id"]`. Inform the user before proceeding.
- *Technical — explicit user request* — user says "document this in the raw layer" even though `semantic_raw_finance` exists: `domain="raw_finance"`, `related_assets=["raw_finance.transactions.tx_id"]`. Confirm intent in one line.

## Workflow

### 1. Determine domain

Search with `search_domains($ARGUMENTS)` (no `domain_type` filter — surfaces both technical and semantic). If no match, retry with `refresh=true` in case the domain was recently created or published. If still no match (or `$ARGUMENTS` is empty), call `list_domains()` and ask the user following the user question convention.

Apply the Domain selection rule above: **if `semantic_<x>` exists, set `domain="semantic_<x>"`** (default — do not ask). If only `<x>` exists and the term is a business concept, inform the user the domain has not been published as a semantic layer yet and ask whether to proceed under the technical domain or abort. Whatever `domain` you choose, all `related_assets` must use the same prefix.

### 2. Guided planning

For each business term, plan these fields:

**Term name**: Propose based on context or ask the user.

**Description**: Markdown text with the complete definition of the term. Propose a description based on the domain context, or ask the user to provide it.

**Asset type**: Execute `list_business_asset_types()` and present available types to the user for selection.

**Related assets** — Explain the hierarchy to the user:
- Format: `collection.table.column`, `collection.table`, or `collection`. The `collection.` prefix must match the `domain` chosen above (in practice, with the `semantic_` prefix unless the technical-domain exception applies).
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
