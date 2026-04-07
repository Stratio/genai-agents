# Guía de Segmentación y Clustering

Referencia operativa para segmentación como herramienta analítica dentro de `/analyze`.

## 1. Tabla de Decisión

| Situación | Enfoque | Cuando preferir |
|-----------|---------|-----------------|
| Segmentos ya definidos por negocio (VIP, Regular, Nuevo) | Rule-based con umbrales | Reglas claras, interpretabilidad máxima |
| Datos transaccionales, segmentación estándar retail | RFM con quintiles | Pocas variables, fácil de comunicar |
| Sin segmentos predefinidos, múltiples variables (>3) | KMeans + silhouette | Variables numéricas, clusters esféricos |
| Clusters irregulares o detección de outliers | DBSCAN | Formas arbitrarias, no se conoce k |

## 2. RFM (Recency, Frequency, Monetary)

**Query MCP**: "fecha de última compra, número total de compras y total gastado por cliente"

**Cálculo**:
1. R = días desde última compra (menor = mejor)
2. F = número de compras (mayor = mejor)
3. M = total gastado (mayor = mejor)
4. Quintiles: `pd.qcut(serie, q=5, labels=[1,2,3,4,5])`. Invertir R (5 = más reciente)
5. Score: concatenar R+F+M como string o sumar para score numérico

**Etiquetas de negocio** (obligatorio — nunca "Segmento 1, 2, 3"):

| Score RFM | Etiqueta | Descripción |
|-----------|----------|-------------|
| 555, 554, 544 | Champions | Compraron reciente, compran frecuente, gastan mucho |
| 543, 444, 435 | Leales | Compras regulares con buen gasto |
| 512, 511, 422 | Potenciales | Compra reciente pero poca frecuencia |
| 155, 154, 144 | En riesgo | Fueron buenos pero hace mucho que no compran |
| 111, 112, 121 | Hibernando | Baja actividad en todas las dimensiones |

Adaptar etiquetas al dominio específico. La tabla es orientativa.

## 3. Clustering con KMeans

**Preprocesamiento obligatorio**:
1. Escalar variables: `StandardScaler()` (KMeans sensible a escala)
2. Manejar nulos: imputar o excluir antes de escalar
3. Variables categóricas: encoding o excluir (KMeans solo numéricas)

**Selección de k**:
1. **Elbow method**: Graficar inertia vs k (k=2..10). Buscar el "codo"
2. **Silhouette score**: `silhouette_score(X, labels)` para cada k. Mayor = mejor
3. Usar ambos para decidir. Si divergen, priorizar silhouette

**Implementación**:
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
# Elegir k con mayor silhouette (o codo en inertia)
```

## 4. Validación de Clusters

| Criterio | Umbral | Acción si falla |
|----------|--------|-----------------|
| Silhouette score | > 0.5 bueno, > 0.25 aceptable | Probar otro k o DBSCAN |
| Tamaño mínimo por cluster | ≥ 5% de la población | Fusionar clusters pequeños |
| Estabilidad | Ejecutar con 3 random seeds diferentes | Si cambia mucho, clusters no son robustos |
| Separacion visual | Scatter 2D (PCA) muestra grupos distinguibles | Si solapan, considerar reducir features |

## 5. Profiling Obligatorio

Tras asignar clusters, SIEMPRE generar perfil de negocio:

1. **Media por segmento como índice base 100**: `(media_cluster / media_total) * 100` por variable
   - Índice > 120 = característica distintiva del segmento
   - Índice < 80 = debilidad relativa del segmento
2. **Tabla resumen**: Una fila por segmento, columnas = variables + tamaño (n y %)
3. **Naming**: Asignar nombre de negocio basado en el perfil. Nunca "Cluster 0, 1, 2"
   - Ejemplo: "Alto valor digital" (índice gasto online = 180, frecuencia = 150)
   - Ejemplo: "Compradores ocasionales" (índice frecuencia = 45, recencia = 60)
4. **Visualización**: Heatmap de índices (segmentos x variables), radar/spider chart por segmento

## 6. DBSCAN (alternativa)

Usar cuando KMeans no funciona bien (clusters irregulares, outliers):
- `eps`: distancia máxima entre puntos del mismo cluster. Estimar con k-distance plot
- `min_samples`: mínimo puntos para formar cluster. Regla: ≥ 2 * n_features
- Puntos con label = -1 son outliers (investigar, no descartar)

## 7. Feature Importance como Herramienta Exploratoria

Cuando la pregunta es "que variables explican más X?" o "que factores influyen en Y?", usar feature importance como técnica exploratoria — **no como modelo predictivo**.

**Cuándo usar**: Para identificar los factores más influyentes en una métrica o segmentación. Útil como complemento al análisis descriptivo cuando hay >5 variables candidatas y las correlaciones simples no son suficientes.

**Implementación**:
```python
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Elegir según el tipo de variable objetivo
# Numerica (ventas, coste) → RandomForestRegressor
# Categorica (churn si/no, segmento) → RandomForestClassifier
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# Extraer importances
importances = pd.Series(model.feature_importances_, index=feature_names)
importances = importances.sort_values(ascending=False)
```

**Visualización**: Bar horizontal con las top 10-15 features, ordenadas por importancia. Título como insight (ej: "El canal digital y la antigüedad explican el 60% de la variación en ventas").

**Reglas**:
- Usar defaults de sklearn — sin hyperparameter tuning ni cross-validation formal
- Es una herramienta exploratoria, no un modelo para producción. Etiquetar siempre como tal
- Complementar con correlaciones y análisis descriptivo para validar los factores identificados
- Si una feature domina (>40% importancia), investigar si hay leakage (variable que "ve" el futuro)
- Reportar como: "Los factores más asociados con [métrica] son..." — nunca como "Las causas de [métrica] son..."
