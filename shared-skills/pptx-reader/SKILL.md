---
name: pptx-reader
description: "Inspect, analyze, and extract content from PowerPoint (.pptx) files intelligently. Use this skill whenever you need to read what's inside a deck — extracting slide text, bullet lists, tables, speaker notes, embedded images, chart data, comments, or visually understanding slide composition. Covers pitch decks, executive briefings, training decks, academic slides, and data-heavy dashboards. Also handles legacy `.ppt` files via LibreOffice conversion. Always run a quick diagnostic before extraction to pick the right strategy."
argument-hint: "[path/to/file.pptx]"
---

# Skill: PPTX Reader

A disciplined approach to getting useful content out of PowerPoint files.
Different decks need different tactics — a prose-heavy policy brief
behaves nothing like a dashboard made of rasterized charts, and neither
behaves like a presentation full of native OOXML charts with editable
data. Diagnosis first, extraction second.

## 1. Two modes: quick and deep

This skill supports two ways of working:

**Quick mode — `scripts/quick_extract.py`**
One-shot extraction that returns structured Markdown. Use it when:
- The deck is "normal" (native `.pptx`, not password-protected)
- You want text + bullets + tables + speaker notes without thinking about XML
- You're batch-processing many files
- You're feeding the output directly to another agent or LLM

**Deep mode — the workflow below**
Step-by-step diagnosis and extraction. Use it when:
- The deck has embedded charts with numeric data you need as a table
- You need per-slide rasterized previews for a vision model
- Speaker notes, comments, or hidden slides need bespoke handling
- The file is a legacy binary `.ppt`
- Quick mode returned empty or garbled text

Default to quick mode. Fall back to deep mode when quick mode isn't enough.

### Quick mode usage

```bash
# Extract everything
python <skill-root>/scripts/quick_extract.py deck.pptx

# Text only, no tables
python <skill-root>/scripts/quick_extract.py deck.pptx --no-tables

# Text only, no speaker notes
python <skill-root>/scripts/quick_extract.py deck.pptx --no-notes

# Include hidden slides (skipped by default)
python <skill-root>/scripts/quick_extract.py deck.pptx --include-hidden

# Force a specific extractor
python <skill-root>/scripts/quick_extract.py deck.pptx --tool python-pptx

# Read from stdin
cat deck.pptx | python <skill-root>/scripts/quick_extract.py -
```

The script:
- Returns Markdown on stdout (per-slide sections with headings, bullets,
  tables, speaker notes in `> Notes:` blockquotes)
- Returns diagnostics on stderr (slide count, hidden slides, which tool
  ran, features skipped)
- Exits 0 on success, 1 on failure
- Auto-detects available tools and falls back through a chain
- Never pollutes stdout — the output is safe to pipe into another tool

The extractor chain tries, in order: **python-pptx → zipfile XML walk →
soffice text conversion**. The first one that produces non-empty
output wins.

### Companion utility — `scripts/rasterize_slides.py`

Separate one-shot that converts a deck to PNGs, one per slide. Useful
when you want to feed slide images to a vision model without running
the full extractor chain.

```bash
# Rasterize every slide at 150 DPI (~1,500 tokens/slide for a vision model)
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides

# Higher DPI for dense content
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides --dpi 300

# Only specific slides
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides --pages 3-7
```

Runs `soffice --headless --convert-to pdf` followed by `pdftoppm`. Both
are pre-installed in the Stratio Cowork sandbox; see README.md for dev
local setup.

## 2. Golden rule for deep mode: diagnose before you extract

Never run `python-pptx` blindly on an unknown deck. A legacy `.ppt`
file will raise an obscure error. A deck with hidden slides will give
you different content than what the author presented. A presentation
with custom fonts not installed will render with substitution you can't
detect from extracted text alone. A two-second diagnostic step saves
ten minutes of debugging garbage output.

Run this inspection block first:

```bash
# What are we dealing with? Is it a ZIP (modern .pptx) or CFB (legacy .ppt)?
file target.pptx

# List the ZIP contents — slides, masters, media, notes
unzip -l target.pptx | head -40

# How many slides?
unzip -l target.pptx | grep -c 'ppt/slides/slide[0-9]'

# Any hidden slides?
unzip -p target.pptx ppt/presentation.xml | grep -o 'show="0"' | wc -l

# Any speaker notes?
unzip -l target.pptx | grep -c 'ppt/notesSlides/notesSlide'

# Any comments?
unzip -l target.pptx | grep -c 'ppt/comments/'

# Embedded media?
unzip -l target.pptx | grep 'ppt/media/' | head -20

# Metadata
unzip -p target.pptx docProps/core.xml
```

What each output tells you:

- **`file`** — `Microsoft PowerPoint 2007+` means modern `.pptx` (ZIP-
  based, readable by `python-pptx`). `Composite Document File V2` or
  `CFB` means legacy `.ppt` — you must convert first (see §11).
- **`unzip -l` count of `ppt/slides/slide*.xml`** — slide count. Decks
  with 50+ slides benefit from page-range extraction instead of a
  full dump.
- **`show="0"` count** — number of hidden slides. The author hid them
  on purpose; decide whether to include them or skip (default in
  quick_extract is skip).
- **`notesSlides` count** — speaker notes present. Essential for pitch
  decks and briefings where the verbal message lives in the notes.
- **`comments/`** — reviewer comments (revision marks). Extract these
  separately when the task is editorial review.
- **`ppt/media/`** — listing shows all embedded images (PNG, JPG),
  audio (WAV, MP3), video (MP4). Sizes hint at substance.
- **`docProps/core.xml`** — author, created/modified timestamps, title,
  subject, keywords.

## 3. Pick a strategy based on deck type

Classify the deck in your head, then apply the matching workflow.

### Prose-heavy decks (policy briefs, pitch decks, internal briefings)

Primary tool: `python-pptx` for text extraction per shape, per slide.

```python
from pptx import Presentation

prs = Presentation("brief.pptx")
for slide_num, slide in enumerate(prs.slides, start=1):
    # Skip hidden slides unless the user asked otherwise
    if getattr(slide, "element", None) is not None:
        if slide.element.get("show") == "0":
            continue

    title = _find_title(slide)
    print(f"## Slide {slide_num}: {title or '(untitled)'}\n")

    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                text = "".join(r.text for r in para.runs).strip()
                if not text:
                    continue
                # Bullet levels: para.level 0-8
                prefix = "  " * (para.level or 0) + "- "
                print(prefix + text)
```

The `_find_title` helper prefers the title placeholder; if absent, it
falls back to the first text frame on the slide. See REFERENCE.md for
the full pattern.

Output convention: one `## Slide N: Title` heading per slide, bullets
with indentation reflecting `para.level`, blank lines between slides.

### Data-heavy decks (dashboards, reports with charts)

A chart inside a PPTX can live in two forms:

1. **Native OOXML chart** (`<c:chart>` in `ppt/charts/chart*.xml`) —
   editable by the user; the underlying data is accessible as XML. You
   can reconstruct the dataframe without vision.
2. **Rasterized image** (chart exported from Excel/matplotlib/plotly
   and pasted as PNG/JPG) — the data is not recoverable from the file;
   you need OCR or a vision model.

Detect which kind is present:

```bash
# Native OOXML charts
unzip -l deck.pptx | grep -c 'ppt/charts/chart'

# Rasterized chart images
unzip -l deck.pptx | grep -E 'ppt/media/.*\.(png|jpg|jpeg|tiff)$'
```

For native charts, parse the XML:

```python
import zipfile
from lxml import etree

NS = {
    "c":  "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "a":  "http://schemas.openxmlformats.org/drawingml/2006/main",
}

with zipfile.ZipFile("deck.pptx") as z:
    for name in sorted(z.namelist()):
        if not name.startswith("ppt/charts/chart") or not name.endswith(".xml"):
            continue
        tree = etree.parse(z.open(name))
        # Series values live under c:ser/c:val/c:numRef/c:numCache/c:pt/c:v
        for ser in tree.iterfind(".//c:ser", NS):
            name_el = ser.find(".//c:tx//c:v", NS)
            ser_name = (name_el.text or "").strip() if name_el is not None else ""
            values = [float(v.text) for v in ser.iterfind(".//c:val//c:v", NS) if v.text]
            print(f"{name}: series='{ser_name}' values={values}")
```

For rasterized charts, rasterize the containing slide and send to a
vision model (see §4).

### Exported decks (all content as page images)

Symptom: every slide is a full-bleed rasterized image with no text
frames. This happens when someone exports slides from Keynote or an
image-based tool and re-saves them as PPT. `python-pptx` returns
empty text per slide.

Workflow: skip text extraction and rasterize every slide.

```bash
python <skill-root>/scripts/rasterize_slides.py deck.pptx --out-dir /tmp/slides --dpi 200
```

Feed the resulting PNGs to a vision model. Expect ~1,600 tokens/slide
at 150 DPI, ~2,800 tokens/slide at 300 DPI.

### Mixed decks

Most real decks are mixed: an intro with prose, a few bullet slides,
two dashboards with native charts, one scanned legacy slide, a
conclusion slide with a screenshot. Don't try to extract everything
with one call. Break it up:

1. Run `quick_extract.py` for the prose parts.
2. Parse `ppt/charts/chart*.xml` for native chart data.
3. Rasterize only the slides that contain rasterized charts or screenshots.
4. Extract speaker notes separately if they carry substance.
5. Merge findings in your final summary.

## 4. Token-awareness when consuming content into an LLM

If you're feeding deck content to Claude or another LLM, cost matters.

| Approach | Approximate tokens per slide |
|---|---|
| Plain text extraction (prose + bullets + tables) | 100–300 |
| Speaker notes only (as prose) | 50–200 |
| Rasterized slide at 150 DPI | ~1,600 |
| Rasterized slide at 300 DPI | ~2,800 |
| Text + rasterized image both | 1,800–3,100 |

A 40-slide deck rasterized at 150 DPI burns ~64K tokens. Text
extraction of the same deck burns 4K–12K. Reserve rasterization for
slides where visual composition genuinely matters: dashboards, diagrams,
screenshots, complex tables where layout encodes meaning.

When precision matters for a specific slide (a dashboard with KPIs
positioned at specific coordinates, a quote slide where typography
carries the message), sending both text and image costs more but gives
the LLM maximum context to cross-check.

## 5. Speaker notes

Notes live in `ppt/notesSlides/notesSlide{N}.xml` (one per slide that
has notes). The text is under the DrawingML namespace, not PresentationML.

```python
from pptx import Presentation

prs = Presentation("brief.pptx")
for idx, slide in enumerate(prs.slides, start=1):
    notes_slide = slide.notes_slide if slide.has_notes_slide else None
    if notes_slide is None:
        continue
    notes_text = "\n".join(
        p.text for p in notes_slide.notes_text_frame.paragraphs if p.text.strip()
    )
    if notes_text:
        print(f"--- Notes for slide {idx} ---\n{notes_text}\n")
```

In pitch decks and executive briefings, the notes often contain the
verbal narrative ("Here we claim X because of Y evidence"). Extracting
just the notes can answer "what does this deck say?" more compactly
than the slide bullets themselves.

## 6. Comments (revision marks)

Reviewer comments live in `ppt/comments/comment{N}.xml`. They're
separate from notes and often carry editorial feedback ("Rephrase this
claim", "Cite source").

```python
import zipfile
from lxml import etree

NS = {
    "p188": "http://schemas.microsoft.com/office/powerpoint/2012/main",
    "p":    "http://schemas.openxmlformats.org/presentationml/2006/main",
}

with zipfile.ZipFile("brief.pptx") as z:
    comment_files = [n for n in z.namelist() if n.startswith("ppt/comments/")]
    for name in sorted(comment_files):
        tree = etree.parse(z.open(name))
        for cm in tree.iterfind(".//p:cm", NS):
            author_idx = cm.get("authorId")
            text_el = cm.find(".//p:text", NS)
            text = (text_el.text or "").strip() if text_el is not None else ""
            if text:
                print(f"[{name} author={author_idx}] {text}")
```

For editorial reviews and redlining workflows, extracting comments
lets you surface feedback without presenting the full deck content.

## 7. Tables

Tables in PPT are shapes with `has_table = True`. Extract cell-by-cell.
Merged cells share the same underlying `_tc`, so deduplicate by
identity.

```python
from pptx import Presentation

def table_to_markdown(shape) -> str:
    rows = []
    for row in shape.table.rows:
        seen = []
        cells = []
        for cell in row.cells:
            cid = id(cell._tc)
            if cid in seen:
                continue
            seen.append(cid)
            text = cell.text.strip().replace("|", "\\|") or " "
            cells.append(text)
        rows.append(cells)
    if not rows:
        return ""
    max_cols = max(len(r) for r in rows)
    rows = [r + [" "] * (max_cols - len(r)) for r in rows]
    header = "| " + " | ".join(rows[0]) + " |"
    sep = "| " + " | ".join(["---"] * max_cols) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join([header, sep, *body])

prs = Presentation("report.pptx")
for slide_num, slide in enumerate(prs.slides, start=1):
    for shape in slide.shapes:
        if shape.has_table:
            print(f"### Table on slide {slide_num}\n")
            print(table_to_markdown(shape))
```

Watch out for:
- **Alternating row backgrounds**: encoded in cell shading, don't show
  up in markdown. Ignore unless the task is design inspection.
- **Merged cells**: the `id(cell._tc)` check above deduplicates. Merged
  cells appear as a single cell with the combined content or empty
  neighbors — document the convention in your output.
- **Numeric formatting**: `cell.text` gives the displayed text, not the
  underlying number. For reconstruction of data, prefer native OOXML
  chart XML over scraping a rendered table.

## 8. Metadata

`docProps/core.xml` carries the document-level metadata:

```python
from pptx import Presentation

prs = Presentation("deck.pptx")
cp = prs.core_properties
print(f"Title:    {cp.title}")
print(f"Author:   {cp.author}")
print(f"Subject:  {cp.subject}")
print(f"Keywords: {cp.keywords}")
print(f"Created:  {cp.created}")
print(f"Modified: {cp.modified}")
print(f"Last modified by: {cp.last_modified_by}")
print(f"Revision: {cp.revision}")
```

`docProps/app.xml` has additional software-level metadata (app version,
slide count, title of slide show, company). Parse with `lxml` when you
need it — python-pptx exposes only the core properties.

## 9. Embedded media (images, audio, video)

Listed under `ppt/media/` inside the ZIP.

```bash
# List everything
unzip -l deck.pptx | grep 'ppt/media/'

# Extract all media
mkdir -p /tmp/media
unzip deck.pptx 'ppt/media/*' -d /tmp/
```

Images (PNG, JPG) are usually the bulk. Audio (WAV, MP3) and video
(MP4, MOV) appear in training and product decks. Python extraction:

```python
import zipfile

with zipfile.ZipFile("deck.pptx") as z:
    media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    for name in media:
        data = z.read(name)
        out_path = f"/tmp/{name.split('/')[-1]}"
        with open(out_path, "wb") as f:
            f.write(data)
        print(f"{name}: {len(data):,} bytes → {out_path}")
```

**Warning**: `ppt/media/` names are assigned by PowerPoint and can
collide with existing filenames when extracted. Sanitize using
`os.path.basename` and write to a fresh directory.

## 10. Hidden slides

The author hid them deliberately — speaker backup, deprecated content,
or slides parked for later. By default, extraction should **skip**
hidden slides. Surface the count in diagnostics so the user knows
they exist.

Detect:

```python
from pptx import Presentation

prs = Presentation("deck.pptx")
hidden = []
for idx, slide in enumerate(prs.slides, start=1):
    # python-pptx exposes _element; hidden slides have show="0"
    if slide._element.get("show") == "0":
        hidden.append(idx)

print(f"Hidden slides: {hidden}")
```

If the user explicitly asks for hidden content, re-run with
`--include-hidden` (quick mode) or add `if hidden` branch in deep mode.

## 11. Legacy `.ppt` files

The binary `.ppt` format (pre-Office 2007) is not a ZIP. `python-pptx`
cannot read it. Convert with LibreOffice first:

```bash
soffice --headless --convert-to pptx --outdir /tmp/ old.ppt
# → /tmp/old.pptx
```

Then process as normal. `quick_extract.py` auto-detects legacy `.ppt`
by file signature and converts transparently — you rarely need to
run the conversion manually.

Expect minor fidelity loss: animations, some custom shapes, and
embedded Excel objects may come through incomplete. For text
extraction this doesn't matter; for structural analysis it does.

## 12. Password-protected decks

If the PPTX opens but reveals encrypted XML inside, `python-pptx` will
raise `PackageNotFoundError`. Modern PPT encryption uses OOXML agile
encryption (not OLECF like legacy `.ppt`).

```python
try:
    from pptx import Presentation
    prs = Presentation("locked.pptx")
except Exception as exc:
    print(f"Cannot open: {exc}")
```

There is no stable Python decryption library for OOXML agile encryption
that works without the password. Ask the user for the password and
use `msoffcrypto-tool` to decrypt to a temp file first:

```bash
pip install msoffcrypto-tool
msoffcrypto-tool locked.pptx decrypted.pptx -p 'the-password'
```

Then process `decrypted.pptx` as normal. Never log or persist the
password.

## 13. Quick-reference cheat sheet

| Task | Tool | Command |
|---|---|---|
| Inspect structure | unzip | `unzip -l deck.pptx` |
| Slide count | unzip + grep | `unzip -l deck.pptx \| grep -c 'ppt/slides/slide[0-9]'` |
| Hidden slides | unzip + grep | `unzip -p deck.pptx ppt/presentation.xml \| grep -o 'show="0"' \| wc -l` |
| Text per slide | python-pptx | `slide.shapes[*].text_frame.paragraphs[*]` |
| Tables | python-pptx | `shape.has_table → shape.table.rows[*].cells[*]` |
| Speaker notes | python-pptx | `slide.notes_slide.notes_text_frame.text` |
| Comments | lxml on XML | Parse `ppt/comments/comment*.xml` |
| Native chart data | lxml on XML | Parse `ppt/charts/chart*.xml` for `<c:ser>` |
| Extract media | unzip | `unzip deck.pptx 'ppt/media/*' -d /tmp/` |
| Metadata | python-pptx | `prs.core_properties` |
| Rasterize slides | soffice + pdftoppm | See `scripts/rasterize_slides.py` |
| Convert legacy `.ppt` | soffice | `soffice --headless --convert-to pptx old.ppt` |

## 14. When to load REFERENCE.md

- Title detection heuristics (placeholder vs first-text-frame fallback)
- Theme inheritance (how placeholder styles flow from slide → layout → master)
- Chart type detection (bar / column / line / pie / scatter / radar from XML)
- Transitions and animations (exposed but rarely useful)
- Custom XML parts (`customXml/item*.xml`, rare but carries metadata)
- Encrypted / signed files advanced handling
