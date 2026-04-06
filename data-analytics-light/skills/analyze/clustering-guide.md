# Rule-Based and RFM Segmentation Guide

Operational reference for segmentation as an analytical tool within `/analyze`. Uses exclusively pandas — no ML dependencies.

## 1. Decision Table

| Situation | Approach | When to prefer |
|-----------|---------|---------------|
| Segments already defined by the business (VIP, Regular, New) | Rule-based with thresholds | Clear rules, maximum interpretability |
| Transactional data, standard retail segmentation | RFM with quintiles | Few variables, easy to communicate |

## 2. RFM (Recency, Frequency, Monetary)

**MCP Query**: "last purchase date, total number of purchases, and total spent per customer"

**Calculation**:
1. R = days since last purchase (lower = better)
2. F = number of purchases (higher = better)
3. M = total spent (higher = better)
4. Quintiles: `pd.qcut(series, q=5, labels=[1,2,3,4,5])`. Invert R (5 = most recent)
5. Score: concatenate R+F+M as string or sum for numeric score

**Business labels** (mandatory — never "Segment 1, 2, 3"):

| RFM Score | Label | Description |
|-----------|-------|-------------|
| 555, 554, 544 | Champions | Purchased recently, buy frequently, spend a lot |
| 543, 444, 435 | Loyal | Regular purchases with good spending |
| 512, 511, 422 | Potential | Recent purchase but low frequency |
| 155, 154, 144 | At risk | Were good but haven't purchased in a long time |
| 111, 112, 121 | Hibernating | Low activity across all dimensions |

Adapt labels to the specific domain. The table is indicative.

## 3. Mandatory Profiling

After assigning segments (whether by rules or RFM), ALWAYS generate a business profile:

1. **Mean per segment as base 100 index**: `(segment_mean / overall_mean) * 100` per variable
   - Index > 120 = distinctive characteristic of the segment
   - Index < 80 = relative weakness of the segment
2. **Summary table**: One row per segment, columns = variables + size (n and %)
3. **Naming**: Assign a business name based on the profile. Never "Segment 0, 1, 2"
   - Example: "High-value digital" (online spending index = 180, frequency = 150)
   - Example: "Occasional buyers" (frequency index = 45, recency = 60)
4. **Visualization**: Index heatmap (segments x variables), radar/spider chart per segment
