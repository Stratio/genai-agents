# Segmentation and Clustering Guide

Operational reference for segmentation as an analytical tool within `/analyze`.

## 1. Decision Table

| Situation | Approach | When to prefer |
|-----------|----------|----------------|
| Segments already defined by the business (VIP, Regular, New) | Rule-based with thresholds | Clear rules, maximum interpretability |
| Transactional data, standard retail segmentation | RFM with quintiles | Few variables, easy to communicate |
| No predefined segments, multiple variables (>3) | KMeans + silhouette | Numeric variables, spherical clusters |
| Irregular clusters or outlier detection | DBSCAN | Arbitrary shapes, k is unknown |

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

## 3. Clustering with KMeans

**Mandatory preprocessing**:
1. Scale variables: `StandardScaler()` (KMeans is sensitive to scale)
2. Handle nulls: impute or exclude before scaling
3. Categorical variables: encoding or exclude (KMeans is numeric-only)

**Selecting k**:
1. **Elbow method**: Plot inertia vs k (k=2..10). Look for the "elbow"
2. **Silhouette score**: `silhouette_score(X, labels)` for each k. Higher = better
3. Use both to decide. If they diverge, prioritize silhouette

**Implementation**:
```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

scores = {}
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    scores[k] = silhouette_score(X_scaled, labels)
# Choose k with highest silhouette (or elbow in inertia)
```

## 4. Cluster Validation

| Criterion | Threshold | Action if it fails |
|-----------|----------|-------------------|
| Silhouette score | > 0.5 good, > 0.25 acceptable | Try another k or DBSCAN |
| Minimum size per cluster | >= 5% of the population | Merge small clusters |
| Stability | Run with 3 different random seeds | If it changes a lot, clusters are not robust |
| Visual separation | 2D scatter (PCA) shows distinguishable groups | If they overlap, consider reducing features |

## 5. Mandatory Profiling

After assigning clusters, ALWAYS generate a business profile:

1. **Mean per segment as base 100 index**: `(cluster_mean / total_mean) * 100` per variable
   - Index > 120 = distinctive characteristic of the segment
   - Index < 80 = relative weakness of the segment
2. **Summary table**: One row per segment, columns = variables + size (n and %)
3. **Naming**: Assign a business name based on the profile. Never "Cluster 0, 1, 2"
   - Example: "High-value digital" (online spending index = 180, frequency = 150)
   - Example: "Occasional buyers" (frequency index = 45, recency = 60)
4. **Visualization**: Index heatmap (segments x variables), radar/spider chart per segment

## 6. DBSCAN (alternative)

Use when KMeans does not work well (irregular clusters, outliers):
- `eps`: maximum distance between points in the same cluster. Estimate with k-distance plot
- `min_samples`: minimum points to form a cluster. Rule: >= 2 * n_features
- Points with label = -1 are outliers (investigate, do not discard)

## 7. Feature Importance as an Exploratory Tool

When the question is "what variables explain X the most?" or "what factors influence Y?", use feature importance as an exploratory technique — **not as a predictive model**.

**When to use**: To identify the most influential factors on a metric or segmentation. Useful as a complement to descriptive analysis when there are >5 candidate variables and simple correlations are not sufficient.

**Implementation**:
```python
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Choose based on the target variable type
# Numeric (sales, cost) → RandomForestRegressor
# Categorical (churn yes/no, segment) → RandomForestClassifier
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Extract importances
importances = pd.Series(model.feature_importances_, index=feature_names)
importances = importances.sort_values(ascending=False)
```

**Visualization**: Horizontal bar with the top 10-15 features, ordered by importance. Title as insight (e.g.: "The digital channel and tenure explain 60% of the variation in sales").

**Rules**:
- Use sklearn defaults — no hyperparameter tuning or formal cross-validation
- It is an exploratory tool, not a production model. Always label it as such
- Complement with correlations and descriptive analysis to validate the identified factors
- If a feature dominates (>40% importance), investigate whether there is leakage (a variable that "sees" the future)
- Report as: "The factors most associated with [metric] are..." — never as "The causes of [metric] are..."
