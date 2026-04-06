---
name: quality-report
description: Generate a formal data quality coverage report in the format chosen by the user (chat, PDF, DOCX, or Markdown on disk). Use when the user wants a document or presentation with the current quality status, after assessing coverage or creating quality rules.
argument-hint: "[format: chat|pdf|docx|md] [filename (optional)]"
---

# Skill: Quality Report Generation

Workflow for generating a structured report with the state of data quality coverage.

## 1. Prerequisites and Report Data

This skill needs quality data to generate the report. Check if it already exists in the current conversation:

**If coverage assessment or rule creation data already exists in the conversation**: use that data directly. This includes both rules created from the gap flow (Flow A) and specific rules created directly by the user (Flow B).

**If there is NO coverage data in the context** (rule inventory, gaps, EDA): a full assessment of the requested scope must be performed first before generating the report. Inform the user and stop.

### Data to collect for the report

If the data is already in context, extract it directly. If missing, obtain it with parallel MCP calls:

```
Parallel:
  A. get_tables_quality_details(domain_name, tables)
  B. get_table_columns_details(domain_name, table)  [for each table]
  C. get_quality_rule_dimensions(collection_name=domain_name)
```

## 2. Format Selection

If the user has not specified a format, ask the user with options following the user question convention:

```
What format do you want the report in?
  1. Chat — structured summary in this conversation (no file)
  2. PDF — formal downloadable document
  3. DOCX — editable Word document
  4. Markdown — .md file on disk
```

If the user has specified the format in the arguments or message, use it directly.

## 3. Report Structure

The report has the same structure regardless of format:

### Cover / Header
- Title: "Data Quality Coverage Report"
- Domain / Collection: [name]
- Scope: [full domain / specific table(s)]
- Generation date: [today]
- Agent: Data Quality Expert

### Section 1 — Executive Summary
- Tables analyzed: N
- Existing quality rules: N
- Estimated global coverage: XX%
- Rules in OK status: N | KO: N | WARNING: N | Not executed: N
- Gaps identified: N critical, N moderate, N low
- Rules created in this session (if applicable): N

### Section 2 — Coverage by Table

Matrix table (include standard and domain-specific dimensions):
```
| Table | Completeness | Uniqueness | Validity | Consistency | Other Dimensions | Coverage |
```

With icon or color legend (depending on format).

### Section 3 — Existing Rules Detail

For each table, list its rules:
```
| Rule | Dimension | Status | % Pass | Description |
```

Highlight (bold or red) rules in KO or WARNING.

### Section 4 — Identified Gaps

Prioritized list of gaps:
- For each gap: table, column, missing dimension, estimated impact, recommendation

### Section 5 — Rules Created in this Session (if applicable)

If quality rules were created in this session, include:
- List of created rules with their SQL
- Coverage before and after (only if a coverage assessment was performed previously; for Flow B rules without prior assessment, omit the coverage comparison)

**For Flow B rules (specific rule)**: indicate they were directly requested by the user, include the described business logic, the SQL validation result (passing records / total, % or count) and the calculated status (OK / KO / WARNING / NO_DATA) based on the applied measurement configuration (measurement_type + threshold_mode + thresholds).

**For Flow A rules (gaps)**: include the SQL validation result with the calculated status. If validation showed KO or WARNING, visually highlight it (bold) as data to review.

### Section 6 — Recommendations and Next Steps

- Priority KO/WARNING rules to investigate
- Critical pending gaps to cover
- Effort estimation for full coverage

## 4. Generation by Format

### Format: Chat

Generate the report directly in markdown within the chat response. Follow the structure in section 3 with well-formatted headers, tables, and lists.

Do not execute Python or create files.

### File formats: PDF, DOCX, and Markdown on disk

All three file formats (PDF, DOCX, MD) use the same Python generator and the same `report-input.json` file. The process is identical except for the `--format` flag and the output file extension.

#### Step 1 — Verify environment

```bash
bash setup_env.sh
```

#### Step 2 — Prepare report-input.json

Get the absolute path of the output directory:
```bash
mkdir -p output/ && readlink -f output/
```

Write `<absolute-path>/report-input.json` with the exact schema that follows. **Field names are literal — the generator reads them with `data.get("field")` and returns `-` if they don't exist.**

**Common errors to avoid (produce blank report):**
- NOT `report_title` → `title`
- NOT `report_date` / `date` → `generated_at`
- NOT `executive_summary` → `summary`
- NOT `total_rules` / `rules_count` → `summary.rules_total`
- NOT `rules_pending` / `rules_not_run` → `summary.rules_not_executed`
- NOT `quality_rules` → `tables[].rules`
- NOT `coverage_by_dimension` (nested object) → flat fields `tables[].completeness`, `tables[].uniqueness`, etc.
- NOT priorities in Spanish (`Alta/Media/Baja`) → `CRITICO|ALTO|MEDIO|BAJO`
- NOT `recommendations` as array of objects → array of **plain strings**
- NOT `calculated_status` in `rules_created` → `status`

```json
{
  "title": "Data Quality Coverage Report — <table> — <domain>",
  "domain": "<domain_name>",
  "scope": "<table(s) or 'Full domain'>",
  "generated_at": "<YYYY-MM-DD>",
  "summary": {
    "tables_analyzed": <N>,
    "rules_total": <N>,
    "rules_ok": <N>,
    "rules_ko": <N>,
    "rules_warning": <N>,
    "rules_not_executed": <N>,
    "coverage_estimate": "<XX%>",
    "gaps_critical": <N>,
    "gaps_moderate": <N>,
    "gaps_low": <N>,
    "rules_created_this_session": <N or null>
  },
  "tables": [
    {
      "name": "<table>",
      "coverage_estimate": "<XX%>",
      "completeness": "<OK|Gap|Partial|N/A>",
      "uniqueness": "<OK|Gap|Partial|N/A>",
      "validity": "<OK|Gap|Partial|N/A>",
      "consistency": "<OK|Gap|Partial|N/A>",
      "rules": [
        {
          "name": "<rule-name>",
          "dimension": "<dimension>",
          "status": "<OK|KO|WARNING>",
          "pass_pct": <0-100 or null>,
          "description": "<description>"
        }
      ],
      "gaps": [
        {
          "column": "<column or '—' if applies to the table>",
          "dimension": "<missing dimension>",
          "priority": "<CRITICO|ALTO|MEDIO|BAJO>",
          "description": "<gap description>"
        }
      ]
    }
  ],
  "rules_created": [
    {
      "name": "<rule-name>",
      "table": "<table>",
      "dimension": "<completeness|uniqueness|validity|consistency|...>",
      "status": "<created|OK|KO|WARNING|SIN_DATOS>"
    }
  ],
  "recommendations": ["<recommendation 1 as plain string>", "<recommendation 2>"]
}
```

**Mapping notes from coverage assessment data:**
- `summary.rules_total` ← total existing rules in the collection (not only executed ones)
- `summary.rules_not_executed` ← rules without results yet (pending)
- `summary.gaps_critical` ← gaps with priority `CRITICO`; `gaps_moderate` ← `ALTO`; `gaps_low` ← `MEDIO` + `BAJO`
- `tables[].completeness/uniqueness/validity/consistency` ← `OK` if there is an active rule, `Gap` if none, `Partial` if incomplete, `N/A` if not applicable
- `tables[].rules[].status` ← for unexecuted rules use `WARNING` (never "Pending" or "Not executed")
- `tables[].gaps[].priority` ← `CRITICO` for PK/FK without rule, `ALTO` for key columns, `MEDIO` for the rest, `BAJO` for optional dimensions
- `rules_created[].status` ← use `"created"` for rules newly created this session without validation; `OK|KO|WARNING|SIN_DATOS` if SQL validation was executed

#### Step 3 — Determine output path

- If the user indicated a name: use that (with the correct extension)
- If not:
  - PDF: `output/quality-report-[domain]-[YYYY-MM-DD].pdf`
  - DOCX: `output/quality-report-[domain]-[YYYY-MM-DD].docx`
  - MD: `output/quality-report-[domain]-[YYYY-MM-DD].md`

#### Step 4 — Validate the JSON (MANDATORY before running the generator)

```bash
.venv/bin/python scripts/validate_report_input.py output/report-input.json
```

- If it ends with `[OK]`: continue to step 5.
- If it ends with `[VALIDATION FAILED]`: read each error, correct the `report-input.json`, and re-run validation until it passes without errors. **Do not run the generator with an invalid JSON** — it will produce a blank report without warning.

#### Step 5 — Run the generator

```bash
.venv/bin/python scripts/quality_report_generator.py \
  --format <pdf|docx|md> \
  --output "output/quality-report-[domain]-[date].<ext>" \
  --input-file output/report-input.json
```

If the user requests PDF and DOCX in the same session, the `report-input.json` can be reused — run the generator twice with different `--format` and `--output`.

## 5. Post-Generation Verification

For file formats (PDF, DOCX, MD on disk):
1. Verify the file exists: `ls -lh output/[filename]`
2. Inform the user: filename, full path, size
3. If generation failed: show the error and offer a chat alternative

## 6. Final Message to the User

After generating the report, present in chat:
- Generation confirmation (or the report itself if chat format)
- File path (if applicable)
- Summary of 2-3 key points from the report
- Question about whether they want anything else (create rules for gaps, expand scope, etc.)
