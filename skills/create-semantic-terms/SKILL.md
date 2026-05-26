---
name: create-semantic-terms
description: "Generate or regenerate semantic terms for the business views of a domain in Stratio Governance. Use when the user wants to refresh the semantic terms of a domain's views after ontology or view changes, or bulk-populate them for a new domain. Accepts the technical domain name (canonical) or the semantic counterpart on input. For business terms in the dictionary, prefer manage-business-terms; for creating the views themselves, prefer create-business-views."
argument-hint: "[domain (optional)]"
---

# Skill: Create Semantic Terms

Generates or regenerates business semantic terms in the Stratio Governance glossary for the business views of a domain. Phase 5 of the semantic layer pipeline.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains. `refresh=true` for cache bypass |
| `list_technical_domain_concepts(domain)` | gov | List views with governance state, semantic terms and mappings |
| `create_semantic_terms(domain, view_names?, user_instructions?, regenerate?)` | gov | Create semantic terms. `domain` accepts the technical name (canonical, recommended) or the semantic counterpart — both work. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |

**Key rules**: `domain_name` immutable. Mandatory confirmation for `regenerate=true`. Build `user_instructions` through the Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11) before invoking. Pre-requisite: views must have SQL mapping before generating semantic terms.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, normalize and discover the canonical technical name:

- If it starts with the `semantic_` prefix → strip the prefix client-side. The tool accepts both forms but the canonical discovery target is the technical domain. Mention to the user that you are using the technical equivalent — both forms are accepted.
- Search with `search_domains($ARGUMENTS, domain_type='technical')`. If it does not match, retry with `refresh=true` in case it is a recently created collection. If it now matches, continue.

If it does not match or there is no argument, list with `list_domains(domain_type='technical')` and ask the user following the user question convention.

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

### 5. Glossary instruction enrichment

Before invoking the MCP tool, apply the Glossary Instruction Enrichment Workflow described in `guides/stratio-semantic-layer-tools.md` §11, scoped to **semantic terms** (i.e., when calling `get_glossary_instructions`, request only the semantic terms phase). This is where the user can pull GenAI semantic term instructions from the data dictionary, supply an external file (business glossary, functional documentation, terminological style guide) as their source, layer free-text definitions on top, or skip enrichment entirely.

If the orchestrator already pre-loaded enriched instructions for this phase during the `build-semantic-layer` flow, reuse them — optionally ask whether the user wants to add anything specific to this phase on top of what was pre-loaded.

The enriched text becomes the `user_instructions` argument of the MCP call in the next step. If the user chose option 4 (skip), `user_instructions` is omitted.

### 6. Execution

Invoke `create_semantic_terms`. To regenerate: pass `regenerate=true` (DESTRUCTIVE). The tool returns a summary of what was processed — present to the user directly.

If there are errors, retry the failed view with improved `user_instructions` (max 2 retries). If it persists, document and continue.

### 7. Summary

Based on the tool's response:
- Terms created/regenerated
- Errors if any
- Suggested next steps:
  - "The semantic layer is ready for review. If the views are still in Draft state, you can send them to Pending Publish by requesting their publication directly. You can create business terms with `/manage-business-terms` to enrich the dictionary"
  - "If you need to fix, add or remove individual foreign key relations between views without regenerating the semantic terms, use `/refine-semantic-foreign-keys`"
