# Additional Analytical Patterns

Detailed implementation of patterns whose triggers are in the "Operationalized analytical patterns" section of AGENTS.md (operationalized patterns table).

## Concentration (Lorenz/Gini)
- **MCP Query**: "cumulative metric by [entity] ordered from highest to lowest"
- **Python**: Sort desc, `cumsum() / total` for Lorenz curve. Gini = 1 - 2 * area under curve (`np.trapz`)
- **Visualization**: Lorenz curve (cumulative line) + perfect equality diagonal + Gini annotated in legend. `legend_position="inside"` (<=3 items)
- **Interpretation**: Gini > 0.6 = high concentration ("The top 20% of customers generate X% of revenue")

## Mix analysis
- **MCP Query**: "metric broken down by components (volume, unit price) in period A and period B"
- **Python**: Decompose total delta into: volume effect (delta_vol x base_price), price effect (delta_price x base_vol), mix effect (delta_vol x delta_price)
- **Visualization**: Waterfall chart with each factor's contribution to the total change
- **Interpretation**: "The EUR X growth is explained Y% by volume and Z% by price"

## Indexation (base 100)
- **MCP Query**: "metrics [monthly] by [dimension] for [period]"
- **Python**: `(series / series.iloc[0]) * 100` per group. Allows comparing relative evolutions
- **Visualization**: Line chart with all series starting at 100 in the base period. `legend_position="bottom"` (multiple series)
- **Interpretation**: "From base, category A grew 45% while B only 12%"

## Deviation vs reference
- **MCP Query**: "metric by [dimension]", calculate average or search for target in knowledge
- **Python**: `deviation = value - reference` per category, sort
- **Visualization**: Diverging bar chart (horizontal) centered on the reference (0). Positive to the right, negative to the left. No legend (each bar is its own category)
- **Interpretation**: "5 of 12 regions exceed the average. The largest positive deviation is X (+23%)"

## Gap analysis
- **MCP Query**: "actual and target metric by [dimension]"
- **Python**: `gap = target - actual`, `pct_gap = gap / target * 100`, sort by gap descending
- **Visualization**: Lollipop chart (point = actual, line to target) or bullet chart by dimension
- **Interpretation**: "The largest gap is in X (EUR45K, 23% of target). Closing the 3 largest gaps contributes EUR120K"
