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

**Key rules**: `domain_name` immutable. Build `user_instructions` through the Glossary Instruction Enrichment Workflow (`skills-guides/stratio-semantic-layer-tools.md` §11) before invoking. `create_sql_mappings` overwrites existing mappings (not destructive at the view level, only replaces the SQL mapping).

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

### 4. Glossary instruction enrichment

Before invoking the MCP tool, apply the Glossary Instruction Enrichment Workflow described in `skills-guides/stratio-semantic-layer-tools.md` §11, scoped to **SQL mappings** (i.e., when calling `get_glossary_instructions`, request only the mapping phase). This is where the user can pull GenAI mapping instructions from the data dictionary, supply an external file (technical documentation, ER diagrams, integration specs, reference SQL scripts) as their source, layer free-text mapping rules on top, or skip enrichment entirely.

If the orchestrator already pre-loaded enriched instructions for this phase during the `build-semantic-layer` flow, reuse them — optionally ask whether the user wants to add anything specific to this phase on top of what was pre-loaded.

The enriched text becomes the `user_instructions` argument of the MCP call in the next step. If the user chose option 4 (skip), `user_instructions` is omitted.

### 5. Execution

Invoke `create_sql_mappings(domain, view_names?, user_instructions?)`. The tool returns a summary of what was processed — present to the user directly.

If there are errors, retry the failed view with improved `user_instructions` (max 2 retries). If it persists, document and continue.

### 6. Summary

Based on the tool's response:
- Mappings created/updated
- Errors if any

### 6.5 Optional pre-publication validation (sample data)

After creating or updating the mappings and before offering publication, offer the user a sample-data check:

- "Do you want me to run the mapping SQL (LIMIT 5) of each processed view and show you the results before deciding on publication?"
- The response of `create_sql_mappings` from §5 already includes `processed_views`: a list of `BusinessViewSummary` entries for the views just processed, each with the freshly generated SQL in `sql_mapping`. Use that SQL verbatim, wrapping it as `SELECT * FROM (<sql_mapping>) AS m LIMIT 5` so the original projection is preserved. **No need** to call `list_technical_domain_concepts` again here.
- Restrict validation to the views in `processed_views` (those actually processed in §5). **Cap by default at 5 views**; if §5 processed more, ask the user which subset to validate.
- For each selected view: run `execute_sql` with the wrapped query. Launch all selected views **in parallel** in the same response.
- Render results as Markdown tables following `skills-guides/stratio-data-tools.md` §4 (default cap of 10 rows in chat).
- **No improvisation**: if `sql_mapping` comes back empty for a view inside `processed_views` (gov backend not yet exposing the field, or the just-created mapping failed to persist), do NOT improvise a SELECT over source tables. Tell the user: "I cannot validate this mapping's SQL from here because the backend is not exposing it. You can validate it from the Governance UI under the view." Skip that view and continue with the others.
- If `execute_sql` is not available in this agent, do not fall back to a natural-language `query_data` over source tables (it would not validate the mapping). Inform the user and point to the Governance UI.
- This step is non-blocking: regardless of the validation outcome, continue to §7 Publication.

### 7. Publication (optional)

After creating or updating mappings, offer publication of the processed views that are in Draft state (verify with `list_technical_domain_concepts`; views already in Pending Publish or Published do not apply):
- "The views with updated mappings are ready to publish. Do you want to publish them? This will change their state to Pending Publish, ready to be published to the data virtualizer."
- If the user accepts → execute `publish_business_views(domain, view_names)` with the processed Draft views → present result: published views + failed (transition not allowed) + not found
- If the user declines → continue with the suggested next step
- Not blocking: the user decides

Suggested next step: "You can generate the semantic terms with `/create-semantic-terms`. If you did not publish now, you can do so later"
