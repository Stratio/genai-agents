---
name: analyze
description: Analisis completo de datos BI/BA — descubrimiento de dominio, EDA y calidad de datos, planificacion de metricas y KPIs con framework analitico, queries de datos via MCP, analisis Python con pandas, visualizaciones, generacion de informes multi-formato y documentacion del razonamiento. Usar cuando el usuario necesite analizar datos de negocio, calcular KPIs, obtener insights o responder preguntas analiticas sobre dominios gobernados.
argument-hint: [pregunta o tema de analisis]
---

# Skill: Analisis BI/BA Completo

Esta guia define el workflow completo para realizar un analisis de Business Intelligence / Business Analytics.

## 1. Parsear la Peticion

- Extraer la pregunta de negocio principal del argumento: $ARGUMENTS
- Identificar sub-preguntas implicitas
- Detectar si menciona un dominio, tablas o metricas especificas
- Detectar si menciona un formato de salida preferido

### 1.1 Triage rapido

Si la peticion se resuelve con una sola llamada MCP (ver Fase 0 de CLAUDE.md), responder directamente:
- Definiciones/conceptos → `stratio_search_domain_knowledge` → chat
- Estructura/columnas → `stratio_list_domain_tables` / `stratio_get_table_columns_details` → chat
- Dato puntual → `stratio_query_data` → chat
- En estos casos, NO continuar con el resto del workflow

Si la peticion requiere analisis (cruce de datos, hipotesis, visualizaciones, multiples metricas), continuar con seccion 2.

## 2. Descubrimiento de Dominio

Leer y seguir `skills-guides/exploration.md` para los pasos de descubrimiento del dominio (listar dominios, seleccionar, explorar tablas, columnas, terminologia y profiling).

## 2.5. EDA y Calidad de Datos

Antes de preguntar al usuario sobre formatos y planificar metricas, entender la realidad de los datos:

1. **Profiling**: Ejecutar `stratio_profile_data` sobre las tablas clave identificadas en el paso 2. Seguir la mecanica y umbrales adaptativos de `skills-guides/exploration.md` sec 7
2. **Evaluar calidad**:
   - **Completitud**: % de nulos por columna. Marcar columnas con >50% nulos como limitacion
   - **Rango temporal**: Verificar que los datos cubren el periodo que el usuario necesita
   - **Outliers**: Identificar valores extremos (IQR) que podrian sesgar promedios o totales
   - **Distribuciones**: Sesgo en numericas, desbalanceo en categoricas
   - **Correlaciones**: Relaciones fuertes entre variables (|r| > 0.7) — pueden indicar multicolinealidad o redundancia
   - **Cardinalidad**: Categoricas con >100 valores unicos son dificiles de visualizar o agrupar
3. **Checklist de suficiencia** — Aplicar ANTES de preguntar formatos:

   | Criterio | Umbral minimo | Si falla |
   |----------|---------------|----------|
   | Registros | >0 | STOP — reformular query |
   | Completitud temporal | ≥80% del periodo pedido | Ofrecer analisis del periodo disponible |
   | Nulos en vars clave | <30% | Alertar limitacion severa, considerar imputacion |
   | Tamano para inferencia | n ≥ 30 | Reportar como exploratorio, sin tests estadisticos |
   | Tamano para clustering | n ≥ 10 × features | Recomendar analisis descriptivo sin segmentacion |
   | Variabilidad | std > 0 en numericas clave | Excluir variable constante |
   | Granularidad | Nivel pedido disponible | Ofrecer agregacion al disponible |

4. **Data Quality Score**: ALTO (80-100%), MEDIO (60-79%), BAJO (<60%). Si BAJO, recomendar mejorar datos o reformular
5. **Informar al usuario**: Generar mini-resumen de calidad + Data Quality Score antes de preguntarle sobre formato y estilo. Ejemplo:
   - "**Calidad: ALTO (85%)**. Los datos cubren de enero 2023 a diciembre 2025. La columna `descuento` tiene un 35% de nulos. Se detectaron 12 outliers en `importe_total` (>3 IQR). La distribucion de `categoria_producto` esta concentrada: 3 de 15 categorias representan el 80% de registros."
6. **Ajustar expectativas**: Si hay limitaciones serias, advertir al usuario de que ciertas metricas o visualizaciones podrian no ser fiables

## 3. Clasificacion y Preguntas al Usuario

> **Nota**: Todas las preguntas con opciones de esta seccion siguen la convencion de preguntas de CLAUDE.md sec 11 (adaptativa al entorno: interactivas si disponibles, lista numerada en chat si no).

### 3.0 Triage vs Analisis

Las preguntas simples (datos puntuales, sin dimensiones de corte) se resuelven en Triage (CLAUDE.md Fase 0) sin invocar esta skill. Todo lo demas es un analisis y sigue el flujo de bloques de preguntas descrito a continuacion.

**Defaults generales:**
- Estilo visual: **Corporativo** (si el usuario no elige otro en Bloque 2)

### 3.1 Bloque 1 — Profundidad, Audiencia y Formato

Una sola interaccion:

| # | Pregunta | Opciones (literales) | Seleccion | Condicion |
|---|----------|---------------------|-----------|-----------|
| 1 | ¿Que profundidad de analisis prefieres? | **Rapido** · **Estandar** (Recomendado) · **Profundo** | Unica | Siempre |
| 2 | ¿Para que audiencia es el analisis? | **C-level/Direccion** · **Manager/Responsable** · **Equipo tecnico/Data** · **Mixta/General** | Unica | Siempre |
| 3 | ¿En que formatos quieres los deliverables? | **Documento** (PDF + DOCX) · **Web** (HTML interactivo con Plotly) · **PowerPoint** (.pptx) | Multiple | Siempre |
| 4 | ¿Quieres que se generen y ejecuten tests unitarios sobre el código Python? | **Sí** (Recomendado): mejora precisión y calidad, pero consume más tiempo, coste y contexto · **No**: ejecución directa sin tests | Única | Solo Estandar/Profundo |

- Los tests validan transformaciones y cálculos antes de ejecutar con datos reales. Mejoran la precisión pero consumen más tokens, tiempo y coste. **En profundidad Rápido, testing se desactiva automáticamente sin preguntar al usuario.**
- La pregunta de formato SIEMPRE permite seleccion multiple
- Las opciones de formato son EXACTAMENTE 3: Documento (PDF + DOCX), Web, PowerPoint. No inventar, no omitir, no sustituir
- Si no selecciona formato → no hay deliverables, el analisis se entrega solo en chat + report.md automatico
- Requisitos adicionales via opcion "Other" (filtros temporales, segmentos, metricas obligatorias)

### 3.2 Bloque 2 — Estructura y Estilo (solo si selecciono formato en Bloque 1)

Una sola interaccion con 2 preguntas. Las opciones son literales — no inventar, no omitir, no sustituir:

| # | Pregunta | Opciones (literales) | Seleccion |
|---|----------|---------------------|-----------|
| 1 | ¿Que estructura prefieres para el reporte? | **Scaffold base** (Recomendado): resumen ejecutivo → metodologia → datos → analisis → conclusiones · **Al vuelo**: estructura libre segun contexto | Unica |
| 2 | ¿Que estilo visual prefieres? | **Corporativo** (`corporate.css`, Recomendado): limpio, profesional · **Formal/academico** (`academic.css`): serif, margenes amplios, estilo paper · **Moderno/creativo** (`modern.css`): colores, gradientes, visualmente atractivo | Unica |

Si no selecciono formato en Bloque 1 → Bloque 2 se omite completamente. Resultado: de 6 a 1-2 interacciones.

## 4. Planificacion

Elaborar un plan detallado siguiendo el framework analitico (seccion 3 de CLAUDE.md):

### 4.0 Contexto historico
Leer en paralelo (si existen):
- `output/ANALYSIS_MEMORY.md` — triage rapido: buscar entradas del mismo dominio. Si hay una entrada relevante, leer su fichero `analysis_memory.md` referenciado en el campo **Detalle** para obtener KPIs, insights y baselines de referencia
- `output/MEMORY.md` — sec "Patrones de Datos Conocidos" del dominio para anticipar problemas de datos conocidos

### 4.1 Librerias adicionales
Evaluar si `requirements.txt` necesita ampliarse

### 4.2 Enfoque analitico: descriptivo, segmentacion o feature importance

Determinar si la pregunta requiere solo analisis descriptivo o tambien segmentacion/clustering o feature importance:

| Escenario | Recomendacion |
|-----------|---------------|
| Describir que paso y por que | Analisis descriptivo (pandas, agrupaciones, comparativas) |
| Descubrir grupos/segmentos no predefinidos | Clustering (RFM, KMeans, DBSCAN). Ver [clustering-guide.md](clustering-guide.md) |
| Identificar factores influyentes (>5 variables) | Feature importance exploratoria. Ver [clustering-guide.md](clustering-guide.md) sec 7 |
| Proyeccion temporal | Proyeccion lineal + IC95%. Ver [advanced-analytics.md](advanced-analytics.md) |

**Deteccion automatica**: Si la pregunta menciona "segmentar", "agrupar", "perfiles" → clustering. Si menciona "que factores influyen", "que explica" → feature importance. Si pide proyeccion temporal → proyeccion lineal (no ML). Inferir el tipo de la pregunta y los datos, no preguntar al usuario.

### 4.3 Hipotesis
Formular hipotesis ANTES de consultar datos. Usar la plantilla de CLAUDE.md sec 3.1. Para cada sub-pregunta identificada en el paso 1:
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

### 4.4 Metricas y KPIs

Para cada KPI, documentar:

| Campo | Descripcion |
|-------|-------------|
| Nombre | Identificador claro |
| Formula | Calculo exacto |
| Granularidad | Temporal: diario/semanal/mensual/trimestral |
| Dimensiones | Ejes de corte (region, producto, segmento) |
| Benchmark | Objetivo, media del sector, o periodo anterior |
| Fuente | Tabla(s) y columna(s) del dominio |
| Test estadistico | Si requiere IC o comparacion entre grupos (ver seccion 4.5b de esta skill) |

**Benchmark Discovery** — Escala segun profundidad (ver matriz de activacion en CLAUDE.md):
- **Rapido**: No buscar activamente. Usar comparacion temporal natural si la query ya incluye dimension tiempo
- **Estandar**: Best-effort silencioso:
  1. `stratio_search_domain_knowledge("target/objetivo de [nombre_KPI]", domain)`
  2. Query MCP adicional para mismo KPI en periodo T-1
  3. Si no hay referencia externa: media/mediana como referencia interna
  Sin benchmark → reportar el dato normalmente, documentar en reasoning
- **Profundo**: Pasos 1-3 + tendencia si >6 puntos temporales + preguntar al usuario

Documentar el benchmark en el campo "Benchmark" del KPI. Los datos sin benchmark se reportan con normalidad — la ausencia solo se marca como limitacion en profundidad Profundo.

### 4.5 Preguntas de datos
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

Este orden es para **planificar** las preguntas. En **ejecucion** (sec 5.2), lanzar en paralelo todas las queries independientes — tipicamente las categorias 1, 2 y 3 se pueden ejecutar simultaneamente. Solo las de categoria 4 (validacion cruzada) pueden requerir resultados previos.

### 4.6 Visualizaciones

Leer y seguir `skills-guides/visualization.md` para seleccion de graficas y principios de visualizacion.

Para cada visualizacion del plan, definir:
- **Pregunta analitica** que responde
- **Tipo de grafica**: Seleccionar segun tabla en `skills-guides/visualization.md` sec 1
- **Variables**: Que va en cada eje, agrupaciones, filtros
- **Titulo**: Formulado como insight, no como descripcion
- **Datos fuente**: Query MCP que alimenta la visualizacion

### 4.6b Tecnicas analiticas avanzadas

Activar segun la profundidad seleccionada (ver matriz de activacion en CLAUDE.md):
- **Estandar**: Consultar [advanced-analytics.md](advanced-analytics.md) cuando sea relevante
- **Profundo**: Consultar [advanced-analytics.md](advanced-analytics.md) sistematicamente

Cubre: rigor estadistico (tests, IC, effect sizes), analisis prospectivo (escenarios, Monte Carlo), root cause analysis, deteccion de anomalias.

### 4.6c Patrones analiticos adicionales

Implementacion detallada de patrones cuyo trigger esta en CLAUDE.md sec 3.2 (Lorenz/Gini, mix, indexacion, desviacion vs referencia, gap).

Cuando un patron se active: consultar [analytical-patterns.md](analytical-patterns.md) para query MCP, Python e interpretacion.

### 4.6d Segmentacion y clustering

Para guia completa de segmentacion (RFM, clustering, validacion, profiling), ver [clustering-guide.md](clustering-guide.md).

Usar cuando el usuario pida segmentacion, agrupacion de clientes/productos, o descubrimiento de perfiles. La guia cubre:
- Tabla de decision (cuando usar rule-based, RFM, KMeans o DBSCAN)
- RFM con quintiles y etiquetas de negocio
- Clustering basico con elbow + silhouette
- Validacion de clusters y profiling obligatorio

Para feature importance como complemento a la segmentacion o al analisis descriptivo, ver [clustering-guide.md](clustering-guide.md) sec 7.

### 4.7 Estructura del deliverable
Secciones, contenido de cada una, formato. Aplicar principios de data storytelling (seccion 6.1)

### 4.8 Presentar plan
Presentar plan completo al usuario y solicitar aprobacion antes de ejecutar

## 5. Ejecucion

### 5.0 Determinar carpeta del analisis
Generar nombre `YYYY-MM-DD_HHMM_nombre_descriptivo` (minusculas, sin tildes, guiones bajos, max 30 chars en el nombre). Declarar en chat. Crear subdirectorios: `output/[ANALISIS_DIR]/scripts/`, `output/[ANALISIS_DIR]/data/`, `output/[ANALISIS_DIR]/assets/`, `output/[ANALISIS_DIR]/reasoning/`, `output/[ANALISIS_DIR]/validation/`.

Persistir el plan aprobado en `output/[ANALISIS_DIR]/plan.md`.
Escribir el plan tal como fue formulado en la Fase 3 (seccion 4) y aprobado por el usuario:
hipotesis, metricas/KPIs, queries de datos, visualizaciones, estructura del deliverable,
complejidad, profundidad, formatos y estilo.

### 5.1 Setup del entorno
```bash
bash setup_env.sh
```
Si hay librerias adicionales, actualizar `requirements.txt` y re-ejecutar setup.

### 5.2 Obtencion de datos
- Usar `stratio_query_data(data_question=..., domain_name=..., output_format="dict")` para cada pregunta de datos. **Lanzar en paralelo** todas las queries independientes definidas en el plan (paso 4.4). Solo serializar si una query necesita el resultado de otra para formularse
- `output_format` solo acepta strings: `"dict"`, `"csv"`, `"markdown"`. Nunca pasar booleanos
- Maximizar lo que se resuelve en el MCP (joins, agregaciones, filtros) antes de recurrir a pandas. Ver reglas "MCP-first" y "Multiples datasets" en CLAUDE.md seccion 4
- NUNCA escribir SQL manualmente
- Si una query falla, reformular la pregunta en lenguaje natural
- Guardar datos intermedios en `output/[ANALISIS_DIR]/data/` como CSV si son necesarios para scripts posteriores

### 5.3 Validacion post-query (obligatorio)
Aplicar las 7 validaciones de la seccion 4 de CLAUDE.md ("Validacion post-query") a cada resultado recibido. Cuando se lanzan queries en paralelo, validar cada resultado conforme llega. Si alguna falla: reformular la pregunta al MCP, informar al usuario, ajustar el plan.

### 5.4 Desarrollo de scripts
- Escribir scripts en `output/[ANALISIS_DIR]/scripts/` con nombres descriptivos que incluyan contexto del analisis
- Cada script debe:
  - Leer datos de `output/[ANALISIS_DIR]/data/` (CSVs guardados previamente) o recibir datos como parametro
  - Realizar transformaciones y calculos
  - Generar visualizaciones en `output/[ANALISIS_DIR]/assets/`
  - Producir outputs en `output/[ANALISIS_DIR]/`
- **Datasets grandes (>100k filas)**: Usar muestreo estratificado para desarrollo rapido, datos completos para la version final

### 5.5 Testing

> **Solo si la profundidad es Estándar/Profundo Y el usuario eligió "Sí" en la pregunta de testing del Bloque 1.** En profundidad Rápido o si el usuario eligió "No", omitir esta sección y ejecutar directamente el script con datos reales.

- Generar `output/[ANALISIS_DIR]/scripts/test_*.py` con tests unitarios ANTES de ejecutar con datos reales
- Usar DataFrames mock con estructura similar a los datos reales
- Validar transformaciones, calculos y formatos de salida
- Ejecutar: `bash -c "source .venv/bin/activate && pytest output/[ANALISIS_DIR]/scripts/test_*.py -v"`
- Solo proceder si los tests pasan

### 5.6 Ejecucion con datos reales
```bash
bash -c "source .venv/bin/activate && python output/[ANALISIS_DIR]/scripts/mi_script.py"
```

### 5.6b Loop de iteracion

Tras revisar resultados iniciales, evaluar si requieren iteracion:

1. **Trigger**: Hallazgo contradice hipotesis, patron inesperado, o pregunta critica no prevista
2. **Accion**: Documentar hallazgo → formular nueva(s) pregunta(s) → queries MCP adicionales (5.2-5.3) → actualizar scripts
3. **Limite**: Max 2 iteraciones. Mas → documentar como analisis de seguimiento
4. **Registro**: Cada iteracion en reasoning: hipotesis → hallazgo → nueva hipotesis → resultado

### 5.6c Complexity Upgrade

Si durante la ejecucion se detecta un hallazgo que excede el alcance del nivel de complejidad actual:

**Triggers:**
- Anomalia: resultado difiere >30% del benchmark o de lo razonable para el dominio
- Inconsistencia: dos queries dan totales que no cuadran (diferencia >5%)
- Patron critico: concentracion Gini >0.8, caida/crecimiento >50% interperiodo, outlier en KPI principal

**Accion:**
1. Pausar la ejecucion normal
2. Informar al usuario siguiendo la convencion de preguntas de CLAUDE.md sec 11: "He detectado [descripcion del hallazgo]. Esto requiere investigacion adicional. ¿Quieres que profundice?" con opciones:
   - "Si, profundizar" → Escalar complejidad, activar fases adicionales (EDA completo, hipotesis sobre el hallazgo, visualizaciones de drill-down)
   - "No, solo documentar" → Registrar hallazgo en el chat y en reasoning como "area de investigacion futura"
3. El upgrade NO reinicia el analisis — extiende el analisis actual con fases adicionales

**Diferencia con el loop de iteracion (5.6b):** El loop refina hipotesis dentro del mismo nivel de complejidad. El upgrade cambia el nivel (ej: Triage → Analisis) y activa capacidades adicionales (EDA, hipotesis formales, visualizaciones).

### 5.7 Generacion de deliverables
Cargar la skill `report` para generar los deliverables en los formatos solicitados.

### 5.8 Reasoning
Generar reasoning en `output/[ANALISIS_DIR]/reasoning/` en tres formatos (.md, .pdf, .html). Contenido obligatorio (ver seccion 9 de CLAUDE.md), incluyendo:
- Hipotesis formuladas y resultado de su validacion
- Resumen de calidad de datos (data quality score)
- "So what" para cada hallazgo principal
- Si se uso feature importance o clustering: enfoque, variables, resultados, limitaciones

### 5.9 Validacion de output final
Antes de reportar al usuario, ejecutar el checklist de validacion del producto terminado (ver paso 12 de la Fase 4 en CLAUDE.md):

1. **Integridad de archivos**: Verificar que todos los archivos declarados en el plan existen (`output/[ANALISIS_DIR]/report.md`, deliverables solicitados, reasoning en 3 formatos, validation en 3 formatos, assets referenciados en report.md, CSVs referenciados en scripts)
2. **Calidad de visualizaciones**: Para cada grafica en `output/[ANALISIS_DIR]/assets/`, verificar tamano >1KB y datos fuente suficientes (>5 valores no-nulos en columna principal). Umbrales por tipo: tendencia >6 puntos, ranking >3, distribucion >10. Si no pasa → excluir del deliverable y documentar por que
3. **Completitud del analisis**: Extraer dimensiones pedidas por el usuario y verificar que cada una aparece en al menos un analisis/grafica. Verificar secciones obligatorias del reasoning
4. **Consistencia de datos**: Para 1-2 KPIs clave, comparar valor reportado en deliverable vs valor en `output/[ANALISIS_DIR]/data/`. Discrepancia >1% → WARNING

Generar `output/[ANALISIS_DIR]/validation/validation.md` con resultados (PASS/WARNING/FAIL por item). Luego generar .html y .pdf con el mismo workflow que reasoning:
```bash
bash -c "source .venv/bin/activate && python tools/md_to_report.py output/[ANALISIS_DIR]/validation/validation.md --style corporate"
```
Incluir resumen de validacion en el reporte final al usuario.

## 6. Reporte Final

### 6.1 Estructura del reporte en chat

Al presentar hallazgos en la conversacion, seguir esta estructura:

1. **Hook**: El hallazgo mas impactante primero
2. Resumen ejecutivo (3-5 bullets con "so what")
3. Insights con datos concretos y contexto comparativo (vs anterior, vs objetivo)
4. Recomendaciones accionables priorizadas (alto impacto + alta confianza primero)
5. Limitaciones y caveats
6. Rutas de archivos generados
7. Sugerencias de analisis de seguimiento

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

Para principios de data storytelling y mapping hallazgos → narrativa, leer `skills-guides/visualization.md` secciones 3 y 4.

## 7. Memoria de Analisis (Confirmacion requerida)

Tras presentar el reporte final, preguntar al usuario (siguiendo la convencion de preguntas de CLAUDE.md sec 11):

"¿Deseas guardar este analisis en la memoria persistente? Se actualizaran el registro de analisis (`ANALYSIS_MEMORY.md`) y la memoria de conocimiento (`MEMORY.md`)."
- **Si** → Continuar con los pasos 7.1, 7.2 y 7.5
- **No** → Saltar todos los pasos de escritura de memoria. Finalizar sin actualizar ningun fichero de memoria

Los pasos siguientes se ejecutan **solo si el usuario responde "Sí"**:

### 7.1 Crear fichero de detalle del analisis

Crear `output/[ANALISIS_DIR]/analysis_memory.md` con el contenido completo:

```markdown
# Memoria del Analisis: Titulo Descriptivo

- **Dominio**: nombre_exacto_dominio
- **Pregunta**: "Pregunta original del usuario"
- **Carpeta**: `output/YYYY-MM-DD_HHMM_nombre/`
- **Reporte**: `output/YYYY-MM-DD_HHMM_nombre/report.md`
- **KPIs**: KPI1: valor (periodo), KPI2: valor (periodo)
- **Insights**: Hallazgo 1 (confianza), Hallazgo 2 (confianza)
- **Data Quality Score**: ALTO/MEDIO/BAJO (N%)
```

### 7.2 Añadir entrada compacta al indice

Añadir entrada al final de `output/ANALYSIS_MEMORY.md` con solo los campos de triage:

```markdown
---

## YYYY-MM-DD HH:MM — Titulo Descriptivo

- **Dominio**: nombre_exacto_dominio
- **Resumen**: Pregunta + hallazgo principal en 1 frase (max ~120 chars)
- **Detalle**: `output/YYYY-MM-DD_HHMM_nombre/analysis_memory.md`

---
```

Si `output/ANALYSIS_MEMORY.md` no existe, crearlo con el header `# Memoria de Analisis`. Las entradas se anaden al final (cronologicas).

## 7.5 Memoria de Conocimiento

Tras escribir en ANALYSIS_MEMORY.md, invocar la skill `/update-memory` para actualizar `output/MEMORY.md` con preferencias, patrones de datos y heuristicas descubiertas en este analisis.

## 8. Propuesta de Conocimiento (Opcional)

Tras presentar el reporte final, preguntar al usuario siguiendo la convencion de preguntas de CLAUDE.md sec 11:
- **Si**: Analizar conversacion y proponer conocimiento al dominio
- **No**: Finalizar sin proponer

Si acepta, cargar la skill `propose-knowledge` con el dominio usado en este analisis.
Si rechaza, finalizar normalmente.

Este paso es SIEMPRE opcional. Nunca proponer automaticamente.
