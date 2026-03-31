#!/usr/bin/env python3
"""
validate_report_input.py
Valida que report-input.json tenga el schema exacto que espera quality_report_generator.py.
Si hay errores, los muestra con el nombre correcto del campo y termina con exit code 1.

Uso:
    python tools/validate_report_input.py [ruta-al-json]
    python tools/validate_report_input.py output/report-input.json
"""
import json
import sys

# Nombres incorrectos que el agente usa frecuentemente → nombre correcto
WRONG_ROOT_ALIASES = {
    "report_title": "title",
    "report_date": "generated_at",
    "date": "generated_at",
    "executive_summary": "summary",
    "global_summary": "summary",
    "output_format": "(eliminar — no es un campo del schema)",
    "domain_description": "(eliminar — no es un campo del schema)",
    "tables_analyzed": "summary.tables_analyzed  (debe estar dentro de 'summary', no en la raiz)",
    "total_rules": "summary.rules_total",
    "rules_count": "summary.rules_total",
    "rules_pending": "summary.rules_not_executed",
    "rules_not_run": "summary.rules_not_executed",
    "coverage_percentage": "summary.coverage_estimate  (string, ej: '62%')",
    "critical_findings": "(eliminar — no es un campo del schema)",
}

WRONG_TABLE_ALIASES = {
    "quality_rules": "rules",
    "coverage_matrix": "(eliminar — usar campos planos: completeness, uniqueness, validity, consistency)",
    "coverage_by_dimension": "(eliminar — usar campos planos: completeness, uniqueness, validity, consistency)",
    "eda_highlights": "(eliminar — no es un campo del schema)",
    "profiling": "(eliminar — no es un campo del schema)",
    "description": "(eliminar — no es un campo del schema en tables[])",
    "row_count": "(eliminar — no es un campo del schema en tables[])",
    "column_count": "(eliminar — no es un campo del schema en tables[])",
    "columns": "(eliminar — no es un campo del schema en tables[])",
}

WRONG_RULE_ALIASES = {
    "result": "pass_pct  (número 0-100 o null, no string como '4500/4500')",
    "notes": "(eliminar — no es un campo del schema en rules[])",
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
        print(f"[ERROR] Fichero no encontrado: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON inválido en {path}: {e}")
        sys.exit(1)

    # --- Raiz ---
    for wrong, correct in WRONG_ROOT_ALIASES.items():
        if wrong in data:
            errors.append(f"Raiz: campo incorrecto '{wrong}' → renombrar a '{correct}'")

    for field in REQUIRED_ROOT:
        if field not in data:
            errors.append(f"Raiz: campo requerido '{field}' no existe")

    # --- summary ---
    summary = data.get("summary")
    if summary is None:
        pass  # ya reportado arriba
    elif not isinstance(summary, dict):
        errors.append(
            f"'summary' debe ser un objeto con subcampos, no un string. "
            f"Valor actual: {repr(str(summary)[:80])}"
        )
    else:
        for field in REQUIRED_SUMMARY:
            if field not in summary:
                errors.append(f"summary: campo requerido '{field}' no existe")
        # coverage_estimate debe ser string
        ce = summary.get("coverage_estimate")
        if ce is not None and not isinstance(ce, str):
            errors.append(
                f"summary.coverage_estimate debe ser string (ej: '62%'), no número. "
                f"Valor actual: {ce}"
            )

    # --- recommendations ---
    recs = data.get("recommendations")
    if recs is not None:
        if not isinstance(recs, list):
            errors.append("'recommendations' debe ser una lista")
        elif recs and not isinstance(recs[0], str):
            errors.append(
                "'recommendations' debe ser array de strings planos, no de objetos. "
                "Ejemplo correcto: [\"Alta — account: Revisar reglas duplicadas.\", \"Media — ...\"]"
            )

    # --- tables ---
    tables = data.get("tables", [])
    if not isinstance(tables, list) or len(tables) == 0:
        errors.append("'tables' debe ser una lista con al menos una tabla")

    for i, t in enumerate(tables):
        tname = t.get("name", f"tables[{i}]")

        for wrong, correct in WRONG_TABLE_ALIASES.items():
            if wrong in t:
                errors.append(f"tabla '{tname}': campo incorrecto '{wrong}' → {correct}")

        for field in REQUIRED_TABLE:
            if field not in t:
                errors.append(f"tabla '{tname}': campo requerido '{field}' no existe")

        for dim in ["completeness", "uniqueness", "validity", "consistency"]:
            val = t.get(dim)
            if val is not None and val not in VALID_COVERAGE:
                errors.append(
                    f"tabla '{tname}': valor inválido en '{dim}': '{val}' "
                    f"→ usar uno de: {sorted(VALID_COVERAGE)}"
                )

        # rules
        for j, r in enumerate(t.get("rules", [])):
            rname = r.get("name", f"rules[{j}]")
            for wrong, correct in WRONG_RULE_ALIASES.items():
                if wrong in r:
                    errors.append(
                        f"tabla '{tname}', regla '{rname}': campo incorrecto '{wrong}' → {correct}"
                    )
            for field in REQUIRED_RULE:
                if field not in r:
                    errors.append(
                        f"tabla '{tname}', regla '{rname}': campo requerido '{field}' no existe"
                    )
            status = r.get("status")
            if status is not None and status not in VALID_RULE_STATUS:
                errors.append(
                    f"tabla '{tname}', regla '{rname}': status inválido '{status}' "
                    f"→ usar OK, KO o WARNING  (para reglas sin ejecutar usar WARNING, nunca 'Pendiente' ni 'Sin ejecución reciente')"
                )
            pass_pct = r.get("pass_pct")
            if pass_pct is not None and not isinstance(pass_pct, (int, float)):
                errors.append(
                    f"tabla '{tname}', regla '{rname}': pass_pct debe ser número (0-100) o null, "
                    f"no string. Valor actual: '{pass_pct}'"
                )

        # gaps
        for j, g in enumerate(t.get("gaps", [])):
            pri = g.get("priority")
            if pri is not None and pri not in VALID_PRIORITY:
                errors.append(
                    f"tabla '{tname}', gap {j} (col '{g.get('column', '?')}'): "
                    f"priority inválida '{pri}' "
                    f"→ usar CRITICO, ALTO, MEDIO o BAJO  (nunca 'Alta', 'Media', 'Baja')"
                )
            for field in REQUIRED_GAP:
                if field not in g:
                    errors.append(
                        f"tabla '{tname}', gap {j}: campo requerido '{field}' no existe"
                    )

    # --- rules_created ---
    for j, r in enumerate(data.get("rules_created", [])):
        rname = r.get("name", f"rules_created[{j}]")
        if "calculated_status" in r:
            errors.append(
                f"rules_created '{rname}': campo incorrecto 'calculated_status' "
                f"→ renombrar a 'status'"
            )
        if "status" not in r:
            errors.append(f"rules_created '{rname}': campo requerido 'status' no existe")

    # --- Resultado ---
    if errors:
        total_rules = sum(len(t.get("rules", [])) for t in tables)
        total_gaps = sum(len(t.get("gaps", [])) for t in tables)
        print(
            f"\n[VALIDATION FAILED] {len(errors)} error(es) en {path} "
            f"({len(tables)} tabla(s), {total_rules} regla(s), {total_gaps} gap(s)):\n"
        )
        for e in errors:
            print(f"  ✗ {e}")
        print(
            "\nCorrige todos los errores anteriores en report-input.json antes de ejecutar el generador.\n"
        )
        sys.exit(1)
    else:
        total_rules = sum(len(t.get("rules", [])) for t in tables)
        total_gaps = sum(len(t.get("gaps", [])) for t in tables)
        print(
            f"[OK] {path} es válido — "
            f"{len(tables)} tabla(s), {total_rules} regla(s), {total_gaps} gap(s)"
        )
        sys.exit(0)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "output/report-input.json"
    validate(path)
