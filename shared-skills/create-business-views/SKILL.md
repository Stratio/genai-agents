---
name: create-business-views
description: "Create, regenerate, delete or publish business views and SQL mappings in Stratio Governance from an ontology."
argument-hint: "[technical domain (optional)]"
---

# Skill: Create Business Views

Creates, regenerates or deletes business views and SQL mappings in Stratio Governance from an existing ontology. Offers to publish views after creating or regenerating them. Phase 3 of the semantic layer pipeline.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains. `refresh=true` for cache bypass |
| `search_ontologies(search_text)` | gov | Search ontologies by free text. Results by relevance |
| `list_ontologies()` | gov | List all existing ontologies |
| `get_ontology_info(name)` | gov | Ontology classes |
| `list_technical_domain_concepts(domain)` | gov | Existing views with governance state, mappings and semantic terms |
| `create_business_views(domain, ontology, class_names?, regenerate?)` | gov | Create views + mappings. Skips existing. With `regenerate=true`: DESTRUCTIVE, deletes and recreates |
| `delete_business_views(domain, view_names)` | gov | DESTRUCTIVE: delete specific views without recreating (protected by Published) |
| `publish_business_views(domain, view_names?)` | gov | Publish views (Draft → Pending Publish). Without `view_names`, publishes all |

**Key rules**: `domain_name` immutable. Mandatory confirmation for `regenerate=true` and `delete`. `user_instructions` pending implementation by the development team — the agent already accounts for it for when it becomes available.

## Workflow

### 1. Determine domain and ontology

**Domain**: If `$ARGUMENTS` contains a name, search with `search_domains($ARGUMENTS, domain_type='technical')`. If it does not match, retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` in case it is a recently created collection. If it now matches, continue. If it does not match or there is no argument, list with `list_domains(domain_type='technical')` and ask the user following the user question convention.

**Ontology**: If the user or the context mentions a specific ontology, search with `search_ontologies(hint)`. If not, execute `list_ontologies()` to see all. If there are several, ask the user which one to use. If only one is relevant for the domain, confirm.

### 2. Evaluate state

Execute in parallel:
- `get_ontology_info(ontology)` → classes available in the ontology
- `list_technical_domain_concepts(domain)` → already created views with their state

Present summary:
```
## State — [domain_name] + [ontology]
| Class | View | State | Mapping | Semantic terms |
|-------|------|-------|---------|----------------|
| Class1 | ✓ | Draft | ✓ | ✗ |
| Class2 | ✗ | — | — | — |
| Class3 | ✓ | Pending Publish | ✗ | ✗ |
```

### 3. Operation selection

Ask the user with options:
1. **Create views for classes without a view** — idempotent: `create_business_views` skips existing ones
2. **Create for specific classes** — multiple selection from classes without a view
3. **Regenerate all** — DESTRUCTIVE: deletes and recreates views + mappings. Requires explicit confirmation with a warning that associated semantic terms are also lost
4. **Regenerate specific classes** — DESTRUCTIVE for the selected ones. Requires confirmation
5. **Delete specific views** — DESTRUCTIVE: removes selected views without recreating them (different from regenerate). Multiple selection. Views with Published state are automatically skipped. Requires confirmation

### 4. Execution

Invoke `create_business_views` (with `regenerate=true` for options 3-4) or `delete_business_views` (option 5). For `delete`: confirm with the user listing the views to delete. The tool returns `deleted` (deleted) and `skipped_published` (skipped due to Published) — present both lists to the user.

If there are errors, retry the failed entity (max 2 retries). If it persists, document and continue.

### 5. Summary

Based on the tool's response:
- Views created/regenerated/deleted
- Mappings generated
- Errors if any

Proactively offer: "If any view does not look right, I can delete it (Published views cannot be deleted)." Not blocking — the user decides.

### 6. Publication (optional)

If views were created or regenerated (does not apply to deletion), offer publication:
- "Do you want to publish the created views? This will change their state to Pending Publish, ready to be published to the data virtualizer."
- If the user accepts → execute `publish_business_views(domain, view_names)` with the created views → present result: published views + failed (transition not allowed) + not found
- If the user declines → continue with the suggested next step
- Not blocking: the user decides

Suggested next step: "You can verify or update the SQL mappings with `/create-sql-mappings`, or generate semantic terms with `/create-semantic-terms`. If you did not publish now, you can do so later"
