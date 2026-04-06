# Advanced Analytical Techniques

Activate based on the selected depth (see activation matrix in Phase 2).

## Statistical rigor and uncertainty

**When to apply statistical tests:**

| Question | Test | Conditions | Implementation |
|----------|------|------------|----------------|
| Difference between 2 groups (numeric) | t-test | Normal, n>30 | `scipy.stats.ttest_ind` |
| Difference between 2 groups (non-normal) | Mann-Whitney U | Non-normal or n<30 | `scipy.stats.mannwhitneyu` |
| Difference between 3+ groups | ANOVA + Tukey | Normal, homoscedastic | `scipy.stats.f_oneway` |
| Relationship between categoricals | Chi-squared | Expected freq. >5 | `scipy.stats.chi2_contingency` |
| Correlation | Pearson / Spearman | Linear / Monotonic | `scipy.stats.pearsonr` / `spearmanr` |
| Significant temporal trend | Mann-Kendall | Series >10 points | `scipy.stats.kendalltau` |

**Rules:**
- ALWAYS report p-value + effect size (Cohen's d, eta-squared, Cramer's V)
- p < 0.05 = significant. p < 0.01 = highly significant
- A significant result with a small effect may not be relevant for the business
- With large samples (>10k), almost everything is "significant" — prioritize effect size
- Calculate CI95% for KPIs: `mean +/- 1.96 * (std / sqrt(n))`. For proportions: `p +/- 1.96 * sqrt(p*(1-p)/n)`

**Communicating uncertainty to business:**

| Technical level | How to communicate it |
|----------------|----------------------|
| CI 95%: [120, 140] | "Between 120 and 140 with high confidence" |
| p < 0.01 | "The difference is real, not due to chance" |
| p > 0.05 | "There is not enough evidence to claim there is a difference" |
| Cohen's d = 0.2 | "The difference exists but is small" |
| Cohen's d = 0.8 | "The difference is large and relevant" |
| R² = 0.65 | "The model explains 65% of the variation" |

**Principle:** NEVER present a number without confidence context. Prefer ranges over single points. Adapt language precision to the audience.

## Prospective analysis and scenarios

Apply when the user asks "what would happen if...", "how will it evolve...", or when the data suggests useful projections.

| Technique | When to use | Implementation | Output |
|-----------|------------|----------------|--------|
| **Scenarios** | Projection with uncertainty | Define assumptions per scenario (+/- X%), calculate impact | Comparison table + fan chart |
| **Sensitivity** | Identify influential variables | Vary 1 variable at a time (+/-10%, +/-20%), measure KPI impact | Tornado chart |
| **Monte Carlo** | Quantify multivariable risk | `numpy.random` with distributions, N=10000 iterations | Histogram + percentiles P5/P50/P95 |
| **Linear projection** | Clear trend with >12 points | `linregress` or `polyfit` + CI95% | Line + confidence band |

**Rules:**
- Always make each scenario's assumptions explicit
- Never present a projection without an uncertainty band
- Label: "Projection based on [assumption], not a prediction"
- For Monte Carlo: document distributions and justification

## Root cause analysis

Activate when a problem, anomaly, or significant deviation is detected.

**Framework:**
1. **Quantify**: Exact magnitude (how much, since when, in which dimensions)
2. **Dimensional drill-down**: Decompose by each dimension (time, region, product, segment, channel). MCP query: "metric by [dimension] in problem period vs reference". Find where the deviation is concentrated
3. **Variance tree**: For the most explanatory dimension, continue drilling down (region -> city, product -> SKU)
4. **5 Whys**: Formulate successive questions until reaching the root cause. Document each level
5. **Correlation vs causation**: Verify temporality (cause precedes effect), logical business mechanism, and rule out confounders. If causation cannot be established, report as "association"

**Visualizations:** Variance waterfall, contribution treemap, event timeline

## Anomaly detection

| Type | Method | Implementation | Criterion |
|------|--------|----------------|----------|
| **Static outliers** | IQR or Z-score | `Q1 - 1.5*IQR` / `Q3 + 1.5*IQR`, or `abs(z) > 3` | Already in EDA (Phase 1.1) |
| **Temporal anomalies** | Deviation from trend+seasonality | `statsmodels.tsa.seasonal_decompose`, residual > 2*std | Series >12 points |
| **Trend change** | Pre/post mean difference | Moving average + t-test between windows | Minimum window: 5 points |
| **Categorical anomalies** | Deviation from expected distribution | Chi-squared vs historical distribution | p < 0.01 |

**Real anomaly vs data error:**
- Verify with `search_domain_knowledge` if there are known events
- If it appears across multiple metrics → probably real
- If only in one column/dimension → probable error → alert, do not report as insight
