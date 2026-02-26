"""Dashboard Builder — Generates self-contained interactive HTML dashboards.

Produces a single HTML file with:
- Global filters (dropdowns, date ranges) that update all charts, KPIs and tables
- Dynamic KPI cards with percentage change indicators
- Sortable tables with click-to-sort
- Plotly charts with CDN (not bundled)
- Embedded JSON data for offline operation
- Responsive CSS + print media support

Usage:
    from dashboard_builder import DashboardBuilder

    db = DashboardBuilder(title="Sales Q4", style="corporate")

    # Add filters
    db.add_filter("region", "Region", options=["Norte", "Sur", "Este", "Oeste"])
    db.add_filter("period", "Periodo", filter_type="date")

    # Add KPIs
    db.add_kpi("revenue", "Ingresos", "1.2M", change=15, prefix="$")
    db.add_kpi("clients", "Clientes activos", "8,432", change=-3)

    # Add a Plotly chart section
    import plotly.express as px
    fig = px.bar(df, x="region", y="ventas")
    db.add_chart_section("ventas-region", "Ventas por Region", fig,
                         nav_label="Ventas")

    # Add a sortable table
    db.add_table("top-products", "Top Productos",
                 headers=["Producto", "Ventas", "Margen"],
                 rows=[["Widget A", {"display": "1,234", "sort_value": "1234"}, "23%"]])

    # Add raw HTML section
    db.add_html_section("commentary", "Comentarios", "<p>Texto libre...</p>",
                        nav_label="Comentarios")

    # Embed data for offline filtering
    db.set_data({"sales": df.to_dict(orient="records")})

    # Build
    db.save("output/dashboard.html")
"""

from __future__ import annotations

import json
from pathlib import Path

from css_builder import build_css


class DashboardBuilder:
    """Builds a self-contained interactive HTML dashboard."""

    def __init__(
        self,
        title: str,
        style: str = "corporate",
        subtitle: str = "",
        author: str = "",
        domain: str = "",
        date: str = "",
        show_cover: bool = True,
        footer: str = "",
        lang: str = "es",
    ) -> None:
        self.title = title
        self.style = style
        self.subtitle = subtitle
        self.author = author
        self.domain = domain
        self.date = date
        self.show_cover = show_cover
        self.footer = footer
        self.lang = lang

        self._filters: list[dict] = []
        self._kpis: list[dict] = []
        self._sections: list[dict] = []  # ordered list of sections
        self._tables: list[dict] = []
        self._data: dict = {}
        self._custom_js: str = ""

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    def add_filter(
        self,
        filter_id: str,
        label: str,
        *,
        filter_type: str = "select",
        options: list[str] | None = None,
    ) -> None:
        """Add a global filter control.

        Args:
            filter_id: Unique identifier (used in JS callbacks).
            label: Display label.
            filter_type: "select" for dropdown, "date" for date range.
            options: List of option values (only for select type).
        """
        self._filters.append({
            "id": filter_id,
            "label": label,
            "type": filter_type,
            "options": options or [],
        })

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------

    def add_kpi(
        self,
        kpi_id: str,
        label: str,
        value: str,
        *,
        change: float | None = None,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        """Add a KPI card.

        Args:
            kpi_id: Unique identifier (used for dynamic updates via JS).
            label: Display label (e.g., "Revenue").
            value: Formatted display value (e.g., "1.2M").
            change: Percentage change (positive/negative). None to hide.
            prefix: Text before value (e.g., "$", "EUR ").
            suffix: Text after value (e.g., "%", " units").
        """
        self._kpis.append({
            "id": kpi_id,
            "label": label,
            "value": value,
            "change": change,
            "prefix": prefix,
            "suffix": suffix,
        })

    # ------------------------------------------------------------------
    # Sections (charts, HTML, tables)
    # ------------------------------------------------------------------

    def add_chart_section(
        self,
        section_id: str,
        title: str,
        plotly_fig,
        *,
        nav_label: str = "",
        description: str = "",
        width: str = "full",
    ) -> None:
        """Add a section containing a Plotly chart.

        Args:
            section_id: Unique section identifier.
            title: Section heading.
            plotly_fig: A plotly Figure object.
            nav_label: Short label for sticky nav. Defaults to title.
            description: Optional HTML text below the chart.
            width: "full" (default), "half" (2 columns) or "third"
                (3 columns). Consecutive sections with the same non-full
                width are grouped in a CSS grid row.
        """
        chart_html = plotly_fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            div_id=f"chart-{section_id}",
            config={"responsive": True},
        )
        self._sections.append({
            "id": section_id,
            "type": "chart",
            "title": title,
            "nav_label": nav_label or title,
            "chart_html": chart_html,
            "description": description,
            "width": width,
        })

    def add_html_section(
        self,
        section_id: str,
        title: str,
        html_content: str,
        *,
        nav_label: str = "",
        width: str = "full",
    ) -> None:
        """Add a section with arbitrary HTML content.

        Args:
            section_id: Unique section identifier.
            title: Section heading.
            html_content: Raw HTML content.
            nav_label: Short label for sticky nav.
            width: "full" (default), "half" (2 columns) or "third"
                (3 columns).
        """
        self._sections.append({
            "id": section_id,
            "type": "html",
            "title": title,
            "nav_label": nav_label or title,
            "html_content": html_content,
            "width": width,
        })

    def add_table(
        self,
        table_id: str,
        title: str,
        headers: list[str],
        rows: list[list],
        *,
        caption: str = "",
        nav_label: str = "",
    ) -> None:
        """Add a sortable table as a section.

        Args:
            table_id: Unique table identifier.
            title: Section heading.
            headers: Column header labels.
            rows: List of row data. Each cell can be a plain value or
                {"display": "1,234", "sort_value": "1234"} for custom sort.
            caption: Optional table caption.
            nav_label: Short label for sticky nav.
        """
        table_data = {
            "id": table_id,
            "title": title,
            "headers": headers,
            "rows": rows,
            "caption": caption,
        }
        self._tables.append(table_data)
        self._sections.append({
            "id": f"table-{table_id}",
            "type": "table",
            "title": title,
            "nav_label": nav_label or title,
            "table": table_data,
        })

    # ------------------------------------------------------------------
    # Data & custom JS
    # ------------------------------------------------------------------

    def set_data(self, data: dict) -> None:
        """Embed data as JSON in the dashboard for offline filtering.

        Args:
            data: Dictionary of datasets. Values should be JSON-serializable
                (e.g., list of dicts from df.to_dict(orient="records")).
        """
        self._data = data

    def add_custom_js(self, js_code: str) -> None:
        """Add custom JavaScript that runs after the dashboard loads.

        Use this to define custom ``updateKPIs(filters)``,
        ``updateCharts(filters)`` and ``updateTables(filters)`` functions
        that respond to filter changes.

        Args:
            js_code: Raw JavaScript code.
        """
        self._custom_js += "\n" + js_code

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self) -> str:
        """Build the complete HTML dashboard string."""
        css, style_name = build_css(self.style, "web")
        data_json = json.dumps(self._data, default=str, ensure_ascii=False)

        # Build sections HTML
        sections_html = self._render_sections(style_name)

        # Build KPIs HTML
        kpis_html = self._render_kpis(style_name) if self._kpis else ""

        # Build filters HTML
        filters_html = self._render_filters() if self._filters else ""

        # Build nav
        nav_html = self._render_nav()

        # Build cover
        cover_html = self._render_cover(style_name) if self.show_cover else ""

        # Assemble
        html = _DASHBOARD_TEMPLATE.format(
            lang=_escape_html(self.lang),
            title=_escape_html(self.title),
            css=css,
            cover=cover_html,
            filters=filters_html,
            nav=nav_html,
            kpis=kpis_html,
            sections=sections_html,
            footer=_escape_html(self.footer or "Dashboard generado automaticamente"),
            data_json=data_json,
            custom_js=self._custom_js,
            author_meta=f'<meta name="author" content="{_escape_html(self.author)}">' if self.author else "",
        )
        return html

    def save(self, path: str | Path) -> Path:
        """Build and save the dashboard to a file.

        Args:
            path: Output file path.

        Returns:
            Resolved Path of the saved file.
        """
        out = Path(path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.build(), encoding="utf-8")
        return out

    # ------------------------------------------------------------------
    # Private renderers
    # ------------------------------------------------------------------

    def _render_cover(self, style_name: str) -> str:
        parts = [f'<div class="cover-page">']
        parts.append(f'  <div class="cover-title">{_escape_html(self.title)}</div>')
        if self.subtitle:
            parts.append(f'  <div class="cover-subtitle">{_escape_html(self.subtitle)}</div>')
        meta_lines = []
        if self.author:
            meta_lines.append(f"<strong>Autor:</strong> {_escape_html(self.author)}")
        if self.domain:
            meta_lines.append(f"<strong>Dominio:</strong> {_escape_html(self.domain)}")
        if self.date:
            meta_lines.append(f"<strong>Fecha:</strong> {_escape_html(self.date)}")
        if meta_lines:
            parts.append('  <div class="cover-meta">')
            for line in meta_lines:
                parts.append(f"    <div>{line}</div>")
            parts.append("  </div>")
        parts.append("</div>")
        return "\n".join(parts)

    def _render_filters(self) -> str:
        parts = ['<div class="filter-bar" id="filter-bar">']
        parts.append('  <div class="filter-bar-title">Filtros</div>')
        parts.append('  <div class="filter-controls">')
        for f in self._filters:
            parts.append(f'    <div class="filter-group">')
            parts.append(f'      <label for="filter-{f["id"]}">{_escape_html(f["label"])}</label>')
            if f["type"] == "select":
                parts.append(f'      <select id="filter-{f["id"]}" class="filter-input" data-filter-id="{f["id"]}" onchange="applyFilters()">')
                parts.append('        <option value="__all__">Todos</option>')
                for opt in f["options"]:
                    parts.append(f'        <option value="{_escape_html(str(opt))}">{_escape_html(str(opt))}</option>')
                parts.append("      </select>")
            elif f["type"] == "date":
                parts.append(f'      <input type="date" id="filter-{f["id"]}-start" class="filter-input filter-date" data-filter-id="{f["id"]}" data-filter-role="start" onchange="applyFilters()">')
                parts.append(f'      <span class="filter-date-sep">&mdash;</span>')
                parts.append(f'      <input type="date" id="filter-{f["id"]}-end" class="filter-input filter-date" data-filter-id="{f["id"]}" data-filter-role="end" onchange="applyFilters()">')
            parts.append("    </div>")
        parts.append('    <button class="filter-reset" onclick="resetFilters()">Limpiar filtros</button>')
        parts.append("  </div>")
        parts.append("</div>")
        return "\n".join(parts)

    def _render_nav(self) -> str:
        if not self._sections:
            return ""
        parts = ['<nav class="nav" id="nav">']
        if self._kpis:
            parts.append('  <a href="#kpis">KPIs</a>')
        for s in self._sections:
            parts.append(f'  <a href="#{s["id"]}">{_escape_html(s["nav_label"])}</a>')
        parts.append("</nav>")
        return "\n".join(parts)

    def _render_kpis(self, style_name: str) -> str:
        container_class = "kpi-grid" if style_name == "modern" else "kpi-container"
        parts = [f'<section id="kpis">', f'<div class="{container_class}" id="kpi-grid">']
        for kpi in self._kpis:
            parts.append(f'  <div class="kpi-card" data-kpi-id="{kpi["id"]}">')
            prefix = _escape_html(kpi.get("prefix", ""))
            suffix = _escape_html(kpi.get("suffix", ""))
            parts.append(f'    <div class="kpi-value">{prefix}{_escape_html(str(kpi["value"]))}{suffix}</div>')
            parts.append(f'    <div class="kpi-label">{_escape_html(kpi["label"])}</div>')
            change = kpi.get("change")
            if change is not None:
                css_class = "positive" if change > 0 else "negative" if change < 0 else ""
                arrow = "\u25b2" if change > 0 else "\u25bc" if change < 0 else ""
                sign = "+" if change > 0 else ""
                parts.append(f'    <div class="kpi-change {css_class}">')
                parts.append(f'      <span class="kpi-change-arrow">{arrow}</span> {sign}{change}%')
                parts.append("    </div>")
            parts.append("  </div>")
        parts.append("</div>")
        parts.append("</section>")
        return "\n".join(parts)

    def _render_sections(self, style_name: str) -> str:
        grid_classes = {"half": "section-grid-2", "third": "section-grid-3"}
        parts = []
        cur_grid: str | None = None
        for idx, s in enumerate(self._sections):
            width = s.get("width", "full")
            grid_cls = grid_classes.get(width)
            next_width = (
                self._sections[idx + 1].get("width", "full")
                if idx + 1 < len(self._sections)
                else "full"
            )
            next_grid_cls = grid_classes.get(next_width)

            # Close current grid if switching to a different grid type
            if cur_grid and grid_cls != cur_grid:
                parts.append("</div>")
                cur_grid = None

            # Open grid wrapper for consecutive non-full sections
            if grid_cls and not cur_grid:
                parts.append(f'<div class="{grid_cls}">')
                cur_grid = grid_cls

            parts.append(f'<section id="{s["id"]}">')
            parts.append(f'  <h2>{_escape_html(s["title"])}</h2>')

            if s["type"] == "chart":
                parts.append(f'  <div class="chart-container">')
                parts.append(f'    {s["chart_html"]}')
                parts.append("  </div>")
                if s.get("description"):
                    parts.append(f'  {s["description"]}')

            elif s["type"] == "html":
                parts.append(f'  {s["html_content"]}')

            elif s["type"] == "table":
                t = s["table"]
                if t.get("caption"):
                    parts.append(f'  <p class="table-caption">{_escape_html(t["caption"])}</p>')
                parts.append('  <div class="table-wrapper">')
                parts.append(f'  <table class="sortable" id="table-{t["id"]}">')
                parts.append("    <thead><tr>")
                for i, header in enumerate(t["headers"]):
                    parts.append(
                        f'      <th onclick="sortTable(\'table-{t["id"]}\', {i})" '
                        f'class="sortable-header" data-sort-dir="none">'
                        f'{_escape_html(str(header))}<span class="sort-icon"></span></th>'
                    )
                parts.append("    </tr></thead>")
                parts.append("    <tbody>")
                for row in t["rows"]:
                    parts.append("      <tr>")
                    for cell in row:
                        if isinstance(cell, dict):
                            parts.append(
                                f'        <td data-sort-value="{_escape_html(str(cell["sort_value"]))}">'
                                f'{_escape_html(str(cell["display"]))}</td>'
                            )
                        else:
                            parts.append(f"        <td>{_escape_html(str(cell))}</td>")
                    parts.append("      </tr>")
                parts.append("    </tbody>")
                parts.append("  </table>")
                parts.append("  </div>")

            parts.append("</section>")

            # Close grid wrapper when next section uses a different width
            if cur_grid and next_grid_cls != cur_grid:
                parts.append("</div>")
                cur_grid = None

        return "\n".join(parts)


# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------

def _escape_html(text: str) -> str:
    """Minimal HTML escaping for attribute and text content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ------------------------------------------------------------------
# HTML template (string-based, no Jinja2 dependency for the builder)
# ------------------------------------------------------------------

_DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {author_meta}
    <title>{title}</title>
    <style>
{css}
    </style>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>

{cover}

{filters}

{nav}

{kpis}

{sections}

<div class="footer">
    <p>{footer}</p>
</div>

<script>
// ============================================================
// Dashboard data store — all data embedded as JSON for offline use
// ============================================================
var DASHBOARD_DATA = {data_json};

// ============================================================
// Number formatting helper
// ============================================================
function formatValue(value, format) {{
    if (value == null || isNaN(value)) return '—';
    switch (format) {{
        case 'currency':
            if (Math.abs(value) >= 1e9) return (value / 1e9).toFixed(1) + 'B';
            if (Math.abs(value) >= 1e6) return (value / 1e6).toFixed(1) + 'M';
            if (Math.abs(value) >= 1e3) return (value / 1e3).toFixed(1) + 'K';
            return value.toFixed(0);
        case 'percent':
            return value.toFixed(1) + '%';
        case 'number':
            if (Math.abs(value) >= 1e9) return (value / 1e9).toFixed(1) + 'B';
            if (Math.abs(value) >= 1e6) return (value / 1e6).toFixed(1) + 'M';
            if (Math.abs(value) >= 1e3) return (value / 1e3).toFixed(1) + 'K';
            return value.toLocaleString();
        default:
            return String(value);
    }}
}}

// ============================================================
// Filter logic
// ============================================================
function getActiveFilters() {{
    var filters = {{}};
    document.querySelectorAll('.filter-input').forEach(function(el) {{
        var id = el.dataset.filterId;
        if (el.tagName === 'SELECT') {{
            if (el.value !== '__all__') filters[id] = el.value;
        }} else if (el.type === 'date' && el.value) {{
            var role = el.dataset.filterRole;
            if (!filters[id]) filters[id] = {{}};
            filters[id][role] = el.value;
        }}
    }});
    return filters;
}}

function applyFilters() {{
    var filters = getActiveFilters();
    if (typeof updateKPIs === 'function') updateKPIs(filters);
    if (typeof updateCharts === 'function') updateCharts(filters);
    if (typeof updateTables === 'function') updateTables(filters);
    document.dispatchEvent(new CustomEvent('dashboard:filter', {{ detail: filters }}));
}}

function resetFilters() {{
    document.querySelectorAll('.filter-input').forEach(function(el) {{
        if (el.tagName === 'SELECT') el.value = '__all__';
        else if (el.type === 'date') el.value = '';
    }});
    applyFilters();
}}

// ============================================================
// Sortable tables
// ============================================================
function sortTable(tableId, colIndex) {{
    var table = document.getElementById(tableId);
    if (!table) return;
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    var th = table.querySelectorAll('thead th')[colIndex];

    var currentDir = th.dataset.sortDir || 'none';
    var newDir = currentDir === 'asc' ? 'desc' : 'asc';

    table.querySelectorAll('thead th').forEach(function(h) {{
        h.dataset.sortDir = 'none';
        h.classList.remove('sort-asc', 'sort-desc');
    }});
    th.dataset.sortDir = newDir;
    th.classList.add('sort-' + newDir);

    rows.sort(function(a, b) {{
        var aVal = a.cells[colIndex].dataset.sortValue || a.cells[colIndex].textContent.trim();
        var bVal = b.cells[colIndex].dataset.sortValue || b.cells[colIndex].textContent.trim();

        var aNum = parseFloat(aVal.replace(/[^0-9.\\-]/g, ''));
        var bNum = parseFloat(bVal.replace(/[^0-9.\\-]/g, ''));
        if (!isNaN(aNum) && !isNaN(bNum)) {{
            return newDir === 'asc' ? aNum - bNum : bNum - aNum;
        }}

        return newDir === 'asc'
            ? aVal.localeCompare(bVal, undefined, {{ numeric: true }})
            : bVal.localeCompare(aVal, undefined, {{ numeric: true }});
    }});

    rows.forEach(function(row) {{ tbody.appendChild(row); }});
}}

// ============================================================
// KPI update helper
// ============================================================
function updateKPICard(id, value, change) {{
    var card = document.querySelector('[data-kpi-id="' + id + '"]');
    if (!card) return;
    var valEl = card.querySelector('.kpi-value');
    var changeEl = card.querySelector('.kpi-change');
    if (valEl) valEl.textContent = value;
    if (changeEl && change !== undefined) {{
        var prefix = change > 0 ? '+' : '';
        changeEl.textContent = prefix + change + '%';
        changeEl.className = 'kpi-change ' + (change > 0 ? 'positive' : change < 0 ? 'negative' : '');
    }}
}}

// ============================================================
// Print support
// ============================================================
window.addEventListener('beforeprint', function() {{
    document.querySelectorAll('.js-plotly-plot').forEach(function(plot) {{
        Plotly.relayout(plot, {{ width: 700, height: 400 }});
    }});
}});
window.addEventListener('afterprint', function() {{
    document.querySelectorAll('.js-plotly-plot').forEach(function(plot) {{
        Plotly.relayout(plot, {{ width: null, height: null, autosize: true }});
    }});
}});

// ============================================================
// Custom JS (user-defined filter handlers, etc.)
// ============================================================
{custom_js}
</script>

</body>
</html>"""
