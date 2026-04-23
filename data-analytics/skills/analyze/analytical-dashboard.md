# Analytical Dashboard — Guide

Guide consumed by `web-craft` when the agent asks it to build an interactive dashboard as the deliverable of an analytical flow (loaded from `/analyze` Phase 4 when the user selected **Dashboard web** as one of the formats in §4.1).

This guide captures the conventions that make an analytical dashboard recognisable: KPI cards up top, global filters that cascade over everything, sortable support tables, Plotly charts with insight-titles, and a composition that reads as analysis rather than as marketing. `web-craft` still applies its own five decisions (tone / type pairing / palette / motion budget / composition) on top of this guide — the tokens come from the centralized theming skill selected in the plan; this guide contributes the **analytical patterns**.

## 1. When to apply this guide

Apply silently when the agent calls `web-craft` from `/analyze` Phase 4 with a Dashboard web deliverable AND the user has not signalled design freedom. Skip entirely when the user's brief contains phrases like:

- "rompe el molde", "dashboard creativo", "experimental", "narrativo", "más libre"
- "algo diferente", "fuera del patrón habitual", "dashboard personalizado"

In those cases `web-craft` operates with its own five decisions from scratch, producing a dashboard that is still valid but without the standard analytical layout.

## 2. Layout — 2 columns, top-down

Recommended section order:

1. **Cover (optional)** — title, subtitle, author, domain, date.
2. **Sticky navigation** — one `nav_label` per section (max 2-3 words each).
3. **Global filters** — dropdowns and date ranges (see §3).
4. **KPI cards** — 3 to 6 key metrics with change vs previous period (see §4).
5. **Main charts** — the most impactful findings first (Hook). Always full-width.
6. **Detail charts** — breakdown and context (Findings). Can be half-width via HTML grid.
7. **Sortable tables** — for manual drill-down (see §5).
8. **Conclusions** — free HTML section with summary and recommendations.

Principles:

- Max **6 KPI cards** — more dilutes attention. Prioritise by business impact.
- Alternate charts and text — do not stack 5 charts in a row without interpretation.
- Plotly charts are **always full-width**: insight-style titles and the toolbar need the space.
- Consecutive HTML sections with `width="half"` group into a 2-column grid; stack on mobile.

## 3. Global filters — when and which

| Data type | Filter | Example |
|---|---|---|
| Categorical dimension with ≤15 values | Dropdown (`<select>`) | Region, Segment, Channel |
| Temporal dimension | Date range (two `<input type="date">`) | Analysis period |
| Categorical dimension with >15 values | No filter — aggregate into "Others" or use sortable table | SKUs, postal codes |
| Continuous metric | No filter — rely on Plotly interactivity (zoom, hover) | Amount, quantity |

Rules:

- **Max 3-4 filters**. More overwhelms the user and complicates the custom JS.
- Each filter must affect **at least 2 sections** (KPIs + charts or tables). If it only affects one, make it a local control in that section.
- Always include an "All" / "Todos" option as default in dropdowns.
- If a date filter exists, populate `start`/`end` with the actual data range.

Implementation pattern (vanilla JS — no framework):

```html
<div class="filters">
  <select data-filter="region">
    <option value="">All regions</option>
    <option value="north">North</option>
    ...
  </select>
  <input type="date" data-filter="from" value="2025-01-01">
  <input type="date" data-filter="until" value="2025-12-31">
</div>

<script>
const filters = {};
document.querySelectorAll('[data-filter]').forEach(el => {
  el.addEventListener('change', () => {
    filters[el.dataset.filter] = el.value;
    applyFilters(filters);
  });
});

function applyFilters(f) {
  updateKPIs(f);
  updateCharts(f);
  updateTables(f);
}
</script>
```

The agent is responsible for implementing `updateKPIs()`, `updateCharts()`, `updateTables()` with the analysis-specific logic. Without them, filters have no effect.

**Data contract** — your HTML must embed the pre-aggregated slices as a global `DASHBOARD_DATA` object; the filter callbacks read from it and re-render. Example pattern (structure of the code your HTML contains — visual styling is web-craft's call):

```javascript
const DASHBOARD_DATA = {
  sales_by_region: [
    {region: 'north', month: '2025-01', revenue: 420000, orders: 1200},
    {region: 'south', month: '2025-01', revenue: 310000, orders: 980},
    // ...
  ],
  top_products: [ /* ... */ ],
};

function updateKPIs(f) {
  let rows = DASHBOARD_DATA.sales_by_region;
  if (f.region) rows = rows.filter(r => r.region === f.region);
  if (f.from)   rows = rows.filter(r => r.month >= f.from);
  if (f.until)  rows = rows.filter(r => r.month <= f.until);
  const total = rows.reduce((s, r) => s + r.revenue, 0);
  document.querySelector('[data-kpi="revenue"] .kpi-value').textContent = formatValue(total, 'currency');
}
```

`updateCharts()` and `updateTables()` follow the same pattern: read from `DASHBOARD_DATA`, filter, re-render. `web-craft` decides the exact CSS, transitions and microcopy — the contract here is purely about data flow.

## 4. KPI cards

Each KPI card contains:

- **Label** (one short line).
- **Value** (current period, formatted with locale-aware number format: `1,234` / `1.234` / `1.2M` / `1.2K`).
- **Change vs previous period**: arrow (↑ / ↓), percentage, color (positive = `state_ok`, negative = `state_danger`, neutral = muted).
- Optional: small sparkline (minimal SVG or CSS bars, no chart library) showing last N periods.

HTML/CSS pattern:

```html
<div class="kpi-card">
  <div class="kpi-label">Revenue</div>
  <div class="kpi-value">€ 1.2M</div>
  <div class="kpi-change positive">↑ 15% vs Q3</div>
</div>
```

```css
.kpi-card {
  background: var(--bg-alt);
  border-left: 4px solid var(--primary);
  padding: 1.5rem;
  border-radius: 4px;
}
.kpi-value { font-family: var(--font-display); font-size: 2rem; }
.kpi-change.positive { color: var(--state-ok); }
.kpi-change.negative { color: var(--state-danger); }
```

Number formatting helper (vanilla, locale-aware). Currency is configurable so USD, GBP, MXN, etc. are one argument away:

```javascript
function formatValue(v, kind, opts = {}) {
  const lang = document.documentElement.lang;
  if (kind === 'currency') return new Intl.NumberFormat(lang, {style:'currency', currency: opts.currency || 'EUR', notation:'compact'}).format(v);
  if (kind === 'percent')  return new Intl.NumberFormat(lang, {style:'percent', maximumFractionDigits:1}).format(v);
  return new Intl.NumberFormat(lang, {notation:'compact'}).format(v);
}

// Usage: formatValue(1234000, 'currency', {currency: 'USD'}) → "$1.2M"
//        formatValue(0.127, 'percent')                       → "12,7 %" (es) / "12.7%" (en)
```

When the KPI needs a non-currency prefix/suffix (e.g. "× 1.2M transactions", "1,234 kg CO₂"), prepend/append the unit in the rendered HTML alongside the formatted number rather than overloading `formatValue`.

## 5. Sortable tables

For reference / drill-down data. Click on a `<th>` reorders the column.

```html
<table class="sortable" data-rows="top-products">
  <thead>
    <tr>
      <th data-sort="text">Product</th>
      <th data-sort="number">Sales</th>
      <th data-sort="percent">Margin</th>
    </tr>
  </thead>
  <tbody id="tbody-top-products"></tbody>
</table>
```

- `data-sort` attribute declares the column type (`text`, `number`, `date`, `percent`).
- Numbers shown formatted (e.g. `"1,234"`) but sorted by raw value — either use a hidden `data-value` on each `<td>` or store raw numbers in `DASHBOARD_DATA` and render on demand.
- Default: no sort. Click asc, click again desc.
- Use sortable tables when the user needs exact values or >7 dimensions. Use charts when the question is about patterns (trend, concentration).

## 6. Charts — Plotly with insight titles

Plotly via CDN (single `<script src="https://cdn.plot.ly/plotly-2.x.min.js">` in `<head>`). Figures embedded as JSON in `DASHBOARD_DATA`, rendered on `DOMContentLoaded` with `Plotly.newPlot()`.

Anti-overlap rules (non-negotiable):

- Title as **insight** ("North concentrates 45%"), not description ("Sales by region").
- Context as subtitle below the title ("Q4 2025, by region").
- Legend **outside the plot area**: bottom for few series, right-outside for many.
- Never `fig.tight_layout()` after `fig.suptitle()` in matplotlib-generated charts — use `fig.subplots_adjust()`. See `chart_layout.py` for the helper.
- `figsize=(7, 4.5)` max for single charts; `figsize=(12, 4.5)` for 2-column subplots. Larger overflows the printable area when writer skills include the chart in a PDF.

Colors: pull the `chart_categorical` palette from the brand tokens (§8). Apply via Plotly `layout.colorway`:

```javascript
Plotly.newPlot(el, data, {
  ...layoutConfig,
  colorway: BRAND_TOKENS.chart_categorical  // array of 5-8 hex strings
});
```

## 7. Performance — embedded data budget

The JSON embedded in `DASHBOARD_DATA` should **not exceed ~500 KB**. Beyond that, initial HTML load feels sluggish.

| Dataset size | Strategy |
|---|---|
| <1,000 rows | Embed directly |
| 1,000-10,000 rows | Pre-aggregate in pandas before embedding. Keep only what KPIs, charts and tables need |
| >10,000 rows | Aggregate in MCP via `query_data`. Embed only summaries. Never ship transactional detail |

Per-component limits:

- Line chart: <500 points per series → downsample to coarser granularity.
- Bar chart: <50 categories → top-N + "Others".
- Sortable table: <200 rows → "showing top N; full detail in CSV export".

Pre-aggregation example (pandas):

```python
# Bad: 50,000 transactions (~5 MB)
data = {"transactions": df.to_dict(orient="records")}

# Good: pre-aggregated slices (~2 KB)
data = {
  "monthly": df.groupby("month").agg(revenue=("amount","sum"), orders=("id","count")).reset_index().to_dict(orient="records"),
  "by_region": df.groupby("region").agg(revenue=("amount","sum")).reset_index().to_dict(orient="records"),
  "top_products": df.groupby("product").agg(revenue=("amount","sum")).nlargest(20, "revenue").reset_index().to_dict(orient="records"),
}
```

## 8. Brand tokens integration

The theme fixed in the plan (see agent instructions §8.3) produces a token bundle. The dashboard consumes it in two places:

**CSS custom properties in `:root`**:

```css
:root {
  --primary: #0a2540;
  --accent:  #d9472b;
  --text:    #1f2937;
  --muted:   #6b7280;
  --rule:    #d1d5db;
  --bg:      #ffffff;
  --bg-alt:  #f3f4f6;
  --state-ok:     #047857;
  --state-warn:   #b45309;
  --state-danger: #b91c1c;
  --font-display: 'Fraunces', Georgia, serif;
  --font-body:    'Inter', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', Consolas, monospace;
}
```

**Plotly `layout.colorway`**: use `chart_categorical` from the token bundle (5-8 ordered hex colors). Keeps charts in conversation with the rest of the artifact.

If the theme declares optional extensions (`motion_budget`, `radius`, `dark_mode`, `chart_sequential`), honour them. `motion_budget` controls the transition CSS; `dark_mode` enables `@media (prefers-color-scheme: dark)`; `chart_sequential` is for heatmaps.

## 9. Motion

CSS-only, no JS. Use keyframes prefixed `dashboard-*` to avoid collisions. Honour `prefers-reduced-motion: reduce` by cancelling animations.

| Budget (from brand tokens) | Effect |
|---|---|
| `none` | No extra motion. Static dashboards, printouts, contexts where motion distracts |
| `minimal` (default) | 320 ms `dashboard-fade-in` on KPI cards and sections on initial mount |
| `expressive` | Staggered `dashboard-rise` on KPI cards (80 ms per card), section reveal, card hover lift |

Keep page-load motion under ~500 ms total. Plotly runs its own chart animations — do not attach CSS animations to `.js-plotly-plot` descendants.

```css
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}

@keyframes dashboard-fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: none; }
}
.kpi-card { animation: dashboard-fade-in 320ms ease-out both; }
```

## 10. Hover and focus states

Every interactive element (filter, sort handle, nav link, KPI card when clickable) needs deliberate hover and focus:

- **Hover**: 1-2 px translate up or 180 ms shadow expansion. Colour-only hover reads as accidental.
- **Focus**: outline in `--primary`, visible on keyboard nav (`:focus-visible`).
- **Active**: depressed state — baseline translate, slightly darker surface.

## 11. Backgrounds

Optional (only if the brand theme declares a `background_style` extension):

- `solid` — base surface wins. Default.
- `gradient-mesh` — layered radial gradients tinted by the accent. Good for editorial dashboards.
- `noise` — static SVG noise behind content. Good for maximalist or brutalist tones. Avoid on dense tables — lowers contrast.
- `grain` — fine dotted pattern at 3 px pitch. Good for analog or editorial tones.

All rendered inline, no external assets.

## 12. Language and accessibility

- Set `<html lang="<user_lang>">` matching the language the agent is conversing in (passed by the agent as `lang=<code>`).
- UI chrome strings ("Filters", "KPIs", "Clear filters", "Sort", column headers, dropdown "All") must be in the user's language. Do not hardcode English.
- Colorblind-friendly palettes (the brand theme's `chart_categorical` is already curated; do not substitute unless the user explicitly overrides).
- Do not rely on color alone — use icons, labels, or patterns for state (OK / warn / danger).
- Alt text on any chart rasterised to image.
- Keyboard navigation for all interactive elements (filters, sortable tables, nav links).

**Labels pattern** — your HTML must include a `LABELS` object with the UI strings translated to the user's language. The chrome renders those strings literally from this object. Example:

```javascript
const LABELS = {
  filters_title: "Filtros",
  filter_all:    "Todos",
  clear_filters: "Limpiar",
  kpis_section:  "Indicadores clave",
  sort_asc:      "Orden ascendente",
  sort_desc:     "Orden descendente",
  // ...one entry per UI string the dashboard shows
};
```

Keep the keys language-neutral; the values are translated. If a key is missing, fall back to the English default — do not leave a `{{placeholder}}` visible.

## 13. Responsive

Breakpoint at `768px`:

- Below: all sections stack vertically. `width="half"` collapses to full. Tables get `overflow-x: auto`.
- Above: two-column grid for `width="half"` HTML sections; filters row horizontal.

Sticky nav sits at the top; hide on mobile if it competes with filters.

## 14. Charts that live alongside: `chart_layout.py`

The local helper `skills/analyze/chart_layout.py` provides `apply_plotly_layout()`, `apply_chart_layout()` (matplotlib) and `to_rgba()` to keep titles / subtitles / legends from overlapping. Use it for any chart exported as PNG (Plotly or matplotlib) before the dashboard embeds it. Plotly figures embedded directly (as JSON) can use `apply_plotly_layout()` on the figure before serialisation.

## 15. Analytical pitfalls to avoid

These are failure modes specific to the analytical-dashboard domain — the generic web pitfalls (viewport meta, font-display, hover states) are already handled by the web-craft discipline, don't repeat them here.

- **Plotly bundle duplication** — when embedding multiple Plotly figures, load Plotly ONCE via a `<script src="https://cdn.plot.ly/plotly-2.x.min.js">` in `<head>` and render every figure with `Plotly.newPlot(el, data, layout)`. Never export each figure with `include_plotlyjs=True` / `full_html=True`: each copy ships ~3 MB, three charts becomes a 9 MB HTML.
- **Title / legend overlap on Plotly** — insight-style titles are longer than default titles. Use `apply_plotly_layout()` from `chart_layout.py`, which reserves space by setting `title.y = 0.95`, legend below the plot area (`y = -0.12`), and margins `t=100, b=80, l=60, r=40`. Never leave the default legend position when the chart has an insight title.
- **Filters that do nothing** — every global filter must trigger `updateKPIs(filters)`, `updateCharts(filters)` and `updateTables(filters)`. If any of those three is missing, the filter visually changes but the dashboard doesn't react. Define all three even if one of them is a no-op.
- **Missing `DASHBOARD_DATA`** — filters run in the browser; the data they filter must be embedded. If the agent forgets to set `DASHBOARD_DATA` before the scripts run, the filters throw and the dashboard silently breaks. Embed the pre-aggregated slices as inline JSON before the scripts that read them.
- **Plotly in half-width grid** — the 2-column grid (`width="half"`) is for HTML sections only (callouts, summary cards, comparative text). Plotly charts always take full width because insight titles and the chart toolbar need the space. Trying to render a Plotly chart in a half-width column truncates the title or the toolbar.

## 16. What this guide does NOT dictate

`web-craft` keeps control of these decisions:

- Specific tone (editorial-serious, technical-minimal, etc.) — comes from the theme.
- Exact typography — comes from `font_pair` in the theme.
- Exact accent / neutral values — come from the theme.
- The micro-composition of individual sections (card inner layout, chart framing, conclusion styling) — `web-craft` designs these per its five-decisions workflow, coherent with the theme.

This guide constrains the **analytical contract** (what a dashboard from `/analyze` contains and how it behaves); `web-craft` provides the **visual voice**.
