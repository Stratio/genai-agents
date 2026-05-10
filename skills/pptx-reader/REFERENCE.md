# pptx-reader — REFERENCE

Advanced patterns for cases the main SKILL.md keeps at a high level.
Load this when the quick workflow doesn't fit the deck in front of you.

## 1. Title detection heuristics

`python-pptx` exposes `slide.shapes.title` when a slide has a title
placeholder (`ph type="title"` or `ph type="ctrTitle"`). But many real
decks use a text box positioned like a title instead of a real
placeholder. Fall back gracefully:

```python
from pptx.enum.text import PP_ALIGN

def find_title(slide) -> str | None:
    # Preferred: real title placeholder
    title_shape = slide.shapes.title
    if title_shape is not None and title_shape.has_text_frame:
        text = title_shape.text_frame.text.strip()
        if text:
            return text

    # Fallback: first non-empty text frame near the top of the slide
    candidates = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text.strip()
        if not text:
            continue
        top = shape.top or 0
        candidates.append((top, text))
    if not candidates:
        return None
    # Closest to the top wins
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]
```

Caveat: for section-divider slides where the "title" is centered on
the page (not at the top), this heuristic returns the wrong thing.
Document this in your extraction diagnostics.

## 2. Theme inheritance (styles flow from master → layout → slide)

Text in a placeholder inherits font face, size, color from the layout,
which inherits from the master. `python-pptx` does not automatically
resolve the inheritance for you — `run.font.name` may return `None`
even when the rendered slide shows Calibri 18pt, because the actual
value lives on the layout or master.

When you need the effective font:

```python
from pptx.util import Pt

def effective_font_name(run, default="Calibri"):
    name = run.font.name
    if name:
        return name
    # Walk up: the paragraph's placeholder → layout → master
    # python-pptx does not expose this walker directly; for most read
    # workflows you can treat a missing name as "inherits from theme"
    # and stop there.
    return default
```

For read-side extraction this rarely matters — the text is the text.
If you need the effective rendered style (e.g. to reproduce it
elsewhere), rasterize the slide and inspect visually instead of
chasing the inheritance chain.

## 3. Chart type detection from OOXML

`ppt/charts/chart*.xml` wraps the chart data inside a `<c:plotArea>`
with a type-specific child element. Detect the type before reading
series data:

```python
from lxml import etree

NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"

CHART_TYPES = {
    "barChart":       "bar/column",
    "lineChart":      "line",
    "pieChart":       "pie",
    "doughnutChart":  "doughnut",
    "areaChart":      "area",
    "scatterChart":   "scatter",
    "bubbleChart":    "bubble",
    "radarChart":     "radar",
    "stockChart":     "stock",
    "surfaceChart":   "surface",
}

def chart_type(chart_xml_path: str) -> str:
    tree = etree.parse(chart_xml_path)
    plot = tree.find(f".//{{{NS_C}}}plotArea")
    if plot is None:
        return "unknown"
    for child in plot:
        tag = etree.QName(child).localname
        if tag in CHART_TYPES:
            return CHART_TYPES[tag]
    return "unknown"
```

For `barChart`, `<c:barDir val="bar"/>` means horizontal; `"col"`
means vertical (column). The same XML element covers both.

## 4. Category axis labels

Besides series values, category labels (x-axis for column charts,
year labels for time series) live under `c:cat/c:strRef/c:strCache` or
`c:cat/c:numRef/c:numCache`:

```python
from lxml import etree

NS = {"c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}

def chart_categories_and_series(chart_xml_path: str):
    tree = etree.parse(chart_xml_path)
    cats_el = tree.find(".//c:cat", NS)
    categories = []
    if cats_el is not None:
        for pt in cats_el.iterfind(".//c:pt/c:v", NS):
            categories.append((pt.text or "").strip())

    series = []
    for ser in tree.iterfind(".//c:ser", NS):
        name_el = ser.find(".//c:tx//c:v", NS)
        name = (name_el.text or "").strip() if name_el is not None else ""
        values = [float(v.text) for v in ser.iterfind(".//c:val//c:v", NS) if v.text]
        series.append({"name": name, "values": values})

    return categories, series
```

Output shape — easy to turn into a pandas DataFrame:

```python
import pandas as pd
categories, series = chart_categories_and_series(path)
df = pd.DataFrame({s["name"]: s["values"] for s in series}, index=categories)
```

## 5. Smart quotes, zero-width characters, soft hyphens

PowerPoint often inserts characters that look invisible but poison
downstream text processing:

- Zero-width space `\u200b`
- Zero-width non-joiner `\u200c`
- Byte-order mark `\ufeff`
- Soft hyphen `\u00ad`
- Smart quotes `\u2018`, `\u2019`, `\u201c`, `\u201d`

Normalize during extraction:

```python
ZW_CHARS = "\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad"
SMART_MAP = {
    "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-",  # en/em dashes
    "\u2026": "...",
}

def normalize_text(s: str) -> str:
    for ch in ZW_CHARS:
        s = s.replace(ch, "")
    for k, v in SMART_MAP.items():
        s = s.replace(k, v)
    return s
```

Apply the normalization after extraction, not before the
python-pptx call — the library handles its own decoding correctly.

## 6. Custom XML parts

Some decks embed `customXml/item1.xml` with out-of-band metadata
(workflow IDs, ERP references, tracked-changes state). Neither
`python-pptx` nor `markitdown` surface it:

```bash
unzip -l deck.pptx | grep '^customXml/'
```

If present, inspect with lxml. Rare in practice but common in
enterprise-generated decks (SharePoint, Microsoft Lists templates).

## 7. Recovering text from a corrupt deck

When `python-pptx` raises `PackageNotFoundError` or `KeyError` on a
seemingly valid file, try the degraded fallback:

```bash
# LibreOffice re-saves the file, often healing corruption
soffice --headless --convert-to pptx --outdir /tmp/ broken.pptx

# Or convert to text directly — loses structure but recovers words
soffice --headless --convert-to txt --outdir /tmp/ broken.pptx
cat /tmp/broken.txt
```

For very degraded files, `strings deck.pptx | grep -v '^[[:space:]]*$'`
can surface readable fragments even when structured parsing fails.
Treat the output as forensics, not data.

## 8. Extraction budget for very large decks

Decks with 100+ slides (training courses, onboarding decks) can take
30+ seconds to parse fully with `python-pptx` and produce 30K–50K
tokens of text.

Strategies:
- Extract only the slides the user asked about (`--pages 10-20` in
  quick mode).
- Extract titles + first 3 bullets per slide to build a cheap table
  of contents, then deep-dive only into the slides of interest.
- For training decks, the notes often contain the narrative and the
  slides contain only keywords — extract notes only (`--no-tables
  --notes-only`) to halve the token cost.

## 9. When extraction is good enough

You can stop when:
- The output reads cleanly and has the structure the downstream
  task needs (headings per slide, bullets at the right indentation,
  tables in markdown form, notes attached to the right slide).
- Hidden slides are accounted for (included or explicitly skipped
  with a count in diagnostics).
- Tables and charts that carry numeric substance were captured
  either as markdown tables or as reconstructed pandas DataFrames.
- Speaker notes and comments were extracted when the task is
  editorial or narrative-focused.

You do not need to capture animations, transitions, slide master
theme metadata, or embedded Excel workbooks unless the task
explicitly calls for them.
