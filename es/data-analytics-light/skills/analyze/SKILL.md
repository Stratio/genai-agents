---
name: analyze
description: "Análisis completo de datos BI/BA — descubrimiento de dominio, EDA y calidad de datos, planificación de métricas y KPIs con framework analítico, queries de datos vía MCP, análisis Python con pandas, visualizaciones. Usar cuando el usuario necesite analizar datos de negocio, calcular KPIs, producir visualizaciones, generar resúmenes gráficos, obtener insights o responder preguntas analíticas sobre dominios gobernados. También se activa para comparaciones multi-métrica, resúmenes de KPIs o cualquier petición que requiera cruzar datos entre dimensiones."
argument-hint: "[pregunta o tema de análisis]"
---

# Skill: Análisis BI/BA Completo

Esta guía define el workflow completo para realizar un análisis de Business Intelligence / Business Analytics.

## 1. Parsear la Petición

- Extraer la pregunta de negocio principal del argumento: $ARGUMENTS
- Identificar sub-preguntas implicitas
- Detectar si menciona un dominio, tablas o métricas específicas

### 1.1 Triage rápido

Si la petición se resuelve con una sola llamada MCP (ver Fase 0), responder directamente:
- Definiciones/conceptos → `search_domain_knowledge` → chat
- Estructura/columnas → `list_domain_tables` / `get_table_columns_details` → chat
- Dato puntual → `query_data` → chat
- En estos casos, NO continuar con el resto del workflow

Si la petición requiere análisis (cruce de datos, hipótesis, visualizaciones, múltiples métricas), continuar con sección 2.

### 1.2 Atajo de entregable rápido

Si la petición trata principalmente de producir un resumen con visualizaciones (resumen gráfico, overview de KPIs, análisis visual) y la conversación ya contiene contexto de dominio (dominio identificado, tablas exploradas, datos consultados en turnos anteriores):

1. **Saltar descubrimiento** — usar el contexto de dominio y tablas de la conversación
2. **EDA mínimo** — solo comprobación de completitud si los datos ya fueron explorados; omitir profiling completo
3. **Auto-detectar parámetros**: profundidad siempre Quick; audiencia inferida del contexto (por defecto Mixed/General)
4. **Presentar un plan breve** con las preguntas de datos y las visualizaciones planeadas. Pedir confirmación al usuario
5. **Ejecutar**: consultar datos → procesar → generar visualizaciones → presentar hallazgos y visualizaciones en el chat

Si la conversación NO contiene contexto de dominio suficiente (sin dominio identificado, sin exploración previa), continuar con el workflow estándar (sección 2 en adelante).

## 2. Descubrimiento de Dominio

Leer y seguir `skills-guides/stratio-data-tools.md` sec 4 para los pasos de descubrimiento del dominio (buscar o listar dominios, seleccionar, explorar tablas, columnas y terminología).

## 3. EDA y Calidad de Datos

Antes de preguntar al usuario y planificar métricas, entender la realidad de los datos:

1. **Profiling**: Ejecutar `profile_data` sobre las tablas clave identificadas en el paso 2. Seguir la mecánica y umbrales adaptativos de `skills-guides/stratio-data-tools.md` sec 5
2. **Evaluar calidad**:
   - **Completitud**: % de nulos por columna. Marcar columnas con >50% nulos como limitación
   - **Rango temporal**: Verificar que los datos cubren el periodo que el usuario necesita
   - **Outliers**: Identificar valores extremos (IQR) que podrían sesgar promedios o totales
   - **Distribuciones**: Sesgo en numéricas, desbalanceo en categóricas
   - **Correlaciones**: Relaciones fuertes entre variables (|r| > 0.7) — pueden indicar multicolinealidad o redundancia
   - **Cardinalidad**: Categóricas con >100 valores únicos son difíciles de visualizar o agrupar
3. **Checklist de suficiencia** — Aplicar ANTES de preguntar al usuario:

   | Criterio | Umbral mínimo | Si falla |
   |----------|---------------|----------|
   | Registros | >0 | STOP — reformular query |
   | Completitud temporal | ≥80% del periodo pedido | Ofrecer análisis del periodo disponible |
   | Nulos en vars clave | <30% | Alertar limitación severa, considerar imputación |
   | Tamaño para inferencia | n ≥ 30 | Reportar como exploratorio, sin tests estadísticos |
   | Variabilidad | std > 0 en numéricas clave | Excluir variable constante |
   | Granularidad | Nivel pedido disponible | Ofrecer agregacion al disponible |

4. **Data Quality Score**: ALTO (80-100%), MEDIO (60-79%), BAJO (<60%). Si BAJO, recomendar mejorar datos o reformular
5. **Informar al usuario**: Generar mini-resumen de calidad + Data Quality Score antes de preguntarle sobre profundidad. Ejemplo:
   - "**Calidad: ALTO (85%)**. Los datos cubren de enero 2023 a diciembre 2025. La columna `descuento` tiene un 35% de nulos. Se detectaron 12 outliers en `importe_total` (>3 IQR). La distribución de `categoria_producto` está concentrada: 3 de 15 categorías representan el 80% de registros."
6. **Ajustar expectativas**: Si hay limitaciones serias, advertir al usuario de que ciertas métricas o visualizaciones podrían no ser fiables

## 4. Clasificación y Preguntas al Usuario

> **Nota**: Todas las preguntas con opciones de esta sección siguen la convención de preguntas (sec 10).

### 4.0 Triage vs Análisis

Las preguntas simples (datos puntuales, sin dimensiones de corte) se resuelven en Triage (Fase 0 del workflow) sin invocar esta skill. Todo lo demás es un análisis y sigue el flujo de bloques de preguntas descrito a continuación.

### 4.1 Bloque 1 — Profundidad, Audiencia y Testing

Una sola interacción:

| # | Pregunta | Opciones (literales) | Selección | Condicion |
|---|----------|---------------------|-----------|-----------|
| 1 | ¿Qué profundidad de análisis prefieres? | **Rápido** · **Estándar** (Recomendado) · **Profundo** | Única | Siempre |
| 2 | ¿Para que audiencia es el análisis? | **C-level/Direccion** · **Manager/Responsable** · **Equipo técnico/Data** · **Mixta/General** | Única | Siempre |
| 3 | ¿Quieres que se generen y ejecuten tests unitarios sobre el código Python? | **Sí** (Recomendado): mejora precisión y calidad, pero consume más tiempo, coste y contexto · **No**: ejecución directa sin tests | Única | Solo Estándar/Profundo |

- Los tests validan transformaciones y cálculos antes de ejecutar con datos reales. Mejoran la precisión pero consumen más tokens, tiempo y coste. **En profundidad Rápido, testing se desactiva automáticamente sin preguntar al usuario.**

## 5. Planificación

Elaborar un plan detallado siguiendo el framework analítico (sec "Framework Analítico" de AGENTS.md):

### 5.1 Enfoque analítico

Determinar si la pregunta requiere análisis descriptivo, segmentación por reglas, o técnicas estadísticas avanzadas:

| Escenario | Recomendación |
|-----------|---------------|
| Describir que paso y por qué | Análisis descriptivo (pandas, agrupaciones, comparativas) |
| Segmentar clientes/productos | Segmentación por reglas o RFM → sec 5.8 |
| Proyectar tendencias | Técnicas estadísticas (statsmodels, seasonal decompose) → sec 5.6 |
| Detectar patrones y anomalías | Análisis estadístico avanzado → sec 5.6 |

### 5.2 Hipótesis
Formular hipótesis ANTES de consultar datos. Usar la plantilla de sec "Pensamiento analítico" de AGENTS.md. Para cada sub-pregunta identificada en el paso 1:
- Que esperamos encontrar y por que
- Que resultado seria sorprendente
- Documentar las hipótesis en el plan para validarlas luego con datos
**Ejemplo completo:**
```
### H1: Ventas Q4 ≥30% superiores al promedio Q1-Q3 por estacionalidad retail
- Enunciado: El ratio ventas_Q4 / promedio(ventas_Q1-Q3) es ≥ 1.30
- Fundamento: Pico estacional observado en nov-dic durante EDA
- Cómo validar: query "ventas totales por trimestre del último año"
- Criterio: ratio ≥ 1.30
→ Resultado: CONFIRMADA (ratio = 1.45)
→ Evidencia: Q4 = €2.1M vs promedio Q1-Q3 = €1.45M
→ So What: Q4 = 36% ventas anuales. Ajustar inventario desde oct, reforzar logística nov
→ Confianza: Alta (3 años de datos, patrón consistente)
```

### 5.3 Métricas y KPIs

Para cada KPI, documentar:

| Campo | Descripción |
|-------|-------------|
| Nombre | Identificador claro |
| Fórmula | Cálculo exacto |
| Granularidad | Temporal: diario/semanal/mensual/trimestral |
| Dimensiones | Ejes de corte (región, producto, segmento) |
| Benchmark | Objetivo, media del sector, o periodo anterior |
| Fuente | Tabla(s) y columna(s) del dominio |
| Test estadístico | Si requiere IC o comparación entre grupos (ver sección 5.6 de esta skill) |

**Benchmark Discovery** — Escala según profundidad (ver matriz de activación):
- **Rápido**: No buscar activamente. Usar comparación temporal natural si la query ya incluye dimensión tiempo
- **Estándar**: Best-effort silencioso:
  1. `search_domain_knowledge("target/objetivo de [nombre_KPI]", domain)`
  2. Query MCP adicional para mismo KPI en periodo T-1
  3. Si no hay referencia externa: media/mediana como referencia interna
  Sin benchmark → reportar el dato normalmente
- **Profundo**: Pasos 1-3 + tendencia si >6 puntos temporales + preguntar al usuario

### 5.4 Preguntas de datos
Lista de preguntas en lenguaje natural para `query_data`. NUNCA escribir SQL.

Para buenas prácticas de formulación y estrategia de queries (orden de planificación, ejecución en paralelo), ver `skills-guides/stratio-data-tools.md` sec 9.

### 5.5 Visualizaciones

Ver [visualization.md](visualization.md) para principios de visualización y data storytelling.

Para cada visualización del plan, definir:
- **Pregunta analítica** que responde
- **Tipo de gráfica**: Seleccionar según la pregunta analítica (ver guía de selección en [visualization.md](visualization.md))
- **Variables**: Que va en cada eje, agrupaciones, filtros
- **Título**: Formulado como insight, no como descripción
- **Datos fuente**: Query MCP que alimenta la visualización

### 5.6 Técnicas analíticas avanzadas

Activar según la profundidad seleccionada (ver matriz de activación):
- **Estándar**: Consultar [advanced-analytics.md](advanced-analytics.md) cuando sea relevante
- **Profundo**: Consultar [advanced-analytics.md](advanced-analytics.md) sistemáticamente

Cubre: rigor estadístico (tests, IC, effect sizes), análisis prospectivo (escenarios, Monte Carlo), root cause analysis, detección de anomalías.

### 5.7 Patrones analíticos adicionales

Implementación detallada de patrones cuyo trigger está en sec 3.2 (Lorenz/Gini, mix, indexación, desviación vs referencia, gap).

Cuando un patrón se active: consultar [analytical-patterns.md](analytical-patterns.md) para query MCP, Python e interpretación.

### 5.8 Segmentación y clustering

Para guía completa de segmentación (RFM, clustering, validación, profiling), ver [clustering-guide.md](clustering-guide.md).

Usar cuando el usuario pida segmentación, agrupación de clientes/productos, o descubrimiento de perfiles. La guía cubre:
- Tabla de decisión (cuando usar rule-based o RFM)
- RFM con quintiles y etiquetas de negocio
- Profiling obligatorio de segmentos

### 5.9 Estructura de la presentación de resultados
Secciones del análisis y orden narrativo para presentar en el chat. Aplicar principios de data storytelling (sección 7.1)

### 5.10 Presentar plan
Presentar plan completo al usuario y solicitar aprobación antes de ejecutar

## 6. Ejecución

### 6.0 Obtención de datos
- Usar `query_data(data_question=..., domain_name=..., output_format="dict")` para cada pregunta de datos. **Lanzar en paralelo** todas las queries independientes definidas en el plan (paso 5.4). Solo serializar si una query necesita el resultado de otra para formularse
- Seguir todas las reglas de `skills-guides/stratio-data-tools.md` (MCP-first, output_format, no SQL manual, ejecución en paralelo)
- Guardar datos intermedios como CSV solo si un script posterior los necesita como input

### 6.1 Validación post-query (obligatorio)
Aplicar las 7 validaciones de `skills-guides/stratio-data-tools.md` sec 7 a cada resultado recibido. Cuando se lanzan queries en paralelo, validar cada resultado conforme llega. Si alguna falla: reformular la pregunta al MCP, informar al usuario, ajustar el plan.

### 6.2 Desarrollo de scripts
- Escribir scripts con nombres descriptivos que incluyan contexto del análisis
- Cada script debe:
  - Leer datos de CSVs guardados previamente o recibir datos como parámetro
  - Realizar transformaciones y cálculos
  - Generar visualizaciones
- **Datasets grandes (>100k filas)**: Usar muestreo estratificado para desarrollo rápido, datos completos para la versión final

### 6.3 Testing

> **Solo si la profundidad es Estándar/Profundo Y el usuario eligió "Sí" en la pregunta de testing del Bloque 1.** En profundidad Rápido o si el usuario eligió "No", omitir esta sección y ejecutar directamente el script con datos reales.

- Generar tests unitarios ANTES de ejecutar con datos reales
- Usar DataFrames mock con estructura similar a los datos reales
- Validar transformaciones, cálculos y formatos de salida
- Solo proceder si los tests pasan

### 6.4 Ejecución con datos reales
Ejecutar scripts con datos reales.

### 6.5 Loop de iteración

Tras revisar resultados iniciales, evaluar si requieren iteración:

1. **Trigger**: Hallazgo contradice hipótesis, patrón inesperado, o pregunta crítica no prevista
2. **Acción**: Documentar hallazgo → formular nueva(s) pregunta(s) → queries MCP adicionales (6.0-6.1) → actualizar scripts
3. **Limite**: Max 2 iteraciones. Más → documentar como análisis de seguimiento
4. **Registro**: Cada iteración documentar en el chat: hipótesis → hallazgo → nueva hipótesis → resultado

### 6.6 Complexity Upgrade

Si durante la ejecución se detecta un hallazgo que excede el alcance del nivel de complejidad actual:

**Triggers:**
- Anomalía: resultado difiere >30% del benchmark o de lo razonable para el dominio
- Inconsistencia: dos queries dan totales que no cuadran (diferencia >5%)
- Patrón crítico: concentración Gini >0.8, caida/crecimiento >50% interperiodo, outlier en KPI principal

**Acción:**
1. Pausar la ejecución normal
2. Informar al usuario siguiendo la convención de preguntas (sec 10): "He detectado [descripción del hallazgo]. Esto requiere investigación adicional. ¿Quieres que profundice?" con opciones:
   - "Sí, profundizar" → Escalar complejidad, activar fases adicionales (EDA completo, hipótesis sobre el hallazgo, visualizaciones de drill-down)
   - "No, solo documentar" → Registrar hallazgo en el chat como "área de investigación futura"
3. El upgrade NO reinicia el análisis — extiende el análisis actual con fases adicionales

**Diferencia con el loop de iteración (6.5):** El loop refina hipótesis dentro del mismo nivel de complejidad. El upgrade cambia el nivel (ej: Triage → Análisis) y activa capacidades adicionales (EDA, hipótesis formales, visualizaciones).

### 6.7 Presentación de resultados
La presentación de resultados se hace en el chat, siguiendo la estructura de la sección 7.1. Las visualizaciones generadas se muestran inline como soporte del análisis.

### 6.8 Validación de output final
Antes de presentar al usuario, verificar:
- Las visualizaciones se generaron correctamente
- Los datos usados son coherentes entre si (totales cuadran, periodos alineados)
- Los hallazgos pasan el checklist "So What?" de la sección 7.1

Si alguna visualización falla, regenerarla o presentar los datos en formato tabla.

## 7. Reporte Final

### 7.1 Estructura del reporte en chat

Al presentar hallazgos en la conversación, seguir esta estructura:

1. **Hook**: El hallazgo más impactante primero
2. Resumen ejecutivo (3-5 bullets con "so what")
3. Insights con datos concretos y contexto comparativo (vs anterior, vs objetivo)
4. Recomendaciones accionables priorizadas (alto impacto + alta confianza primero)
5. Limitaciones y caveats
6. Sugerencias de análisis de seguimiento

**Checklist "So What?" obligatorio** — Para CADA hallazgo antes de incluirlo:

| Pregunta | Malo (dato) | Bueno (insight accionable) |
|----------|-------------|--------------------------|
| **Magnitud?** | "Las ventas bajaron" | "Bajaron 12%, ≈€45K/mes" |
| **Vs. qué?** | "Norte va bien" | "Norte +23% vs media nacional, +8% vs target" |
| **Qué hacer?** | "Mejorar retención" | "Programa fidelización en Premium (45% vs 72% benchmark) → ROI €120K/año" |
| **Confianza?** | "Clientes prefieren A" | Adaptar a profundidad: Rápido="67% (n=450, Alta)"; Estándar="67% (n=450, IC95%: 62-72%)"; Profundo="67% (n=450, IC95%: 62-72%, p<0.001)" |

Si un hallazgo no pasa las 4 preguntas → es información, no insight. No va al resumen ejecutivo.

**Clasificación de insights** — Determina ubicación en el reporte:
- **CRITICO**: Alto impacto + alta confianza → Resumen ejecutivo, recomendación firme
- **IMPORTANTE**: Alto impacto + baja confianza → Sección principal, investigar más
- **INFORMATIVO**: Bajo impacto → Apéndice, sin recomendación

Para principios de data storytelling y mapping hallazgos → narrativa, leer [visualization.md](visualization.md) secciones 3 y 4.

## 8. Propuesta de Conocimiento (Opcional)

Tras presentar el reporte final, preguntar al usuario siguiendo la convención de preguntas (sec 10):
- **Si**: Analizar conversación y proponer conocimiento al dominio
- **No**: Finalizar sin proponer

Si acepta, cargar la skill `propose-knowledge` con el dominio usado en este análisis.
Si rechaza, finalizar normalmente.

Este paso es SIEMPRE opcional. Nunca proponer automáticamente.
