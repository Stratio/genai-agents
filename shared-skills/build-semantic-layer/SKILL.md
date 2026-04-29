---
name: build-semantic-layer
description: "Build the full semantic layer of a technical domain end-to-end in Stratio Governance, orchestrating the five phases of the pipeline (technical terms → ontology → business views → SQL mappings → semantic terms), with optional view publishing between mappings and semantic terms. Requires an existing data collection — use create-data-collection first if it does not exist. Use when the user wants to build, complete, regenerate or audit the full semantic layer of a domain, rather than invoking an individual phase skill."
argument-hint: "[technical domain (optional)]"
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

### 3. Glossary instruction enrichment (pre-load for the whole pipeline)

Apply the Glossary Instruction Enrichment Workflow described in `skills-guides/stratio-semantic-layer-tools.md` §11 **once**, covering the four phases of the pipeline that accept `user_instructions`: technical terms, ontology, SQL mappings, and semantic terms.

When asking the user the four-option question (§11.2), scope it to "for the phases of this pipeline" and treat the answer as the policy for all of them; offer a per-phase override only if the user explicitly asks. Combine the glossary-derived instructions with any reference files the user wants to bring (option 3) and any free-text business rules or definitions they layer on top.

The output is **per-phase enriched text** that this skill keeps in the planning context for the rest of the run. Each phase invocation in step 5 reuses the slice for its phase as `user_instructions` without asking the four-option question again. Phases that the user later decides to skip in step 4 simply do not consume their slice — that is fine.

If the user picked option 4 (skip), no `user_instructions` are produced for any phase and the pipeline runs without enrichment.

### 4. Execution plan

Based on the diagnosis, list the phases that need work:
- Indicate which phases are complete (offer to skip or force regeneration)
- Indicate which phases are pending or partial
- Warn about dependencies between phases (e.g., "Views require an ontology")

Request global plan approval before executing.

### 5. Sequential execution

Execute each phase in strict order, calling the tools directly:

**Phase 1 — Technical terms** (if needed):
- `create_technical_terms(domain, table_names?, user_instructions?)` passing the technical-terms slice of the pre-loaded enrichment as `user_instructions` (omit the parameter if the user chose to skip enrichment in step 3)
- Present the tool summary to the user

**Phase 2 — Ontology** (if needed):
- Interactive planning: ask the user about essential classes and naming conventions
- The ontology slice of the pre-loaded enrichment already covers reference files, glossary instructions and free-text rules — feed it into the planning context. Only re-prompt if the user explicitly wants to add something new for this phase
- Explore domain: `list_domain_tables` + `get_tables_details` + `get_table_columns_details`
- Propose ontology plan in Markdown → review with user → iterate (max 3)
- `create_ontology(domain, name, ontology_plan)` or `update_ontology(domain, name, update_plan)`
- Verify: `get_ontology_info(name)` — present structure and offer: "If you want to delete any class before continuing, I can do it (classes with Published views cannot be deleted)." If the user requests deletion → `delete_ontology_classes(ontology_name, class_names)` → report deleted/skipped → verify again

**Phase 3 — Business views** (if needed):
- `create_business_views(domain, ontology, class_names?)` with the ontology from the previous step
- Present the tool summary to the user
- Offer: "If any view does not look right, I can delete it before continuing with mappings (Published views cannot be deleted)." If the user requests deletion → `delete_business_views(domain, view_names)` → report deleted/skipped

**Phase 4 — SQL Mappings** (if needed; covers new views from Phase 3 and existing views without mapping):
- `create_sql_mappings(domain, view_names?, user_instructions?)` passing the mapping slice of the pre-loaded enrichment as `user_instructions` (omit if skipped in step 3)
- Present the tool summary to the user
- The response includes `processed_views`: each entry carries `sql_mapping` — the freshly generated mapping SQL. **Keep this list in the orchestration context**; the optional pre-publication validation block below uses it directly (no need to re-fetch with `list_technical_domain_concepts`)

**Optional pre-publication validation (mappings)**:
- Before asking about publication, offer the user a sample-data check on the freshly created mappings: "Do you want me to run the mapping SQL (LIMIT 5) of each view and show you the results before deciding on publication?"
- Use the `processed_views` list returned by Phase 4's `create_sql_mappings` call (each entry carries the freshly generated SQL in `sql_mapping`). Use that SQL verbatim, wrapping it as `SELECT * FROM (<sql_mapping>) AS m LIMIT 5` so the original projection is preserved. No need to call `list_technical_domain_concepts` again here.
- If the user accepts, list the candidate views and **cap by default at 5 views**. If `processed_views` has more, ask the user which subset to validate.
- For each selected view: run `execute_sql` with the wrapped query. Launch all selected views **in parallel** in the same response.
- Render results as Markdown tables following `skills-guides/stratio-data-tools.md` §3.5 (default cap of 10 rows in chat).
- **No improvisation**: if `sql_mapping` comes back empty for a view inside `processed_views` (gov backend not yet exposing the field, or mapping failed to persist), do NOT improvise a SELECT over source tables. Tell the user: "I cannot validate this mapping's SQL from here because the backend is not exposing it. You can validate it from the Governance UI under the view." Skip that view and continue with the others.
- If `execute_sql` is not available in this agent, do not fall back to a natural-language `query_data` over source tables (it would not validate the mapping). Inform the user and point to the Governance UI.

**Publication (optional, between Phase 4 and Phase 5)**:
- The business views and their mappings are complete. Ask the user: "Do you want to publish the views now (Pending Publish) or continue first with the semantic terms?"
- **If publishing**: Execute `publish_business_views(domain)` → present result: published views + failed (transition not allowed) + not found → continue with Phase 5
- **If not publishing**: Proceed directly to Phase 5. Remind in the final summary that the views remain in Draft

**Phase 5 — Semantic terms** (if needed):
- Verify that the views have mappings (prerequisite)
- `create_semantic_terms(domain, view_names?, user_instructions?)` passing the semantic-terms slice of the pre-loaded enrichment as `user_instructions` (omit if skipped in step 3)
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

### 7. Optional post-publication validation (semantic layer)

If the views were published during the pipeline (or were already published), offer a sanity check on the live semantic layer:

- "The semantic domain `semantic_[name]` is now available. Do you want me to run 1–3 business questions against it to confirm the views and terms respond as expected?"
- **Propagation latencies to handle**:
  - **After `publish_business_views`**: views typically become queryable within ~60 seconds.
  - **After `create_semantic_terms`** (Phase 5): semantic terms are typically queryable as part of the live layer after ~90 seconds — `query_data` may not yet resolve a question that relies on a freshly created semantic term.
  - **Pattern**: if the first `query_data` / `execute_sql` call fails because the domain or term is not yet visible, inform the user, wait the appropriate window (60s post-publish, 90s post-Phase-5), retry once. If still failing, propose continuing later. Tell the user explicitly which propagation window is being respected so they understand the wait.
- If the user accepts, ask them for 1–3 business questions OR propose them. **Pattern for proposed questions** (deterministic, not free-form): pick one ontology class with the highest number of mapped attributes and propose: (a) `count(*)` of the corresponding view, (b) top-5 grouping by a categorical attribute if any exists, (c) min/max/avg over a numeric attribute if any exists. List the proposals as numbered options before executing.
- Resolve each question with `query_data` (preferred — uses the governed semantic layer with NL). If the user wants to see / tweak the generated SQL before running, use `generate_sql` first and offer `execute_sql` afterwards.
- Render results following `skills-guides/stratio-data-tools.md` §3.5 (default cap 10 rows).
- If validation surfaces unexpected results (empty, type mismatches, semantic terms not found), report it and suggest next steps: `/create-semantic-terms` to refine, or `/create-sql-mappings` to fix the SQL.
- If the agent does not have data tools (`query_data`, `execute_sql`, `generate_sql`), point the user to the Governance UI / data analytics agent and skip.
