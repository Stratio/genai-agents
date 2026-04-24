---
name: create-technical-terms
description: "Create or regenerate technical terms — descriptions of tables and columns — in Stratio Governance for an entire technical domain, and seed the collection description when missing. Use when the user wants to document tables and columns, bulk-generate descriptions for a new domain, refresh them after schema changes, or recover missing technical terms."
argument-hint: "[technical domain (optional)]"
---

# Skill: Create Technical Terms

Creates technical descriptions for tables and columns of a domain in Stratio Governance. Phase 1 of the semantic layer pipeline.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains (includes description if exists). `refresh=true` for cache bypass |
| `list_domain_tables(domain)` | sql | List tables with their descriptions (indicates if they already have technical terms) |
| `create_technical_terms(domain, table_names?, user_instructions?, regenerate?)` | gov | Create technical terms. Skips existing. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |

**Key rules**: `domain_name` immutable (exact value from `list_domains` or `search_domains`). Mandatory confirmation for `regenerate=true`. Offer `user_instructions` before invoking.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS, domain_type='technical')`. If it matches a result, continue. If it does not match, retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` in case it is a recently created collection. If it now matches, continue. If it still does not match or there is no argument, list domains with `list_domains(domain_type='technical')` and ask the user following the user question convention.

### 2. Evaluate state

Execute `list_domain_tables(domain)` to evaluate the current state:
- Tables with description → already have generated technical terms
- Tables without description → pending generation
- If the domain has a description (visible in `list_domains(domain_type='technical')`) → the general description already exists

Present summary to the user:
```
## State — [domain_name]
- Total tables: N
- With technical terms: X
- Pending: Y
- Domain description: Yes/No
```

### 3. Scope selection

Ask the user with options:
1. **Create for all tables** — idempotent: `create_technical_terms` skips tables that already have a description
2. **Create for specific tables** — multiple selection from pending tables
3. **Regenerate all** — DESTRUCTIVE: deletes and recreates. Requires explicit confirmation
4. **Regenerate specific tables** — DESTRUCTIVE for the selected ones. Requires explicit confirmation

### 4. user_instructions

Before executing, offer the user the opportunity to provide additional context:
- **Local files**: If the user has documentation, glossaries, data dictionaries or specifications → **read them** and extract relevant definitions to include as context
- **Domain definitions**: Business concepts, specific column values, relationships between entities that the AI should know
- Examples: "The column `status` has values: A=active, I=inactive, S=suspended", "The `film_*` tables belong to the movie catalog module", "The field `last_update` is an audit timestamp, not a business one"

Do not suggest options that the tool controls internally (language, audience, format). If the user does not provide instructions, continue without the parameter. Not blocking.

### 5. Execution

Invoke `create_technical_terms`. To regenerate: pass `regenerate=true` (DESTRUCTIVE). The tool returns a summary of what was processed — present that summary to the user directly. Do not call additional tools post-creation to avoid filling up context.

**Note on domain description**: `create_technical_terms` automatically generates the domain/collection description if it does not have one. It is not necessary to call `create_collection_description` as a separate step.

### 6. Summary

Based on the tool's response, present:
- Tables processed
- Errors if any (retry failed entities with improved `user_instructions`, max 2 retries)
- Suggested next step: "You can create an ontology with `/create-ontology`"
