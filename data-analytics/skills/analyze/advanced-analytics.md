# Tecnicas Analiticas Avanzadas

Activar segun la profundidad seleccionada (ver matriz de activacion en Fase 2 del workflow (AGENTS.md)).

## Rigor estadistico e incertidumbre

**Cuando aplicar tests estadisticos:**

| Pregunta | Test | Condiciones | Implementacion |
|----------|------|-------------|----------------|
| Diferencia entre 2 grupos (numerico) | t-test | Normales, n>30 | `scipy.stats.ttest_ind` |
| Diferencia entre 2 grupos (no normal) | Mann-Whitney U | No normales o n<30 | `scipy.stats.mannwhitneyu` |
| Diferencia entre 3+ grupos | ANOVA + Tukey | Normales, homocedasticos | `scipy.stats.f_oneway` |
| Relacion entre categoricas | Chi-cuadrado | Frec. esperadas >5 | `scipy.stats.chi2_contingency` |
| Correlacion | Pearson / Spearman | Lineal / Monotonico | `scipy.stats.pearsonr` / `spearmanr` |
| Tendencia temporal significativa | Mann-Kendall | Serie >10 puntos | `scipy.stats.kendalltau` |

**Reglas:**
- SIEMPRE reportar p-valor + tamano del efecto (Cohen's d, eta-cuadrado, V de Cramer)
- p < 0.05 = significativo. p < 0.01 = altamente significativo
- Resultado significativo con efecto pequeno puede no ser relevante para el negocio
- Con muestras grandes (>10k), casi todo es "significativo" — priorizar tamano del efecto
- Calcular IC95% para KPIs: `mean +/- 1.96 * (std / sqrt(n))`. Para proporciones: `p +/- 1.96 * sqrt(p*(1-p)/n)`

**Comunicacion de incertidumbre al negocio:**

| Nivel tecnico | Como comunicarlo |
|---------------|-----------------|
| IC 95%: [120, 140] | "Entre 120 y 140 con alta confianza" |
| p < 0.01 | "La diferencia es real, no es azar" |
| p > 0.05 | "No hay evidencia suficiente para afirmar que hay diferencia" |
| Cohen's d = 0.2 | "La diferencia existe pero es pequena" |
| Cohen's d = 0.8 | "La diferencia es grande y relevante" |
| R² = 0.65 | "El modelo explica el 65% de la variacion" |

**Principio:** NUNCA presentar un numero sin contexto de confianza. Preferir rangos a puntos unicos. Adaptar precision del lenguaje a la audiencia.

## Analisis prospectivo y escenarios

Aplicar cuando el usuario pregunte "que pasaria si...", "como evolucionara...", o cuando los datos sugieran proyecciones utiles.

| Tecnica | Cuando usar | Implementacion | Output |
|---------|------------|----------------|--------|
| **Escenarios** | Proyeccion con incertidumbre | Definir supuestos por escenario (+/- X%), calcular impacto | Tabla comparativa + fan chart |
| **Sensibilidad** | Identificar variables influyentes | Variar 1 variable a la vez (+/-10%, +/-20%), medir impacto en KPI | Tornado chart |
| **Monte Carlo** | Cuantificar riesgo multivariable | `numpy.random` con distribuciones, N=10000 iteraciones | Histograma + percentiles P5/P50/P95 |
| **Proyeccion lineal** | Tendencia clara con >12 puntos | `linregress` o `polyfit` + IC95% | Line + banda de confianza |

**Reglas:**
- Siempre explicitar supuestos de cada escenario
- Nunca presentar proyeccion sin banda de incertidumbre
- Etiquetar: "Proyeccion basada en [supuesto], no prediccion"
- Para Monte Carlo: documentar distribuciones y justificacion

## Root cause analysis

Activar cuando se detecta un problema, anomalia o desviacion significativa.

**Framework:**
1. **Cuantificar**: Magnitud exacta (cuanto, desde cuando, en que dimensiones)
2. **Drill-down dimensional**: Descomponer por cada dimension (tiempo, region, producto, segmento, canal). Query MCP: "metrica por [dimension] en periodo problema vs referencia". Buscar donde se concentra la desviacion
3. **Arbol de varianza**: Para la dimension mas explicativa, seguir profundizando (region -> ciudad, producto -> SKU)
4. **5 Whys**: Formular preguntas sucesivas hasta llegar a la causa raiz. Documentar cada nivel
5. **Correlacion vs causacion**: Verificar temporalidad (causa precede efecto), mecanismo logico de negocio, y descartar factores confusores. Si no se puede establecer causacion, reportar como "asociacion"

**Visualizaciones:** Waterfall de varianza, treemap de contribucion, timeline de eventos

## Deteccion de anomalias

| Tipo | Metodo | Implementacion | Criterio |
|------|--------|----------------|----------|
| **Outliers estaticos** | IQR o Z-score | `Q1 - 1.5*IQR` / `Q3 + 1.5*IQR`, o `abs(z) > 3` | Ya en EDA (Fase 1.5) |
| **Anomalias temporales** | Desviacion de tendencia+estacionalidad | `statsmodels.tsa.seasonal_decompose`, residuo > 2*std | Serie >12 puntos |
| **Cambio de tendencia** | Diferencia de medias pre/post | Media movil + t-test entre ventanas | Ventana minima: 5 puntos |
| **Anomalias categoricas** | Desviacion de distribucion esperada | Chi-cuadrado vs distribucion historica | p < 0.01 |

**Anomalia real vs error de datos:**
- Verificar con `stratio_search_domain_knowledge` si hay eventos conocidos
- Si aparece en multiples metricas → probablemente real
- Si solo en una columna/dimension → probable error → alertar, no reportar como insight
