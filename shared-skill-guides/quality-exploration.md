# Quality Exploration and Context Guide

Steps for exploring and validating domains before executing any quality assessment.

## 1. Domain Discovery

For the standard discovery workflow (list domains, critical domain_name rule, explore tables, table and column detail), follow sections 4.1 to 4.4 of `skills-guides/stratio-data-tools.md`.

**Technical domains**: This agent also supports technical domains in addition to semantic ones. If the user requests to work with a technical domain, use `search_domains(search_text, domain_type="technical")` or `list_domains(domain_type="technical")`. For technical domains, steps 4.3 (table detail via `get_tables_details`) and 4.5 (terminology via `search_domain_knowledge`) may return limited or empty information — this is expected and should not block the workflow. Compensate with greater weight on the EDA (section 3) and direct validation with the user.

**Launch in parallel** when dealing with independent tables.

## 2. Quality Context (MANDATORY)

Dimension definitions must always be obtained before assessing:

`get_quality_rule_dimensions(collection_name=domain_name)` to know exactly what each dimension means in this specific domain and how many dimensions it supports.

Additionally, execute `quality_rules_metadata(domain_name=domain_name)` before assessing to have fresh AI metadata on the rules (description, dimension). Without `force_update` — only processes rules without metadata or modified ones. Non-blocking: if it fails, continue with the workflow normally.

This step is **MANDATORY** and fundamental for the following reasons:
- **Domain-Specific Dimensions**: Each domain may have its own dimensions defined in its quality document, beyond the standard ones.
- **Definitions and Ambiguity**: Since some dimensions are ambiguous by nature, the domain definition may differ from the standard one (e.g., what a domain considers `consistency` may be different from the general definition). The domain definition ALWAYS prevails.
- **Variability**: Do not assume that `completeness` always means the same thing or that all domains support the same set of dimensions.

## 3. Statistical Profiling (EDA)

For the base rules on using `profile_data` (generate SQL with `generate_sql`, never manual SQL, use the `limit` parameter instead of LIMIT in SQL), see `skills-guides/stratio-data-tools.md` sec 3 and 5.

`profile_data` is the main tool for understanding the reality of the data and grounding quality rules. **It requires a SQL query as a parameter.**

**Mandatory procedure:**
1. Generate the SQL first with `generate_sql(data_question="all fields from table X", domain_name="Y")`.
2. Pass the result to the `query` parameter of `profile_data`.
3. Use adaptive profiling according to the estimated dataset size (`limit` parameter).

| Column type        | What to look for in profiling                                                          |
|--------------------|----------------------------------------------------------------------------------------|
| **Any type**       | `missing_count`: if there are nulls, it justifies a `completeness` rule.               |
| **Keys/IDs**       | `distinct_count`: if less than total, there are duplicates (invalidates `uniqueness`).  |
| **Numeric**        | `min`, `max`, `mean`: detects outliers or invalid values for `validity`.                |
| **Categorical**    | `top_values`: basis for `validity` rules (enumerations).                                |
| **Dates**          | `min`, `max`: detects future dates or "dummy" values (1900/9999).                       |
| **...**            | ...                                                                                     |

**Launch in parallel** for all tables of interest during the initial assessment phase.
