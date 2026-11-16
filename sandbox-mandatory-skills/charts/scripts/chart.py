#!/usr/bin/env python3
"""Checks charts before they reach the chat of GenAI UI.

  check [FILE|-]          every ```chart and ```mermaid block in a reply (or a bare chart
                          JSON) GenAI UI can draw
  embed PNG [TITLE]       the PNG exists and is not empty; prints the ![TITLE](path) line

A block GenAI UI cannot read shows as code. ```chart blocks are checked with the rules of
genai-ui's `parseChatChart` (chat-chart.utils.ts); ```mermaid blocks with Mermaid's own
parser, the version GenAI UI draws them with, through mermaid_check.mjs (Node).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

AXIS = {"bar", "line", "area", "pie", "waterfall", "scatter", "bubble", "radar", "map"}
TYPES = AXIS | {"progress", "gauge", "pinmap", "histogram", "heatmap", "table"}
REGIONS = {"world_countries", "Spain-communities", "Spain-provinces", "United States"}
BLOCK = re.compile(r"^```(chart|mermaid)[ \t]*\n([\s\S]*?)\n```[ \t]*$", re.M)


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _cell(v):
    return v is None or isinstance(v, str) or _num(v)


def problem(source: str) -> str | None:
    """Why GenAI UI would show this ```chart block as code, or None if it draws it."""
    try:
        raw = json.loads(source)
    except json.JSONDecodeError as e:
        return f"not valid JSON: {e}"
    if not isinstance(raw, dict):
        return "not a JSON object"
    kind = raw.get("type")
    if kind not in TYPES:
        return f"type {kind!r} is not one of {', '.join(sorted(TYPES))}"

    if kind == "histogram":
        counts, edges = raw.get("counts"), raw.get("bin_edges")
        if not (isinstance(counts, list) and counts and all(map(_num, counts))):
            return "histogram: counts must be a non-empty list of numbers"
        if not (isinstance(edges, list) and all(map(_num, edges)) and len(edges) == len(counts) + 1):
            return "histogram: bin_edges must be numbers, one more than counts"
        return None

    rows = raw.get("data")
    if not (isinstance(rows, list) and rows and all(isinstance(r, dict) for r in rows)):
        return "data must be a non-empty list of objects"
    if not all(_cell(v) for r in rows for v in r.values()):
        return "every value in data must be a number, a string or null"
    if kind == "table":
        return None

    if kind == "pinmap":
        lat, lon = raw.get("lat"), raw.get("lon")
        if not (isinstance(lat, str) and isinstance(lon, str)):
            return "pinmap: lat and lon must name columns"
        if not all(_num(r.get(lat)) and _num(r.get(lon)) for r in rows):
            return f"pinmap: every row needs numbers in {lat!r} and {lon!r}"
        return None

    if kind == "heatmap":
        x, y, value = raw.get("x"), raw.get("y"), raw.get("value")
        if not all(isinstance(c, str) for c in (x, y, value)):
            return "heatmap: x, y and value must name columns"
        for i, r in enumerate(rows):
            if not all(isinstance(r.get(c), str) or _num(r.get(c)) for c in (x, y)):
                return f"row {i}: {x!r} and {y!r} must be strings or numbers"
            if not (_num(r.get(value)) or (value in r and r[value] is None)):
                return f"row {i}: {value!r} must be a number or null"
        return None

    y = raw.get("y")
    y = [y] if isinstance(y, str) else y
    if not (isinstance(y, list) and y and all(isinstance(c, str) for c in y)):
        return "y must name a column, or a non-empty list of columns"

    if kind in ("progress", "gauge"):
        if not _num(rows[0].get(y[0])):
            return f"{kind}: the first row needs a number in {y[0]!r}"
        if kind == "progress" and not (_num(raw.get("goal")) and raw["goal"] > 0):
            return "progress: goal must be a number > 0"
        segs = raw.get("segments")
        if kind == "gauge" and not (
            isinstance(segs, list) and segs and all(
                isinstance(s, dict) and _num(s.get("min")) and _num(s.get("max")) and isinstance(s.get("label"), str)
                for s in segs)):
            return 'gauge: segments must be a non-empty list of {"min": n, "max": n, "label": "…"}'
        return None

    x = raw.get("x")
    if not isinstance(x, str):
        return "x must name a column"
    for i, r in enumerate(rows):
        if not (isinstance(r.get(x), str) or _num(r.get(x))):
            return f"row {i}: {x!r} must be a string or a number"
        bad = [c for c in y if not (r.get(c) is None and c in r or _num(r.get(c)))]
        if bad:
            return f"row {i}: {', '.join(map(repr, bad))} must be numbers or null"
    label = raw.get("label")
    if kind in ("scatter", "bubble") and "label" in raw and not (
            isinstance(label, str) and all(label in r for r in rows)):
        return f"{kind}: label must name a column every row has"
    if kind == "bubble":
        size = raw.get("size")
        if not (isinstance(size, str) and all(_num(r.get(size)) for r in rows)):
            return "bubble: size must name a column with a number in every row"
    if kind == "map" and raw.get("region") not in REGIONS:
        return f"map: region must be one of {', '.join(sorted(REGIONS))}"
    return None


def mermaid_problems(sources: list[str]) -> list[str | None] | str:
    """Mermaid's parse error for each diagram (None if it reads it), or why they could not be checked."""
    node = shutil.which("node")
    if not node:
        return "node is not installed"
    script = Path(__file__).with_name("mermaid_check.mjs")
    run = subprocess.run([node, str(script)], input=json.dumps(sources), capture_output=True, text=True, timeout=120)
    if run.returncode:
        return run.stderr.strip() or f"exit {run.returncode}"
    return json.loads(run.stdout)


SNAKE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)+$")


def raw_names(source: str) -> list[str]:
    """The block's column names that read as a database's (`duracion_media`): the chart shows them as they are."""
    try:
        rows = json.loads(source).get("data") or []
    except (json.JSONDecodeError, AttributeError):
        return []
    names = {k for r in rows if isinstance(r, dict) for k in r}
    return sorted(n for n in names if SNAKE.match(n))


def check(text: str) -> int:
    text = re.sub(r"\r\n?", "\n", text)
    blocks = [(m.group(1), m.group(2)) for m in BLOCK.finditer(text)]
    if not blocks and "```" not in text:
        blocks = [("chart", text)]  # a bare JSON
    if not blocks:
        print("no ```chart or ```mermaid block found")
        return 1
    charts = [source for kind, source in blocks if kind == "chart"]
    diagrams = [source for kind, source in blocks if kind == "mermaid"]
    failed = 0
    for i, source in enumerate(charts, 1):
        why = problem(source)
        print(f"chart {i}: {'OK' if why is None else 'shows as code: ' + why}")
        failed += why is not None
        if names := raw_names(source):
            print(f"chart {i}: hint: the chart shows these column names as they are; name them as they should read"
                  f" (\"Duración media (min)\", not \"duracion_media\"): {', '.join(names)}")
    if diagrams:
        found = mermaid_problems(diagrams)
        if isinstance(found, str):
            print(f"mermaid: {len(diagrams)} block(s) not checked ({found}); follow the rules in SKILL.md")
        else:
            for i, why in enumerate(found, 1):
                print(f"mermaid {i}: OK" if why is None else f"mermaid {i}: shows as code:\n    " + why.replace("\n", "\n    "))
                failed += why is not None
    return 1 if failed else 0


def embed(png: str, title: str) -> int:
    path = Path(png).resolve()
    if not path.is_file() or path.stat().st_size == 0:
        print(f"{png}: missing or empty, run the script that draws it", file=sys.stderr)
        return 1
    root = Path(os.environ.get("USER_WORKSPACE", "/root")) / "project"
    try:
        shown = path.relative_to(root.resolve())
    except ValueError:
        shown = Path(os.path.relpath(path))
    print(f"![{title}]({shown.as_posix()})")
    return 0


def main(argv: list[str]) -> int:
    if argv[:1] == ["check"] and len(argv) <= 2:
        src = argv[1] if len(argv) == 2 else "-"
        return check(sys.stdin.read() if src == "-" else Path(src).read_text(encoding="utf-8"))
    if argv[:1] == ["embed"] and len(argv) in (2, 3):
        return embed(argv[1], argv[2] if len(argv) == 3 else Path(argv[1]).stem.replace("_", " "))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
