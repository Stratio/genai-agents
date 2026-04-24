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
| `create_ontology(domain, name, ontology_plan)` | gov | Create new ontology with Markdown plan |
| `update_ontology(domain, name, update_plan)` | gov | Add new classes to existing ontology |
| `delete_ontology_classes(ontology_name, class_names)` | gov | DESTRUCTIVE: delete specific classes (protected by Published) |

**Key rules**: `domain_name` immutable. Ontologies are ADD+DELETE: `update` adds classes, `delete_ontology_classes` deletes classes (protected: classes with dependent Published views are skipped). Existing classes cannot be modified. Naming: no spaces (→ underscores), no special characters. Offer `user_instructions` before invoking.

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
- Do you have additional files with relevant information? (ontologies .owl/.ttl, business documents, CSVs). If they provide paths → **read the files** to extract context
- Do you have existing ontologies as reference? (if yes → `get_ontology_info` or read local file)
- What classes or entities do you consider essential?
- Any important aspects about format and naming conventions?
- Any additional instructions for the AI that will generate the ontology?

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

According to the decision from step 2:
- **New ontology**: `create_ontology(domain, name, ontology_plan)` with the approved Markdown plan
- **Extend existing**: `update_ontology(domain, name, update_plan)` — new classes only
- **Delete classes**: DESTRUCTIVE operation — confirm with the user listing the classes to delete and warning that dependent business views will be refreshed. Execute `delete_ontology_classes(ontology_name, class_names)`. Report the result: deleted classes (`deleted`) and skipped classes due to Published views (`skipped_locked`)

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
