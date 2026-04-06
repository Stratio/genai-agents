# Shared Guide: Visualization and Data Storytelling

Principles shared by `/analyze` and `/report`.

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
- Colors consistent with the chosen theme (via `get_palette()`, never hardcode)
- **Transparency**: For colors with alpha (confidence bands, fill_between, overlapping areas), use `to_rgba(color, alpha)` from `tools/chart_layout.py`. Accepts hex (`"#1a365d"`) or RGB tuple and returns `"rgba(R,G,B,A)"` compatible with Plotly and matplotlib. **NEVER** concatenate alpha to hex (`"#1a365d80"`) — Plotly rejects it
- Annotations for notable points (peaks, drops, anomalies)
- **Accessibility**: Use colorblind-friendly palettes, do not rely on color alone (use shapes/patterns), alt text on images
- **Headless backend**: Use `matplotlib.use('Agg')` at the start of the script and `bbox_inches='tight'` in `savefig()`. If the image does not render, fallback to SVG
- **Anti-overlap layout**: Title as insight on top, context as subtitle, legend positioned below the chart or to the right exterior. Use `tools/chart_layout.py` (`apply_chart_layout` / `apply_plotly_layout`) for standard layout. **NEVER** `fig.tight_layout()` after `fig.suptitle()` — use `fig.subplots_adjust()`
- **Figsize for PDF/HTML**: Use `figsize=(7, 4.5)` as maximum for individual charts (the printable area of A4 with default margins is ~160mm ~ 6.3"). For 2-column subplots use `figsize=(12, 4.5)`. Exceeding these dimensions causes overflow in WeasyPrint because `md_to_report.py` converts `![alt](img.png)` to `<p><img>` (not `<figure>`), without width containment CSS.
- **Disparate scales**: Before plotting multiple series on the same axis, check if magnitudes differ by more than 3x. If so, use subplots with independent Y scales instead of a shared axis. For bars with multiple series, use grouped bars (dodge), never overlap with alpha. **Mandatory checklist before plotting series together:**
  1. Calculate `max(series_A) / max(series_B)`. If ratio > 3 → separate subplots with independent Y scales
  2. Calculate variation range of each series (`max - min`). If they differ by more than 10x → grouped bars are misleading (one series looks flat). Separate into subplots or use indices (base 100)
  3. Moving average: only add it if it provides visual information. If the moving average is nearly identical to the original series (small window, smooth series), do NOT add it — it generates overlapping lines that confuse without adding insight
  4. Comparative grouped bars: if values of one category fluctuate 5pp and the other 50pp, the first one's bars look flat. Use separate subplots or normalize both to index

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

Principles for composing web dashboards with `tools/dashboard_builder.py` (`DashboardBuilder`).

### 5.1 When to use dashboard vs standalone charts

| Situation | Recommended format |
|-----------|-------------------|
| The user needs to explore data across different dimensions (region, period, segment) | **Dashboard with filters** |
| Executive audience: KPI summary + 2-3 key charts | **Simple dashboard** (KPIs + charts, no filters or 1 filter) |
| Formal report with extensive narrative and methodology | **PDF/DOCX** (not dashboard) |
| Point findings without needed interactivity | **Standalone charts** in chat or report |

### 5.2 Dashboard layout

Recommended section order (top to bottom):

1. **Cover** (optional) — title, subtitle, author, domain, date
2. **Global filters** — only those relevant to the analysis (see 5.3)
3. **KPI cards** — 3-6 key metrics with % change vs previous period
4. **Main charts** — the most important findings first (Hook)
5. **Detail charts** — breakdown and context (Findings)
6. **Sortable tables** — support data for manual drill-down
7. **Conclusions** (HTML section) — summary and recommendations

**Layout principles:**
- Max 6 KPI cards — more than 6 dilutes attention. Prioritize by business impact
- Alternate charts and text — do not stack 5 charts in a row without interpretation
- Each section with a short `nav_label` (max 2-3 words) for the sticky nav
- **Multi-column grid**: Use `width="half"` in `add_html_section()` to place comparative HTML content side by side (2 columns). Consecutive half-width sections are grouped automatically. On mobile they collapse to 1 column. **Plotly charts are always full-width** — insight-style titles and the Plotly toolbar need full width to display correctly

### 5.3 Filters: when and which

| Data type | Recommended filter | Example |
|----------|-------------------|---------|
| Categorical dimension with <=15 values | **Dropdown** (`filter_type="select"`) | Region, Segment, Channel |
| Temporal dimension | **Date range** (`filter_type="date"`) | Analysis period |
| Categorical dimension with >15 values | Do not use filter — aggregate into "Others" or use sortable table | SKUs, postal codes |
| Continuous metric | Do not use filter — use interactive chart (Plotly zoom/hover) | Amount, quantity |

**Rules:**
- Max 3-4 filters — more than 4 overwhelms the user and complicates custom JS
- Each filter must affect at least 2 dashboard sections (if it only affects 1, make it a local control for that section)
- Always include "All" as the default option in dropdowns
- If there is a date filter, populate `start`/`end` with the actual data range

### 5.4 Sortable tables vs charts

| Use sortable table when... | Use chart when... |
|---------------------------|------------------|
| The user needs to look up specific values (e.g.: "how much did product X sell") | The question is about patterns (trend, concentration, distribution) |
| There are >7 dimensions to compare | There are <=7 categories to compare visually |
| Data has important precision (decimals, exact dates) | Orders of magnitude matter more than exact values |
| It is a reference/support detail table | It is a key analysis finding |

**Tip**: Use custom `sort_value` for formatted columns (e.g.: display "1,234 EUR" but sort by `1234`). This allows the table to be both readable and functional.

### 5.5 Dashboard performance

#### Embedded data size

| Dataset size | Strategy | Example |
|-------------|----------|---------|
| <1,000 rows | Embed directly with `set_data()` | Monthly sales by region (12 months x 5 regions = 60 rows) |
| 1,000-10,000 rows | Pre-aggregate in pandas before embedding. Embed only the aggregations needed for KPIs, charts, and tables | Daily transactions for a year → aggregate to weekly by segment |
| >10,000 rows | Aggregate in MCP (`query_data`). Embed only the summary. Never bring transactional detail to the dashboard | Millions of transactions → top 20 products, monthly trend, global KPIs |

**Rule**: The JSON embedded in `DASHBOARD_DATA` should not exceed ~500 KB. More than that slows initial HTML loading.

#### Limits per component

| Component | Recommended limit | If exceeded |
|-----------|------------------|-------------|
| Line chart | <500 points per series | Downsample: aggregate to coarser granularity (daily → weekly) |
| Bar chart | <50 categories | Group into "Others" or use top-N + "Rest" |
| Sortable table | <200 rows | Show top-N with note "showing the top N". For full detail, export CSV |
| KPI cards | 3-6 | Prioritize by business impact (already covered in 5.2) |
| Filters | 3-4 | Already covered in 5.3 |

#### Pre-aggregation in pandas

Before calling `set_data()`, aggregate data to the level needed for each dashboard component:

```python
# NO: embed 50,000 transactions
db.set_data({"transactions": df.to_dict(orient="records")})  # ~5 MB

# YES: pre-aggregate for each component
data = {
    "monthly": df.groupby("month").agg({"revenue": "sum", "orders": "count"}).reset_index().to_dict(orient="records"),
    "by_region": df.groupby("region").agg({"revenue": "sum"}).reset_index().to_dict(orient="records"),
    "top_products": df.groupby("product").agg({"revenue": "sum"}).nlargest(20, "revenue").reset_index().to_dict(orient="records"),
}
db.set_data(data)  # ~2 KB
```
