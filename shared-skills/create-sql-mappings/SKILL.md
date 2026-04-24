---
name: create-sql-mappings
description: "Create or update the SQL mappings of existing business views in Stratio Governance, without recreating the views, and optionally publish them afterwards. Use when the user wants to correct a mapping, fix the SQL of a view, add missing columns, or recover from a partial mapping creation. For end-to-end regeneration of views + mappings, prefer create-business-views."
argument-hint: "[technical domain (optional)]"
---

# Skill: Create SQL Mappings

Creates or updates SQL mappings for existing business views in Stratio Governance. Phase 4 of the semantic layer pipeline. Useful for correcting or improving mappings without the need to recreate views.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains. `refresh=true` for cache bypass |
| `list_technical_domain_concepts(domain)` | gov | List views with governance state and mapping |
| `create_sql_mappings(domain, view_names?, user_instructions?)` | gov | Create or update SQL mappings for existing views |
| `publish_business_views(domain, view_names?)` | gov | Publish views (Draft → Pending Publish). Without `view_names`, publishes all |

**Key rules**: `domain_name` immutable. Offer `user_instructions` before invoking. `create_sql_mappings` overwrites existing mappings (not destructive at the view level, only replaces the SQL mapping).

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS, domain_type='technical')`. If it does not match, retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` in case it is a recently created collection. If it now matches, continue. If it does not match or there is no argument, list with `list_domains(domain_type='technical')` and ask the user following the user question convention.

### 2. Evaluate state

Execute `list_technical_domain_concepts(domain)` to obtain the list of views with their governance state and mapping.

Present summary:
```
## SQL Mappings — [domain_name]
| View | State | Mapping |
|------|-------|---------|
| View1 | Draft | ✓ |
| View2 | Draft | ✗ |
| View3 | Pending Publish | ✓ |
```

### 3. View selection

Ask the user with options:
1. **All views without mapping** — safe, only creates where missing
2. **Specific views** — multiple selection (can include views with existing mapping to update it)
3. **Update existing mappings** — overwrites the SQL mapping, does not delete the view or its semantic terms

### 4. user_instructions

Offer the user the opportunity to provide additional context:
- **Local files**: If the user has technical documentation, ER diagrams, integration specifications or reference SQL scripts → **read them** and extract relevant information to include as context
- **Mapping rules**: Relationships between tables, preferred JOIN types, exclusion filters, data transformations
- Examples: "Use LEFT JOIN to preserve records without matches", "Main table for JOINs: accounts", "Exclude records with status='DELETED'", "Use COALESCE for nullable fields", "Dates in epoch milliseconds format"

Do not suggest options that the tool controls internally (language, output format). If the user does not provide instructions, continue without the parameter. Not blocking.

### 5. Execution

Invoke `create_sql_mappings(domain, view_names?, user_instructions?)`. The tool returns a summary of what was processed — present to the user directly.

If there are errors, retry the failed view with improved `user_instructions` (max 2 retries). If it persists, document and continue.

### 6. Summary

Based on the tool's response:
- Mappings created/updated
- Errors if any

### 7. Publication (optional)

After creating or updating mappings, offer publication of the processed views that are in Draft state (verify with `list_technical_domain_concepts`; views already in Pending Publish or Published do not apply):
- "The views with updated mappings are ready to publish. Do you want to publish them? This will change their state to Pending Publish, ready to be published to the data virtualizer."
- If the user accepts → execute `publish_business_views(domain, view_names)` with the processed Draft views → present result: published views + failed (transition not allowed) + not found
- If the user declines → continue with the suggested next step
- Not blocking: the user decides

Suggested next step: "You can generate the semantic terms with `/create-semantic-terms`. If you did not publish now, you can do so later"
