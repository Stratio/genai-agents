# Técnicas Analíticas Avanzadas

Activar según la profundidad seleccionada (ver matriz de activación en Fase 2).

## Rigor estadístico e incertidumbre

**Cuándo aplicar tests estadísticos:**

| Pregunta | Test | Condiciones | Implementación |
|----------|------|-------------|----------------|
| Diferencia entre 2 grupos (numérico) | t-test | Normales, n>30 | `scipy.stats.ttest_ind` |
| Diferencia entre 2 grupos (no normal) | Mann-Whitney U | No normales o n<30 | `scipy.stats.mannwhitneyu` |
| Diferencia entre 3+ grupos | ANOVA + Tukey | Normales, homocedásticos | `scipy.stats.f_oneway` |
| Relacion entre categóricas | Chi-cuadrado | Frec. esperadas >5 | `scipy.stats.chi2_contingency` |
| Correlación | Pearson / Spearman | Lineal / Monotónico | `scipy.stats.pearsonr` / `spearmanr` |
| Tendencia temporal significativa | Mann-Kendall | Serie >10 puntos | `scipy.stats.kendalltau` |

**Reglas:**
- SIEMPRE reportar p-valor + tamaño del efecto (Cohen's d, eta-cuadrado, V de Cramer)
- p < 0.05 = significativo. p < 0.01 = altamente significativo
- Resultado significativo con efecto pequeño puede no ser relevante para el negocio
- Con muestras grandes (>10k), casi todo es "significativo" — priorizar tamaño del efecto
- Calcular IC95% para KPIs: `mean +/- 1.96 * (std / sqrt(n))`. Para proporciones: `p +/- 1.96 * sqrt(p*(1-p)/n)`

**Comunicación de incertidumbre al negocio:**

| Nivel técnico | Como comunicarlo |
|---------------|-----------------|
| IC 95%: [120, 140] | "Entre 120 y 140 con alta confianza" |
| p < 0.01 | "La diferencia es real, no es azar" |
| p > 0.05 | "No hay evidencia suficiente para afirmar que hay diferencia" |
| Cohen's d = 0.2 | "La diferencia existe pero es pequeña" |
| Cohen's d = 0.8 | "La diferencia es grande y relevante" |
| R² = 0.65 | "El modelo explica el 65% de la variación" |

**Principio:** NUNCA presentar un número sin contexto de confianza. Preferir rangos a puntos únicos. Adaptar precisión del lenguaje a la audiencia.

## Análisis prospectivo y escenarios

Aplicar cuando el usuario pregunte "que pasaría si...", "como evolucionará...", o cuando los datos sugieran proyecciones útiles.

| Técnica | Cuándo usar | Implementación | Output |
|---------|------------|----------------|--------|
| **Escenarios** | Proyección con incertidumbre | Definir supuestos por escenario (+/- X%), calcular impacto | Tabla comparativa + fan chart |
| **Sensibilidad** | Identificar variables influyentes | Variar 1 variable a la vez (+/-10%, +/-20%), medir impacto en KPI | Tornado chart |
| **Monte Carlo** | Cuantificar riesgo multivariable | `numpy.random` con distribuciones, N=10000 iteraciones | Histograma + percentiles P5/P50/P95 |
| **Proyección lineal** | Tendencia clara con >12 puntos | `linregress` o `polyfit` + IC95% | Line + banda de confianza |

**Reglas:**
- Siempre explicitar supuestos de cada escenario
- Nunca presentar proyección sin banda de incertidumbre
- Etiquetar: "Proyección basada en [supuesto], no predicción"
- Para Monte Carlo: documentar distribuciones y justificación

## Root cause analysis

Activar cuando se detecta un problema, anomalía o desviación significativa.

**Framework:**
1. **Cuantificar**: Magnitud exacta (cuanto, desde cuándo, en qué dimensiones)
2. **Drill-down dimensional**: Descomponer por cada dimensión (tiempo, región, producto, segmento, canal). Query MCP: "métrica por [dimensión] en periodo problema vs referencia". Buscar donde se concentra la desviación
3. **Árbol de varianza**: Para la dimensión más explicativa, seguir profundizando (región -> ciudad, producto -> SKU)
4. **5 Whys**: Formular preguntas sucesivas hasta llegar a la causa raíz. Documentar cada nivel
5. **Correlación vs causación**: Verificar temporalidad (causa precede efecto), mecanismo lógico de negocio, y descartar factores confusores. Si no se puede establecer causación, reportar como "asociación"

**Visualizaciones:** Waterfall de varianza, treemap de contribución, timeline de eventos

## Detección de anomalías

| Tipo | Método | Implementación | Criterio |
|------|--------|----------------|----------|
| **Outliers estáticos** | IQR o Z-score | `Q1 - 1.5*IQR` / `Q3 + 1.5*IQR`, o `abs(z) > 3` | Ya en EDA (Fase 1.1) |
| **Anomalías temporales** | Desviación de tendencia+estacionalidad | `statsmodels.tsa.seasonal_decompose`, residuo > 2*std | Serie >12 puntos |
| **Cambio de tendencia** | Diferencia de medias pre/post | Media móvil + t-test entre ventanas | Ventana mínima: 5 puntos |
| **Anomalías categóricas** | Desviación de distribución esperada | Chi-cuadrado vs distribución histórica | p < 0.01 |

**Anomalía real vs error de datos:**
- Verificar con `search_domain_knowledge` si hay eventos conocidos
- Si aparece en múltiples métricas → probablemente real
- Si solo en una columna/dimensión → probable error → alertar, no reportar como insight
