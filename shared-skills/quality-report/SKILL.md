---
name: quality-report
description: "Generate a formal data quality coverage report in the format chosen by the user — chat, PDF, DOCX, PPTX, web dashboard, web article, poster or XLSX coverage matrix. Delegates file generation to the agent's writer skills (pdf-writer, docx-writer, pptx-writer, web-craft, canvas-craft, xlsx-writer) plus the centralized theming skill; chat format works standalone, file formats are offered only when the host agent declares the matching writer skill. Use when the user wants a quality report, coverage summary, quality dashboard, executive deck of quality findings, or any deliverable that consolidates assess-quality results."
argument-hint: "[format: chat|pdf|docx|pptx|web|poster|xlsx] [filename (optional)]"
---

# Skill: Quality Report Generation

Guidance-first workflow to produce a structured data quality coverage report. This skill orchestrates: it collects and composes the content, resolves the brand theme, and delegates the file-format generation to the host agent's writer skills. Only the Chat format is produced standalone by this skill.

## 1. Prerequisites and report data

This skill needs quality data to generate the report. Check if it already exists in the current conversation:

**If coverage assessment or rule creation data already exists in the conversation**: use that data directly. This includes both rules created from the gap flow (Flow A) and specific rules created directly by the user (Flow B).

**If there is NO coverage data in the context** (rule inventory, gaps, EDA): a full assessment of the requested scope must be performed first before generating the report. Inform the user and stop.

### Data to collect for the report

If the data is already in context, extract it directly. If missing, obtain it with parallel MCP calls:

```
Parallel:
  A. get_tables_quality_details(domain_name, tables)
  B. get_table_columns_details(domain_name, table)  [for each table]
  C. get_quality_rule_dimensions(domain_name=domain_name)
  D. get_critical_data_elements(collection_name=domain_name)  [if not already in context]
```

## 2. Format selection

### 2.1 Pre-check — writer skills availability (MANDATORY first step)

Before offering file-format options, confirm which writer skills the host agent declares. If the host agent does NOT declare `pdf-writer`, `docx-writer`, `pptx-writer`, `web-craft`, `canvas-craft` nor `xlsx-writer`, the only format available is Chat — skip §2.2 entirely and proceed with §5.1 (Chat).

This check is blocking: DO NOT offer file formats that the host agent cannot materialise, and DO NOT attempt to load a writer skill that is not declared by the host agent, even if the user insists on a file format.

### 2.2 Format options

If at least one writer skill is declared, ask the user following the user question convention. Only offer the options whose required skill is declared by the agent:

- **Chat** — structured summary in this conversation (no file). Always available.
- **PDF** — typographic multi-page document. Requires `pdf-writer`.
- **DOCX** — editable Word document. Requires `docx-writer`.
- **PowerPoint** — executive summary deck (16:9 by default). Requires `pptx-writer`.
- **Dashboard web** — interactive HTML with filters, KPI cards and sortable tables. Requires `web-craft`.
- **Web article / Narrative report** — self-contained HTML page, narrative or editorial layout. Requires `web-craft`.
- **Poster / Infographic** — single-page visual summary for print or publication. Requires `canvas-craft`.
- **Excel (XLSX)** — multi-sheet tabular coverage workbook (cover + coverage matrix with conditional formatting + rules detail + gaps + recommendations). Requires `xlsx-writer`.

Multiple selection is allowed (the same content materialises in several formats using the same internal `quality-report.md`).

If the user specified the format in the arguments or message, use it directly and skip the question.

## 3. Report structure

The report has the same structure regardless of format. Six canonical sections in this fixed order:

1. **Cover / Header** — title, domain, scope, generation date, agent name.
2. **Executive summary** — tables analysed, rules total, breakdown OK/KO/WARNING/NOT_EXECUTED, coverage estimate, gaps by priority (CRITICO/ALTO/MEDIO/BAJO), rules created this session.
3. **Coverage by table** — matrix of tables × dimensions with icon-coded status.
4. **Rules detail** — per table: rules with name, dimension, status, % pass, description. KO and WARNING visually highlighted.
5. **Identified gaps** — prioritised list with table, column, dimension, priority, description and recommendation.
6. **Recommendations and next steps** — prioritised bullets.

If the user created rules via `create-quality-rules` in the current conversation, an optional **Rules created in this session** section goes between §4 and §5.

For the full layout contract (iconography, KPI cards, per-format composition, deterministic rules for audit), see `quality-report-layout.md` in this skill folder.

## 4. Branding decisions

Before invoking any writer skill for a file format, fix the theme following the host agent's branding cascade. When the host agent declares a format→skill contract with a §Branding decisions sub-section, follow that cascade — it is typically 5 levels: pin → explicit signal → intra-session continuity → MEMORY preference → curated proposal.

**Primary neutral default for quality reports** (when no cascade rule resolves to a specific theme): `forensic-audit`. It matches the audit register of a coverage report and keeps month-over-month reruns of the same dataset visually stable. The curated proposal should prefer themes whose descriptor mentions "audit", "technical", "editorial" or "corporate".

If the user asks for neutrality explicitly ("no me importa el diseño" / "make it neutral" / "hazlo neutro"), apply `technical-minimal` as the sober fallback — maximum restraint, predictable output for non-audit contexts.

The chosen theme is recorded silently as the last line of the internal `quality-report.md` (e.g. `theme applied: forensic-audit`). Informational, not a contract.

## 5. Deliverable generation

### 5.1 Chat format

Emit the report directly as markdown in the current response, following the six canonical sections from §3. No file is produced, no writer skill is invoked, the branding cascade does not run.

End the message with the summary of 2-3 key points per §7.

### 5.2 Markdown on disk (optional, trivial)

If the user asks for a `.md` file on disk (not Chat, not one of the writer-backed formats), write it directly with the Write tool at `output/<folder>/<slug>-quality-report.md`. No writer skill involved — markdown is plain text.

Use the same folder convention as §5.3.

### 5.3 File formats (PDF, DOCX, PPTX, Dashboard web, Web article, Poster)

1. **Folder**: create `output/YYYY-MM-DD_HHMM_quality_<slug>/` (all artefacts live here). `<slug>` = domain or scope normalised (lowercase ASCII, accents stripped, spaces replaced by underscores, max 30 chars). Example: `2026-04-24_1530_quality_analiticabanca`.

2. **Brand tokens (once, before any visual format)**: load the centralized theming skill (`brand-kit`) with the theme fixed in §4. The theme file provides the token bundle — colours, typography, chart palette — that downstream writer skills consume so every deliverable looks coherent.

3. **Assemble the content source**: write `output/<folder>/quality-report.md` in the user's language, containing every canonical section from §3 using the structure described in `quality-report-layout.md` §10. When a section has no data, include the heading and an explicit "No X detected" line — do not omit silently. Apply the deterministic layout rules from `quality-report-layout.md` §11 (fixed section order, KPI card order, matrix column order, gap ordering, item limits per format). This internal file is the single source of truth the writer skills consume.

4. **For each selected format, load the matching writer skill and produce the deliverable. Follow `quality-report-layout.md` for the format-specific composition**:

   - **PDF** → load `pdf-writer`. Output: `<slug>-quality-report.pdf`. The deliverable must render the six canonical sections, apply brand tokens, honour the KPI cards pattern from the layout guide §5, and follow the PDF composition rules from §6.1 (header/footer on every page, repeat matrix header on page breaks, portrait unless dimension count >8).
   - **DOCX** → load `docx-writer`. Output: `<slug>-quality-report.docx`. Same six sections; use Word-native tables for the coverage matrix and rules detail so the user can edit them. Preserve heading styles (`Heading 1`, `Heading 2`, …).
   - **PowerPoint** → load `pptx-writer`. Output: `<slug>-quality-summary.pptx`. 16:9 by default; 4:3 only if the user asked explicitly. Target ≤12 slides following the outline in `quality-report-layout.md` §6.3.
   - **Dashboard web** → load `web-craft`. Output: `<slug>-quality-dashboard.html`. Apply the quality-specific layout from §6.4 (exactly the four KPI cards from §5, interactive coverage heatmap, filters for dimension/status/priority, sortable tables). If the host agent also declares a general `analytical-dashboard.md` guide, load it alongside so the generic dashboard patterns (global filters, Plotly via CDN, data budget, responsive, motion, language) apply on top.
   - **Web article / Narrative report** → load `web-craft`. Output: `<slug>-quality-article.html`. Do NOT apply the dashboard layout from §6.4. Use artifact class `Page` or `Article`. Render the six canonical sections as a scrollable, self-contained HTML page: narrative headings, inline KPI callouts, embedded Plotly coverage charts as figures, static HTML tables (not sortable). Same content as other formats; presentation is editorial, not interactive.
   - **Poster / Infographic** → load `canvas-craft`. Output: `<slug>-quality-poster.pdf` or `<slug>-quality-poster.png`. Single-page composition per §6.5 (KPI band top, central heatmap, top-3 gaps + top-3 recommendations in flanking columns, A3 portrait by default).
   - **Excel (XLSX)** → load `xlsx-writer`. Output: `<slug>-quality-report.xlsx`. Multi-sheet workbook per `quality-report-layout.md` §6.6 (Cover with 4 KPI cards as merged-cell band, Coverage matrix as native Table with conditional formatting for OK/KO/WARNING/NOT_EXECUTED, Rules detail grouped by table, Gaps prioritised, optional Rules-created-this-session, Recommendations). No Excel formulas (all values are displayed data); no native charts (the coverage matrix is itself the heatmap). Brand tokens apply to fill colors, border colors and state colors only — XLSX uses the reader's system fonts, not embedded fonts.

5. **Filename convention**: `<slug>` = descriptive domain/scope (as defined in step 1). Internal files (`quality-report.md`) stay without prefix.

6. **Verify each file exists on disk with `ls -lh output/<folder>/` after each writer skill returns.** If a file is missing, regenerate — do NOT report partial success to the user.

## 6. Post-generation verification

For file formats:
1. `ls -lh output/<folder>/` — confirm every expected file is present with non-zero size.
2. If any file is missing or zero-size: regenerate that format before returning to the user.

## 7. Final message to the user

After generation, present in chat:

- Generation confirmation (for Chat: the report itself; for files: folder path + list of generated artefacts with sizes).
- 2-3 key points from the report (e.g. top coverage gap, most critical KO rule, biggest improvement vs a previous report if available).
- Follow-up question (create rules for the detected gaps, expand scope to other tables, schedule periodic re-evaluation, etc.).
