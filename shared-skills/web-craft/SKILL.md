---
name: web-craft
description: "Build distinctive, production-grade interactive frontends (HTML/CSS/JS, React, Vue) with deliberate aesthetic direction. Use when the user asks for a component, page, landing, dashboard, interactive artifact, or any styled web UI. Produces working code that avoids generic defaults — typography, palette, motion and composition are chosen, not assumed."
argument-hint: "[component|page|dashboard|landing] [purpose or brief]"
---

# Skill: Web Craft

Guide for building interactive web artifacts with real aesthetic intent. The deliverable is code that runs: HTML, CSS, JavaScript; React or Vue components when the surrounding stack calls for it. Every artifact should carry the fingerprint of a deliberate visual choice — not the default look a generator would produce.

The user provides the brief: what to build, who uses it, what technical constraints apply. The scope may be a single component or a full landing page.

**Scope**: this skill handles artifacts that live in a browser and respond to interaction. For single-page static artifacts (posters, covers, certificates, marketing one-pagers, infographics) the artifact is not interactive and belongs to a different tool. For multi-page typographic documents (reports, invoices, contracts, zines) the output is a document, not a web interface, and also belongs to a different tool. When uncertain, consult `skills-guides/visual-craftsmanship.md` for the selection criterion.

## 1. Read the foundation

Read and follow `skills-guides/visual-craftsmanship.md`. It defines the shared principles, anti-patterns, palette roles, type pairing philosophy and craftsmanship checklist used across every visual skill in this monorepo. This skill adds the web-specific decisions on top.

## 2. Decide before coding

Work through the five decisions below before writing markup. Capture the outcome briefly — two or three paragraphs in chat is enough — so the implementation serves a stated intent, not a drifting feel.

### 2.1 Classify the artifact
Pick one:
- **Interactive component** — a discrete element intended to slot into a host (button, card, form, chart block, menu).
- **Page** — a complete page with header, content, and footer as needed.
- **Landing** — a marketing or product page optimised for a single message and a single action.
- **Dashboard** — a data-forward interactive surface (KPIs, filters, charts, tables).
- **Interactive artifact** — an experiential piece: a toy, a demo, a visual experiment.

The class shapes the type pairing, the motion budget, and the expected density of content.

### 2.2 Pick a tone (one, committed)
Choose exactly one:
- Editorial-serious
- Technical-minimal
- Warm-magazine
- Brutalist-raw
- Luxury-refined
- Industrial-utilitarian
- Playful-toy
- Retro-futuristic
- Natural-organic
- Forensic-audit

Uncommitted tone is the single most common cause of generic output. If two tones feel equally right for the brief, force a choice — half-and-half loses both.

The first six tones follow the shared taxonomy in `skills-guides/visual-craftsmanship.md`; the remaining four are web-specific additions that rarely apply to static artifacts.

### 2.3 Choose a type pairing
One display face + one body face, with deliberate contrast. Some pairings that work well in the browser:

| Tone | Display | Body |
|---|---|---|
| Editorial-serious | Fraunces or Instrument Serif | Inter variable or IBM Plex Sans |
| Technical-minimal | Work Sans or Instrument Sans | JetBrains Mono (for numerals) + Inter body |
| Warm-magazine | Big Shoulders Display | Lora |
| Brutalist-raw | Boldonse or Archivo Black | Inter condensed |
| Luxury-refined | Italiana or Fraunces Italic | Crimson Pro |
| Playful-toy | Bungee | Work Sans |
| Natural-organic | Young Serif | Fraunces body |
| Forensic-audit | IBM Plex Mono | IBM Plex Serif |

These are starting points, not mandates. Substitute freely when the brief calls for something else. The point is never to default to Inter + Arial for everything.

Serve fonts through `@import` from Google Fonts or the foundry's official delivery, or bundle WOFF2 alongside the artifact. Do not ship fonts without their licence files if the artifact is for external distribution.

### 2.4 Commit to a palette
One dominant accent, one deep neutral for text (rarely pure black), one pale neutral for backgrounds (not pure white), optional accent colours. Declare the palette in CSS custom properties; never hand-type the same hex twice.

Concrete values come from the theme, not from this skill.

- **If the agent has a centralized theming skill available** (a brand-kit-style skill that ships a catalog of themes plus a workflow for the user to pick or define one), run that workflow BEFORE coding. The chosen theme supplies the token set that maps onto the `:root` below.
- **If no such skill is present**, improvise tokens coherent with the deliverable context, following the tonal palette roles in `skills-guides/visual-craftsmanship.md`.

The `:root` block below uses placeholders to make it clear where the values come from:

```css
:root {
    --accent: <hex>;               /* dominant — sparing, 5–15% of surface */
    --text: <hex>;                 /* deep neutral */
    --surface: <hex>;              /* pale neutral */
    --rule: <hex>;                 /* subtle dividers (often derived from text) */
    --positive: <hex>;             /* state accent — use only for state */
    --negative: <hex>;
}
```

### 2.5 Set rhythm, motion budget and composition
- **Margins and columns**: generous margins communicate confidence; cramped margins read as a word-processor. Decide the baseline grid (often 4 or 8 px).
- **Motion budget**: `none` (static), `minimal` (fade-in on mount, hover transitions), `expressive` (staggered reveal, scroll-triggered, hero transitions). Respect `prefers-reduced-motion: reduce` without exception.
- **Composition**: one hero moment per view is enough. Grid-breaking in one place; strict grid everywhere else. Asymmetry where it serves the content.

## 3. Implement

With the five decisions recorded, write the code. Some practical rules:

### Typography
- Use a variable font where available; fewer HTTP requests, more weight flexibility.
- Establish a modular type scale (for example 1.250 × or 1.333 ×) and stick to it.
- Line-height: 1.4–1.6 for body; 1.05–1.2 for display.
- Avoid text shadows on body copy.

### Colour and theme
- CSS custom properties for everything. Override at `:root` for dark mode via `@media (prefers-color-scheme: dark)` when the design supports it.
- Apply the accent to 5–15 % of the visible surface — no more. Saturation earns its place through scarcity.

### Motion
- Prefer CSS-only animations with `@keyframes` prefixed to avoid collision with host pages.
- Honour `@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }`.
- For React: Motion library (formerly Framer Motion) for choreographed transitions. For Vue: Vue Motion or native CSS-based transitions.
- Page-load motion should be short (roughly 250–400 ms total). Staggered reveals via `animation-delay: calc(var(--index) * 80ms)`.

### Composition
- Asymmetry is a tool, not a rule. Use it when it serves the hierarchy.
- Negative space is content. Empty regions communicate.
- One grid-breaking element per view; everything else obeys the grid.

### Backgrounds
- Solid colour is fine. Flat white is rarely the best choice.
- Gradient meshes, noise textures, and grain overlays add atmosphere without imagery.
- If using imagery, crop boldly. Cropped images feel composed; centred full-bleed usually does not.

### Dashboards specifically
- Display face for hero KPI numbers; body face for labels, captions, tooltips.
- Monospaced or tabular-lining numerals in dense data tables.
- Hover states on every interactive element; they should communicate affordance, not just colour-swap.
- Filters and controls grouped and aligned — not scattered in a row.
- Charts: single-colour or two-colour palettes per chart; avoid rainbow categoricals unless the data genuinely has many categories with no ordinal relation.

## 4. Final pass

Work the craftsmanship checklist from `visual-craftsmanship.md` before declaring done:
- Alignment holds at every breakpoint.
- Reduced-motion preference is honoured.
- No Lorem, no placeholder images, no default demo strings.
- Fonts load with `font-display: swap` or equivalent; fallback stack is sensible.
- Accent colour appears in the intended proportion — not leaking through the surface.
- Hover, focus, and active states all exist and all follow the tone.

Polish over addition. If the instinct is to add one more element, instead refine what is already there.
