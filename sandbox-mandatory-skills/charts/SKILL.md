---
name: charts
description: "Show a chart, graph, plot, KPI or diagram in the chat of GenAI UI. Use whenever a reply in the conversation would show one (a chart of data, a KPI against its target, a map, a flowchart, a sequence, a Gantt, a mindmap), whether the person asks for it (\"chart\", \"graph\", \"plot\", \"gráfica\", \"gráfico\", \"diagrama\", \"visualiza\", \"dibuja\") or it supports an insight. Load it before drawing anything with text characters or writing a plotting script. Also for a chart or a diagram in a Markdown artifact, which GenAI UI draws the same way. Not for an HTML artifact, a report or a dashboard file: those follow their own skill."
license: Stratio proprietary
metadata:
  system: true
---

# Charts in the Chat

A chart shown in the conversation is never text. GenAI UI draws three things in a reply, and the same in the page of a Markdown artifact:

| What | How | GenAI UI shows |
|---|---|---|
| A simple chart of data | a `chart` block | an interactive chart, downloadable as PNG |
| A diagram | a `mermaid` block | a diagram |
| Any other chart | a PNG embedded with `![title](path)` | the image |

**Never draw a chart with characters** (`█`, `▇`, `#`, ASCII or Unicode bars, text sparklines in a code block): nobody can read values off them and GenAI UI cannot show them as a chart. Exact values go in a markdown table.

`scripts/chart.py`, beside this file, checks what you write (§4); run it from this skill's directory or give its full path.

## 1. Simple chart → `chart` block

One of the types below, with up to ~50 rows (a `heatmap`, `pinmap` or `map` up to ~200): a fenced block with the language `chart` holding one JSON object, on lines of its own, next to the insight it supports:

````
```chart
{"type": "bar", "title": "BAI holds around 80K a month", "x": "month", "y": ["bai"], "data": [{"month": "2023-05", "bai": 81470.07}, {"month": "2023-06", "bai": 79281.40}]}
```
````

| `type` | Use it for | Fields besides `data` |
|---|---|---|
| `bar`, `line`, `area` | Comparison, trend | `x`: category or period column; `y`: numeric column, or a list for several series |
| `pie` | Composition, <=5 categories | `x`: slices; `y`: their value (the first is drawn) |
| `waterfall` | How a total moves from one value to another (variance bridge) | `x`: steps in order; `y`: each step's change, positive or negative |
| `scatter` | Correlation of two numeric columns | `x`, `y`: the two numeric columns (the first `y` is drawn); `label`: the column that names each point, shown when hovered (give it whenever the points are categories, products, people…) |
| `bubble` | A scatter with a third measure | `x`, `y`, `label` as in `scatter`; `size`: the numeric column that sizes each point |
| `radar` | Profiles compared on several metrics | `x`: the metrics' names; `y`: one numeric column per profile |
| `progress` | A KPI against its target | `y`: the KPI's column, read from the first row; `goal`: the target, > 0 |
| `gauge` | A KPI on labelled bands | `y`: the KPI's column, read from the first row; `segments`: `[{"min": 0, "max": 45, "label": "Good"}, …]` covering its range |
| `heatmap` | A measure across two categories (day × hour, region × product) | `x`: the column of its columns; `y`: the column of its rows; `value`: the numeric column that shades each cell |
| `histogram` | Distribution of one measure | `counts`: rows per bin; `bin_edges`: the bins' edges, one more than `counts`; no `data` |
| `map` | A value by geography | `region`: `world_countries`, `Spain-communities`, `Spain-provinces` or `United States`; `x`: the regions' column, as ISO codes (`ES`, `ES-MD`, `ES-M`, `US-CA`); `y`: their value |
| `pinmap` | Places on a map | `lat`, `lon`: the columns of each point's coordinates |
| `table` | Exact values to sort and compare | none: the rows as they are |

- `title`: the insight the chart shows ("BAI holds around 80K a month", not "BAI by month"), optional
- **Column names are what the chart shows**: the axis titles, the legend, the tooltip and the table of its data. Name them as they should read, in the person's language and with their unit (`"Duración media (min)"`, `"Ventas (k€)"`), not as the database names them (`duracion_media`)
- `data`: the rows, every value a number, a string or `null`; the `y` columns numbers (or `null`). Take the values from the data as they are, never rounded or invented, and order the periods
- Valid JSON only (double quotes, no comments, no trailing commas). A block GenAI UI cannot draw shows as code: check it before you send it (§4)

## 2. Diagram → `mermaid` block

A process, a flow, a sequence, a hierarchy, a timeline or an architecture (flowchart, sequence, Gantt of a real schedule, mindmap, timeline, state, ER, class, C4, requirement…) goes in a fenced block with the language `mermaid`.

**Not for data.** A chart of data is a `chart` block, never a Mermaid `pie`, `xychart-beta`, `quadrantChart` or `radar-beta`: only a `chart` block takes the values as they are and draws them like the rest of GenAI UI's charts. A count per month is a `bar`, not a Gantt; a cloud of points is a `scatter` or `bubble` with the real values, not a quadrant scaled to 0–1. Never `sankey-beta`: Mermaid cannot read a single accented letter in it, quoted or not; a flow of quantities is a PNG (§3).

Mermaid's grammar is strict and each diagram type has its own: one stray character and the whole block shows as code. Write it so it reads:

- **Quote every text** that has spaces, accents, `ñ`, `¿`, parentheses, colons, hyphens or other punctuation: titles, axes, labels, node text, point names and every argument of a C4 element (`A["Pago (tarjeta)"]`, `x-axis "Menor duración" --> "Mayor duración"`, `Rel(c, a, "Elige película")`, `"Acción" : 10`)
- **Keywords stay in English**, whatever the language of the text: `satisfies`, `contains`, `traces`, `derives`, `refines`, `verifies`, `copies` in a requirement diagram; `risk: low|medium|high`; `verifymethod: analysis|inspection|test|demonstration`
- **Ids are plain**: letters, digits and `_` (`req_1`, `api_server`); a value like `id: REQ-1` is quoted
- **No empty blocks**: a `Deployment_Node`, `Boundary` or `subgraph` holds at least one element
- **Only the documented statements** of each type: no `AddElementTag` or `$tags` in C4
- **Relations of a `C4Dynamic` are numbered by Mermaid** in the order they are written: their labels carry no numbers (`Rel(c, a, "Elige película")`, not `"1. Elige película"`)
- `quadrantChart` points are numbers from `0` to `1` written `0.xx` or `1`, never `1.0` or `1.00`

**Check any diagram but a plain flowchart or sequence** (C4, requirement, Gantt, state, ER, class, quadrant…) before you send it (§4): those are the types whose grammar breaks.

## 3. Any other chart → PNG

Box plots, subplots, annotations, a flow of quantities (Sankey), more rows than a `chart` block takes:

1. **Draw it with a script** that saves a PNG in the `assets/` folder of the output you are working in, or `output/assets/` if there is none, with a descriptive name. With matplotlib or seaborn, start with `plt.style.use("<this skill's directory>/genai.mplstyle")` (after `sns.set_theme()` if you call it): the colors, axes and resolution of GenAI UI's charts, so the PNG reads like the rest. Name the axes and the legend as in §1.
   - **Never draw a chart by hand** out of shapes (patches, paths, rectangles) when a library draws it: the layout comes out wrong. A Sankey is plotly's `go.Sankey`, saved with `fig.write_image(path, scale=2)` (kaleido is installed), its nodes in the palette of `genai.mplstyle` (`#128bd3`, `#ec7e13`, `#2ca02c`…) and each link in its source's color at 35% opacity.
2. **Run the script** in the same turn. A script that draws a chart is not the chart: never hand over the script alone. If it fails, fix it and run it again. Then open the PNG (read it) and look at it: labels on top of each other, shapes off the canvas or values that do not add up are fixed before it is sent.
3. **Get the line that embeds it**, which also checks the PNG exists and is not empty:

   ```bash
   python3 scripts/chart.py embed <png> "BAI holds around 80K a month"
   # ![BAI holds around 80K a month](output/assets/monthly_bai.png)
   ```

4. **Put that line in the reply**, on a line of its own next to the insight it supports. GenAI UI shows the image there. A path the reply only names, in backticks or in the text, is not shown.

## 4. Check before you send

````bash
python3 scripts/chart.py check reply.md      # the reply with its blocks, or a chart's JSON; '-' reads stdin
python3 scripts/chart.py check - <<'EOF'      # or the blocks themselves, before writing the reply
```mermaid
C4Dynamic
  …
```
EOF
````

It checks every `chart` block with GenAI UI's rules and every `mermaid` block with the Mermaid version GenAI UI draws it with, and prints why a block would show as code, with the line Mermaid stopped at. It exits 1 if one would: fix it and check again. If it says the Mermaid blocks were not checked (no validator in this sandbox), follow the rules above.
