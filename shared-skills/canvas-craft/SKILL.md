---
name: canvas-craft
description: "Create single-page visual artifacts — posters, covers, certificates, marketing one-pagers, infographics — as PDF or PNG. Produces pieces where composition dominates over prose: typography becomes a visual element, imagery and form carry meaning. Use when the user asks for a visual piece rather than a document or an interface."
argument-hint: "[poster|cover|certificate|infographic|one-pager] [brief]"
---

# Skill: Canvas Craft

Guide for producing single-page visual artifacts rendered as PDF or PNG. The artifact is static, visually led, and treats typography as part of the composition rather than a vehicle for long prose.

**Scope**: this skill handles single-page pieces where roughly seventy per cent or more of the surface is visual composition — colour, form, typography-as-shape. For multi-page typographic documents (analytical reports, contracts, invoices, zines) the output is a document and belongs to a different tool. For interactive browser artifacts (components, pages, dashboards) the artifact is alive in a browser and also belongs to a different tool. When uncertain, consult `skills-guides/visual-craftsmanship.md` for the selection criterion.

## 1. Read the foundation

Read and follow `skills-guides/visual-craftsmanship.md`. It defines the shared principles, anti-patterns, palette roles, type pairing philosophy and craftsmanship checklist used across every visual skill in this monorepo. This skill adds the canvas-specific workflow on top.

## 2. Two-step workflow

Canvas artifacts are made in two passes: a brief philosophy that sets the visual intent, then the piece itself.

### Step A — Declare the visual philosophy

Write a short aesthetic manifesto (3–5 paragraphs) that names the visual world the artifact inhabits. The manifesto is private to the session — it is not the output — but it disciplines every subsequent choice. Save it as a `.md` file alongside the final artifact for traceability.

The manifesto should include:
- **A movement name** (one or two words of your own invention — for example *Granite Ink*, *Slow Signal*, *Weathered Plate*, *Quiet Architecture*, *Sun-Printed*). Do not reuse names from other sources.
- **Form and space**: how the composition breathes, where density lives, what the artifact's skeleton looks like.
- **Colour and material**: the palette, the surface texture (paper grain, risograph misregister, flat coated stock, etched metal, washed ink), and what each colour is asked to do.
- **Scale and rhythm**: which elements are huge, which recede, what the pacing feels like at a glance versus up close.
- **Typography as element**: how type participates in the composition — as display block, as caption anchor, as spatial marker, as texture.

Keep it specific enough to disqualify the wrong choices, open enough to let the composition emerge. A well-written manifesto lets a sibling artifact be produced later with a coherent family feel.

### Step B — Express the philosophy on the canvas

With the manifesto in hand, build the piece. Work through these decisions explicitly:

- **Page size**: A4, A3, A2, Letter, Tabloid, square (1080×1080 for social). Commit before composing — resizing later destroys spatial decisions.
- **Margins and safe area**: generous margins; nothing touches the edge unless the composition intends to bleed. Leave breathing room.
- **Grid and anchoring**: even without visible rules, a three-column or five-column grid keeps the composition deliberate. One grid-breaking element per page is enough.
- **Hierarchy**: at most three focal levels (hero, secondary, anchor). Everything else serves these.
- **Typography**: usually two typefaces, sometimes one, rarely three. At least one appears as a visual element — large, cropped, interacting with shapes.
- **Imagery and form**: original forms, abstractions, patterns. If using photography, crop boldly or strip to silhouette. Avoid stock aesthetics.
- **Text density**: minimal. A title, a subtitle, a small set of anchoring strings. No paragraphs. If the piece needs paragraphs, it is probably not a canvas artifact.

## 3. Tooling

Canvas artifacts in this monorepo are built in Python:

- **PDF**: `reportlab`. Register custom fonts from `fonts/` at the top of every script using `TTFont` and `registerFontFamily`.
- **PNG**: render the reportlab PDF first, then convert to PNG at 300 DPI with `pdf2image` (which wraps Poppler). One source of truth for both formats.

```python
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

FONTS_DIR = Path(__file__).parent / "fonts"

def register_fonts():
    pdfmetrics.registerFont(TTFont("Fraunces", FONTS_DIR / "Fraunces-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Fraunces-Bold", FONTS_DIR / "Fraunces-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Fraunces-It", FONTS_DIR / "Fraunces-Italic.ttf"))
    registerFontFamily("Fraunces", normal="Fraunces", bold="Fraunces-Bold",
                       italic="Fraunces-It")
    # register only the families you will actually use
```

To produce a PNG alongside the PDF:

```python
from pdf2image import convert_from_path

images = convert_from_path("output.pdf", dpi=300)
images[0].save("output.png", "PNG")
```

Never rely on reportlab's built-in Helvetica for final artifacts. Those faces produce the flat default look this skill actively resists.

### Canvas-specific palette

Artifacts rendered for print benefit from:
- Deep neutrals that are not `#000` (warm espresso, cold indigo, blue-black).
- Off-whites as backgrounds rather than pure `#fff`. Bone, cream, paper, clay.
- Saturation that survives print compression. Pastels tend to wash out; deeper tones hold.

Define RGB in `0–1` floats for reportlab (`colors.Color(0.85, 0.27, 0.17)`). Keep the palette to four declared colours or fewer.

## 4. Combined pipeline: cover + body

When the brief is a report with a designed cover, this skill produces the cover page only. The multi-page body is assembled by the typographic document tool (see `skills-guides/visual-craftsmanship.md` for the selection criterion). Final merge with `pypdf`:

```python
from pypdf import PdfWriter
writer = PdfWriter()
writer.append("cover.pdf")
writer.append("body.pdf")
writer.write("final.pdf")
```

Keep the cover's last page margins consistent with the body's first page for a clean transition.

## 5. Fonts

Use the curated OFL families bundled in `fonts/`. The set covers an editorial serif display, a heavy sans display, and a refined contemporary serif — enough range for type-as-element compositions. Expand the set when a brief needs a mono or a playful display face (see `fonts/README.md` §"Extending the set").

See `fonts/README.md` for the family list, source, download date and commit SHA. Each family is accompanied by its `OFL.txt`. To redistribute an artifact using these fonts in external contexts, include the OFL.txt for each family used.

Do not mix more than three families. Two is almost always enough.

## 6. Final pass

Work the craftsmanship checklist from `visual-craftsmanship.md` before declaring done:
- Margins honour the grid. Nothing falls off the page. Nothing overlaps unintentionally.
- The piece reads at a glance: the hero moment arrives first, the secondary information supports it, the anchor text is legible without effort.
- Typography appears in the weights and styles chosen; no default weight slipped into a heading.
- The palette appears in the declared proportions — the accent is not spreading into the background.
- No stock patterns, no placeholder imagery, no Lorem.
- The composition feels deliberate at a metre's distance and rewards closer inspection.

**Polish over addition.** If the instinct is to add another shape or typographic flourish, refine what is already on the page instead.

When multiple pages are requested, treat each as a related piece within the same visual world — the manifesto should carry across, with each page offering a distinct composition rather than a template variant.
