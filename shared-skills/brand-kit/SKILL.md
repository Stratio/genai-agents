---
name: brand-kit
description: "Centralized catalog of visual identity themes (colors, typography, tone, chart palettes, sizing) that any output skill (docx-writer, pptx-writer, pdf-writer, web-craft, canvas-craft) consumes to produce branded deliverables. Ships with 10 curated themes and is extensible — clients can add their own themes as individual markdown files. Use this skill before generating any visual deliverable to fix the brand tokens the output skills will apply."
argument-hint: "[theme name | 'custom' | 'scaffold']"
---

# Skill: brand-kit

Branding lives in one place. This skill provides a curated catalog of
visual identity themes — each one a complete, coherent bundle of colors,
typography, chart palettes, sizing and tone — that any output skill knows
how to consume. Pick a theme once and every downstream artifact (DOCX,
PPTX, PDF, web, single-page visual) inherits it consistently.

The skill does not generate artifacts by itself. It provides tokens.

## Available themes

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

The catalog lives inline here so the agent sees it the moment the skill
is loaded — no extra file read needed to present the options.

## Workflow (invoke this BEFORE any output skill with visual dimension)

Whenever the agent is about to generate a deliverable that has any visual
expression (DOCX report, PPTX deck, PDF document, HTML landing, single-page
PDF/PNG), run this flow first to fix the brand tokens. Skipping this step
produces inconsistent artifacts — different fonts, different accents, no
shared chart palette across the same project.

### 1. Present the catalog to the user

Show the user the "Available themes" table above. Keep the presentation
brief — one line per theme with `Theme · Tone · Best for` is enough.

### 2. Ask which source the user wants

Following the agent's question convention, offer three paths:

- **Predefined theme** — pick one from the catalog by name.
- **Ad-hoc custom** — user provides colors (hex codes) and fonts directly
  in the conversation. Map the inputs into the canonical token contract
  (see §Token contract below).
- **External scaffold** — user points to a file (PDF brand guide, client
  branding document, design memo). Read the file and derive tokens from
  it — again, normalizing to the canonical contract.

### 3. Load the chosen theme

If a predefined theme was chosen, read `themes/<name>.md` — that file
contains the full token set. If the user provided custom inputs or a
scaffold, build the same structure in memory from those inputs.

### 4. Pass tokens to the output skill

When you invoke the downstream output skill (docx-writer, pptx-writer,
pdf-writer, web-craft, canvas-craft), supply the loaded tokens. Each
output skill knows how to map the canonical tokens to its native format
(Python dict for python-docx / python-pptx, HexColor for reportlab, CSS
custom properties for web).

## Token contract

Every theme file follows the same contract so the output skills can
consume any theme interchangeably. The contract has a **core** (mandatory)
and **optional extensions**.

### Core (every theme must provide these)

**Colors** (10 hex tokens):

| Token | Role |
|---|---|
| `primary` | titles, top rules, cover accents |
| `ink` | body text (rarely pure black — kinder mid-slate works better) |
| `muted` | captions, footnotes, secondary text |
| `rule` | thin dividers, subtle borders |
| `bg` | page / main surface |
| `bg_alt` | table bands, callout fills, alternate surfaces |
| `accent` | CTAs, highlights, intentional pops (5–15 % of surface) |
| `state_ok` | positive indicators |
| `state_warn` | alerts |
| `state_danger` | critical errors |

**Typography** (3 families + 4 sizes):

| Token | Role |
|---|---|
| `display` | h1/h2/cover — usually the most expressive face |
| `body` | paragraph copy |
| `mono` | code, numerals in tables, technical strings |
| `size_h1`, `size_h2`, `size_body`, `size_caption` | point sizes |

Every font entry names a fallback stack so the theme degrades gracefully
when the primary family is not available.

**Chart categorical palette**: an ordered list of 5–8 hex colors, curated
so the first N look balanced for any N series count. The first two
entries commonly coincide with `primary` and `accent` to keep charts in
conversation with the rest of the artifact.

### Optional extensions (themes may provide; output skills consume if present)

- `motion_budget` — `"minimal"` / `"restrained"` / `"expressive"`. Used
  by web-craft for transitions and pptx animations.
- `radius` — border-radius in pixels. Used by web-craft.
- `dark_mode` — subset providing dark-mode `primary` / `ink` / `bg` /
  `accent`. Used by web-craft when a dark variant is requested. If the
  theme omits `dark_mode` and a dark variant is needed, derive it by
  inverting `bg` ↔ `ink` while keeping `primary` / `accent`.
- `chart_sequential` — base color for sequential / heatmap scales.
- `print` — subset of tokens tuned for printed PDF delivery (`paper`,
  `ink`, `rule`, optionally `accent`). Used by `pdf-writer`. Declare it
  when the screen tokens would degrade on paper (pure white `bg` or
  pure black `ink`). If absent, `pdf-writer` applies generic print
  sensibilities.

## Custom and external themes (when none of the 10 fit)

If the user provides their own brand (ad-hoc hex + fonts, or an
external brand file as scaffold), fold it into the same contract
before handing off. Keep the user's explicit values and fill the
gaps with coordinated defaults:

- `ink`, `muted`, `rule`: neutrals derived from or tuned against
  `primary` (a softer dark slate, a low-chroma mid-gray, a pale tint).
- `bg`/`bg_alt`: near-white and a 2–4 % tint of it.
- State colors: semantic (green / amber / red), tuned to the theme's
  warmth.
- Chart categorical: start with `primary` and `accent`, extend to
  5–8 hues with wide perceptual separation.

Show the derived set back to the user for confirmation before
handing off.

## Extensibility

The token contract is stable: clients can add their own theme files in
`themes/` (same structure as the shipped ones) or keep their branding
in a separate local skill. Output skills reference "centralized theming
skill" generically — the `local skill wins` rule in the monorepo makes
a local `<agent>/skills/<brand>/` override this shared one when both
exist.

## When this skill is NOT the right tool

- **No visual artifact** (pure chat answer, SQL query, code refactor).
  Skip the skill.
- **The agent's AGENTS.md pins a single theme.** Load it directly and
  skip the user question.
