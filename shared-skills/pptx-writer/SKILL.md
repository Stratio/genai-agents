---
name: pptx-writer
description: "Create, manipulate, and polish PowerPoint (.pptx) decks with intentional design. Use this skill whenever you need to generate a new deck (pitch, sales briefing, executive summary, training, academic, report-style, town-hall) or transform an existing one (merge, split, reorder, delete slides, find-replace in slide text and speaker notes, convert legacy .ppt to .pptx, rasterize slides, export to PDF). This skill treats design seriously — every deck it produces has intentional typography, colour and layout, never the generic Calibri-everywhere default. For filling native OOXML charts with real data rather than pasting chart images, load REFERENCE.md."
argument-hint: "[deck type or description]"
---

# Skill: PPTX Writer

This skill produces PowerPoint decks that look designed, not generated.
Most automated PPT output is visually dead: Calibri body, solid black
on white, the default 10×7.5 aspect ratio, a blue heading bar if
you're lucky. That's the baseline this skill actively resists.

Before writing a single line of code, commit to a design direction.
The code serves the design, not the other way around.

## 1. Design-first workflow

Every deck generation task, regardless of size, follows five steps:

1. **Classify the deck** — what category is it? (See the taxonomy
   below.) This governs density, tone and structure downstream.
2. **Pick a visual tone** — editorial-modern, corporate-formal,
   technical-minimal, warm-conversational, academic-sober,
   playful-energetic. Pick one and execute it confidently. A timid
   "a bit of everything" deck is the worst outcome.
3. **Select a type pairing** — one display face for titles and
   headings, one body face for prose and bullets. Two typefaces is
   almost always enough. Because PPT uses the reader's system fonts
   unless you embed, choose pairings that degrade gracefully —
   Calibri / Aptos / Inter / Arial are universal safe defaults.
4. **Define a palette** — one dominant accent colour, one deep
   neutral for body text (rarely pure black), one pale neutral for
   backgrounds or rules, plus state colours (success / warning /
   danger) used sparingly. Real saturation, not washed-out pastels
   by default.
5. **Set the rhythm** — density target (pitch: 1 idea per slide;
   executive briefing: 3–4 bullets; training: 5–7 bullets + a
   figure), a section divider every 4–6 slides so the audience
   breathes, consistent vertical spacing inside every slide.

Only then open `python-pptx`.

### Deck taxonomy and starting points

| Category | Typical tone | Display face | Body face | Density |
|---|---|---|---|---|
| Pitch / VC deck | Editorial-modern | Inter / IBM Plex Sans | Inter | 1 idea/slide |
| Sales / product demo | Warm-conversational | Inter | Inter | visual-heavy |
| Executive briefing | Corporate-formal | IBM Plex Serif | IBM Plex Serif | 3–4 bullets |
| Training / how-to | Technical-minimal | IBM Plex Sans | IBM Plex Sans | 5–7 bullets + figures |
| Academic / research | Academic-sober | Libre Baskerville | Libre Baskerville | prose + formulas |
| Analytical report-style | Editorial-serious | Crimson Pro | Inter | dense tables/charts |
| Town-hall / all-hands | Warm-conversational | Inter | Inter | KPIs grandes, emotivo |

These are starting points, not mandates. Break them when the brief
calls for it. The point is **never default to python-pptx's blank
Calibri-on-white template**.

### When this skill is not the right fit

- **Single-page posters / covers / certificates** — composition-
  dominated static artifacts belong to `canvas-craft`, not here.
- **Interactive dashboards in a browser** — `web-craft` handles those.

## 2. Aspect ratio

Decks ship in **16:9 (10 × 5.625 inches)** by default. Legacy 4:3
(10 × 7.5 inches) is reserved for decks that will be projected on
old hardware or embedded in older document templates. Never mix
aspect ratios within the same deck.

`python-pptx` creates 16:9 decks by default when you load the bundled
scaffold (`assets/blank.pptx`). If you skip the scaffold and call
`Presentation()` directly, you'll get python-pptx's built-in template
which is **4:3** — always load the scaffold unless a user-provided
template dictates otherwise.

If the user provides their own corporate `.pptx` or `.potx` template
(see §12), load that instead; the template's master sets the aspect
ratio.

## 3. Theme application

Design tokens (colors, typography, sizes) do not live in this skill —
they come from the theme chosen for the deck.

- If a centralized theming skill is available (brand-kit-style),
  run its workflow BEFORE authoring; it returns a token set that maps
  onto the `DESIGN` dict below.
- Otherwise, improvise tokens coherent with the deliverable following
  the tonal palette roles in `skills-guides/visual-craftsmanship.md`.

The `DESIGN` dict in the scaffold uses placeholders — fill them from
the theme, don't hard-code.

## 4. A proper starting template

Instead of reaching for `python-pptx` defaults, use this scaffold
and adapt:

```python
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt, Emu

# 1. Commit to the design tokens up front — they never change mid-deck.
#    Fill these from the chosen theme (see §3).
SCAFFOLD = Path(__file__).parent / "assets" / "blank.pptx"

DESIGN = {
    # Palette (hex — convert to RGBColor at use site)
    "primary":     "<hex>",   # titles, rules, primary accents
    "accent":      "<hex>",   # pops, CTAs, highlight bars
    "ink":         "<hex>",   # body text
    "muted":       "<hex>",   # captions, metadata
    "rule":        "<hex>",   # dividers
    "bg":          "<hex>",   # slide background
    "bg_alt":      "<hex>",   # secondary surfaces, table bands
    # Typography
    "display":     "<font-family>",
    "body":        "<font-family>",
    # Sizes (pt)
    "size_title":    <pt>,
    "size_subtitle": <pt>,
    "size_heading":  <pt>,
    "size_body":     <pt>,
    "size_small":    <pt>,
}

def hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

# 2. Load the scaffold — it's 16:9 and has a clean blank layout.
prs = Presentation(str(SCAFFOLD))

# 3. Derive safe-area constants dynamically from the slide size.
SLIDE_W = prs.slide_width or Inches(10).emu
SLIDE_H = prs.slide_height or Inches(5.625).emu
MARGIN = Inches(0.5)
TITLE_TOP = Inches(0.4)
TITLE_H = Inches(0.9)
CONTENT_TOP = TITLE_TOP + TITLE_H + Inches(0.2)
CONTENT_H = SLIDE_H - CONTENT_TOP - Inches(0.5)
CONTENT_W = SLIDE_W - 2 * MARGIN
BLANK_LAYOUT = prs.slide_layouts[6]  # index 6 is Blank in the bundled scaffold

# 4. Small helpers (in real use, lift these into your own utils module).
def add_title(slide, text: str) -> None:
    box = slide.shapes.add_textbox(MARGIN, TITLE_TOP, CONTENT_W, TITLE_H)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = DESIGN["display"]
    run.font.size = Pt(DESIGN["size_title"])
    run.font.bold = True
    run.font.color.rgb = hex_to_rgb(DESIGN["primary"])

def add_accent_bar(slide, width_in: float = 1.6, height_in: float = 0.08) -> None:
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN, TITLE_TOP + TITLE_H + Emu(10000),
        Inches(width_in), Inches(height_in),
    )
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = hex_to_rgb(DESIGN["accent"])

# 5. Build slides.
cover = prs.slides.add_slide(BLANK_LAYOUT)
add_title(cover, "The deck title")
add_accent_bar(cover)

content = prs.slides.add_slide(BLANK_LAYOUT)
add_title(content, "Section heading")
# ... add bullets, tables, figures etc.

prs.save("output.pptx")
```

Three rules the scaffold enforces:

- **Always `slide_layouts[6]` (Blank)**. Other layouts embed
  placeholders that fight your design. Position everything
  explicitly with `add_textbox` / `add_shape`.
- **Always `text_frame.word_wrap = True`**. It's off by default;
  without it, python-pptx silently clips overflow.
- **Always compute safe-area from `prs.slide_width / slide_height`.**
  Hardcoded 4:3 constants will break on a 16:9 scaffold and vice versa.

## 5. Fonts

PPT uses the reader's system fonts unless you embed them in
`ppt/fonts/`. Consequences:

- **Default path**: use widely-installed typefaces (Calibri, Aptos,
  Inter, Arial, Times New Roman, Georgia, Cambria). Works everywhere
  without extra steps.
- **Embed path**: technically possible by writing to `ppt/fonts/` and
  referencing in `embeddedFontLst`, but only fully honoured by Word-
  family PowerPoint 2016+ on Windows. Mac Office silently ignores
  embedded fonts; LibreOffice is partial; Web Office substitutes.

Recommendation: stick to safe defaults unless the deck is only going
to be opened by Windows PowerPoint. Inform the user if a chosen
pairing requires a non-standard face (e.g. "IBM Plex Serif + IBM
Plex Mono works on Windows, renders as substitution on Mac").

## 6. Palette guidance

A designed deck has at most three colour families on any given slide:
primary (one accent colour, saturated, used for 5–15% of surface),
neutral (body text and backgrounds), and state colours
(success/warning/danger) used sparingly for KPIs or callouts.

Never mix two different blues, two different reds, or two different
accent saturations in the same deck. Commit to concrete values up
front and apply them uniformly across every slide.

Where those concrete values come from depends on what the agent has:

- If a centralized theming skill is available, the chosen theme
  supplies a complete, coherent token set (primary, accent, ink,
  muted, rule, bg, bg_alt, typography, sizes). Use it verbatim.
- Otherwise, improvise from the tonal palette roles in
  `skills-guides/visual-craftsmanship.md`.

## 7. Slide types you'll build

Below are the compositions worth mastering. Snippets for each live
in `REFERENCE.md`; here is the menu.

- **Cover** — title, subtitle, author, date, accent bar. No other
  content.
- **Agenda** — a numbered list of sections, each with a one-line
  summary. Keep to 3–7 items; more means the deck is too long.
- **Section divider** — bold oversized section name, often with the
  section number ("01 / 05"). Forces the audience to reset their
  attention between chunks.
- **Title + content** — a single heading and 3–7 bullets or a short
  paragraph. The workhorse slide.
- **Two-column** — parallel lists or pro/con or problem/solution.
- **Image with text** — hero image (left or right) with a title and
  short caption on the other side.
- **KPI slide** — one large number (36–54 pt), a concise label, an
  optional unit; or a 3-across KPI row.
- **Table** — structured data, 3–10 rows typical; more than 15 rows
  usually means it belongs on a full page, not a slide. See §7 on
  the table-style override you must apply.
- **Chart** — native OOXML chart for bar/column/line/pie/area/
  scatter/radar/bubble (editable by the user); pre-rendered image
  for anything python-pptx doesn't support (waterfall, sunburst,
  sankey, combo).
- **Quote** — one sentence, attribution, visual whitespace.
  Typography is the subject of the slide.
- **Conclusion / call to action** — 3 bullets or 1 headline + the
  next-step line. Avoid "Thank you" as the final slide; end on the
  message.

## 8. Tables

`python-pptx` tables inherit a pastel theme style by default that
looks like Microsoft's 2003-era default. **Always override it
aggressively**. The baseline override, in words:

- Header row: filled with the primary colour, text white, bold,
  body or display face at 16–18 pt, left-aligned for prose columns
  and right-aligned for numerics.
- Body rows: no vertical grid lines, a subtle horizontal rule
  between rows, alternating band colour (white / `bg_alt`) for
  readability.
- Row height: slightly generous (12–15 pt of padding inside cells);
  cramped rows read as a spreadsheet screenshot.

The full snippet lives in `REFERENCE.md` §Table with style override;
call it from every table-producing slide.

## 9. Images

Placed via `slide.shapes.add_picture(path, left, top, width, height)`.
Two rules:

- **Never distort the aspect ratio.** Compute target dimensions so
  that the image fits inside a safe-area box while preserving
  proportions. Helper snippet in `REFERENCE.md` §Image with
  preserved aspect ratio.
- **Prefer transparent-background PNG** when the slide has a non-
  white background; a JPG with baked-in white will leave a visible
  rectangle. Render charts from matplotlib / plotly with
  `dpi=200, facecolor="none"` before inserting.

## 10. Charts

PPT charts have a huge quality-of-life advantage over images: the
user can double-click them and edit the underlying data in an
Excel-like dialog. For any chart type python-pptx supports, prefer
a native chart over a rendered image.

Supported types:

| Type | python-pptx enum | When to use |
|---|---|---|
| Column / bar | `XL_CHART_TYPE.COLUMN_CLUSTERED`, `BAR_CLUSTERED` | comparing categories |
| Line | `XL_CHART_TYPE.LINE` | trend over time |
| Pie / doughnut | `XL_CHART_TYPE.PIE`, `DOUGHNUT` | 3–6 part-of-whole slices |
| Area | `XL_CHART_TYPE.AREA` | cumulative over time |
| Scatter | `XL_CHART_TYPE.XY_SCATTER` | correlation |
| Radar | `XL_CHART_TYPE.RADAR` | multi-dimensional comparison |
| Bubble | `XL_CHART_TYPE.BUBBLE` | three-variable scatter |

Not supported (use pre-rendered image instead):

- Waterfall, sunburst, sankey, combo (bar+line on same chart), map
  charts, funnel, histograms with custom binning.

Snippet in `REFERENCE.md` §Native OOXML chart — bar / column / line.

## 11. Speaker notes

Pitch decks, executive briefings, training decks and academic
presentations all live by their speaker notes — the verbal script
that accompanies the visual. A deck generated without notes is a
half-delivery for these categories.

```python
slide.notes_slide.notes_text_frame.text = "The spoken narrative for this slide."
```

Multi-paragraph notes are supported; separate with `\n` or call
`add_paragraph()` for richer structure. Speaker notes inherit
python-pptx's default font; you rarely need to style them.

For pitch and training decks, treat "generate speaker notes"
as part of the task definition, not a bonus.

## 12. Post-build validation and PDF export

After building, always verify the result. Three snippets in
`REFERENCE.md`:

- **Structural validation** (§Structural validation): reopen the
  saved PPTX and emit a manifest — slides, aspect ratio, shapes by
  type (text / picture / table / chart / other), speaker-notes
  coverage, and whether every text frame has `word_wrap=True`
  (overflow safety). Catches corruption, clipped text frames or
  missing slides *before* the deck ships. Runs in ~100 ms; do it on
  every build.
- **Visual validation** (§Visual validation): convert to PDF via
  LibreOffice and rasterize per-slide PNGs with `pdftoppm`. Inspect
  each PNG for overflow, awkward contrast, cramped spacing, broken
  images. Regenerate and re-validate; 2–3 iterations is normal.
- **PDF export** (§Export PDF): one-liner via
  `soffice --headless --convert-to pdf`. Default deliverable is the
  PPTX on its own. Only add a sibling PDF when the user explicitly
  asks for it or when the brief clearly implies distribution outside
  PowerPoint (external share, email attachment, audience without
  Office, "I'll send it around", publication). If you're not sure,
  deliver only the PPTX — the user can ask for the PDF afterwards.

Visual validation and PDF export require `libreoffice` and
`poppler-utils`. Structural validation only needs `python-pptx`.

## 13. User-provided templates (`.potx` / `.pptx`)

When a user provides a corporate template — with their logo, master
slide, fonts and colour palette — ignore the scaffold and load
their file:

```python
from pptx import Presentation
prs = Presentation("path/to/client_template.pptx")

# Inspect the layouts the template provides. Corporate templates
# usually ship 5–10 named layouts: Cover, Section, Title+Content,
# Image+Caption, Two-Column, Table, KPI, Thanks.
for i, layout in enumerate(prs.slide_layouts):
    print(i, layout.name)

# Pick layouts that match your intent. Respect the placeholders —
# the template's designer positioned them for a reason.
cover = prs.slides.add_slide(prs.slide_layouts[0])
cover.placeholders[0].text = "The deck title"  # title placeholder
if len(cover.placeholders) > 1:
    cover.placeholders[1].text = "Subtitle / date / author"

content = prs.slides.add_slide(prs.slide_layouts[2])
content.placeholders[0].text = "Section heading"
# The content placeholder is usually index 1; its text frame accepts
# bullets via paragraphs with p.level.
```

When using a client template:

- **Do not override the master**. The colours, fonts and logo are
  the template's identity.
- **Do not use `slide_layouts[6]` (Blank).** The whole point of the
  template is its designed layouts.
- **Do use `placeholders`** rather than `add_textbox`. The template
  designed the placeholders' positions.
- **Still enforce `word_wrap = True`** and still validate visually.

Snippet in `REFERENCE.md` §Using a client template.

## 14. Structural operations

For manipulating existing decks (merge, split, reorder, delete,
find-replace across slides and notes, convert legacy `.ppt`), see
`STRUCTURAL_OPS.md`. Those are copy-paste snippets; run them from
a small script, don't try to import them as a module.

## 15. Known limitations

`python-pptx` covers ~80% of real-world deck authoring cleanly. The
remaining 20% either needs raw OOXML manipulation or is not
supported at all:

- **Animations and slide transitions** — not supported. A snippet
  for the simplest fade transition exists in `REFERENCE.md` but is
  fragile; prefer no transitions in generated decks.
- **SmartArt** — not supported. Draw the equivalent with
  `add_shape` calls (arrows between rectangles for a process flow,
  stacked rectangles for a hierarchy).
- **Embedded videos / audio** — writing works but many renderers
  drop them silently. Not recommended.
- **Macros (VBA)** — `.pptx` has no VBA. If the user needs macros,
  the file has to be `.pptm` and that is out of scope.
- **Advanced chart types** (waterfall, sunburst, sankey, combo) —
  render as image.
- **Exact-font rendering on every machine** — see §4.

Document the limitation in the deck's speaker notes or a brief
appendix slide when it affects the deliverable.

## 16. Quick-reference cheat sheet

| Task | Approach |
|---|---|
| Create deck | `Presentation("assets/blank.pptx")` then add slides from `slide_layouts[6]` |
| New slide | `prs.slides.add_slide(BLANK_LAYOUT)` |
| Title text | `add_textbox(...).text_frame` with `word_wrap=True` |
| Bullet list | text frame with one paragraph per bullet, `p.level` for indent |
| Table with design override | see `REFERENCE.md` §Table with style override |
| Image preserving aspect | see `REFERENCE.md` §Image with preserved aspect ratio |
| KPI box | see `REFERENCE.md` §KPI box |
| Native chart | see `REFERENCE.md` §Native OOXML chart |
| Speaker notes | `slide.notes_slide.notes_text_frame.text = "..."` |
| Visual preview | `soffice --convert-to pdf` + `pdftoppm -r 150` |
| Export PDF | `soffice --headless --convert-to pdf out.pptx` |
| Merge / split / reorder | see `STRUCTURAL_OPS.md` |
| Convert `.ppt` legacy | `soffice --headless --convert-to pptx old.ppt` |
| User template | load `.pptx`/`.potx` directly as scaffold |

## 17. When to load REFERENCE.md

- Full snippets for each slide type (cover, agenda, section divider,
  title+content, bullets, two-column, image-with-text, KPI,
  table-with-override, chart, quote, conclusion)
- Native OOXML chart construction for bar / column / line / pie /
  area / scatter / radar / bubble
- Dynamic safe-area helpers working for any aspect ratio
- Visual validation pipeline (PPTX → PDF → PNG per slide)
- PDF export one-liner
- i18n labels (English / Spanish) for Agenda / Conclusions / Slide N of M
- Using a client template (`.potx` / `.pptx`) — navigating layouts
  and placeholders
