# brand-kit

Centralized catalog of visual identity (colors, typography, chart
palettes, sizing, tone) that every output skill in the monorepo
(`docx-writer`, `pptx-writer`, `pdf-writer`, `web-craft`,
`canvas-craft`) knows how to consume. Ships with **10 curated themes**
and is **extensible by the client**: add your own themes following the
guide at the end of this file.

## What this solves

When an agent is about to generate a visual deliverable — a DOCX report,
a PPTX deck, a landing page, a PDF brief — it needs coherent design
tokens: a primary color, a display font, a chart palette, a tone. Before
this skill existed, every output skill defined its own inline example
palette, values drifted between skills, and clients had no single place
to say "here is my brand". `brand-kit` fixes that: one place for tokens,
every output skill consumes the same contract.

## Themes shipped

| Theme | Tone family | Best for |
|---|---|---|
| [editorial-serious](themes/editorial-serious.md) | editorial-serious | long-form analytical reports, legal briefs, policy |
| [technical-minimal](themes/technical-minimal.md) | technical-minimal | dashboards, engineering docs, runbooks |
| [warm-magazine](themes/warm-magazine.md) | warm-magazine | communications, marketing, storytelling |
| [forensic-audit](themes/forensic-audit.md) | forensic-audit | audit, compliance, security reports |
| [academic-sober](themes/academic-sober.md) | editorial-serious | research papers, whitepapers, policy |
| [modern-product](themes/modern-product.md) | technical-minimal | product decks, launches, pitch |
| [brutalist-raw](themes/brutalist-raw.md) | brutalist-raw | data dumps, developer reports, exploratory |
| [luxury-refined](themes/luxury-refined.md) | luxury-refined | board decks, executive summaries |
| [industrial-utilitarian](themes/industrial-utilitarian.md) | industrial-utilitarian | operations reports, logistics, SRE |
| [corporate-formal](themes/corporate-formal.md) | editorial-serious | steering committees, regulated reporting |

Each theme file contains the full token set: the 10 core colors, the
chart categorical palette, the typography block (families + sizes +
fallbacks), tone family, recommended use cases, and anti-patterns.

## How agents use it

When the agent is about to generate any visual deliverable, it runs
this flow:

1. Presents the catalog above to the user.
2. Asks whether to use one of the predefined themes, define an ad-hoc
   theme (providing hex codes and fonts directly), or point to an
   external brand file as a scaffold.
3. Loads the chosen theme (or derives it from the user's inputs).
4. Passes the tokens to the output skill that generates the artifact.

The full flow lives in `SKILL.md` (the contract the LLM follows). This
README is for you, the human reading the repo.

## Adding your own theme

### 1. Duplicate an existing theme as a template

`editorial-serious.md` is the most neutral starting point:

```
cp themes/editorial-serious.md themes/acme-corporate.md
```

The filename is the **technical identifier** — kebab-case, preferably
in English (the identifier stays the same across language overlays).

### 2. Fill in the tokens

Open the new file and replace the values. **Keep the token names
exactly as they are** — the output skills look them up by name:

**Core (mandatory, do not omit):**
- 10 colors: `primary`, `ink`, `muted`, `rule`, `bg`, `bg_alt`,
  `accent`, `state_ok`, `state_warn`, `state_danger`
- 3 font families with fallbacks: `display`, `body`, `mono`
- 4 point sizes: `h1`, `h2`, `body`, `caption`
- Chart categorical palette: 5–8 ordered hex colors

**Optional extensions (skip if not applicable):**
- `motion_budget` (`minimal` / `restrained` / `expressive`)
- `radius` (pixels, for web-craft)
- `dark_mode` (subset with dark-variant `primary` / `ink` / `bg` /
  `accent`)
- `chart_sequential` (base color for heatmaps / sequential scales)
- `print` (subset of tokens tuned for printed PDF: warm `paper` instead
  of pure white, warm near-black `ink`, warmer hairlines — consumed by
  `pdf-writer`. Declare it if the theme will be used in print and the
  screen values would degrade on paper)

The `## Tone family` section should point to one of the eight tones
defined in `skills-guides/visual-craftsmanship.md`
(`editorial-serious`, `technical-minimal`, `warm-magazine`,
`brutalist-raw`, `luxury-refined`, `industrial-utilitarian`,
`playful-toy`, `forensic-audit`), or declare a new tone with a short
description.

### 3. Register the theme in TWO places

Add a row for the new theme in both tables so the catalog stays
consistent:

1. The **"Themes shipped"** table in this `README.md` (so humans see
   it when they open the folder).
2. The **"Available themes"** table in `SKILL.md` (so the agent
   discovers it when the skill is loaded).

With those two entries in place, any agent that includes `brand-kit`
will offer the new theme as a regular option, exactly like the bundled
ten.

## Your brand does not HAVE to live here

If you prefer to keep client branding in a dedicated skill (e.g.
`<agent>/skills/acme-brand-kit/`), the output skills consume it the
same way — they reference the concept of a centralized theming skill
without naming `brand-kit`. The `local skill wins` rule in the monorepo
guarantees that a local `brand-kit` (or an `acme-brand-kit`) overrides
this shared one for that agent.

## Anti-patterns when extending

- **Do not rename core tokens** — output skills look them up by name.
- **Do not embed images or logos in the theme file** — a theme defines
  tokens, not assets.
- **Do not invent tokens outside the contract** — unknown keys are
  silently ignored.
- For translations, use the `es/` overlay instead of mixing languages
  inside a file.
