---
name: report
description: "Professional report generation in multiple formats (PDF, DOCX, interactive web with Plotly, PowerPoint). Use when the user needs to generate reports, dashboards, executive summaries, presentations, or any formal deliverable from data analysis or conversation exploration."
argument-hint: "[format: pdf|web|pptx] [topic (optional)]"
---

# Skill: Report Generation

Guide for generating professional reports in multiple formats from data and analyses.

## 1. Determine Format, Structure, and Style

Parse argument: $ARGUMENTS

If the format is not specified, ask the user the following 3 questions in a single interaction, following the question convention.

**Rendering rules — MANDATORY**:
- Present **every** option literally, one option per line. Never collapse, summarise, omit or reword options, even when an option looks "advanced" or secondary. The user must see all of them to make an informed choice.
- Follow the question convention for the delivery mechanism — the agent uses an interactive question tool when the environment provides one, or a numbered list in chat otherwise. Do not hard-code the tool name; let the convention resolve it.
- Each question is its own numbered block in chat renderings.
- Keep the **labels** (Corporate, Academic, Modern, Design-first, Base scaffold, On the fly, Document, Web, PowerPoint) verbatim — they map to internal routing. Translate only the surrounding prose if the user is in another language.

### Question 1 — In what formats do you want the deliverables? (multiple selection)
- **Document** — PDF + DOCX
- **Web** — Interactive HTML with Plotly
- **PowerPoint** — `.pptx`

### Question 2 — What structure do you prefer for the report? (single selection)
- **Base scaffold** *(Recommended)* — executive summary → methodology → data → analysis → conclusions
- **On the fly** — free structure based on context

### Question 3 — What visual style do you prefer? (single selection)
- **Corporate** *(Recommended)* — `corporate.css`, clean and professional
- **Academic** — `academic.css`, serif typography, wide margins, paper style
- **Modern** — `modern.css`, colour and gradients, visually appealing
- **Design-first** — commit to a deliberate aesthetic direction (tone, type pairing, palette, motion budget) derived from the report's subject matter. Recommended when the deliverable is a high-visibility piece — executive summaries for a board, launch briefs, narrative reports where the visual voice is part of the message. See §4.1 for the workflow.

Notes:
- Question 1 ALWAYS allows multiple selection (the user may want several formats).
- If no format is selected, only a text response is given in chat.
- `output/[ANALYSIS_DIR]/report.md` is always generated automatically as internal documentation (no option needed).
- If the format comes from the argument (`$ARGUMENTS`), skip directly to questions 2 and 3.

### 1.1 Filename convention for deliverables

User-facing deliverables are written with a descriptive prefix so they are recognisable after download, outside their folder:

- `<slug>-report.pdf`, `<slug>-report.docx` (Document format)
- `<slug>-dashboard.html` (Web format)
- `<slug>-presentation.pptx` (PowerPoint format)

`<slug>` is the descriptive part of `[ANALYSIS_DIR]` — the folder is `YYYY-MM-DD_HHMM_<slug>/`, so `<slug>` is everything after the timestamp prefix. Internal files (`plan.md`, `reasoning.md`, `report.md`, `validation.md`, `aesthetic.json`) stay without prefix.

## 2. Verify Available Data

- Check if previous data exists in `output/[ANALYSIS_DIR]/data/` (CSVs, DataFrames)
- Check if charts exist in `output/[ANALYSIS_DIR]/assets/`
- If there is no data: inform the user that they first need to run an analysis
- If there is partial data: ask whether to reuse or regenerate

### 2.1 Visualization and storytelling

Read and follow `skills-guides/visualization.md` for:
- Chart type selection based on analytical question (sec 1)
- Visualization and accessibility principles (sec 2)
- Data storytelling: Hook→Context→Findings→Tension→Resolution narrative structure (sec 3)
- Mapping analytical findings → narrative role (sec 4)

**Report-specific — Anti-overlap layout**: Title as insight on top, context as subtitle, legend positioned below the chart or to the right exterior. Use `tools/chart_layout.py` for standard layout.

## 3. Environment Setup

```bash
bash setup_env.sh
```
Verify that format dependencies are available (weasyprint for PDF, python-pptx for PowerPoint, etc.).

## 3.1 Language of Generated Deliverables

All generators (`DOCXGenerator`, `PDFGenerator`, `DashboardBuilder`, `md_to_report.py`) use a shared i18n catalogue in `tools/i18n.py` for their static labels (scaffold headings "Executive Summary" / "Methodology" / …, cover labels "Author:" / "Domain:" / "Date:", dashboard chrome "Filters" / "Clear filters" / "KPIs", the HTML `lang` attribute, the default report title, etc.).

**Pass the user's language explicitly when invoking any generator** so the static chrome matches the chat language:

- Python API (`DOCXGenerator`, `PDFGenerator`, `DashboardBuilder`): pass `lang="<code>"` to `render_scaffold` / `render_from_markdown` / `render_from_html` / the constructor (whichever applies). Optionally pass `labels={...}` to override specific keys.
- CLI (`md_to_report.py`): pass `--lang <code>` (and optionally `--labels-json '{...}'`).

Resolution order when you don't pass `lang`: the `.agent_lang` file written at packaging time → `"en"`. So a package built with `--lang es` defaults to Spanish labels even without explicit `lang`. Supported catalogue languages today: `en`, `es`. Unknown codes fall back to English per key; pass `labels={...}` to inject translations for other languages.

## 4. Style Tools

All formats share the same source of truth for colors and fonts:

- **CSS (PDF, Web):** `build_css(style, target)` from `tools/css_builder.py` assembles tokens + theme + target
- **Non-CSS (PPTX, DOCX):** `get_palette(style)` from `tools/css_builder.py` returns RGB colors and fonts
- **Reasoning (Markdown → PDF/HTML):** `tools/md_to_report.py` with options `--style`, `--cover`, `--author`, `--domain`

```python
from css_builder import build_css, get_palette
css, name = build_css("corporate", "pdf")    # Assembled CSS
palette = get_palette("corporate")           # {"primary": (0x1a,0x36,0x5d), "font_main": "Inter", ...}
```

## 4.1 Design-first workflow (when question 3 selects "Design-first")

When the user picks "Design-first" in question 3, run this five-step checklist **before** invoking any generator. Persist the result as `output/[ANALYSIS_DIR]/aesthetic.json` and pass it as `aesthetic_direction` to `DashboardBuilder`, `PDFGenerator`, `DOCXGenerator`, `create_presentation`, `chart_layout.get_chart_colors`, and `md_to_report.py --aesthetic`. This keeps the HTML, PDF, DOCX and PPTX visually coherent.

1. **Classify the artifact** — `executive-dashboard` / `technical-report` / `editorial-brief` / `forensic-audit`. The class governs the next five decisions.
2. **Choose a tone (pick one, commit)** — `editorial-serious` / `technical-minimal` / `executive-editorial` / `forensic-audit` / `maximalist-analytical` / `brutalist-data`. Half-and-half is not an option.
3. **Type pairing** — one display face + one body face from the "Type pairings by artifact class" table in `skills-guides/dashboard-aesthetics.md`. Write the result as `font_pair: [display, body]`.
4. **Palette** — derive a dominant accent from the data subject (finance → deep blue or oxblood; operations → cool steel or forest; audit → deep red on bone; consumer → a saturated primary). Fill a `palette_override` dict with CSS-level keys (`"--primary"`, `"--accent"`, `"--text-primary"`, …) that match the tokens of the chosen base style. *Note:* in `academic`, the token for the "primary" role is `--heading-color`; overriding `--primary` there is inert — consult the "Caveat — `academic`" note in `skills-guides/dashboard-aesthetics.md`.
5. **Motion budget** (dashboards only) — `none` / `minimal` / `expressive`. No JS, CSS-only, `@keyframes` prefixed with `dashboard-`, `prefers-reduced-motion` honoured.
6. **Background style** (optional) — `solid` / `gradient-mesh` / `noise` / `grain`. Decide whether the artifact earns atmosphere beyond a flat surface.

Write the resulting `aesthetic.json` with this schema (extra keys are rejected by `md_to_report.py --aesthetic`):

```json
{
  "tone": "editorial-serious",
  "palette_override": {"--primary": "#0a2540", "--accent": "#d9472b"},
  "font_pair": ["Fraunces", "Inter"],
  "motion_budget": "expressive",
  "background_style": "gradient-mesh"
}
```

**Order of operations**: create `output/[ANALYSIS_DIR]/` before writing `aesthetic.json`. If the file already exists from a previous run and the user now picks a different style, overwrite it and add a line to `reasoning.md`:

> *Aesthetic direction (content of `aesthetic.json`)*: tone=…, palette_override=…, font_pair=…, motion_budget=…, background_style=….

See `skills-guides/dashboard-aesthetics.md` for interactive-specific guidance (motion, hover, backgrounds, type-at-screen) and `skills-guides/visual-craftsmanship.md` for the transversal principles (anti-patterns, palette roles, craftsmanship checklist).

## 5. Generation by Format

### 5.1 Document (PDF + DOCX)
If the user selected "Document": see [document-guide.md](document-guide.md) for the complete PDFGenerator, DOCXGenerator pipeline and pitfalls.

### 5.2 Web (Interactive Dashboard)
If the user selected "Web": see [web-guide.md](web-guide.md) for the complete DashboardBuilder pipeline, capabilities, workflow, and pitfalls.

### 5.3 PowerPoint
If the user selected "PowerPoint": see [powerpoint-guide.md](powerpoint-guide.md) for the complete pptx_layout pipeline, slide design, and pitfalls.

### 5.4 Markdown (always generated)
Generated automatically in all analyses, without the user needing to select it.
1. Write .md directly with:
   - Markdown tables for tabular data
   - Mermaid blocks for flow diagrams or relationships
   - References to charts in `output/[ANALYSIS_DIR]/assets/`
2. Save in `output/[ANALYSIS_DIR]/report.md`

## 6. Reasoning

Generate reasoning according to the selected depth (see sec "Reasoning" of AGENTS.md):

- **Quick**: Do not generate file. Key notes in chat.
- **Standard/Deep**: Generate `output/[ANALYSIS_DIR]/reasoning/reasoning.md`. If the user requested override to other formats (PDF, HTML, DOCX), convert with `tools/md_to_report.py --style corporate --lang <user_lang>` (add `--docx` if applicable).

Documenting:
- Format(s) generated and justification
- Structure chosen and why
- Data used and their sources
- Design decisions
- Paths of all generated files

## 7. Delivery

**Before reporting**, run existence verification:
```bash
ls -lh output/[ANALYSIS_DIR]/
```
If any requested file does not appear in the listing → go back to step 5 (generation) and regenerate it. Only report to the user when all files are confirmed on disk.

Then report in chat:
- Format(s) generated
- File path(s)
- Content preview (executive summary)
- Instructions for opening/using the deliverable
