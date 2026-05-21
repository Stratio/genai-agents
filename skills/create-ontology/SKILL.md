---
name: create-ontology
description: "Create, extend or delete classes of an ontology in Stratio Governance, with interactive planning from reference files (.owl/.ttl, CSVs, business docs) before creation. Use when the user wants to model a domain ontology, add classes to an existing one, seed classes from reference documents, or remove obsolete classes. For generating the business views from the ontology, prefer create-business-views."
argument-hint: "[technical domain (optional)]"
---

# Skill: Create, Extend or Delete Ontology Classes

Creates, extends or deletes classes of an ontology in Stratio Governance through interactive planning with the user. Phase 2 of the semantic layer pipeline.

## MCP Tools Used

| Tool | Server | Purpose |
|------|--------|---------|
| `search_domains(search_text, domain_type='technical')` | sql | **Prefer**. Search technical domains by free text. Results by relevance |
| `list_domains(domain_type='technical', refresh?)` | sql | List all technical domains. `refresh=true` for cache bypass |
| `list_domain_tables(domain)` | sql | Get domain tables |
| `get_tables_details(domain, tables)` | sql | Table details: business rules, context |
| `get_table_columns_details(domain, table)` | sql | Table columns (for planning data properties) |
| `search_domain_knowledge(question, domain)` | sql | Search existing knowledge |
| `search_ontologies(search_text)` | gov | Search ontologies by free text. Results by relevance |
| `list_ontologies()` | gov | List all existing ontologies |
| `get_ontology_info(name)` | gov | Class structure, data properties and relationships |
| `create_ontology(domain, name, ontology_plan, best_effort?)` | gov | Create new ontology with Markdown plan. Optional `best_effort` (bool, default off): deliver the last attempted result with warnings if supervisors keep rejecting after all retries + plan rebuilds. See `guides/stratio-semantic-layer-tools.md` §2 and §7.2 |
| `update_ontology(domain, name, update_plan, best_effort?)` | gov | Add new classes to existing ontology. Optional `best_effort` (bool, default off): same delivery semantics as `create_ontology`. ADD-only — classes added in best-effort mode can only be removed with `delete_ontology_classes` |
| `delete_ontology(ontology_name)` | gov | DESTRUCTIVE: delete the entire ontology and all its classes (protected by Published). Use in the post-best-effort recovery flow (see workflow §4.b) or to clean up obsolete ontologies |
| `delete_ontology_classes(ontology_name, class_names)` | gov | DESTRUCTIVE: delete specific classes (protected by Published). Preferred when only a few classes — added in best-effort mode or otherwise — need to be removed while keeping the rest of the ontology intact |

**Key rules**: `domain_name` immutable. Ontologies are ADD+DELETE: `update_ontology` adds classes; `delete_ontology_classes` deletes specific classes; `delete_ontology` deletes the entire ontology (protected: classes with dependent Published views are skipped; published ontologies cannot be deleted). Existing classes cannot be modified. Naming: no spaces (→ underscores), no special characters. Build the planning context through the Glossary Instruction Enrichment Workflow (`guides/stratio-semantic-layer-tools.md` §11) before proposing the ontology plan. Best-effort delivery via the optional `best_effort` argument is **opt-in** and only affects how quality rejections during class/view generation are handled; it does **not** override pre-generation feasibility failures (plan deemed unachievable with the available tables, table/size caps exceeded, governance services unreachable) — those still fail the call.

## Workflow

### 1. Determine domain

If `$ARGUMENTS` contains a domain name, search with `search_domains($ARGUMENTS, domain_type='technical')`. If it does not match, retry with `search_domains($ARGUMENTS, domain_type='technical', refresh=true)` in case it is a recently created collection. If it now matches, continue. If it still does not match or there is no argument, list domains with `list_domains(domain_type='technical')` and ask the user following the user question convention.

### 2. Evaluate existing ontologies

Execute in parallel:
- `search_ontologies(domain_or_context)` or `list_ontologies()` → existing ontologies. Prefer `search_ontologies` if the user mentions a specific ontology; use `list_ontologies()` if the full list is needed
- `list_domain_tables(domain)` → tables available for the ontology

If there are ontologies, show the user:
- "No ontology found → we will create a new one"
- "Already exists [name] with N classes → we can extend, delete classes or create a new one"

If applicable, execute `get_ontology_info(name)` to show existing structure.

### 3. Interactive planning

This is the core of the skill. Ask the user, grouping to minimize interactions:

**Question block** (a single interaction):
- Do you have an existing ontology to take as reference? (if yes → `get_ontology_info` or read local file)
- What classes or entities do you consider essential?
- Any important aspects about format and naming conventions?

**Glossary instruction enrichment**:

Before proposing the plan, apply the Glossary Instruction Enrichment Workflow described in `guides/stratio-semantic-layer-tools.md` §11, scoped to **ontology** (i.e., when calling `get_glossary_instructions`, request only the ontology phase). This is where the user can pull GenAI ontology instructions from the data dictionary, supply an external file (.owl/.ttl, business document, CSV) as their source, layer free-text comments on top, or skip enrichment entirely.

If the orchestrator already pre-loaded enriched instructions for this phase during the `build-semantic-layer` flow, reuse them — optionally ask whether the user wants to add anything specific to this phase.

The enriched text becomes part of the planning context that feeds the proposed Markdown plan below. When the underlying MCP starts accepting `user_instructions` for `create_ontology` / `update_ontology`, that same text will also be passed through to the call.

**Domain exploration** (in parallel with the interaction if possible):
- `list_domain_tables(domain)` + `get_tables_details(domain, tables)` → understand tables and their context
- `get_table_columns_details(domain, table)` for key tables → available data for data properties
- `search_domain_knowledge(question, domain)` → existing terminology

**Propose plan**:
1. Propose ontology name (no spaces → underscores, no special characters)
2. Propose **Markdown plan** with:
   - Proposed classes with description
   - Data properties per class
   - Relationships between classes
   - Source tables for each class
3. Present plan to the user for review
4. Iterate until approval (max 3 refinement iterations)

### 4. Execution

#### 4.a Nominal call

According to the decision from step 2:
- **New ontology**: `create_ontology(domain, name, ontology_plan)` with the approved Markdown plan
- **Extend existing**: `update_ontology(domain, name, update_plan)` — new classes only
- **Delete specific classes**: DESTRUCTIVE operation — confirm with the user listing the classes to delete and warning that dependent business views will be refreshed. Execute `delete_ontology_classes(ontology_name, class_names)`. Report the result: deleted classes (`deleted`) and skipped classes due to Published views (`skipped_locked`)
- **Delete the entire ontology**: DESTRUCTIVE operation — confirm with the user that the named ontology and **all its classes** will be deleted. Execute `delete_ontology(ontology_name)`. Report whether the deletion succeeded or whether it was blocked because the ontology is in a non-deletable status

#### 4.b Recovery flow if `create_ontology` / `update_ontology` returns an error

**Important distinction**: if the failure response says the chain stopped **before generating any class** (typical wordings: the plan is not achievable with the available tables, required tables are missing, the request exceeds table/size limits, the plan could not be validated), the ontology was **not** persisted — just re-call `create_ontology` with an adjusted plan. The flow below applies **only** when the chain produced or partially produced classes and quality validation kept rejecting them.

In that case, present the user with the six options below and let them pick. **Confirm explicitly with the user before any call to `delete_ontology` (options A, D, E)** — the destructive-hint MCP annotation is informative, not enforcement.

| Option | Steps | When to choose |
|---|---|---|
| **A — Clean and retry with best-effort** | `delete_ontology(name)` → `create_ontology(name, plan, best_effort=True)` | Plan is right; user accepts a sub-optimal ontology with warnings instead of more retries |
| **B — Complete what's missing via update with best-effort** | `update_ontology(name, update_plan_for_missing_classes, best_effort=True)` | Base ontology was created; classes/views missing; user accepts sub-optimal new classes |
| **C — Complete what's missing via update in strict mode** | `update_ontology(name, corrected_update_plan)` (no `best_effort`) | Base ontology is fine; user adjusts the update plan to pass quality validation |
| **D — Clean and retry with a corrected plan** | `delete_ontology(name)` → `create_ontology(name, corrected_plan)` (no `best_effort`) | Structural problems in the original plan; reset and reattempt in strict mode |
| **E — Just clean** | `delete_ontology(name)` (no recreate) | User wants to wipe the failed attempt and stop here |
| **F — Leave as-is and review/fix manually in Governance UI** | (no tool call) | User accepts the partial ontology and will refine it manually |

Default suggestion heuristic (the user always has the final word):

- Only specific classes failed and the rest of the ontology is healthy → suggest C (cheaper, non-destructive).
- Transversal or base-structure issues → suggest D.
- Plan looks right but validation thrash is preventing finishing → suggest A.

After executing the chosen option, jump back to **step 5 (Verification)** to confirm the resulting state.

### 5. Verification

Execute `get_ontology_info(name)` to confirm the created structure. Present to the user:
- Generated classes with their data properties
- Established relationships
- Differences from the plan (if any)

Proactively offer: "If after reviewing it you want to remove any class, I can do it (classes with Published views cannot be deleted)." Not blocking — the user decides whether to continue or delete something.

### 6. Summary

- Ontology created/extended with name and number of classes
- Generated classes vs planned
- Warnings or issues found
- Suggested next step: "You can create the business views with `/create-business-views`"
