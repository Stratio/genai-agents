#!/usr/bin/env python3
"""
validate_report_input.py
Validates that report-input.json matches the exact schema expected by quality_report_generator.py.
If there are errors, displays them with the correct field name and exits with code 1.

Usage:
    python scripts/validate_report_input.py [path-to-json]
    python scripts/validate_report_input.py output/report-input.json
"""
import json
import sys

# Incorrect names frequently used by the agent -> correct name
WRONG_ROOT_ALIASES = {
    "report_title": "title",
    "report_date": "generated_at",
    "date": "generated_at",
    "executive_summary": "summary",
    "global_summary": "summary",
    "output_format": "(remove — not a schema field)",
    "domain_description": "(remove — not a schema field)",
    "tables_analyzed": "summary.tables_analyzed  (must be inside 'summary', not at root)",
    "total_rules": "summary.rules_total",
    "rules_count": "summary.rules_total",
    "rules_pending": "summary.rules_not_executed",
    "rules_not_run": "summary.rules_not_executed",
    "coverage_percentage": "summary.coverage_estimate  (string, e.g.: '62%')",
    "critical_findings": "(remove — not a schema field)",
}

WRONG_TABLE_ALIASES = {
    "quality_rules": "rules",
    "coverage_matrix": "(remove — use flat fields: completeness, uniqueness, validity, consistency)",
    "coverage_by_dimension": "(remove — use flat fields: completeness, uniqueness, validity, consistency)",
    "eda_highlights": "(remove — not a schema field)",
    "profiling": "(remove — not a schema field)",
    "description": "(remove — not a schema field in tables[])",
    "row_count": "(remove — not a schema field in tables[])",
    "column_count": "(remove — not a schema field in tables[])",
    "columns": "(remove — not a schema field in tables[])",
}

WRONG_RULE_ALIASES = {
    "result": "pass_pct  (number 0-100 or null, not a string like '4500/4500')",
    "notes": "(remove — not a schema field in rules[])",
}

REQUIRED_ROOT = ["title", "domain", "scope", "generated_at", "summary", "tables"]
REQUIRED_SUMMARY = [
    "tables_analyzed", "rules_total", "rules_ok", "rules_ko",
    "rules_warning", "rules_not_executed", "coverage_estimate",
    "gaps_critical", "gaps_moderate", "gaps_low",
]
REQUIRED_TABLE = ["name", "completeness", "uniqueness", "validity", "consistency"]
REQUIRED_RULE = ["name", "dimension", "status"]
REQUIRED_GAP = ["column", "dimension", "priority", "description"]

VALID_COVERAGE = {"OK", "Gap", "Parcial", "N/A"}
VALID_RULE_STATUS = {"OK", "KO", "WARNING"}
VALID_PRIORITY = {"CRITICO", "ALTO", "MEDIO", "BAJO"}


def validate(path: str) -> None:
    errors = []

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}")
        sys.exit(1)

    # --- Root ---
    for wrong, correct in WRONG_ROOT_ALIASES.items():
        if wrong in data:
            errors.append(f"Root: incorrect field '{wrong}' -> rename to '{correct}'")

    for field in REQUIRED_ROOT:
        if field not in data:
            errors.append(f"Root: required field '{field}' is missing")

    # --- summary ---
    summary = data.get("summary")
    if summary is None:
        pass  # already reported above
    elif not isinstance(summary, dict):
        errors.append(
            f"'summary' must be an object with subfields, not a string. "
            f"Current value: {repr(str(summary)[:80])}"
        )
    else:
        for field in REQUIRED_SUMMARY:
            if field not in summary:
                errors.append(f"summary: required field '{field}' is missing")
        # coverage_estimate must be a string
        ce = summary.get("coverage_estimate")
        if ce is not None and not isinstance(ce, str):
            errors.append(
                f"summary.coverage_estimate must be a string (e.g.: '62%'), not a number. "
                f"Current value: {ce}"
            )

    # --- recommendations ---
    recs = data.get("recommendations")
    if recs is not None:
        if not isinstance(recs, list):
            errors.append("'recommendations' must be a list")
        elif recs and not isinstance(recs[0], str):
            errors.append(
                "'recommendations' must be an array of plain strings, not objects. "
                "Correct example: [\"High — account: Review duplicate rules.\", \"Medium — ...\"]"
            )

    # --- tables ---
    tables = data.get("tables", [])
    if not isinstance(tables, list) or len(tables) == 0:
        errors.append("'tables' must be a list with at least one table")

    for i, t in enumerate(tables):
        tname = t.get("name", f"tables[{i}]")

        for wrong, correct in WRONG_TABLE_ALIASES.items():
            if wrong in t:
                errors.append(f"table '{tname}': incorrect field '{wrong}' -> {correct}")

        for field in REQUIRED_TABLE:
            if field not in t:
                errors.append(f"table '{tname}': required field '{field}' is missing")

        for dim in ["completeness", "uniqueness", "validity", "consistency"]:
            val = t.get(dim)
            if val is not None and val not in VALID_COVERAGE:
                errors.append(
                    f"table '{tname}': invalid value in '{dim}': '{val}' "
                    f"-> use one of: {sorted(VALID_COVERAGE)}"
                )

        # rules
        for j, r in enumerate(t.get("rules", [])):
            rname = r.get("name", f"rules[{j}]")
            for wrong, correct in WRONG_RULE_ALIASES.items():
                if wrong in r:
                    errors.append(
                        f"table '{tname}', rule '{rname}': incorrect field '{wrong}' -> {correct}"
                    )
            for field in REQUIRED_RULE:
                if field not in r:
                    errors.append(
                        f"table '{tname}', rule '{rname}': required field '{field}' is missing"
                    )
            status = r.get("status")
            if status is not None and status not in VALID_RULE_STATUS:
                errors.append(
                    f"table '{tname}', rule '{rname}': invalid status '{status}' "
                    f"-> use OK, KO or WARNING  (for unexecuted rules use WARNING, never 'Pendiente' or 'Sin ejecucion reciente')"
                )
            pass_pct = r.get("pass_pct")
            if pass_pct is not None and not isinstance(pass_pct, (int, float)):
                errors.append(
                    f"table '{tname}', rule '{rname}': pass_pct must be a number (0-100) or null, "
                    f"not a string. Current value: '{pass_pct}'"
                )

        # gaps
        for j, g in enumerate(t.get("gaps", [])):
            pri = g.get("priority")
            if pri is not None and pri not in VALID_PRIORITY:
                errors.append(
                    f"table '{tname}', gap {j} (col '{g.get('column', '?')}'): "
                    f"invalid priority '{pri}' "
                    f"-> use CRITICO, ALTO, MEDIO or BAJO  (never 'Alta', 'Media', 'Baja')"
                )
            for field in REQUIRED_GAP:
                if field not in g:
                    errors.append(
                        f"table '{tname}', gap {j}: required field '{field}' is missing"
                    )

    # --- rules_created ---
    for j, r in enumerate(data.get("rules_created", [])):
        rname = r.get("name", f"rules_created[{j}]")
        if "calculated_status" in r:
            errors.append(
                f"rules_created '{rname}': incorrect field 'calculated_status' "
                f"-> rename to 'status'"
            )
        if "status" not in r:
            errors.append(f"rules_created '{rname}': required field 'status' is missing")

    # --- Result ---
    if errors:
        total_rules = sum(len(t.get("rules", [])) for t in tables)
        total_gaps = sum(len(t.get("gaps", [])) for t in tables)
        print(
            f"\n[VALIDATION FAILED] {len(errors)} error(s) in {path} "
            f"({len(tables)} table(s), {total_rules} rule(s), {total_gaps} gap(s)):\n"
        )
        for e in errors:
            print(f"  ✗ {e}")
        print(
            "\nFix all errors above in report-input.json before running the generator.\n"
        )
        sys.exit(1)
    else:
        total_rules = sum(len(t.get("rules", [])) for t in tables)
        total_gaps = sum(len(t.get("gaps", [])) for t in tables)
        print(
            f"[OK] {path} is valid — "
            f"{len(tables)} table(s), {total_rules} rule(s), {total_gaps} gap(s)"
        )
        sys.exit(0)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "output/report-input.json"
    validate(path)
