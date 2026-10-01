#!/usr/bin/env python3
"""Embed the fonts this skill ships into a page, as data: URIs.

    python3 embed_fonts.py --list
    python3 embed_fonts.py index.html "Crimson Pro" "JetBrains Mono"

For an installation without internet access, where Google Fonts does not load. The
page carries a `/* fonts */` comment inside its <style>; this replaces it with one
@font-face per file of each family (each weight and style the family ships), so the
base64 never passes through the conversation. A family that is not shipped is
reported, and the page keeps the theme's fallback stack for it.

The fonts are the OFL families the visual skills ship (fonts/, with their licences).
Family, weight and style come from each file's own name and OS/2 tables.

Standard library only.
"""

import base64
import json
import struct
import sys
from pathlib import Path

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"
PLACEHOLDER = "/* fonts */"


def _tables(data: bytes) -> dict[str, tuple[int, int]]:
    count = struct.unpack(">H", data[4:6])[0]
    tables = {}
    for i in range(count):
        tag, _, offset, length = struct.unpack(">4sIII", data[12 + 16 * i : 28 + 16 * i])
        tables[tag.decode("latin-1")] = (offset, length)
    return tables


def _family(data: bytes, tables) -> str:
    offset, _ = tables["name"]
    _, count, strings = struct.unpack(">HHH", data[offset : offset + 6])
    names = {}
    for i in range(count):
        record = data[offset + 6 + 12 * i : offset + 18 + 12 * i]
        platform, encoding, _, name_id, length, start = struct.unpack(">HHHHHH", record)
        if platform == 3 and encoding in (0, 1) and name_id in (1, 16):
            raw = data[offset + strings + start : offset + strings + start + length]
            names[name_id] = raw.decode("utf-16-be")
    # 16 is the typographic family ("Crimson Pro"); 1 may carry the style ("... Bold").
    return names.get(16) or names.get(1, "")


def describe(path: Path) -> dict:
    data = path.read_bytes()
    tables = _tables(data)
    weight, italic = 400, False
    if "OS/2" in tables:
        offset, _ = tables["OS/2"]
        weight = struct.unpack(">H", data[offset + 4 : offset + 6])[0]
        italic = bool(struct.unpack(">H", data[offset + 62 : offset + 64])[0] & 1)
    variable = "fvar" in tables
    return {
        "family": _family(data, tables),
        "weight": "100 900" if variable else str(weight),
        "style": "italic" if italic else "normal",
        "file": path.name,
    }


def catalog() -> dict[str, list[dict]]:
    families: dict[str, list[dict]] = {}
    for path in sorted(FONTS_DIR.glob("*.ttf")):
        face = describe(path)
        families.setdefault(face["family"], []).append(face)
    return families


def font_face(face: dict) -> str:
    data = base64.b64encode((FONTS_DIR / face["file"]).read_bytes()).decode("ascii")
    return (
        "@font-face {\n"
        f"  font-family: '{face['family']}';\n"
        f"  font-style: {face['style']};\n"
        f"  font-weight: {face['weight']};\n"
        "  font-display: swap;\n"
        f"  src: url(data:font/ttf;base64,{data}) format('truetype');\n"
        "}"
    )


def embed(page: Path, families: list[str]) -> dict:
    text = page.read_text(encoding="utf-8")
    if PLACEHOLDER not in text:
        raise SystemExit(f"{page} has no {PLACEHOLDER} comment to replace.")
    shipped = catalog()
    found = [f for f in families if f in shipped]
    rules = [font_face(face) for f in found for face in shipped[f]]
    page.write_text(text.replace(PLACEHOLDER, "\n".join(rules), 1), encoding="utf-8")
    return {
        "page": str(page),
        "embedded": found,
        "missing": [f for f in families if f not in shipped],
        "bytes": page.stat().st_size,
    }


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["--list"]:
        print(json.dumps({f: [x["file"] for x in faces] for f, faces in catalog().items()}, indent=2))
        return 0
    if len(args) < 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    print(json.dumps(embed(Path(args[0]), args[1:]), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
