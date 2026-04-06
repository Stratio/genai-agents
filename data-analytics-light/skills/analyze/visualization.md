# Guide: Visualization and Data Storytelling

Shared principles for `/analyze`.

## 1. Chart Type Selection

Choose based on the analytical question:

| Analytical question | Recommended type | Avoid |
|---|---|---|
| Composition (parts of a whole) | Stacked bar, treemap, pie (<=5 categories) | Pie with >5 categories |
| Comparison between categories | Bar chart (horizontal if long names) | Line chart |
| Temporal trend | Line chart, area chart | Bar chart (except for discrete periods) |
| Distribution | Histogram, box plot, violin | Pie chart |
| Correlation | Scatter plot, heatmap | Bar chart |
| Ranking | Horizontal bar chart sorted | Unsorted table |
| Geographic | Choropleth map | Tables with region codes |
| Highlighted KPIs | Cards with value + change % + sparkline | Numbers in text only |

## 2. General Principles

- Max 5-7 elements per chart (group into "Others" if there are more)
- Descriptive title as insight + subtitle with period/filter
- Y-axis starts at 0 for bars (avoid visual manipulation)
- Annotations for notable points (peaks, drops, anomalies)
- **Accessibility**: Colorblind-friendly palettes, do not rely solely on color (use shapes/patterns if possible)
- **Disparate scales**: If multiple series differ by more than 3x in magnitude, use subplots with independent Y scales instead of a shared axis

## 3. Data Storytelling

Narrative structure for presenting findings (not just sequential):

1. **Hook**: The most impactful or surprising data point first — capture attention
2. **Context**: Why it matters, what was the prior situation or the target
3. **Findings**: From general to specific, each with its "so what"
4. **Tension**: What doesn't fit, what is surprising, what requires urgent attention
5. **Resolution**: Concrete recommendations with estimated impact

**Principles:**
- Each section of the report should tell a story, not just show data
- Chart titles as insights ("The North region accounts for 45%"), not descriptions ("Sales by region")
- Numbers always with comparative context (vs previous period, vs target, vs average)
- Do not present data without interpretation — every table or chart needs an explanatory paragraph
- Adapt level of detail and vocabulary to the audience

## 4. Mapping Findings to Narrative

Map each finding to its narrative role:

| Finding type | Narrative role | Report location |
|-------------|---------------|-----------------|
| CRITICAL insight (high impact + high confidence) | **Hook** | Opening — first data point mentioned |
| CONFIRMED hypothesis (expected) | **Context / Findings** | Body — baseline |
| REFUTED hypothesis / anomaly | **Tension** | Unexpected findings |
| High impact + high confidence recommendation | **Resolution** | Closing — call to action |
| Data or analysis limitation | **Caveat** | Methodology or finding footnote |
| INFORMATIONAL finding (low impact) | **Supporting detail** | Appendix |

**Narrative minimum**: Hook + at least 1 Tension + Resolution. If everything confirms expectations, look for the least obvious nuance for the Tension.

## 5. Corporate Palette

Use in order of priority:

| Order | Hex | Name | Usage |
|-------|---------|--------|-----|
| 1 | `#1a365d` | Dark blue | Primary — main series, highlighted bars |
| 2 | `#2b6cb0` | Medium blue | Primary light — secondary series |
| 3 | `#3182ce` | Light blue | Accent — trend lines, highlights |
| 4 | `#38a169` | Green | Success — positive values, growth |
| 5 | `#d69e2e` | Amber | Warning — attention values |
| 6 | `#e53e3e` | Red | Danger — negative values, drops |
