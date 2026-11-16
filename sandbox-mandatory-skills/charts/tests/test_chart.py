import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location("chart", Path(__file__).resolve().parents[1] / "scripts" / "chart.py")
chart = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(chart)

BAR = {"type": "bar", "title": "t", "x": "m", "y": ["v"], "data": [{"m": "2023-05", "v": 1.5}, {"m": "2023-06", "v": None}]}


@pytest.mark.parametrize("spec", [
    BAR,
    {**BAR, "y": "v"},
    {"type": "table", "data": [{"a": "x", "b": None}]},
    {"type": "histogram", "counts": [3, 5], "bin_edges": [0, 1, 2]},
    {"type": "pinmap", "lat": "la", "lon": "lo", "data": [{"la": 40.4, "lo": -3.7}]},
    {"type": "progress", "y": "k", "goal": 100, "data": [{"k": 80}]},
    {"type": "gauge", "y": "k", "segments": [{"min": 0, "max": 50, "label": "Good"}], "data": [{"k": 20}]},
    {"type": "bubble", "x": "a", "y": ["b"], "size": "c", "data": [{"a": 1, "b": 2, "c": 3}]},
    {"type": "map", "region": "Spain-communities", "x": "r", "y": ["v"], "data": [{"r": "ES-MD", "v": 7}]},
    {"type": "heatmap", "x": "h", "y": "d", "value": "v", "data": [{"h": 9, "d": "Mon", "v": 0}, {"h": 10, "d": "Mon", "v": None}]},
    {"type": "scatter", "x": "a", "y": "b", "label": "n", "data": [{"a": 1, "b": 2, "n": "Sci-Fi"}]},
])
def test_draws(spec):
    assert chart.problem(json.dumps(spec)) is None


@pytest.mark.parametrize("source, why", [
    ("{'type': 'bar'}", "not valid JSON"),
    (json.dumps({**BAR, "type": "sankey"}), "type 'sankey'"),
    (json.dumps({**BAR, "data": []}), "data must be"),
    (json.dumps({**BAR, "data": [{"m": "a", "v": "1"}]}), "must be numbers or null"),
    (json.dumps({**BAR, "data": [{"m": "a"}]}), "must be numbers or null"),
    (json.dumps({**BAR, "data": [{"m": "a", "v": True}]}), "every value in data"),
    (json.dumps({"type": "histogram", "counts": [1, 2], "bin_edges": [0, 1]}), "bin_edges"),
    (json.dumps({"type": "progress", "y": "k", "goal": 0, "data": [{"k": 1}]}), "goal"),
    (json.dumps({"type": "map", "region": "Spain", "x": "r", "y": ["v"], "data": [{"r": "ES", "v": 1}]}), "region"),
    (json.dumps({"type": "heatmap", "x": "h", "y": "d", "data": [{"h": 9, "d": "Mon", "v": 1}]}), "heatmap: x, y and value"),
    (json.dumps({"type": "heatmap", "x": "h", "y": "d", "value": "v", "data": [{"h": 9, "d": "Mon", "v": "1"}]}), "number or null"),
    (json.dumps({"type": "scatter", "x": "a", "y": "b", "label": "n", "data": [{"a": 1, "b": 2}]}), "label must name"),
    (json.dumps({"type": "scatter", "x": "a", "y": "b", "label": None, "data": [{"a": 1, "b": 2}]}), "label must name"),
])
def test_shows_as_code(source, why):
    assert why in chart.problem(source)


def test_check_reads_every_block_of_a_reply(capsys):
    reply = f"Sales hold.\n\n```chart\n{json.dumps(BAR)}\n```\n\n```mermaid\ngraph TD; A-->B\n```\n\n```chart\n{{}}\n```\n"
    assert chart.check(reply) == 1
    assert capsys.readouterr().out.splitlines()[:2] == ["chart 1: OK", "chart 2: shows as code: type None is not one of "
                                                        + ", ".join(sorted(chart.TYPES))]


def test_check_takes_a_bare_json():
    assert chart.check(json.dumps(BAR)) == 0


def test_embed(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("USER_WORKSPACE", str(tmp_path))
    png = tmp_path / "project" / "output" / "assets" / "monthly_bai.png"
    png.parent.mkdir(parents=True)
    png.write_bytes(b"")
    assert chart.embed(str(png), "BAI") == 1
    png.write_bytes(b"\x89PNG")
    assert chart.embed(str(png), "BAI") == 0
    assert capsys.readouterr().out == "![BAI](output/assets/monthly_bai.png)\n"


def test_mermaid_not_checked_without_node(monkeypatch, capsys):
    monkeypatch.setattr(chart.shutil, "which", lambda _: None)
    assert chart.check("```mermaid\nflowchart LR\n  A --> B\n```\n") == 0
    assert "not checked (node is not installed)" in capsys.readouterr().out


_VENDOR = Path(chart.os.environ.get("MERMAID_DIR", "/opt/mermaid"))
needs_mermaid = pytest.mark.skipif(
    not (chart.shutil.which("node") and (_VENDOR / "mermaid.min.js").is_file()),
    reason="no Mermaid validator (MERMAID_DIR with jsdom and mermaid.min.js)",
)


@needs_mermaid
def test_mermaid_parsed_as_genai_ui_does(capsys):
    reply = (
        '```mermaid\nflowchart LR\n  A["Pago (tarjeta)"] --> B[Fin]\n```\n'
        "```mermaid\nflowchart LR\n  A[Pago (tarjeta)] --> B\n```\n"
        '```mermaid\npie title Ventas\n  "Acción" : 10\n```\n'
        "```mermaid\nsankey-beta\n\nAcción,Pagado,10\n```\n"
    )
    assert chart.check(reply) == 1
    out = capsys.readouterr().out
    assert "mermaid 1: OK" in out and "mermaid 3: OK" in out
    assert "mermaid 2: shows as code:" in out and "mermaid 4: shows as code:" in out


def test_hints_at_database_column_names_without_failing(capsys):
    block = {"type": "bar", "x": "mes", "y": ["num_alquileres"], "data": [{"mes": "Ene", "num_alquileres": 0}]}
    assert chart.check(json.dumps(block)) == 0
    out = capsys.readouterr().out
    assert "hint:" in out and "num_alquileres" in out and "mes," not in out
    assert chart.raw_names(json.dumps({**block, "data": [{"Mes": "Ene", "Alquileres": 0}]})) == []
    assert chart.raw_names("{not json") == []


def test_the_matplotlib_style_loads_with_the_app_palette():
    plt = pytest.importorskip("matplotlib.pyplot")
    plt.style.use(str(Path(__file__).resolve().parents[1] / "genai.mplstyle"))
    assert plt.rcParams["axes.prop_cycle"].by_key()["color"][0] == "#128bd3"
    assert plt.rcParams["savefig.dpi"] == 150
