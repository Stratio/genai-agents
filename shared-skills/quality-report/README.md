# quality-report

Shared skill that coordinates the production of the formal data quality coverage report. Guidance-first: orchestrates content assembly and delegates file generation to the host agent's writer skills (`pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`, `xlsx-writer`) plus the centralized theming skill (`brand-kit`).

Each host agent picks the allowed formats based on which writer skills it declares in its `shared-skills` manifest.

## Exception to the self-containment rule

Shared skills are normally self-contained — no SKILL.md in `shared-skills/` references another shared-skill by name, so any skill can be packaged standalone.

`quality-report` is an **explicit exception**: its `SKILL.md` references `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`, `xlsx-writer` and `brand-kit` by name. The rationale is pragmatic — the same report structure must materialise in 7 distinct output formats (web-craft serves both Dashboard and Web article), and each format has a dedicated writer skill with its own guidance-first workflow. Inlining every format pipeline inside `quality-report` would duplicate thousands of lines of instruction that already live in the writer skills.

**Contract enforced by the monorepo**: any agent that declares `quality-report` in its `shared-skills` manifest should also declare `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft`, `xlsx-writer` and `brand-kit` so the skill can materialise the full range of file formats. A chat-oriented agent may opt out of the writer bundle; in that case `quality-report`'s pre-check detects the absence of writers and restricts the offering to the Chat format, so the writer-skill references in the SKILL.md are never triggered at runtime.

## What it does

- Pulls quality coverage data from conversation context (or via MCP if missing): rule inventory, dimension definitions, table metadata, profiling.
- Composes the canonical six-section report structure (Executive summary → Coverage → Rules → Gaps → Recommendations) in the user's language.
- Writes an internal `quality-report.md` as single source of truth inside `output/YYYY-MM-DD_HHMM_quality_<slug>/`.
- For Chat format: renders directly in the response, no writer skill invoked.
- For file formats (PDF, DOCX, PPTX, Dashboard web, Web article/Narrative report, Poster/Infographic, XLSX): resolves the brand theme through the host agent's branding cascade, loads the matching writer skill and produces the deliverable applying brand tokens and following `quality-report-layout.md`.

## Files in this skill

- `SKILL.md` — entry point, workflow and format-selection logic.
- `quality-report-layout.md` — canonical structure, iconography, KPI cards, per-format composition, deterministic layout rules for audit.
- `README.md` — this file.

## Local guide

- `quality-report-layout.md` — applied by the writer skills when they produce a quality-report deliverable. Describes what the report contains and how it behaves across formats; leaves visual voice (tone, typography, motion) to the writer skills.

## Dependencies

None for this skill directly. All file generation is delegated to the writer skills declared by the host agent. Each writer skill manages its own runtime dependencies.

## MCPs

- **Governance (`gov`):** `get_tables_quality_details`, `get_quality_rule_dimensions`, `quality_rules_metadata`.
- **Data (`sql`):** `get_table_columns_details`, `get_tables_details` — invoked only when the upstream `assess-quality` context is missing and the skill needs to backfill.

Most invocations arrive with the context already populated by `assess-quality`, so in practice the skill mostly reads from the conversation state rather than calling MCPs directly.

## Including this skill in an agent

When adding `quality-report` to an agent's `shared-skills` manifest, declare it together with the writer skills `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` and `xlsx-writer`, plus the centralized theming skill `brand-kit`. That bundle is what lets the agent deliver the full range of formats (PDF, DOCX, PPTX, Dashboard web, Web article/Narrative report, Poster/Infographic, XLSX). If the agent is chat-oriented and omits the writers by design, only the Chat format will be offered to the user — which is a valid, supported configuration.
