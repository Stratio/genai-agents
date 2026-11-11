# Shared Guide: Visualization and Data Storytelling

Principles shared by `/analyze` analytical and deliverable phases. Dashboard-specific composition, filters, sortable tables and performance patterns live in `analytical-dashboard.md` (this skill).

## 1. Chart Type Selection

Choose based on the analytical question:

| Analytical question | Recommended type | Avoid |
|---|---|---|
| Composition (parts of a whole) | Stacked bar, treemap, pie (<=5 categories) | Pie with >5 categories |
| Comparison between categories | Bar chart (horizontal if names are long) | Line chart |
| Temporal trend | Line chart, area chart | Bar chart (unless discrete periods) |
| Distribution | Histogram, box plot, violin | Pie chart |
| Correlation | Scatter plot, heatmap | Bar chart |
| Ranking | Horizontal bar chart sorted | Unsorted table |
| Geographic | Choropleth map | Tables with region codes |
| Highlighted KPIs | Cards with value + % change + sparkline | Numbers in text only |

## 2. Visualization Principles

- Max 5-7 elements per chart (group into "Others" if there are more)
- Always descriptive title + subtitle with period/filter
- Y-axis start at 0 for bars (avoid visual manipulation)
- Colors consistent with the active brand theme — use the `chart_categorical` palette provided by `brand-kit` (see AGENTS.md §8.3), never hardcode
- **Transparency**: For colors with alpha (confidence bands, fill_between, overlapping areas), use `to_rgba(color, alpha)` from `skills/analyze/chart_layout.py`. Accepts hex (`"#1a365d"`) or RGB tuple and returns `"rgba(R,G,B,A)"` compatible with Plotly and matplotlib. **NEVER** concatenate alpha to hex (`"#1a365d80"`) — Plotly rejects it
- Annotations for notable points (peaks, drops, anomalies)
- **Accessibility**: Use colorblind-friendly palettes, do not rely on color alone (use shapes/patterns), alt text on images
- **Headless backend**: Use `matplotlib.use('Agg')` at the start of the script and `bbox_inches='tight'` in `savefig()`. If the image does not render, fallback to SVG
- **Anti-overlap layout**: Title as insight on top, context as subtitle, legend positioned below the chart or to the right exterior. Use `skills/analyze/chart_layout.py` (`apply_chart_layout` / `apply_plotly_layout`) for standard layout. **NEVER** `fig.tight_layout()` after `fig.suptitle()` — use `fig.subplots_adjust()`
- **Figsize for PDF/HTML**: Use `figsize=(7, 4.5)` as maximum for individual charts (A4 printable width ~160mm ~ 6.3"). For 2-column subplots use `figsize=(12, 4.5)`. Writer skills apply their own width containment via their templates — staying within these figsizes keeps the chart legible across PDF, DOCX and HTML.
- **Disparate scales**: Before plotting multiple series on the same axis, check if magnitudes differ by more than 3x. If so, use subplots with independent Y scales instead of a shared axis. For bars with multiple series, use grouped bars (dodge), never overlap with alpha. **Mandatory checklist before plotting series together:**
  1. Calculate `max(series_A) / max(series_B)`. If ratio > 3 → separate subplots with independent Y scales
  2. Calculate variation range of each series (`max - min`). If they differ by more than 10x → grouped bars are misleading (one series looks flat). Separate into subplots or use indices (base 100)
  3. Moving average: only add it if it provides visual information. If the moving average is nearly identical to the original series (small window, smooth series), do NOT add it — it generates overlapping lines that confuse without adding insight
  4. Comparative grouped bars: if values of one category fluctuate 5pp and the other 50pp, the first one's bars look flat. Use separate subplots or normalize both to index

**Mandatory implementation**: Whenever a Python script plots multiple series on the same axis, include the following helper and call it before `px.bar` / `px.line`. If it returns `False`, replace the combined chart with `make_subplots(rows=N, cols=1)` — one series per row — or normalize both series to index base 100 when relative comparison is the focus.

```python
def _compatible_scales(series: dict) -> bool:
    """Return True if series share a comparable scale (single-axis is safe).
    series: {label: pd.Series, ...}
    Thresholds from visualization.md sec 2: max-ratio <= 3, range-ratio <= 10.
    """
    maxs = {k: v.abs().max() for k, v in series.items()}
    ranges = {k: v.max() - v.min() for k, v in series.items()}
    max_ratio = max(maxs.values()) / (min(maxs.values()) + 1e-9)
    range_ratio = max(ranges.values()) / (min(ranges.values()) + 1e-9)
    return max_ratio <= 3 and range_ratio <= 10

# Example: MoM chart with two business segments
# series = {"Comercial": df_com["MoM_Growth"], "Empresas": df_emp["MoM_Growth"]}
# if not _compatible_scales(series):
#     # build make_subplots(rows=2, cols=1) instead of a single px.bar
```

## 3. Data Storytelling

Narrative structure for presenting findings (not just sequential):

1. **Hook**: The most impactful or surprising data point first — capture attention
2. **Context**: Why it matters, what the previous situation or target was
3. **Findings**: From general to specific, each with its "so what"
4. **Tension**: What does not fit, what is surprising, what requires urgent attention
5. **Resolution**: Concrete recommendations with estimated impact

**Principles:**
- Each report section should tell a story, not just show data
- Chart titles as insights ("The North region concentrates 45%"), not descriptions ("Sales by region")
- **Mandatory title-chart verification**: Before finalizing a chart, verify that the visual pattern seen in the chart matches the title's insight. Common errors:
  - Title says "diverging trajectories" but the lines cross multiple times → the actual pattern is crossing volatility, not divergence
  - Title says "stability" but the Y-axis amplifies small variations → adjust scale or reformulate insight
  - Title highlights a pattern from one series but the chart shows another series that visually dominates → rethink the composition
- Numbers always with comparative context (vs previous period, vs target, vs average)
- Do not present data without interpretation — every table or chart needs an explanatory paragraph
- Adapt level of detail and vocabulary to the audience
- **Known anomalies**: If a data point is a confirmed anomaly (e.g.: first month with opening accumulation), exclude it from comparative charts or mark it clearly with annotation + reduced opacity. Do not leave it as a normal point that distorts the visual scale and confuses the reader

## 4. Mapping Analytical Findings → Narrative

Map each finding to its narrative role:

| Finding type | Narrative role | Report placement |
|-------------|---------------|-----------------|
| CRITICAL insight (high impact + high confidence) | **Hook** | Opening — first data point mentioned |
| CONFIRMED hypothesis (expected) | **Context / Findings** | Body — baseline |
| REFUTED hypothesis / anomaly | **Tension** | Unexpected findings |
| High impact + high confidence recommendation | **Resolution** | Closing — call to action |
| Data or analysis limitation | **Caveat** | Methodology or finding footnote |
| INFORMATIONAL finding (low impact) | **Supporting detail** | Appendix |

**Narrative minimum**: Hook + at least 1 Tension + Resolution. If everything confirms expectations, look for the least obvious nuance for the Tension.

## 5. Interactive Dashboard

For dashboard composition, layout, filters, sortable tables, KPI cards and performance patterns, see [analytical-dashboard.md](analytical-dashboard.md). That guide is loaded by `web-craft` when the agent produces an analytical dashboard from `/analyze` Phase 4.

## 6. Charts in the Chat

A chart shown in the conversation (the Chat format, or a chart the user asks for in a reply) is never text. A simple chart is a `chart` block GenAI UI draws as an interactive chart; any other is a PNG.

**Simple chart → `chart` block.** Bar, line, area or pie, with one category or period column and up to ~50 rows: write a fenced block with the language `chart` holding one JSON object, next to the insight it supports:

````
```chart
{"type": "bar", "title": "BAI holds around 80K a month", "x": "month", "y": ["bai"], "data": [{"month": "2023-05", "bai": 81470.07}, {"month": "2023-06", "bai": 79281.40}]}
```
````

- `type`: `bar`, `line`, `area` or `pie`; `title`: the insight (§3), optional
- `x`: the column of the categories or periods (a pie's slices); `y`: the numeric column, or a list of them for several series (a pie draws the first)
- `data`: the rows, each with the `x` column and every `y` column as a number (or `null`). Take the values from the MCP results as they are, never rounded or invented, and order the periods
- Valid JSON only (double quotes, no comments, no trailing commas). A block GenAI UI cannot draw shows as code

**Any other chart → PNG.** Heatmaps, distributions, scatter, maps, subplots, annotations or more rows:

- **Never draw a chart with characters** (`█`, `▇`, `#`, ASCII or Unicode bars, text sparklines in a code block). Nobody can read values off them and GenAI UI cannot show them as a chart. Exact values go in a markdown table instead
- **Draw it as a PNG** with a script, following §2: save it in `output/[ANALYSIS_DIR]/assets/<descriptive_name>.png` with `dpi=150` and `bbox_inches='tight'`
- **Run the script.** A script that draws a chart is not the chart: run it in the same turn, check that the PNG exists and is not empty (`ls -l`), and fix it and run it again if it fails. Never hand over the script alone
- **Name the image in the reply** by its path from the project root, in backticks, next to the insight it supports: `` `output/2026-11-11_1630_monthly_bai/assets/monthly_bai.png` ``. GenAI UI shows every image the reply names inline under the answer. Do not use markdown image syntax (`![...](...)`): the chat cannot resolve a workspace path in it
