"""Tests for chart_layout.py — verify anti-overlap layout helpers."""

import sys
from pathlib import Path
import pytest

# Ensure tools/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mpl_fig_ax():
    """Create a matplotlib figure with a simple line plot + legend."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6], label="Series A")
    ax.plot([1, 2, 3], [6, 5, 4], label="Series B")
    yield fig, ax
    plt.close(fig)


@pytest.fixture
def mpl_fig_ax_no_legend():
    """Create a matplotlib figure without legend labels."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    yield fig, ax
    plt.close(fig)


@pytest.fixture
def mpl_fig_subplots():
    """Create a matplotlib figure with multiple subplots."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar([1, 2, 3], [4, 5, 6], label="Bar A")
    axes[1].plot([1, 2, 3], [7, 8, 9], label="Line B")
    yield fig, axes
    plt.close(fig)


@pytest.fixture
def plotly_fig():
    """Create a simple Plotly bar figure."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Bar(x=["A", "B", "C"], y=[10, 20, 15], name="Sales"))
    fig.add_trace(go.Bar(x=["A", "B", "C"], y=[8, 18, 12], name="Costs"))
    return fig


# ---------------------------------------------------------------------------
# Tests: apply_chart_layout (matplotlib)
# ---------------------------------------------------------------------------

class TestApplyChartLayout:
    def test_sets_suptitle(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="North accounts for 45%", context="Q4 2025")

        assert fig._suptitle is not None
        assert fig._suptitle.get_text() == "North accounts for 45%"

    def test_sets_subtitle(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="Insight", context="Period Q4")

        assert ax.get_title() == "Period Q4"

    def test_legend_bottom_default(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="Test", context="Ctx")

        legend = ax.get_legend()
        assert legend is not None
        # Legend should be anchored below the axes
        bbox = legend.get_bbox_to_anchor()
        assert bbox is not None

    def test_legend_right(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="Test", legend_position="right")

        legend = ax.get_legend()
        assert legend is not None

    def test_legend_inside(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="Test", legend_position="inside")

        legend = ax.get_legend()
        assert legend is not None
        assert legend.get_frame().get_alpha() == 0.8

    def test_no_legend_handles(self, mpl_fig_ax_no_legend):
        """Should work without error when no legend labels exist."""
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax_no_legend
        apply_chart_layout(fig, ax, insight="No legend", context="Test")

        assert fig._suptitle.get_text() == "No legend"
        assert ax.get_legend() is None

    def test_subplots_primary_ax(self, mpl_fig_subplots):
        """Should apply layout to the specified primary axes."""
        from chart_layout import apply_chart_layout

        fig, axes = mpl_fig_subplots
        apply_chart_layout(fig, axes[0], insight="Subplots test", context="Two panels")

        assert fig._suptitle.get_text() == "Subplots test"
        assert axes[0].get_title() == "Two panels"

    def test_reserves_space(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="Test", context="Ctx")

        params = fig.subplotpars
        assert params.top == pytest.approx(0.88)
        assert params.bottom == pytest.approx(0.18)

    def test_empty_context(self, mpl_fig_ax):
        from chart_layout import apply_chart_layout

        fig, ax = mpl_fig_ax
        apply_chart_layout(fig, ax, insight="Insight only")

        assert fig._suptitle.get_text() == "Insight only"
        assert ax.get_title() == ""


# ---------------------------------------------------------------------------
# Tests: apply_plotly_layout
# ---------------------------------------------------------------------------

class TestApplyPlotlyLayout:
    def test_combined_html_title(self, plotly_fig):
        from chart_layout import apply_plotly_layout

        apply_plotly_layout(plotly_fig, insight="Sales up 12%", context="vs Q3 2025")

        title = plotly_fig.layout.title
        assert "<b>Sales up 12%</b>" in title.text
        assert "vs Q3 2025" in title.text

    def test_legend_horizontal_bottom(self, plotly_fig):
        from chart_layout import apply_plotly_layout

        apply_plotly_layout(plotly_fig, insight="Test")

        legend = plotly_fig.layout.legend
        assert legend.orientation == "h"
        assert legend.y == -0.12
        assert legend.xanchor == "center"

    def test_legend_right(self, plotly_fig):
        from chart_layout import apply_plotly_layout

        apply_plotly_layout(plotly_fig, insight="Test", legend_position="right")

        legend = plotly_fig.layout.legend
        assert legend.xanchor == "left"
        assert legend.x == 1.02

    def test_legend_inside(self, plotly_fig):
        from chart_layout import apply_plotly_layout

        apply_plotly_layout(plotly_fig, insight="Test", legend_position="inside")

        legend = plotly_fig.layout.legend
        assert legend.xanchor == "right"
        assert "rgba" in legend.bgcolor

    def test_margins(self, plotly_fig):
        from chart_layout import apply_plotly_layout

        apply_plotly_layout(plotly_fig, insight="Test")

        margin = plotly_fig.layout.margin
        assert margin.t == 100
        assert margin.b == 80
        assert margin.l == 60
        assert margin.r == 40

    def test_title_without_context(self, plotly_fig):
        from chart_layout import apply_plotly_layout

        apply_plotly_layout(plotly_fig, insight="Insight only")

        title_text = plotly_fig.layout.title.text
        assert "<b>Insight only</b>" in title_text
        assert "<br>" not in title_text


# ---------------------------------------------------------------------------
# Tests: get_chart_colors
# ---------------------------------------------------------------------------

class TestGetChartColors:
    def test_returns_correct_count(self):
        from chart_layout import get_chart_colors

        colors = get_chart_colors("corporate", n=5)
        assert len(colors) == 5

    def test_returns_hex_strings(self):
        from chart_layout import get_chart_colors

        colors = get_chart_colors("corporate", n=3)
        for c in colors:
            assert c.startswith("#")
            assert len(c) == 7  # #rrggbb

    def test_cycles_when_n_exceeds_palette(self):
        from chart_layout import get_chart_colors

        colors = get_chart_colors("corporate", n=20)
        assert len(colors) == 20

    def test_default_style(self):
        from chart_layout import get_chart_colors

        colors = get_chart_colors(n=4)
        assert len(colors) == 4
