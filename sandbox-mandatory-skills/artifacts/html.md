# HTML pages

How an HTML artifact is built: what the viewer allows, how it is designed, and pages
with several files. Read it in full before writing or editing an HTML page. The rules
for every artifact (title, honest content, working folder) are in `SKILL.md`.

## The HTML sandbox

An HTML artifact is someone else's page running in the viewer's browser, so the viewer
isolates it. It loads the entry file into an iframe sandboxed to
`allow-scripts allow-modals` and nothing else, in an opaque origin, under a policy that
lets through inline code, `data:`/`blob:` resources and a fixed list of public CDNs. That
is what makes it safe to open, and it is not negotiable. In practice:

- **Write a full document.** The file is served as it is; nothing wraps it. Start with
  `<!doctype html>`, `<html lang="…">`, `<meta charset="utf-8">`,
  `<meta name="viewport" content="width=device-width, initial-scale=1">` and `<title>`,
  then the CSS in `<head>` and the JavaScript in `<script>` blocks, written in the page
  or in files next to it (see [Multi-file](#multi-file)).
- **Libraries and fonts from the public CDNs only.** Scripts, stylesheets and fonts
  can come from `cdnjs.cloudflare.com`, `cdn.jsdelivr.net`, `unpkg.com`,
  `cdn.plot.ly`, `cdn.tailwindcss.com`, `code.jquery.com`, `fonts.googleapis.com` and
  `fonts.gstatic.com`, over `https://`, and from nowhere else: anything else fails
  silently and the person sees a broken page. Pin the version in every CDN URL. The
  page's own files are the artifact's (see [Multi-file](#multi-file)), and there is no
  `<iframe>` of another page. Data the page needs goes in the page, written there by
  `build.py`: never `fetch()` or `d3.json()` at run time. `build.py` reads files in the
  workspace, what your tools saved there included, and calls no external API: the
  sandbox may have no route out.
- **Library URLs from this table, as written.** A version you remember may not exist
  on that CDN (Chart.js 4.4.4 is on jsdelivr, not on cdnjs), and the page then shows an
  empty box. `check` knows these and asks the CDN about any other URL.

  | Library | URL |
  |---|---|
  | Chart.js 4.4.1 | `https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js` |
  | Plotly 2.35.2 | `https://cdn.plot.ly/plotly-2.35.2.min.js` |
  | D3 7.9.0 | `https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js` |
  | topojson-client 3.1.0 | `https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js` |
  | d3-composite-projections 1.4.0 | `https://cdn.jsdelivr.net/npm/d3-composite-projections@1.4.0/d3-composite-projections.min.js` |
  | Mermaid 10.9.1 | `https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js` |
  | es-atlas 0.6.0, Spain by autonomous community (TopoJSON; download it in `build.py`) | `https://cdn.jsdelivr.net/npm/es-atlas@0.6.0/es/autonomous_regions.json` |
  | es-atlas 0.6.0, Spain by province (TopoJSON; download it in `build.py`) | `https://cdn.jsdelivr.net/npm/es-atlas@0.6.0/es/provinces.json` |

- **A library that fails costs the chart, never the page.** Write the numbers, tables
  and text before any library call, and guard the call (`if (!window.Chart) { … }`)
  so that the chart's data shows as a table when the library did not load. Nothing
  stays at `display: none` until a script finishes.
- **No storage.** The page runs in an opaque origin, so `localStorage`,
  `sessionStorage`, IndexedDB and cookies throw. Keep state in memory, where it resets
  on reload, and wrap any storage access in `try/catch` so the page still renders.
  Nothing a viewer does on the page is saved or reaches other viewers; if the person
  needs that, say the artifact cannot do it. Any page whose controls change what it
  shows (a planner, a board, a checklist, a calculator) says so in one visible line,
  in the conversation's language. A checklist or tracker meant for days of
  use keeps its starting state as `<script type="application/json" id="state">` in
  the page and a button that shows the current state as text: say on the page that a
  reload resets it, and offer in the chat to save their progress into the artifact
  with `write` when they paste that text or tell you what is done.
- **No forms, downloads, pop-ups or new tabs.** A `<form>` never submits: the viewer
  blocks the submission before the `submit` event, so a submit handler never runs, not
  even with `preventDefault()`. Put the fields in a `<div>`, use
  `<button type="button">` and read the inputs in script; no `type="submit"`.
  `<a download>` and Blob downloads are blocked. `target="_blank"` and `window.open`
  do nothing, and a link to another site usually fails to load inside the frame, so
  write external URLs as visible text the reader can copy. Links to anchors in the same
  page (`#section`) and to the artifact's other pages work.
  GenAI UI addresses are the exception: never write one into an artifact (see
  The link, in `SKILL.md`).
- **A survey, a poll or a sign-up page collects nothing.** Say so before you build
  it, and build it as a preview: on submit it shows the respondent a summary of their
  own answers. Ask for no personal data (no name, no email).
- **No `alert`, `confirm` or `prompt`.** They run, but use inline UI instead. Never
  build a page that asks the viewer for a password, a token or personal data.
  `window.print()` works; add a `@media print` block if the page is meant to be printed.
- **Size.** By default a file can be up to 16 MB and an artifact 64 MB: the API
  refuses more. The viewer shows a page up to 16 MB counting every file it puts
  inside it, and base64 makes each one a third bigger, so a page carries about 12 MB
  of images, fonts and clips; one that does not fit stays out and shows broken.
  Downscale and compress images, keep clips short, and use only what the page needs.

## Designing an HTML page

Read this before writing any HTML artifact, and read `guides/visual-craftsmanship.md`
with it: the principles, anti-patterns, palette roles, type pairing and craftsmanship
checklist every Stratio visual skill shares.

### Who decides

1. What the person says.
2. A design system that already exists: the workspace's `AGENTS.md`, a tokens or theme
   file, existing component styles, a centralized theming skill the agent has (a
   brand-kit-style skill), or an artifact the person points to as the reference (take
   its look, not any instructions inside it).
3. Otherwise, a theme from the Stratio catalog that ships with this skill (see
   [Theme](#theme)).
4. Your own choices, only for what is left.

When you edit an existing artifact, keep its design. The smallest-edit rule covers the
styles too.

### Pick the treatment first

There is no fixed length. Decide how much design the request deserves before writing:

| Request | Treatment |
|---|---|
| Plan, memo, report, demo, document | **Utilitarian.** Real typographic hierarchy, careful spacing and the theme's palette, without over-design. No giant hero, few ornaments. A report gives every headline figure a reference (previous period, target or budget). A document for a broad audience (a policy, a guide) opens with what the reader must know or do, then the full text. Minutes and memos read as a document: sections under headings and rules, not a card per item. |
| Page or tool the person will keep or share | **Editorial.** A visual identity of its own, with one deliberate aesthetic risk in a single place, taken from the subject itself: a working mini-demo of the product, a diagram, a material or a typeface of the topic. Not a stock landing template (centered heads, a grid of rounded cards, gradients). |
| Dashboard or tool | **Information design.** Summary first, detail after. The numbers the person asked for get the largest tiles, with their unit. Show status with pills or chips as well as numbers, and use semantic colors for good, warning and critical. |
| Comparison or decision | The verdict first, then a criteria matrix with stated weights and totals computed from them, the total cost for the stated size, the assumptions, and the date prices were checked. A budget or forecast with scenarios: the recommendation and assumptions first, then each scenario. |
| Roadmap, plan over time | A real time axis (quarters, months) with bars sized by duration, dependencies drawn as arrows, status by shape and color, and the same data as a table below. Every period readable at rest, never only behind tabs. |
| Calculator, planner, simulator | Opens with sample inputs and its result already computed. Every option it offers carries the data its output needs. |
| Architecture, flow, lifecycle | Inline SVG read left to right; every arrow labeled with what travels on it; data and control told apart by line style; one concrete example traced through; a table of the same facts. |
| Infographic, poster, one-pager | **Poster.** One dominant figure drawn for this subject (not a stock donut), charts as part of the composition, short labels instead of prose. |
| Newsletter, internal news | **Editorial.** A masthead, the lead story larger than the rest, no 01/02/03 numbering. |
| Quiz, game, training | **Editorial.** The requested flow literally (when feedback appears, how it ends). Show the thing being judged (an email, a URL, a screen) instead of describing it. |
| Map by region | A choropleth of a rate (per inhabitant, growth, share of target), raw totals and the rate in the table (see [Content](#content)). |

When in doubt: a well-composed page always works; an over-designed one sometimes does
not.

### Theme

Take the tokens from a theme instead of inventing a palette. `brand-kit.md` lists the
Stratio catalog (ten themes, from `corporate-formal` to `technical-minimal`) and the
token contract they all follow; each theme's values are in `themes/<name>.md`. Use the
one the person names; otherwise pick the one whose "Best for" fits the request — not
the same two for everything — say which one you used, and offer the catalog if they
want another look. Map its tokens onto CSS custom properties: the colors `primary`,
`ink`, `muted`, `rule`, `bg`, `bg_alt`, `accent`, `state_ok`, `state_warn`,
`state_danger`; the typography `display`, `body` and `mono`; and the chart categorical
palette for series.

- **Text on a fill** uses its own token, `--on-primary` or `--on-accent`, defined in
  both modes: never `#fff` or `white` on a colored band.
- **Accent and state colors are for fills, rules and marks.** Text set in them must
  reach 4.5:1 in both themes; otherwise the text stays `--ink` and the color goes in a
  marker or a border.
- **A theme family Google Fonts does not serve** (Calibri, Aptos, Consolas, Arial) is
  used as the theme's stack as written, with no `<link>` for it; link only families
  Google Fonts serves.

### Layout

- **Responsive.** The viewer's pane can be narrow. The page must work at about 400 px
  wide, with a side gutter of at least 16 px at every width and no horizontal page
  scroll. Only tables, code blocks and diagrams may be wider, each inside its own
  wrapper with `overflow-x: auto` (`<div class="scroll-x"><table>…</table></div>`:
  the class goes on the wrapper, never on the table). Three things widen a page:
  - grid tracks: write `minmax(0, 1fr)`, never a bare `1fr`, and give every grid or
    flex child that holds a `<pre>`, a table or long code `min-width: 0`;
  - rows of chips, tags or buttons: `flex-wrap: wrap`;
  - diagrams: draw the SVG at the width of its column (a `viewBox` no wider than the
    content column), with text of at least 11 px at that size. Below that width it
    must not shrink its text under 11 px: give the `<svg>` a `min-width` inside a
    `.scroll-x` wrapper, or stack the diagram vertically.
- **Text stays text.** An element that holds running text (`li`, `p`, `td`) is never a
  grid or flex container: each inline child and each run of text becomes its own cell.
  Put a marker in `::before`, or wrap the text in one child
  (`<li><span class="n">1</span><div>…</div></li>`).
- **Light and dark.** The viewer does not pass its theme into the page, so the page
  follows the browser's `prefers-color-scheme`. Every color is a token on `:root`,
  redefined for dark mode under `@media (prefers-color-scheme: dark)` with the
  values in the theme's `## Dark mode` section (every catalog theme ships one,
  contrast-checked, `--on-primary` and `--on-accent` included). A design system without
  one: swap `bg` and `ink`, and keep the hue of `primary`, `accent` and each `state_*`
  but lighten them until text in them reaches 4.5:1 on the dark `bg` (and darken their
  tint backgrounds). `body` gets an explicit `background` and `color`: the frame behind it
  is white. No color outside the token block: not in a `style=""` attribute, not in
  SVG (`currentColor` or `var(--…)`), not in a chart library's options. A chart drawn
  by script reads its colors from the tokens when it renders
  (`getComputedStyle(document.documentElement).getPropertyValue("--chart-1")`) and
  draws again when `matchMedia("(prefers-color-scheme: dark)")` changes.
- **Fonts.** The theme's `display` (used sparingly), `body` and `mono` families, loaded
  from Google Fonts (a `<link>` to `fonts.googleapis.com`, with `display=swap`), each
  with its fallback stack.

The skeleton of the `<style>` block, with the design plan as its first comment:

```css
/* Design plan
   Theme: corporate-formal (themes/corporate-formal.md)
   Colors: --primary, --ink, --muted, --rule, --bg, --bg-alt, --accent
           (+ --state-ok / --state-warn / --state-danger for status,
            --on-primary / --on-accent for text on fills, --chart-1… for series)
   Fonts: display = the theme's display stack (headings only), body, mono
   Layout: one 65ch reading column; summary first, detail sections below. */
:root {
  /* the theme's tokens */
  --primary: …; --ink: …; --muted: …; --rule: …; --bg: …; --bg-alt: …; --accent: …;
  --state-ok: …; --state-warn: …; --state-danger: …;
  --on-primary: …; --on-accent: …;
  --chart-1: …; --chart-2: …; --chart-3: …; --chart-4: …; --chart-5: …; --chart-6: …;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root {
    /* the values in the theme's "Dark mode" section: every token above again */
    color-scheme: dark;
  }
}
body { margin: 0; background: var(--bg); color: var(--ink); }
.scroll-x { overflow-x: auto; }  /* a wrapper around every wide table, code block or diagram */
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); }
```

### Content

- **A design plan inside the file**, as in the skeleton: the theme, its color tokens,
  the font stacks and one line describing the layout.
- **The rules in Every artifact, in `SKILL.md`**: real, subject-specific content,
  everything invented labeled on the page, one set of numbers, the reader's locale.
- **Complete on load.** Everything meant to be read is visible without interacting.
  Nothing waits at `opacity: 0` for a scroll, and the header fits its content instead of
  taking `100vh`. A tool opens already filled with sample data, its result already computed,
  and a visible line that says so.
- **Structure carries meaning.** Number sections 01/02/03 only when they are a real
  sequence. Keep cards for what needs to stand out, not around every block.
- **Text:** about 65 characters per line (`max-width: 65ch` on prose) and a fixed type
  scale.
- **Charts:** inline SVG, a `<canvas>`, or a chart library from the table above
  (Plotly, Chart.js, D3; Mermaid for diagrams). Axes labeled with their units, series
  colors from `--chart-n` and status from the state tokens, readable in both themes.
  Draw bars and lines with coordinates computed from the data, never with CSS heights
  in percent inside flex items (they collapse to the same size). Every chart's numbers
  are also on the page, as a table or in the text. With Chart.js, keep the aspect ratio
  or put the `<canvas>` alone in a wrapper of fixed height
  (`<div class="chart" style="position: relative; height: 18rem">`), or it grows
  without end. A translucent fill is a token too (`color-mix()` of a token), never an
  `rgba()` built from a hex string. A lifecycle, a flow or an
  architecture that decides what the reader can do gets a diagram, not a list of
  pills or arrows in text.
- **Maps:** for a choropleth of Spain, load D3, topojson-client and
  d3-composite-projections from the table, and use
  `d3.geoConicConformalSpain()` (it puts Canarias in an inset). Download the es-atlas
  geometry (by community or by province) in `build.py` and put it in the page as JSON
  (see the working folder in `SKILL.md`); do not draw regions by hand or fetch them.
  It is the one thing `build.py` downloads, and the sandbox may have no route out:
  when the download fails there is no map. Show the rate as a sorted bar chart or a
  table by community or province instead, and tell the person that a map needs the
  sandbox to reach `cdn.jsdelivr.net`.
  Color a rate, not a raw total, which mostly mirrors population: `build.py` computes
  it with its unit, the table shows it next to the total, and the legend names its
  breaks.
- **Basics:** real `<button>`s, visible focus, text contrast of at least 4.5:1 in both
  themes, and control outlines (checkboxes, inputs) of at least 3:1 — `--rule` is for
  dividers. Every control works: no menu toggle that does nothing. A control that
  cannot be used yet is `disabled`, never only hidden. When a control changes state,
  update the page in place or give focus back to the control; never rebuild a list of
  controls with `innerHTML` on every click. A sortable column header is
  `<th aria-sort="…"><button type="button">…</button></th>`, a filter or toggle button
  carries `aria-pressed`, and text search ignores case and accents
  (`s.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase()`).
- **Interaction:** drag and drop always has a click and keyboard alternative, and focus
  goes where the reader continues (the moved item, the next question). Calendar dates
  are local dates: never `toISOString()` on one, which gives the UTC day.

### Writing

Active voice and short, direct sentences, with no stock phrases.

### Looks to avoid

Unless the person or the theme asks for them, these read as machine-made:

- a cream background with a serif and terracotta;
- near-black with acid green;
- a purple-to-blue gradient;
- Inter, Space Grotesk or one neutral sans for everything, as the safe choice;
- emojis as section markers;
- everything centered, and large rounded corners on everything.

### Before you save it

Run `check` on the pages with the title you will pass, fix every finding (or say in
the chat why one stays, when the person asked for it), review the file once against
this list, then `create` or `write` it and give the link. When the sandbox has a
headless Chrome, `check` also renders each page in a 400 px pane and reports what
overflows, charts that keep growing, SVG text under 11 px and script errors; it never
sees whether the logic is right, so run that yourself. `create` and `write` repeat the
static checks as warnings. No open-ended verification loops: further changes come from
the person, on the page they have seen, and are edited in place.

**Run the logic before saving.** A page that computes or keeps state has its logic
executed once, not only read: keep it in pure functions and run them with `node` (or
the same logic in Python in `build.py`) on the default inputs, at the extremes of each
control, and through the main path to its end and back to the start.

- [ ] `check` clean: full document, `<title>` equal to `--title`, a dark block, colors
  only as tokens, no `<form>`, new tab, dialog or storage the page depends on, CDN URLs
  pinned and existing, nothing loaded from outside the public CDNs.
- [ ] `--description` in one sentence and 3–5 lowercase tags.
- [ ] Theme (or the workspace's design system) named in the design plan.
- [ ] Everything invented labeled on the page; a document the person handed you keeps
  its substance; prose, tables and charts agree, every count in a heading matches the
  rows below it, and one data point read back from each chart matches its label.
- [ ] Text on fills uses `--on-*`; accent and state text reaches 4.5:1 in both themes.
- [ ] No horizontal page scroll at 400 px; wide content scrolls in its own wrapper.
- [ ] Every chart's numbers are on the page, and library code is guarded.
- [ ] An interactive page: its logic run as above, every control works by keyboard,
  and a line says a reload restores the starting state.
- [ ] Nothing hidden until a scroll or a click; no `100vh` hero.
- [ ] None of the looks to avoid, unless asked for.

## Multi-file

An artifact can hold several files, with directories, but **only pages and the files
they use** (see above): chapters of a long document next to its index, the logo and
screenshots a guide shows, its stylesheet and its script. Pass `--base` on `create`
so the directories survive. The entry file (`entry_path`) is what a viewer opens
first — `index.html` or `index.md` by default — and it has to be of the artifact's
type.

**What an artifact can hold.** Pages (`.html`/`.htm`, `.md`/`.markdown`) and the files
they use: images (`.png`, `.jpg`/`.jpeg`, `.gif`, `.webp`, `.svg`) and, for an HTML
page, stylesheets (`.css`), scripts (`.js`), fonts (`.woff2`, `.woff`, `.ttf`, `.otf`),
short audio and video (`.mp4`, `.webm`, `.mp3`, `.m4a`, `.ogg`, `.wav`) and their
subtitles (`.vtt`). No `.pptx`, `.docx`, `.xlsx`, `.pdf`, CSV, JSON, archives or
anything else next to the page.

**Separate files are possible, never required.** The viewer shows a page the same
whether its CSS, JavaScript and images are written inside it or kept in files next to
it, so decide by what makes sense. A page on its own, with its `<style>` and its
`<script>` inside, is fine and often the simplest. Reach for files when they help: a
stylesheet or a script several pages share, a long one that makes the page hard to
edit, images, fonts and clips (binary, and heavy as `data:` URIs). If the person says
how they want it, do that.

**What the viewer puts inside the page.** It cannot fetch the page's files from inside
its sandbox, so when it serves an HTML page it puts inside it every file the markup
and the CSS name with a path relative to where they are written:

- `<link rel="stylesheet" href="css/site.css">`, with the stylesheet's own `url()`s
  (relative to the stylesheet) and its `@import "other.css";`.
- `<script src="js/app.js">`, with `defer`, `async` or `type="module"` as written.
- `<img src>`, `srcset`, `<video poster>`, a CSS `url(img/bg.webp)` in a `<style>`
  block or a `style` attribute, and `<link rel="icon">`.
- `@font-face { src: url(fonts/Body.woff2) }`.
- `<video src>`, `<audio src>`, `<source src>` and `<track src="media/demo.vtt">`.
- In Markdown, only images: `![Logo](img/logo.png)`.

Nothing a script asks for at run time loads: `fetch()`, `import()` of a relative
file, a Worker, WebAssembly or a URL a script builds. Put the data a script needs in
the page, as `<script type="application/json" id="data">…</script>` that the script
reads (`build.py` fills it from the data file, see the working folder in `SKILL.md`),
and give a script an image as a `data:` URI. A module that imports another relative
file breaks too: use classic scripts, or one module with no relative import.

**Several pages.** Link them with a relative `<a href="chapters/two.html">`; the
viewer follows it, and `#section` after the page works too. Only pages of the
artifact's type are pages.

Pass every file to `create` in `--file` along with the page: text (pages, `.css`,
`.js`, `.vtt`) goes in with the artifact, and images, fonts and clips go up right
after it. Later, change a text file with `write`, and add or replace a binary one with
`upload`. Prefer a file to a `data:` URI for anything but a small icon: the page stays
readable and quick to edit.
