# Bundled Fonts

All fonts in this directory are distributed under the **SIL Open Font
License 1.1** (OFL). You are free to use, modify, and redistribute them
as part of this skill's output PDFs, including for commercial purposes.

The per-family license texts are in the `*-OFL.txt` files.

## Font inventory

### Serif body faces — long-form reading

- **Crimson Pro** — modern literary serif, excellent on screen and print
- **Lora** — warm contemporary serif, slightly calligraphic
- **Libre Baskerville** — refined classical serif, formal documents
- **IBM Plex Serif** — neutral technical serif (part of the IBM Plex superfamily)

### Sans-serif faces — UI, display, technical docs

- **Instrument Sans** — geometric sans with subtle humanist warmth
- **Work Sans** — workhorse sans, versatile
- **Outfit** — rounded modern sans, approachable

### Display faces — headlines, titles, posters

- **Instrument Serif** — high-contrast editorial serif, beautiful at large sizes
- **Big Shoulders** — condensed display sans, strong editorial presence
- **Italiana** — airy didone, ceremonial / luxurious tone
- **Young Serif** — bold friendly serif, good for warm headlines

### Monospace — figures, code, tabular data

- **JetBrains Mono** — developer-favorite mono with great readability
- **IBM Plex Mono** — matching mono from the IBM Plex family
- **DM Mono** — geometric mono, clean and understated

## License notes

- Most fonts here include their `*-OFL.txt` file alongside.
- **IBM Plex family** (Serif and Mono) are released by IBM under OFL 1.1.
  The canonical license text is published at
  https://github.com/IBM/plex and reproduced in `OFL.txt` at the root
  of this `fonts/` directory when present.
- **Instrument Serif** is bundled without a separate OFL file because
  it was originally released alongside Instrument Sans under the same
  OFL grant — the `InstrumentSans-OFL.txt` applies to both families.

## Recommended pairings

| Context | Display | Body | Mono |
|---|---|---|---|
| Literary report | Instrument Serif | Crimson Pro | IBM Plex Mono |
| Financial doc | Instrument Sans Bold | IBM Plex Serif | IBM Plex Mono |
| Invoice / receipt | Instrument Sans Bold | Instrument Sans | JetBrains Mono |
| Newsletter | Big Shoulders | Lora | — |
| Formal certificate | Italiana | Libre Baskerville | — |
| Technical doc | Outfit Bold | IBM Plex Serif | IBM Plex Mono |
| Friendly report | Young Serif | Lora | DM Mono |

## Registering fonts in reportlab

See the main `SKILL.md` for the full pattern. Minimal example:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

FONTS = Path(__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Body", FONTS / "CrimsonPro-Regular.ttf"))
```

Only register the faces you actually use — every registration embeds
the font data into the output PDF.

## Adding more fonts

To extend this library with additional OFL fonts:

1. Download the TTF files from the font's official source (Google
   Fonts, GitHub, etc.).
2. Copy the TTFs into this directory.
3. Copy the license text as `<FamilyName>-OFL.txt` alongside.
4. Add an entry to this README under the appropriate category.

Only use OFL-licensed fonts or fonts with equivalently permissive
licenses. Commercial fonts from foundries require per-use licensing
and cannot be bundled here.
