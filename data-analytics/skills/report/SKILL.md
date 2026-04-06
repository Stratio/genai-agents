---
name: report
description: Professional report generation in multiple formats (PDF, DOCX, interactive web with Plotly, PowerPoint) from data analysis. Use when the user needs to generate reports, dashboards, presentations, or documentation from analyzed data.
argument-hint: '[format: pdf|web|pptx] [topic (optional)]'
---

# Skill: Report Generation

Guide for generating professional reports in multiple formats from data and analyses.

## 1. Determine Format, Structure, and Style

Parse argument: $ARGUMENTS

If the format is not specified, ask the user the following 3 questions in a single interaction, following the question convention (sec "User Interaction" of AGENTS.md) (adaptive to the environment: interactive if available, numbered list in chat if not). Options are literal — do not invent, omit, or substitute:

| # | Question | Options (literal) | Selection |
|---|----------|-------------------|-----------|
| 1 | In what formats do you want the deliverables? | **Document** (PDF + DOCX) · **Web** (Interactive HTML with Plotly) · **PowerPoint** (.pptx) | Multiple |
| 2 | What structure do you prefer for the report? | **Base scaffold** (Recommended): executive summary → methodology → data → analysis → conclusions · **On the fly**: free structure based on context | Single |
| 3 | What visual style do you prefer? | **Corporate** (`corporate.css`, Recommended): clean, professional · **Formal/academic** (`academic.css`): serif, wide margins, paper style · **Modern/creative** (`modern.css`): colors, gradients, visually appealing | Single |

- Question 1 ALWAYS allows multiple selection (the user may want several formats)
- If no format is selected, only a text response is given in chat
- `output/[ANALYSIS_DIR]/report.md` is always generated automatically as internal documentation (no option needed)
- If the format comes from the argument ($ARGUMENTS), skip directly to asking about structure and style (questions 2 and 3)

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
- **Standard/Deep**: Generate `output/[ANALYSIS_DIR]/reasoning/reasoning.md`. If the user requested override to other formats (PDF, HTML, DOCX), convert with `tools/md_to_report.py --style corporate` (add `--docx` if applicable).

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
