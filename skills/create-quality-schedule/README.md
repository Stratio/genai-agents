# create-quality-schedule

Creates a **folder-level schedule** that runs all quality rules contained in one or more Stratio Governance collections automatically on a Quartz cron calendar. Schedules at the folder / collection level — not per individual rule — and always requires explicit user confirmation.

## What it does

- Resolves the target collections (validating each name exactly against `search_domains` / `list_domains`) and supports scheduling multiple collections in a single call.
- Optional table filter: when the user wants to run the schedule only on specific tables of a collection, validates those tables exist (`list_domain_tables`).
- Verifies each collection actually has rules via `get_tables_quality_details` and presents a per-collection rule count with OK/KO/Warning/Not-executed breakdown.
- Warns for empty collections (no point in scheduling them) and for KO rules (which will keep triggering alerts).
- Collects schedule parameters: name (suggested as `plan-[domain]-[frequency]`), business description (no scheduling details inside it, no technical column names), Quartz cron expression translated from natural-language frequency, optional start datetime (ISO 8601), timezone (defaults to `Europe/Madrid`), execution size (`XS` default, up to `XL` for large domains).
- Presents a full plan and waits for explicit approval before calling `create_quality_rule_planification`.

## When to use it

- The user wants to automate recurring quality checks (daily, weekly, monthly) for a domain or a set of domains.
- The user wants a single schedule to cover several collections together.
- For creating the **rules themselves**, prefer `create-quality-rules` — this skill only schedules rules that already exist.
- For filtering execution to specific tables within a collection, pass the table filter in step 1.2.

## Dependencies

### Other skills
- **Prerequisite:** `create-quality-rules` (the schedule is meaningful only if rules exist).
- **Typical predecessors:** `assess-quality` → `create-quality-rules` → `create-quality-schedule`.
- **Reference to load beforehand:** `stratio-semantic-layer` (governance MCP rules).

### Guides
None. Cron-translation examples and size guidance are inline in `SKILL.md`.

### MCPs
- **Data (`sql`):** `search_domains`, `list_domains`, `list_domain_tables`.
- **Governance (`gov`):** `get_tables_quality_details`, `create_quality_rule_planification`.

### Python
None — prompt-only skill.

### System
None.

## Bundled assets
None.

## Notes

- **Critical approval pause:** `create_quality_rule_planification` is **never** called without explicit user confirmation.
- **Default timezone is `Europe/Madrid`.** The skill does not ask about the timezone unless the user explicitly mentions another.
- **Default execution size is `XS`.** Use `M` / `L` / `XL` only for large domains or hundreds of rules — the skill does not ask unless the user raises performance concerns.
- **Very low-frequency cron expressions** (every second/minute) are refused; the skill explains the risk and suggests a reasonable minimum.
- **Cron translation from natural language** is built into the skill: "daily at 9" → `0 0 9 * * ?`, "every Monday at 8:30" → `0 30 8 ? * MON`, etc.
