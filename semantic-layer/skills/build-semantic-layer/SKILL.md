---
name: build-semantic-layer
description: Complete pipeline to build the semantic layer of a technical domain.
  Orchestrates the 5 phases in sequence with state diagnosis, optional publication,
  and progress tracking.
argument-hint: [technical domain (optional)]
---

# Skill: Build Semantic Layer (Complete Pipeline)

Orchestrates the 5 phases of the semantic layer construction pipeline for an existing technical domain. Diagnoses the current state, proposes an execution plan, executes each phase in sequence, and offers to publish the views after completing the mappings.

**Important**: This skill calls the MCP tools directly (inline). It does NOT delegate to other skills — skills cannot programmatically invoke other skills. The shared skills for each phase exist for independent use by the user; the pipeline replicates them in an integrated manner.

For a complete tools and rules reference, see `skills-guides/stratio-semantic-layer-tools.md`.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS, domain_type='technical')`.

- If it matches a result → use it and continue with step 2.
- If it does NOT match → immediately retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` to force a cache bypass (the collection may have been recently created). If it now appears → use it and continue with step 2. If it still does not appear → the collection may still be propagating internally. Inform the user: "The domain does not appear yet. It may take 1-2 minutes to propagate. Retrying in 60 seconds...". Wait 60 seconds and execute `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` again. If it now appears → continue. If not → inform the user and ask them to retry later.
- If there is no argument → execute `list_domains(domain_type='technical')` and present the list of existing domains to the user for selection, following the user question convention.

If the user chooses a domain → continue with step 2.

### 2. Full diagnosis

Execute in parallel:
- `list_domains(domain_type='technical')` → verify if the domain has a general description
- `list_domain_tables(domain)` → tables with/without descriptions (= technical terms)
- `list_ontologies` → existing ontologies (or `search_ontologies(text)` if searching for a specific one)
- `list_technical_domain_concepts(domain)` → views, mappings, semantic terms

For each relevant ontology: `get_ontology_info(name)`.

Present **status dashboard**:
```
## Semantic Layer Status — [domain_name]
| Phase | Status | Detail |
|-------|--------|--------|
| Domain description | ✓ / ✗ | Has/does not have description |
| Technical terms | Partial (15/20) | 5 tables without description |
| Ontology | ✓ Complete | "my_ontology" — 8 classes |
| Business views | Partial (6/8) | 2 classes without view |
| SQL Mappings | Partial (5/6) | 1 view without mapping |
| Publication | ✗ Draft | 0/6 views published |
| Semantic terms | ✗ Pending | 0/6 views |
```

### 3. General context

Ask the user for global context that applies to all phases:
- "Do you have reference files (documentation, glossaries, specifications) that I should read to better understand the domain? Are there business definitions, rules, or key concepts that you want reflected in the semantic layer? If not, reply 'Continue'."
- If the user provides file paths → **read them** and extract relevant information as global context
- The extracted context will be passed as `user_instructions` in each phase that supports it
- Only ask again in specific phases if the user needs different instructions

### 4. Execution plan

Based on the diagnosis, list the phases that need work:
- Indicate which phases are complete (offer to skip or force regeneration)
- Indicate which phases are pending or partial
- Warn about dependencies between phases (e.g., "Views require an ontology")

Request global plan approval before executing.

### 5. Sequential execution

Execute each phase in strict order, calling the tools directly:

**Phase 1 — Technical terms** (if needed):
- `create_technical_terms(domain, table_names?, user_instructions?)` with the global instructions
- Present the tool summary to the user

**Phase 2 — Ontology** (if needed):
- Interactive planning: ask the user about classes, reference files (ontologies .owl/.ttl, business documents, CSVs), naming conventions
- If the user provides paths to local files → **read them** to extract context and enrich the plan
- Explore domain: `list_domain_tables` + `get_tables_details` + `get_table_columns_details`
- Propose ontology plan in Markdown → review with user → iterate (max 3)
- `create_ontology(domain, name, ontology_plan)` or `update_ontology(domain, name, update_plan)`
- Verify: `get_ontology_info(name)` — present structure and offer: "If you want to delete any class before continuing, I can do it (classes with Published views cannot be deleted)." If the user requests deletion → `delete_ontology_classes(ontology_name, class_names)` → report deleted/skipped → verify again

**Phase 3 — Business views** (if needed):
- `create_business_views(domain, ontology, class_names?)` with the ontology from the previous step
- Present the tool summary to the user
- Offer: "If any view does not look right, I can delete it before continuing with mappings (Published views cannot be deleted)." If the user requests deletion → `delete_business_views(domain, view_names)` → report deleted/skipped

**Phase 4 — SQL Mappings** (if needed; covers new views from Phase 3 and existing views without mapping):
- `create_sql_mappings(domain, view_names?, user_instructions?)` with the global instructions
- Present the tool summary to the user

**Publication (optional, between Phase 4 and Phase 5)**:
- The business views and their mappings are complete. Ask the user: "Do you want to publish the views now (Pending Publish) or continue first with the semantic terms?"
- **If publishing**: Execute `publish_business_views(domain)` → present result: published views + failed (transition not allowed) + not found → continue with Phase 5
- **If not publishing**: Proceed directly to Phase 5. Remind in the final summary that the views remain in Draft

**Phase 5 — Semantic terms** (if needed):
- Verify that the views have mappings (prerequisite)
- `create_semantic_terms(domain, view_names?, user_instructions?)` with the global instructions
- Present the tool summary to the user

**After each phase**:
- Report updated progress (mini-dashboard)
- If it fails: offer options to the user:
  - **Retry** with improved `user_instructions`
  - **Skip** this phase (warn about dependencies: "If you skip the ontology, views cannot be created")
  - **Abort** the pipeline

### 6. Final summary

Present an updated dashboard with the final state:
```
## Semantic Layer Completed — [domain_name]
| Phase | Status | Actions taken |
|-------|--------|---------------|
| Technical terms | ✓ | 20 tables processed |
| Ontology | ✓ | "my_ontology" created — 8 classes |
| Business views | ✓ | 8 views created |
| SQL Mappings | ✓ | 8 mappings generated |
| Publication | ✓ / ✗ | Pending Publish / Draft |
| Semantic terms | ✓ | 8 views with terms |
```

Include:
- Actions taken per phase
- Errors encountered and how they were resolved
- Suggestions for next steps:
  - "You can create business terms with `/manage-business-terms` to enrich the dictionary"
  - If the views were published during the pipeline: "The views are in Pending Publish status, awaiting publication to the data virtualizer"
  - If the views were NOT published: "The views remain in Draft status. You can publish them by requesting it directly or from the Governance UI"
  - "Once published to the virtualizer, the semantic layer will be available as domain `semantic_[name]`"
