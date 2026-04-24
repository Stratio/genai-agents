# web-craft

Shared skill for building production-grade interactive web frontends (HTML/CSS/JS, React, Vue) with deliberate aesthetic direction. Produces working code — components, pages, landing sites, dashboards, interactive artifacts — that avoids the generic "Inter + soft purple + Bootstrap cards" default.

Companion visual skills: `canvas-craft` for single-page static artefacts (posters, covers, certificates), and `pdf-writer` for multi-page typographic documents. The three share the `visual-craftsmanship.md` guide and complement each other — use the disambiguation table in that guide when in doubt.

## What it does

- Takes the user's brief (what to build, who uses it, technical constraints) and drives a five-decision design pass before writing code: artifact class, tone, type pairing, palette, rhythm / motion.
- Picks a single committed tone from a 10-tone taxonomy (8 shared families + 4 web-specific additions: playful-toy, retro-futuristic, natural-organic, forensic-audit).
- Produces CSS with custom-property palettes, variable fonts via `@import` or bundled WOFF2, modular type scales, and motion budgets that honour `prefers-reduced-motion`.
- Generates React components (Motion library for choreography) or Vue components (Vue Motion or native CSS) when the stack calls for them.
- Runs a craftsmanship checklist on the output: alignment at every breakpoint, accent colour within 5–15% of the surface, no placeholder strings, hover/focus/active states coherent with the tone.

## When to use it

- The user asks for a component, page, landing, dashboard, or interactive artifact.
- A static artefact with typography as visual element (poster, cover, one-pager) — **do not** use `web-craft`, use `canvas-craft`.
- A multi-page prose or tabular document (report, invoice, contract) — **do not** use `web-craft`, use `pdf-writer`.
- An interactive dashboard with KPIs is a clear `web-craft` case.

## Dependencies

### Other skills
- **Companion visual skills:** `canvas-craft` (static single-page), `pdf-writer` (typographic documents).
- **Optional theming skill:** a centralized theming skill (e.g. `brand-kit`) is **strongly recommended**. When one is available the agent runs its theme-selection workflow *before* coding; the chosen theme supplies the tokens for the `:root` block. When no theming skill is present the skill improvises tokens following `visual-craftsmanship.md`.

### Guides
- `visual-craftsmanship.md` — shared aesthetic principles for every visual skill: the five design decisions, tone taxonomy, palette roles, type-pairing philosophy, anti-patterns to refuse, and the disambiguation table between `web-craft` / `canvas-craft` / `pdf-writer`.

### MCPs
None.

### Python
None — this skill produces web code, not Python.

### System
- **Browser runtime only** — the output runs in any modern browser.
- **Optional:** Node.js / npm if the host project builds React or Vue components with a bundler. The skill does not require a build step itself; it ships code that can be consumed either way.
- **Optional:** font files — fonts are served from Google Fonts / official foundries via `@import` by default; bundle WOFF2 locally only when the artifact is for external distribution (include licence files).

## Bundled assets
None. Fonts and images are either fetched at runtime (Google Fonts) or provided by the host project.

## Notes

- **Commit to one tone.** Lukewarm mixes of two tones is the single most common cause of generic output.
- **Accent colour scarcity:** apply the dominant accent to 5–15% of the visible surface; saturation earns its place through restraint.
- **Motion budget is explicit:** `none`, `minimal`, or `expressive`. Any animation must respect `@media (prefers-reduced-motion: reduce)`.
- **Fonts from Google Fonts are fine for internal artifacts;** for external distribution, bundle WOFF2 with licence files.
