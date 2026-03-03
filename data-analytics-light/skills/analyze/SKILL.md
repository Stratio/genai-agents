---
name: analyze
description: Analisis completo de datos BI/BA — descubrimiento de dominio, EDA y calidad de datos, planificacion de metricas y KPIs con framework analitico, queries de datos via MCP, analisis Python con pandas, visualizaciones. Usar cuando el usuario necesite analizar datos de negocio, calcular KPIs, obtener insights o responder preguntas analiticas sobre dominios gobernados.
argument-hint: [pregunta o tema de analisis]
---

# Skill: Analisis BI/BA Completo

Esta guia define el workflow completo para realizar un analisis de Business Intelligence / Business Analytics.

## 1. Parsear la Peticion

- Extraer la pregunta de negocio principal del argumento: $ARGUMENTS
- Identificar sub-preguntas implicitas
- Detectar si menciona un dominio, tablas o metricas especificas

### 1.1 Triage rapido

Si la peticion se resuelve con una sola llamada MCP (ver Fase 0), responder directamente:
- Definiciones/conceptos → `stratio_search_domain_knowledge` → chat
- Estructura/columnas → `stratio_list_domain_tables` / `stratio_get_table_columns_details` → chat
- Dato puntual → `stratio_query_data` → chat
- En estos casos, NO continuar con el resto del workflow

Si la peticion requiere analisis (cruce de datos, hipotesis, visualizaciones, multiples metricas), continuar con seccion 2.

## 2. Descubrimiento de Dominio

Leer y seguir `skills-guides/exploration.md` para los pasos de descubrimiento del dominio (listar dominios, seleccionar, explorar tablas, columnas, terminologia y profiling).

## 2.5. EDA y Calidad de Datos

Antes de preguntar al usuario y planificar metricas, entender la realidad de los datos:

1. **Profiling**: Ejecutar `stratio_profile_data` sobre las tablas clave identificadas en el paso 2. Seguir la mecanica y umbrales adaptativos de `skills-guides/exploration.md` sec 7
2. **Evaluar calidad**:
   - **Completitud**: % de nulos por columna. Marcar columnas con >50% nulos como limitacion
   - **Rango temporal**: Verificar que los datos cubren el periodo que el usuario necesita
   - **Outliers**: Identificar valores extremos (IQR) que podrian sesgar promedios o totales
   - **Distribuciones**: Sesgo en numericas, desbalanceo en categoricas
   - **Correlaciones**: Relaciones fuertes entre variables (|r| > 0.7) — pueden indicar multicolinealidad o redundancia
   - **Cardinalidad**: Categoricas con >100 valores unicos son dificiles de visualizar o agrupar
3. **Checklist de suficiencia** — Aplicar ANTES de preguntar al usuario:

   | Criterio | Umbral minimo | Si falla |
   |----------|---------------|----------|
   | Registros | >0 | STOP — reformular query |
   | Completitud temporal | ≥80% del periodo pedido | Ofrecer analisis del periodo disponible |
   | Nulos en vars clave | <30% | Alertar limitacion severa, considerar imputacion |
   | Tamano para inferencia | n ≥ 30 | Reportar como exploratorio, sin tests estadisticos |
   | Variabilidad | std > 0 en numericas clave | Excluir variable constante |
   | Granularidad | Nivel pedido disponible | Ofrecer agregacion al disponible |

4. **Data Quality Score**: ALTO (80-100%), MEDIO (60-79%), BAJO (<60%). Si BAJO, recomendar mejorar datos o reformular
5. **Informar al usuario**: Generar mini-resumen de calidad + Data Quality Score antes de preguntarle sobre profundidad. Ejemplo:
   - "**Calidad: ALTO (85%)**. Los datos cubren de enero 2023 a diciembre 2025. La columna `descuento` tiene un 35% de nulos. Se detectaron 12 outliers en `importe_total` (>3 IQR). La distribucion de `categoria_producto` esta concentrada: 3 de 15 categorias representan el 80% de registros."
6. **Ajustar expectativas**: Si hay limitaciones serias, advertir al usuario de que ciertas metricas o visualizaciones podrian no ser fiables

## 3. Clasificacion y Preguntas al Usuario

> **Nota**: Todas las preguntas con opciones de esta seccion siguen la convencion de preguntas (sec 10).

### 3.0 Triage vs Analisis

Las preguntas simples (datos puntuales, sin dimensiones de corte) se resuelven en Triage (Fase 0 del workflow) sin invocar esta skill. Todo lo demas es un analisis y sigue el flujo de bloques de preguntas descrito a continuacion.

### 3.1 Bloque 1 — Profundidad, Audiencia y Testing

Una sola interaccion:

| # | Pregunta | Opciones (literales) | Seleccion | Condicion |
|---|----------|---------------------|-----------|-----------|
| 1 | ¿Que profundidad de analisis prefieres? | **Rapido** · **Estandar** (Recomendado) · **Profundo** | Unica | Siempre |
| 2 | ¿Para que audiencia es el analisis? | **C-level/Direccion** · **Manager/Responsable** · **Equipo tecnico/Data** · **Mixta/General** | Unica | Siempre |
| 3 | ¿Quieres que se generen y ejecuten tests unitarios sobre el código Python? | **Sí** (Recomendado): mejora precisión y calidad, pero consume más tiempo, coste y contexto · **No**: ejecución directa sin tests | Única | Solo Estandar/Profundo |

- Los tests validan transformaciones y cálculos antes de ejecutar con datos reales. Mejoran la precisión pero consumen más tokens, tiempo y coste. **En profundidad Rápido, testing se desactiva automáticamente sin preguntar al usuario.**

## 4. Planificacion

Elaborar un plan detallado siguiendo el framework analitico (seccion 3):

### 4.1 Enfoque analitico

Determinar si la pregunta requiere analisis descriptivo, segmentacion por reglas, o tecnicas estadisticas avanzadas:

| Escenario | Recomendacion |
|-----------|---------------|
| Describir que paso y por que | Analisis descriptivo (pandas, agrupaciones, comparativas) |
| Segmentar clientes/productos | Segmentacion por reglas o RFM → sec 4.8 |
| Proyectar tendencias | Tecnicas estadisticas (statsmodels, seasonal decompose) → sec 4.6 |
| Detectar patrones y anomalias | Analisis estadistico avanzado → sec 4.6 |

### 4.2 Hipotesis
Formular hipotesis ANTES de consultar datos. Usar la plantilla de sec 3.1. Para cada sub-pregunta identificada en el paso 1:
- Que esperamos encontrar y por que
- Que resultado seria sorprendente
- Documentar las hipotesis en el plan para validarlas luego con datos
**Ejemplo completo:**
```
### H1: Ventas Q4 ≥30% superiores al promedio Q1-Q3 por estacionalidad retail
- Enunciado: El ratio ventas_Q4 / promedio(ventas_Q1-Q3) es ≥ 1.30
- Fundamento: Pico estacional observado en nov-dic durante EDA
- Como validar: query "ventas totales por trimestre del ultimo ano"
- Criterio: ratio ≥ 1.30
→ Resultado: CONFIRMADA (ratio = 1.45)
→ Evidencia: Q4 = €2.1M vs promedio Q1-Q3 = €1.45M
→ So What: Q4 = 36% ventas anuales. Ajustar inventario desde oct, reforzar logistica nov
→ Confianza: Alta (3 anos de datos, patron consistente)
```

### 4.3 Metricas y KPIs

Para cada KPI, documentar:

| Campo | Descripcion |
|-------|-------------|
| Nombre | Identificador claro |
| Formula | Calculo exacto |
| Granularidad | Temporal: diario/semanal/mensual/trimestral |
| Dimensiones | Ejes de corte (region, producto, segmento) |
| Benchmark | Objetivo, media del sector, o periodo anterior |
| Fuente | Tabla(s) y columna(s) del dominio |
| Test estadistico | Si requiere IC o comparacion entre grupos (ver seccion 4.6 de esta skill) |

**Benchmark Discovery** — Escala segun profundidad (ver matriz de activacion):
- **Rapido**: No buscar activamente. Usar comparacion temporal natural si la query ya incluye dimension tiempo
- **Estandar**: Best-effort silencioso:
  1. `stratio_search_domain_knowledge("target/objetivo de [nombre_KPI]", domain)`
  2. Query MCP adicional para mismo KPI en periodo T-1
  3. Si no hay referencia externa: media/mediana como referencia interna
  Sin benchmark → reportar el dato normalmente
- **Profundo**: Pasos 1-3 + tendencia si >6 puntos temporales + preguntar al usuario

### 4.4 Preguntas de datos
Lista de preguntas en lenguaje natural para `stratio_query_data`. NUNCA escribir SQL.

**Buenas practicas para formular preguntas al MCP:**
- **Ser especifico con periodos**: "ventas mensuales del ultimo anio" en vez de "ventas"
- **Incluir dimensiones**: "por region y categoria de producto"
- **Especificar metricas**: "total de ingresos y numero de transacciones"
- **Usar additional_context**: Para definiciones no obvias (ej: "Clientes activos = al menos 1 compra en 90 dias")
- **Una pregunta = un dataset**: No mezclar preguntas no relacionadas
- **Pensar en granularidad**: Necesito datos agregados o detalle transaccional?

**Estrategia de queries** — orden de PLANIFICACION (pensar de lo general a lo especifico):
1. **Contexto general**: Totales, conteos basicos → entender la magnitud del dataset
2. **Queries dimensionales**: Por tiempo, segmento, region → encontrar patrones y tendencias
3. **Queries de detalle**: Top/bottom N, outliers → profundizar en los hallazgos
4. **Queries de validacion**: Cruces de datos, checks de consistencia → asegurar fiabilidad

Este orden es para **planificar** las preguntas. En **ejecucion** (sec 5.0), lanzar en paralelo todas las queries independientes — tipicamente las categorias 1, 2 y 3 se pueden ejecutar simultaneamente. Solo las de categoria 4 (validacion cruzada) pueden requerir resultados previos.

### 4.5 Visualizaciones

Ver [visualization.md](visualization.md) para principios de visualizacion y data storytelling.

Para cada visualizacion del plan, definir:
- **Pregunta analitica** que responde
- **Tipo de grafica**: Seleccionar segun la pregunta analitica (ver guia de seleccion en [visualization.md](visualization.md))
- **Variables**: Que va en cada eje, agrupaciones, filtros
- **Titulo**: Formulado como insight, no como descripcion
- **Datos fuente**: Query MCP que alimenta la visualizacion

### 4.6 Tecnicas analiticas avanzadas

Activar segun la profundidad seleccionada (ver matriz de activacion):
- **Estandar**: Consultar [advanced-analytics.md](advanced-analytics.md) cuando sea relevante
- **Profundo**: Consultar [advanced-analytics.md](advanced-analytics.md) sistematicamente

Cubre: rigor estadistico (tests, IC, effect sizes), analisis prospectivo (escenarios, Monte Carlo), root cause analysis, deteccion de anomalias.

### 4.7 Patrones analiticos adicionales

Implementacion detallada de patrones cuyo trigger esta en sec 3.2 (Lorenz/Gini, mix, indexacion, desviacion vs referencia, gap).

Cuando un patron se active: consultar [analytical-patterns.md](analytical-patterns.md) para query MCP, Python e interpretacion.

### 4.8 Segmentacion y clustering

Para guia completa de segmentacion (RFM, clustering, validacion, profiling), ver [clustering-guide.md](clustering-guide.md).

Usar cuando el usuario pida segmentacion, agrupacion de clientes/productos, o descubrimiento de perfiles. La guia cubre:
- Tabla de decision (cuando usar rule-based o RFM)
- RFM con quintiles y etiquetas de negocio
- Profiling obligatorio de segmentos

### 4.9 Estructura de la presentacion de resultados
Secciones del analisis y orden narrativo para presentar en el chat. Aplicar principios de data storytelling (seccion 6.1)

### 4.10 Presentar plan
Presentar plan completo al usuario y solicitar aprobacion antes de ejecutar

## 5. Ejecucion

### 5.0 Obtencion de datos
- Usar `stratio_query_data(data_question=..., domain_name=..., output_format="dict")` para cada pregunta de datos. **Lanzar en paralelo** todas las queries independientes definidas en el plan (paso 4.4). Solo serializar si una query necesita el resultado de otra para formularse
- `output_format` solo acepta strings: `"dict"`, `"csv"`, `"markdown"`. Nunca pasar booleanos
- Maximizar lo que se resuelve en el MCP (joins, agregaciones, filtros) antes de recurrir a pandas. Ver reglas "MCP-first" y "Multiples datasets" en seccion 4
- NUNCA escribir SQL manualmente
- Si una query falla, reformular la pregunta en lenguaje natural
- Guardar datos intermedios como CSV solo si un script posterior los necesita como input

### 5.1 Validacion post-query (obligatorio)
Aplicar las 7 validaciones de la seccion 4 ("Validacion post-query") a cada resultado recibido. Cuando se lanzan queries en paralelo, validar cada resultado conforme llega. Si alguna falla: reformular la pregunta al MCP, informar al usuario, ajustar el plan.

### 5.2 Desarrollo de scripts
- Escribir scripts con nombres descriptivos que incluyan contexto del analisis
- Cada script debe:
  - Leer datos de CSVs guardados previamente o recibir datos como parametro
  - Realizar transformaciones y calculos
  - Generar visualizaciones
- **Datasets grandes (>100k filas)**: Usar muestreo estratificado para desarrollo rapido, datos completos para la version final

### 5.3 Testing

> **Solo si la profundidad es Estándar/Profundo Y el usuario eligió "Sí" en la pregunta de testing del Bloque 1.** En profundidad Rápido o si el usuario eligió "No", omitir esta sección y ejecutar directamente el script con datos reales.

- Generar tests unitarios ANTES de ejecutar con datos reales
- Usar DataFrames mock con estructura similar a los datos reales
- Validar transformaciones, calculos y formatos de salida
- Solo proceder si los tests pasan

### 5.4 Ejecucion con datos reales
Ejecutar scripts con datos reales.

### 5.5 Loop de iteracion

Tras revisar resultados iniciales, evaluar si requieren iteracion:

1. **Trigger**: Hallazgo contradice hipotesis, patron inesperado, o pregunta critica no prevista
2. **Accion**: Documentar hallazgo → formular nueva(s) pregunta(s) → queries MCP adicionales (5.0-5.1) → actualizar scripts
3. **Limite**: Max 2 iteraciones. Mas → documentar como analisis de seguimiento
4. **Registro**: Cada iteracion documentar en el chat: hipotesis → hallazgo → nueva hipotesis → resultado

### 5.6 Complexity Upgrade

Si durante la ejecucion se detecta un hallazgo que excede el alcance del nivel de complejidad actual:

**Triggers:**
- Anomalia: resultado difiere >30% del benchmark o de lo razonable para el dominio
- Inconsistencia: dos queries dan totales que no cuadran (diferencia >5%)
- Patron critico: concentracion Gini >0.8, caida/crecimiento >50% interperiodo, outlier en KPI principal

**Accion:**
1. Pausar la ejecucion normal
2. Informar al usuario siguiendo la convencion de preguntas (sec 10): "He detectado [descripcion del hallazgo]. Esto requiere investigacion adicional. ¿Quieres que profundice?" con opciones:
   - "Si, profundizar" → Escalar complejidad, activar fases adicionales (EDA completo, hipotesis sobre el hallazgo, visualizaciones de drill-down)
   - "No, solo documentar" → Registrar hallazgo en el chat como "area de investigacion futura"
3. El upgrade NO reinicia el analisis — extiende el analisis actual con fases adicionales

**Diferencia con el loop de iteracion (5.5):** El loop refina hipotesis dentro del mismo nivel de complejidad. El upgrade cambia el nivel (ej: Triage → Analisis) y activa capacidades adicionales (EDA, hipotesis formales, visualizaciones).

### 5.7 Presentacion de resultados
La presentacion de resultados se hace en el chat, siguiendo la estructura de la seccion 6.1. Las visualizaciones generadas se muestran inline como soporte del analisis.

### 5.8 Validacion de output final
Antes de presentar al usuario, verificar:
- Las visualizaciones se generaron correctamente
- Los datos usados son coherentes entre si (totales cuadran, periodos alineados)
- Los hallazgos pasan el checklist "So What?" de la seccion 6.1

Si alguna visualizacion falla, regenerarla o presentar los datos en formato tabla.

## 6. Reporte Final

### 6.1 Estructura del reporte en chat

Al presentar hallazgos en la conversacion, seguir esta estructura:

1. **Hook**: El hallazgo mas impactante primero
2. Resumen ejecutivo (3-5 bullets con "so what")
3. Insights con datos concretos y contexto comparativo (vs anterior, vs objetivo)
4. Recomendaciones accionables priorizadas (alto impacto + alta confianza primero)
5. Limitaciones y caveats
6. Sugerencias de analisis de seguimiento

**Checklist "So What?" obligatorio** — Para CADA hallazgo antes de incluirlo:

| Pregunta | Malo (dato) | Bueno (insight accionable) |
|----------|-------------|--------------------------|
| **Magnitud?** | "Las ventas bajaron" | "Bajaron 12%, ≈€45K/mes" |
| **Vs. que?** | "Norte va bien" | "Norte +23% vs media nacional, +8% vs target" |
| **Que hacer?** | "Mejorar retencion" | "Programa fidelizacion en Premium (45% vs 72% benchmark) → ROI €120K/ano" |
| **Confianza?** | "Clientes prefieren A" | Adaptar a profundidad: Rapido="67% (n=450, Alta)"; Estandar="67% (n=450, IC95%: 62-72%)"; Profundo="67% (n=450, IC95%: 62-72%, p<0.001)" |

Si un hallazgo no pasa las 4 preguntas → es informacion, no insight. No va al resumen ejecutivo.

**Clasificacion de insights** — Determina ubicacion en el reporte:
- **CRITICO**: Alto impacto + alta confianza → Resumen ejecutivo, recomendacion firme
- **IMPORTANTE**: Alto impacto + baja confianza → Seccion principal, investigar mas
- **INFORMATIVO**: Bajo impacto → Apendice, sin recomendacion

Para principios de data storytelling y mapping hallazgos → narrativa, leer [visualization.md](visualization.md) secciones 3 y 4.

## 7. Propuesta de Conocimiento (Opcional)

Tras presentar el reporte final, preguntar al usuario siguiendo la convencion de preguntas (sec 10):
- **Si**: Analizar conversacion y proponer conocimiento al dominio
- **No**: Finalizar sin proponer

Si acepta, cargar la skill `propose-knowledge` con el dominio usado en este analisis.
Si rechaza, finalizar normalmente.

Este paso es SIEMPRE opcional. Nunca proponer automaticamente.
