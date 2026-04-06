# Web Generation Guide (Interactive Dashboard)

Operational reference for the web dashboard pipeline within `/report`.

## Principle

Self-contained HTML (a single file, no server). Inline CSS with `build_css(style, "web")`. Plotly via CDN. Data embedded in JSON for offline operation.

## DashboardBuilder

Use `tools/dashboard_builder.py` (`DashboardBuilder`) to generate interactive dashboards with filters, dynamic KPI cards, and sortable tables:

```python
from dashboard_builder import DashboardBuilder

db = DashboardBuilder(title="Q4 Analysis", style="corporate",
                      subtitle="Period Oct-Dec 2025", author="BI Team",
                      domain="Sales", date="2025-12-15")

# 1. Global filters (dropdowns and/or date range)
db.add_filter("region", "Region", options=["North", "South", "East", "West"])
db.add_filter("period", "Period", filter_type="date")

# 2. KPI cards with % change indicator
db.add_kpi("revenue", "Revenue", "1.2M", change=15, prefix="EUR ")
db.add_kpi("clients", "Active customers", "8,432", change=-3)

# 3. Sections with Plotly charts
fig = px.bar(df, x="region", y="sales")
apply_plotly_layout(fig, insight="North concentrates 45%",
                    context="Sales by region, Q4 2025")
db.add_chart_section("sales-region", "Sales by Region", fig,
                     nav_label="Sales")

# 4. Sortable tables (click-to-sort by column)
db.add_table("top-products", "Top Products",
             headers=["Product", "Sales", "Margin"],
             rows=[["Widget A", {"display": "1,234", "sort_value": "1234"}, "23%"]])

# 5. Free HTML sections (comments, callouts)
db.add_html_section("conclusions", "Conclusions",
                    "<p>Free text with findings...</p>",
                    nav_label="Conclusions")

# 6. Embedded data for offline filtering
db.set_data({"sales": df.to_dict(orient="records")})

# 7. Custom JS for filtering logic (updateKPIs, updateCharts, updateTables)
db.add_custom_js("""
function updateKPIs(filters) {
    var data = DASHBOARD_DATA.sales;
    if (filters.region) data = data.filter(r => r.region === filters.region);
    var total = data.reduce((s, r) => s + r.ventas, 0);
    updateKPICard('revenue', formatValue(total, 'currency'));
}
""")

db.save("output/[ANALYSIS_DIR]/dashboard.html")
```

## Dashboard Capabilities

- **Global filters**: Dropdowns and date range that update KPIs, charts, and tables via `applyFilters()`. The agent defines `updateKPIs(filters)`, `updateCharts(filters)`, and `updateTables(filters)` in custom JS
- **Dynamic KPI cards**: Value + % change with arrow and color indicator (green positive, red negative). Updatable via `updateKPICard(id, value, change)`
- **Sortable tables**: Click on header to sort asc/desc. Support for custom `sort_value` (e.g.: display "1,234" but sort by 1234)
- **Grid layout**: `width="half"` in `add_html_section()` to place HTML content in 2 columns. Consecutive half-width sections are automatically grouped in CSS grid. Plotly charts (`add_chart_section()`) are always full-width so that insight-style titles and the toolbar display correctly
- **Number formatting**: `formatValue(value, format)` available in JS — supports `'currency'` ($1.2M), `'percent'` (45.1%), `'number'` (2.3K). Use it in custom JS to avoid rewriting formatting logic
- **Embedded JSON data**: `DASHBOARD_DATA` available in JS for server-less filtering
- **Print media**: Hides filters and nav, adjusts charts to 700px, prevents page-break within sections
- **Responsive**: Stacked filters on mobile, tables with horizontal scroll

## Generation Workflow

1. Generate script: `output/[ANALYSIS_DIR]/scripts/generate_web.py --style modern`
2. The script imports `DashboardBuilder` and builds the dashboard programmatically
3. Save in `output/[ANALYSIS_DIR]/dashboard.html`

## Common Pitfalls

- `include_plotlyjs=True` duplicates the library (~3MB) if there are multiple charts → `DashboardBuilder` already includes Plotly via CDN in `<head>` and generates charts with `full_html=False`
- Without `<meta name="viewport">` the HTML is not responsive on mobile → `DashboardBuilder` includes it automatically
- Use the styles from `styles/web/base.css` which already have sticky nav, hover, filters, sortable tables, print media, and responsive → `DashboardBuilder` assembles CSS via `build_css(style, "web")`
- Title/legend overlap: NEVER leave the legend in default position when the chart has a title with descriptive text. Use `apply_plotly_layout` from `tools/chart_layout.py` or configure manually: title with `y=0.95`, horizontal legend at bottom with `y=-0.12`, `margin.t=100` and `margin.b=80`
- **Custom JS**: The functions `updateKPIs(filters)`, `updateCharts(filters)`, and `updateTables(filters)` are called automatically when a filter changes. If they are not defined, filters will have no effect — the agent MUST implement them via `add_custom_js()` with the analysis-specific logic
- **Embedded data**: Always call `db.set_data()` with the data needed for filtering. Without embedded data, filters cannot work offline. See `skills-guides/visualization.md` sec 5.5 for size limits and pre-aggregation
- **Grid layout**: Plotly charts are always full-width (they do not accept the `width` parameter). Only `add_html_section()` supports `width="half"` for lightweight HTML content in 2 columns (e.g.: callouts, summary tables, comparative text). Do not use grid for charts — insight-style titles overflow in narrow containers
- **formatValue**: Use `formatValue(value, 'currency')` in custom JS instead of writing manual formatting logic. Supports `'currency'`, `'percent'`, and `'number'` with K/M/B abbreviations
