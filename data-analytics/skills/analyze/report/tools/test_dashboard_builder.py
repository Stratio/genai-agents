"""Tests for dashboard_builder.py — DashboardBuilder."""

import json
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ensure tools/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_builder import DashboardBuilder, _escape_html


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def builder():
    """Return a DashboardBuilder with basic config."""
    return DashboardBuilder(
        title="Test Dashboard",
        style="corporate",
        subtitle="Q4 2025",
        author="Test Author",
        domain="Sales",
        date="2025-12-15",
    )


@pytest.fixture
def mock_plotly_fig():
    """Return a mock Plotly figure that produces minimal HTML."""
    fig = MagicMock()
    fig.to_html.return_value = '<div id="chart-test">mock chart</div>'
    return fig


# ---------------------------------------------------------------------------
# Basic build
# ---------------------------------------------------------------------------

class TestBasicBuild:
    def test_build_returns_html_string(self, builder):
        html = builder.build()
        assert "<!DOCTYPE html>" in html
        assert "<title>Test Dashboard</title>" in html

    def test_build_includes_css(self, builder):
        html = builder.build()
        # Should contain assembled CSS from corporate tokens + theme + web target
        assert "var(--primary" in html or "--primary" in html

    def test_build_includes_plotly_cdn(self, builder):
        html = builder.build()
        assert "cdn.plot.ly/plotly-" in html
        assert ".min.js" in html

    def test_build_includes_cover(self, builder):
        html = builder.build()
        assert "cover-page" in html
        assert "Test Dashboard" in html
        assert "Test Author" in html
        assert "Sales" in html

    def test_build_no_cover(self):
        db = DashboardBuilder(title="No Cover", show_cover=False)
        html = db.build()
        # The CSS may contain .cover-page rules, but no actual cover div should be rendered
        assert '<div class="cover-page">' not in html

    def test_build_includes_viewport_meta(self, builder):
        html = builder.build()
        assert 'name="viewport"' in html

    def test_build_includes_author_meta(self, builder):
        html = builder.build()
        assert 'name="author"' in html
        assert "Test Author" in html

    def test_build_default_lang_en(self, builder):
        html = builder.build()
        assert 'lang="en"' in html

    def test_build_custom_lang(self):
        db = DashboardBuilder(title="Test", lang="en")
        html = db.build()
        assert 'lang="en"' in html


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------

class TestFilters:
    def test_add_select_filter(self, builder):
        builder.add_filter("region", "Region", options=["North", "South"])
        html = builder.build()
        assert 'id="filter-region"' in html
        assert "North" in html
        assert "South" in html
        assert 'value="__all__"' in html

    def test_add_date_filter(self, builder):
        builder.add_filter("period", "Period", filter_type="date")
        html = builder.build()
        assert 'type="date"' in html
        assert 'data-filter-role="start"' in html
        assert 'data-filter-role="end"' in html

    def test_no_filters_no_filter_bar(self, builder):
        html = builder.build()
        # CSS may contain .filter-bar rules, but no actual filter bar div should be rendered
        assert 'id="filter-bar"' not in html

    def test_reset_button_present(self, builder):
        builder.add_filter("x", "X", options=["A"])
        html = builder.build()
        assert "resetFilters()" in html
        assert "Clear filters" in html


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------

class TestKPIs:
    def test_add_kpi(self, builder):
        builder.add_kpi("revenue", "Revenue", "1.2M", change=15, prefix="EUR ")
        html = builder.build()
        assert 'data-kpi-id="revenue"' in html
        assert "1.2M" in html
        assert "Revenue" in html
        assert "EUR" in html
        assert "+15%" in html

    def test_kpi_negative_change(self, builder):
        builder.add_kpi("churn", "Churn", "5.2%", change=-8)
        html = builder.build()
        assert "negative" in html
        assert "-8%" in html

    def test_kpi_no_change(self, builder):
        builder.add_kpi("count", "Total", "100")
        html = builder.build()
        assert 'data-kpi-id="count"' in html
        # No change indicator
        assert "kpi-change" not in html.split('data-kpi-id="count"')[1].split("</div>")[3]

    def test_no_kpis_no_section(self, builder):
        html = builder.build()
        assert 'id="kpis"' not in html


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

class TestSections:
    def test_add_chart_section(self, builder, mock_plotly_fig):
        builder.add_chart_section("sales", "Sales", mock_plotly_fig, nav_label="Sales")
        html = builder.build()
        assert 'id="sales"' in html
        assert "mock chart" in html
        assert "chart-container" in html
        mock_plotly_fig.to_html.assert_called_once()

    def test_add_html_section(self, builder):
        builder.add_html_section("notes", "Notes", "<p>Hello</p>", nav_label="Notes")
        html = builder.build()
        assert 'id="notes"' in html
        assert "<p>Hello</p>" in html

    def test_nav_includes_sections(self, builder, mock_plotly_fig):
        builder.add_chart_section("s1", "Section 1", mock_plotly_fig, nav_label="S1")
        builder.add_html_section("s2", "Section 2", "<p>x</p>", nav_label="S2")
        html = builder.build()
        assert 'href="#s1"' in html
        assert 'href="#s2"' in html
        assert ">S1<" in html
        assert ">S2<" in html

    def test_chart_section_description(self, builder, mock_plotly_fig):
        builder.add_chart_section("s", "T", mock_plotly_fig, description="<p>extra</p>")
        html = builder.build()
        assert "<p>extra</p>" in html

    def test_chart_sections_always_full_width(self, builder, mock_plotly_fig):
        """Charts are always full-width — no grid wrapper."""
        builder.add_chart_section("a", "A", mock_plotly_fig)
        builder.add_chart_section("b", "B", mock_plotly_fig)
        html = builder.build()
        assert '<div class="section-grid-2">' not in html

    def test_half_width_html_sections_in_grid(self, builder):
        """Consecutive half-width HTML sections are grouped in a grid."""
        builder.add_html_section("a", "A", "<p>A</p>", width="half")
        builder.add_html_section("b", "B", "<p>B</p>", width="half")
        html = builder.build()
        assert '<div class="section-grid-2">' in html

    def test_full_width_html_no_grid(self, builder):
        builder.add_html_section("a", "A", "<p>A</p>")
        builder.add_html_section("b", "B", "<p>B</p>")
        html = builder.build()
        assert '<div class="section-grid-2">' not in html

    def test_mixed_html_widths(self, builder):
        """Half-width HTML sections followed by full-width: grid closes before full."""
        builder.add_html_section("a", "A", "<p>A</p>", width="half")
        builder.add_html_section("b", "B", "<p>B</p>", width="half")
        builder.add_html_section("c", "C", "<p>C</p>")  # full
        html = builder.build()
        assert '<div class="section-grid-2">' in html
        # The full-width section should NOT be inside the grid
        grid_end = html.index("</div>", html.index("section-grid-2"))
        section_c = html.index('id="c"')
        assert section_c > grid_end

    def test_chart_has_no_width_parameter(self, mock_plotly_fig):
        """add_chart_section does not accept width parameter."""
        db = DashboardBuilder(title="Test")
        # Should raise TypeError for unexpected keyword argument
        with pytest.raises(TypeError):
            db.add_chart_section("x", "X", mock_plotly_fig, width="half")


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

class TestTables:
    def test_add_sortable_table(self, builder):
        builder.add_table(
            "products", "Top Products",
            headers=["Name", "Sales"],
            rows=[["Widget A", "1234"], ["Widget B", "5678"]],
            caption="Top 2 products",
        )
        html = builder.build()
        assert 'id="table-products"' in html
        assert "sortTable(" in html
        assert "Widget A" in html
        assert "Widget B" in html
        assert "sortable-header" in html

    def test_table_custom_sort_value(self, builder):
        builder.add_table(
            "t1", "T",
            headers=["X"],
            rows=[[{"display": "1,234", "sort_value": "1234"}]],
        )
        html = builder.build()
        assert 'data-sort-value="1234"' in html
        assert "1,234" in html

    def test_table_in_nav(self, builder):
        builder.add_table("t1", "My Table", headers=["A"], rows=[["x"]], nav_label="Table")
        html = builder.build()
        assert 'href="#table-t1"' in html
        assert ">Table<" in html


# ---------------------------------------------------------------------------
# Data embedding
# ---------------------------------------------------------------------------

class TestDataEmbedding:
    def test_set_data_embedded_as_json(self, builder):
        data = {"sales": [{"region": "North", "amount": 100}]}
        builder.set_data(data)
        html = builder.build()
        assert "DASHBOARD_DATA" in html
        # Verify the JSON is valid by finding it in the HTML
        assert '"region": "North"' in html or '"region":"North"' in html

    def test_empty_data(self, builder):
        html = builder.build()
        assert "DASHBOARD_DATA" in html
        assert "{}" in html


# ---------------------------------------------------------------------------
# Custom JS
# ---------------------------------------------------------------------------

class TestCustomJS:
    def test_add_custom_js(self, builder):
        builder.add_custom_js("function updateKPIs(f) { console.log(f); }")
        html = builder.build()
        assert "function updateKPIs(f)" in html

    def test_multiple_custom_js(self, builder):
        builder.add_custom_js("var a = 1;")
        builder.add_custom_js("var b = 2;")
        html = builder.build()
        assert "var a = 1;" in html
        assert "var b = 2;" in html


# ---------------------------------------------------------------------------
# JavaScript infrastructure
# ---------------------------------------------------------------------------

class TestJSInfrastructure:
    def test_applyfilters_function(self, builder):
        html = builder.build()
        assert "function applyFilters()" in html

    def test_resetfilters_function(self, builder):
        html = builder.build()
        assert "function resetFilters()" in html

    def test_sorttable_function(self, builder):
        html = builder.build()
        assert "function sortTable(" in html

    def test_updatekpicard_function(self, builder):
        html = builder.build()
        assert "function updateKPICard(" in html

    def test_print_support(self, builder):
        html = builder.build()
        assert "beforeprint" in html
        assert "afterprint" in html

    def test_formatvalue_function(self, builder):
        html = builder.build()
        assert "function formatValue(" in html


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

class TestSave:
    def test_save_creates_file(self, builder, tmp_path):
        out = tmp_path / "test_dashboard.html"
        result = builder.save(out)
        assert result.exists()
        content = result.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content

    def test_save_creates_parent_dirs(self, builder, tmp_path):
        out = tmp_path / "sub" / "dir" / "dashboard.html"
        result = builder.save(out)
        assert result.exists()


# ---------------------------------------------------------------------------
# Escaping
# ---------------------------------------------------------------------------

class TestEscaping:
    def test_escape_html_basic(self):
        assert _escape_html('<script>') == '&lt;script&gt;'
        assert _escape_html('"hello"') == '&quot;hello&quot;'
        assert _escape_html('a & b') == 'a &amp; b'

    def test_title_escaped_in_output(self):
        db = DashboardBuilder(title='Test <script>alert(1)</script>')
        html = db.build()
        assert '<script>alert(1)</script>' not in html
        assert '&lt;script&gt;' in html


# ---------------------------------------------------------------------------
# Style variants
# ---------------------------------------------------------------------------

class TestStyles:
    @pytest.mark.parametrize("style", ["corporate", "modern", "academic"])
    def test_build_with_each_style(self, style):
        db = DashboardBuilder(title="Test", style=style)
        db.add_kpi("k1", "KPI", "100", change=5)
        html = db.build()
        assert "<!DOCTYPE html>" in html

    def test_modern_uses_kpi_grid(self):
        db = DashboardBuilder(title="Test", style="modern")
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        assert "kpi-grid" in html

    def test_corporate_uses_kpi_container(self):
        db = DashboardBuilder(title="Test", style="corporate")
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        assert "kpi-container" in html


class TestAestheticDirection:
    """The optional ``aesthetic_direction`` dict applies palette, type and
    motion overrides on top of the base style. Default behaviour (None)
    must match the legacy rendering."""

    def test_no_aesthetic_direction_leaves_baseline(self):
        db = DashboardBuilder(title="Test", style="corporate")
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        assert "/* === override === */" not in html
        assert "dashboard-rise" not in html
        assert "dashboard-fade-in" not in html

    def test_palette_override_rewrites_primary_token(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"palette_override": {"--primary": "#0a2540"}},
        )
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        assert "/* === override === */" in html
        assert "#0a2540" in html

    def test_font_pair_applies_body_token_and_display_rule(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"font_pair": ["Fraunces", "Inter"]},
        )
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        # Body flows through --font-main override.
        assert "--font-main: 'Inter'" in html
        # Display is emitted as a selector rule, not a token.
        assert "h1, h2, .kpi-value { font-family: 'Fraunces'; }" in html

    def test_motion_expressive_emits_staggered_keyframes_and_reduced_motion(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"motion_budget": "expressive"},
        )
        db.add_kpi("k1", "KPI", "100")
        db.add_kpi("k2", "KPI", "200")
        html = db.build()
        assert "@keyframes dashboard-rise" in html
        assert "animation-delay" in html
        assert "prefers-reduced-motion" in html

    def test_motion_minimal_emits_fade_in_only(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"motion_budget": "minimal"},
        )
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        assert "@keyframes dashboard-fade-in" in html
        assert "dashboard-rise" not in html
        assert "prefers-reduced-motion" in html

    def test_background_gradient_mesh_injects_body_rule(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"background_style": "gradient-mesh"},
        )
        html = db.build()
        assert "radial-gradient" in html

    def test_background_noise_injects_svg_filter(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"background_style": "noise"},
        )
        html = db.build()
        assert "feTurbulence" in html

    def test_motion_none_leaves_no_keyframes(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"motion_budget": "none"},
        )
        db.add_kpi("k1", "KPI", "100")
        html = db.build()
        assert "@keyframes dashboard-fade-in" not in html
        assert "@keyframes dashboard-rise" not in html

    def test_background_solid_is_noop(self):
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"background_style": "solid"},
        )
        html = db.build()
        assert "radial-gradient" not in html
        assert "feTurbulence" not in html

    def test_caller_dict_not_mutated(self):
        """Applying the aesthetic must not leak private state back to the caller."""
        aesthetic = {"font_pair": ["Fraunces", "Inter"]}
        db = DashboardBuilder(
            title="Test", style="corporate", aesthetic_direction=aesthetic,
        )
        db.build()
        assert "_display_font" not in aesthetic, (
            "DashboardBuilder mutated the caller's aesthetic dict"
        )

    def test_noise_preserves_sticky_nav(self):
        """body > *:not(.nav) — the sticky nav selector must be excluded."""
        db = DashboardBuilder(
            title="Test", style="corporate",
            aesthetic_direction={"background_style": "noise"},
        )
        html = db.build()
        assert "body > *:not(.nav)" in html
        assert "body > * { position: relative" not in html
