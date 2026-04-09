---
name: create-semantic-terms
description: "Generate or regenerate business semantic terms in the Stratio Governance glossary for the business views of a domain."
argument-hint: "[technical domain (optional)]"
---

# Skill: Create Semantic Terms

Generates or regenerates business semantic terms in the Stratio Governance glossary for the business views of a domain. Phase 5 of the semantic layer pipeline.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains. `refresh=true` for cache bypass |
| `list_technical_domain_concepts(domain)` | gov | List views with governance state, semantic terms and mappings |
| `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | gov | Create semantic terms. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |

**Key rules**: `domain_name` immutable. Mandatory confirmation for `regenerate=true`. Offer `user_instructions` before invoking. Pre-requisite: views must have SQL mapping before generating semantic terms.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS, domain_type='technical')`. If it does not match, retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` in case it is a recently created collection. If it now matches, continue. If it does not match or there is no argument, list with `list_domains(domain_type='technical')` and ask the user following the user question convention.

### 2. Evaluate state

Execute `list_technical_domain_concepts(domain)` to obtain the list of views with their governance state, mappings and semantic terms.

Present summary:
```
## Semantic Terms — [domain_name]
| View | State | Mapping | Semantic terms |
|------|-------|---------|----------------|
| View1 | Draft | ✓ | ✓ |
| View2 | Pending Publish | ✓ | ✗ |
| View3 | Draft | ✗ | — |
```

### 3. Verify pre-requisite

Views need SQL mapping to generate semantic terms. If there are views without mapping:
- Warn the user: "The following views do not have SQL mapping: [list]. Semantic terms cannot be generated for them."
- Suggest: "Use `/create-sql-mappings` or `/create-business-views` to generate the mappings first"
- Continue only with views that have mapping

### 4. Scope selection

Ask the user with options (only views with mapping):
1. **Create for views without terms** — idempotent
2. **Specific views** — multiple selection
3. **Regenerate all** — DESTRUCTIVE: deletes existing terms and recreates. Requires explicit confirmation
4. **Regenerate specific views** — DESTRUCTIVE for the selected ones. Requires confirmation

### 5. user_instructions

Offer the user the opportunity to provide additional context:
- **Local files**: If the user has business glossaries, functional documentation or terminological style guides → **read them** and extract relevant definitions to include as context
- **Domain definitions**: Business meaning of key concepts, relationships between entities, rules that the AI should reflect in the terms
- Examples: "The concept 'actor' in this domain refers to movie actors, not system actors", "The `film` views should reflect that rental_rate is the rental price per day"

Do not suggest options that the tool controls internally (language, audience, format). If the user does not provide instructions, continue without the parameter. Not blocking.

### 6. Execution

Invoke `create_semantic_terms`. To regenerate: pass `regenerate=true` (DESTRUCTIVE). The tool returns a summary of what was processed — present to the user directly.

If there are errors, retry the failed view with improved `user_instructions` (max 2 retries). If it persists, document and continue.

### 7. Summary

Based on the tool's response:
- Terms created/regenerated
- Errors if any
- Suggested next step: "The semantic layer is ready for review. If the views are still in Draft state, you can send them to Pending Publish by requesting their publication directly. You can create business terms with `/manage-business-terms` to enrich the dictionary"
