# Canvas Craft — Font Set

Curated OFL font families bundled with `canvas-craft`. Chosen for single-page visual artifacts: editorial display, heavy sans display, and refined serif for type-as-element compositions.

## Families

| Family | Role | Files | Licence | Source | Commit SHA | Retrieved |
|---|---|---|---|---|---|---|
| Fraunces (variable) | Editorial serif display with optical-size, weight and wonk axes | `Fraunces-Variable.ttf`, `Fraunces-Italic-Variable.ttf` | OFL 1.1 | https://github.com/undercasetype/Fraunces (upstream); binary retrieved from `googlefonts/fraunces` mirror | `ad58030f7daa` | 2026-04-20 |
| Archivo Black | Heavy sans display for punctuating visual composition | `Archivo-Black.ttf`, `Archivo-BlackItalic.ttf` | OFL 1.1 | https://github.com/Omnibus-Type/Archivo | `b5d63988ce19` | 2026-04-20 |
| Instrument Serif | Refined contemporary serif for display moments and anchors | `InstrumentSerif-Regular.ttf`, `InstrumentSerif-Italic.ttf` | OFL 1.1 | https://github.com/Instrument/instrument-serif | `65c0ef225f38` | 2026-04-20 |

Each family is accompanied by its licence file (`{Family}-OFL.txt`). Redistributing an artifact that embeds these fonts requires keeping the OFL file for each family used.

## Intentional overlap with other visual skills

`Instrument Serif` appears in more than one skill within the same monorepo. The overlap is deliberate — each consumer uses the family for a different purpose (long-form body prose in one, display slices across a composition in another). Keeping each skill with its own copy preserves standalone packaging at a minor duplication cost (~140 KB).

Outside this single family, the set is disjoint from every other visual skill in the monorepo, which lean on body-oriented serifs and a mono (Crimson Pro, IBM Plex Serif, Lora, Libre Baskerville, Work Sans, Young Serif, JetBrains Mono).

## Extending the set

More display families can be added when a specific artifact requires them — candidates include Boldonse (Atipo Foundry), Redaction (Titl Brigade), Playfair Display, DM Serif Display. Download from the foundry's official distribution, include the OFL.txt, and register the family and commit SHA in the table above.

## Not included

- Space Grotesk — intentionally excluded. The family is over-represented in AI-generated output and reads as a default choice rather than a deliberate one.
- Inter, Roboto, Arial, system-ui — not bundled; if a brief requires a generic sans, reach for a distinctive alternative first.
