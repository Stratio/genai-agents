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

Si la peticion se resuelve con una sola llamada MCP (ver Fase 0 del workflow (AGENTS.md)), responder directamente:
- Definiciones/conceptos → `search_domain_knowledge` → chat
- Estructura/columnas → `list_domain_tables` / `get_table_columns_details` → chat
- Dato puntual → `query_data` → chat
- En estos casos, NO continuar con el resto del workflow

Si la peticion requiere analisis (cruce de datos, hipotesis, visualizaciones, multiples metricas), continuar con seccion 2.

## 2. Descubrimiento de Dominio

Leer y seguir `skills-guides/stratio-data-tools.md` sec 4 para los pasos de descubrimiento del dominio (listar dominios, seleccionar, explorar tablas, columnas y terminologia).

## 3. EDA y Calidad de Datos

Antes de preguntar al usuario sobre formatos y planificar metricas, entender la realidad de los datos:

1. **Profiling**: Ejecutar `profile_data` sobre las tablas clave identificadas en el paso 2. Seguir la mecanica y umbrales adaptativos de `skills-guides/stratio-data-tools.md` sec 5
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

## 4. Clasificacion y Preguntas al Usuario

> **Nota**: Todas las preguntas con opciones de esta seccion siguen la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md).

### 4.0 Triage vs Analisis

Las preguntas simples (datos puntuales, sin dimensiones de corte) se resuelven en Triage (Fase 0 del workflow) sin invocar esta skill. Todo lo demas es un analisis y sigue el flujo de bloques de preguntas descrito a continuacion.

**Defaults generales:**
- Estilo visual: **Corporativo** (si el usuario no elige otro en Bloque 2)

### 4.1 Bloque 1 — Profundidad, Audiencia y Formato

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
- **Si selecciona uno o mas formatos → los deliverables SE GENERAN SIEMPRE, independientemente de la profundidad elegida. Rapido/Estandar/Profundo afecta al analisis, no a los entregables.**
- Requisitos adicionales via opcion "Other" (filtros temporales, segmentos, metricas obligatorias)

### 4.2 Bloque 2 — Estructura y Estilo (solo si selecciono formato en Bloque 1)

Una sola interaccion con 2 preguntas. Las opciones son literales — no inventar, no omitir, no sustituir:

| # | Pregunta | Opciones (literales) | Seleccion |
|---|----------|---------------------|-----------|
| 1 | ¿Que estructura prefieres para el reporte? | **Scaffold base** (Recomendado): resumen ejecutivo → metodologia → datos → analisis → conclusiones · **Al vuelo**: estructura libre segun contexto | Unica |
| 2 | ¿Que estilo visual prefieres? | **Corporativo** (`corporate.css`, Recomendado): limpio, profesional · **Formal/academico** (`academic.css`): serif, margenes amplios, estilo paper · **Moderno/creativo** (`modern.css`): colores, gradientes, visualmente atractivo | Unica |

Si no selecciono formato en Bloque 1 → Bloque 2 se omite completamente. Resultado: de 6 a 1-2 interacciones.

## 5. Planificacion

Elaborar un plan detallado siguiendo el framework analitico (sec "Framework Analitico" de AGENTS.md):

### 5.0 Contexto historico
Leer en paralelo (si existen):
- `output/ANALYSIS_MEMORY.md` — triage rapido: buscar entradas del mismo dominio. Si hay una entrada relevante, leer su fichero `analysis_memory.md` referenciado en el campo **Detalle** para obtener KPIs, insights y baselines de referencia
- `output/MEMORY.md` — sec "Patrones de Datos Conocidos" del dominio para anticipar problemas de datos conocidos

### 5.1 Librerias adicionales
Evaluar si `requirements.txt` necesita ampliarse

### 5.2 Enfoque analitico: descriptivo, segmentacion o feature importance

Determinar si la pregunta requiere solo analisis descriptivo o tambien segmentacion/clustering o feature importance:

| Escenario | Recomendacion |
|-----------|---------------|
| Describir que paso y por que | Analisis descriptivo (pandas, agrupaciones, comparativas) |
| Descubrir grupos/segmentos no predefinidos | Clustering (RFM, KMeans, DBSCAN). Ver [clustering-guide.md](clustering-guide.md) |
| Identificar factores influyentes (>5 variables) | Feature importance exploratoria. Ver [clustering-guide.md](clustering-guide.md) sec 7 |
| Proyeccion temporal | Proyeccion lineal + IC95%. Ver [advanced-analytics.md](advanced-analytics.md) |

**Deteccion automatica**: Si la pregunta menciona "segmentar", "agrupar", "perfiles" → clustering. Si menciona "que factores influyen", "que explica" → feature importance. Si pide proyeccion temporal → proyeccion lineal (no ML). Inferir el tipo de la pregunta y los datos, no preguntar al usuario.

### 5.3 Hipotesis
Formular hipotesis ANTES de consultar datos. Usar la plantilla de sec "Pensamiento analitico" de AGENTS.md. Para cada sub-pregunta identificada en el paso 1:
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

### 5.4 Metricas y KPIs

Para cada KPI, documentar:

| Campo | Descripcion |
|-------|-------------|
| Nombre | Identificador claro |
| Formula | Calculo exacto |
| Granularidad | Temporal: diario/semanal/mensual/trimestral |
| Dimensiones | Ejes de corte (region, producto, segmento) |
| Benchmark | Objetivo, media del sector, o periodo anterior |
| Fuente | Tabla(s) y columna(s) del dominio |
| Test estadistico | Si requiere IC o comparacion entre grupos (ver [advanced-analytics.md](advanced-analytics.md)) |

**Benchmark Discovery** — Escala segun profundidad (ver matriz de activacion en AGENTS.md sec 2):
- **Rapido**: No buscar activamente. Usar comparacion temporal natural si la query ya incluye dimension tiempo
- **Estandar**: Best-effort silencioso:
  1. `search_domain_knowledge("target/objetivo de [nombre_KPI]", domain)`
  2. Query MCP adicional para mismo KPI en periodo T-1
  3. Si no hay referencia externa: media/mediana como referencia interna
  Sin benchmark → reportar el dato normalmente, documentar en reasoning
- **Profundo**: Pasos 1-3 + tendencia si >6 puntos temporales + preguntar al usuario

Documentar el benchmark en el campo "Benchmark" del KPI. Los datos sin benchmark se reportan con normalidad — la ausencia solo se marca como limitacion en profundidad Profundo.

### 5.5 Preguntas de datos
Lista de preguntas en lenguaje natural para `query_data`. NUNCA escribir SQL.

Para buenas practicas de formulacion y estrategia de queries (orden de planificacion, ejecucion en paralelo), ver `skills-guides/stratio-data-tools.md` sec 9.

### 5.6 Visualizaciones

Leer y seguir `skills-guides/visualization.md` para seleccion de graficas y principios de visualizacion.

Para cada visualizacion del plan, definir:
- **Pregunta analitica** que responde
- **Tipo de grafica**: Seleccionar segun tabla en `skills-guides/visualization.md` sec 1
- **Variables**: Que va en cada eje, agrupaciones, filtros
- **Titulo**: Formulado como insight, no como descripcion
- **Datos fuente**: Query MCP que alimenta la visualizacion

### 5.7 Tecnicas analiticas avanzadas

Activar segun la profundidad seleccionada (ver matriz de activacion en AGENTS.md sec 2):
- **Estandar**: Consultar [advanced-analytics.md](advanced-analytics.md) cuando sea relevante
- **Profundo**: Consultar [advanced-analytics.md](advanced-analytics.md) sistematicamente

Cubre: rigor estadistico (tests, IC, effect sizes), analisis prospectivo (escenarios, Monte Carlo), root cause analysis, deteccion de anomalias.

### 5.8 Patrones analiticos adicionales

Implementacion detallada de patrones cuyo trigger esta en sec "Patrones analiticos operacionalizados" de AGENTS.md (Lorenz/Gini, mix, indexacion, desviacion vs referencia, gap).

Cuando un patron se active: consultar [analytical-patterns.md](analytical-patterns.md) para query MCP, Python e interpretacion.

### 5.9 Segmentacion y clustering

Para guia completa de segmentacion (RFM, clustering, validacion, profiling), ver [clustering-guide.md](clustering-guide.md).

Usar cuando el usuario pida segmentacion, agrupacion de clientes/productos, o descubrimiento de perfiles. La guia cubre:
- Tabla de decision (cuando usar rule-based, RFM, KMeans o DBSCAN)
- RFM con quintiles y etiquetas de negocio
- Clustering basico con elbow + silhouette
- Validacion de clusters y profiling obligatorio

Para feature importance como complemento a la segmentacion o al analisis descriptivo, ver [clustering-guide.md](clustering-guide.md) sec 7.

### 5.10 Estructura del deliverable
Secciones, contenido de cada una, formato. Aplicar principios de data storytelling (seccion 7.1)

### 5.11 Presentar plan
Presentar plan completo al usuario y solicitar aprobacion antes de ejecutar.

Al final de la presentacion del plan, incluir una nota breve:
> Si dispones de documentacion adicional, benchmarks de referencia, informes previos o datos complementarios que puedan enriquecer el analisis, puedes compartirlos ahora.

No convertir esta nota en pregunta bloqueante. Es una invitacion, no un paso obligatorio. Si el usuario no aporta nada, continuar sin esperar respuesta adicional mas alla de la aprobacion del plan.

## 6. Ejecucion

### 6.0 Determinar carpeta del analisis
Generar nombre `YYYY-MM-DD_HHMM_nombre_descriptivo` (minusculas, sin tildes, guiones bajos, max 30 chars en el nombre). Declarar en chat. Crear subdirectorios: `output/[ANALISIS_DIR]/scripts/`, `output/[ANALISIS_DIR]/data/`, `output/[ANALISIS_DIR]/assets/`. Si profundidad >= Estandar, crear tambien `output/[ANALISIS_DIR]/reasoning/` y `output/[ANALISIS_DIR]/validation/`.

Persistir el plan aprobado en `output/[ANALISIS_DIR]/plan.md`.
Escribir el plan tal como fue formulado en la Fase 3 (seccion 5) y aprobado por el usuario:
hipotesis, metricas/KPIs, queries de datos, visualizaciones, estructura del deliverable,
complejidad, profundidad, formatos y estilo.

### 6.1 Setup del entorno
```bash
bash setup_env.sh
```
Si hay librerias adicionales, actualizar `requirements.txt` y re-ejecutar setup.

### 6.2 Obtencion de datos
- Usar `query_data(data_question=..., domain_name=..., output_format="dict")` para cada pregunta de datos. **Lanzar en paralelo** todas las queries independientes definidas en el plan (paso 5.5). Solo serializar si una query necesita el resultado de otra para formularse
- Seguir todas las reglas de `skills-guides/stratio-data-tools.md` (MCP-first, output_format, no SQL manual, ejecucion en paralelo)
- Guardar datos intermedios en `output/[ANALISIS_DIR]/data/` como CSV si son necesarios para scripts posteriores

### 6.3 Validacion post-query (obligatorio)
Aplicar las 7 validaciones de `skills-guides/stratio-data-tools.md` sec 7 a cada resultado recibido. Cuando se lanzan queries en paralelo, validar cada resultado conforme llega. Si alguna falla: reformular la pregunta al MCP, informar al usuario, ajustar el plan.

### 6.4 Desarrollo de scripts
- Escribir scripts en `output/[ANALISIS_DIR]/scripts/` con nombres descriptivos que incluyan contexto del analisis
- Cada script debe:
  - Leer datos de `output/[ANALISIS_DIR]/data/` (CSVs guardados previamente) o recibir datos como parametro
  - Realizar transformaciones y calculos
  - Generar visualizaciones en `output/[ANALISIS_DIR]/assets/`
  - Producir outputs en `output/[ANALISIS_DIR]/`
- **Datasets grandes (>100k filas)**: Usar muestreo estratificado para desarrollo rapido, datos completos para la version final

### 6.5 Testing

> **Solo si la profundidad es Estándar/Profundo Y el usuario eligió "Sí" en la pregunta de testing del Bloque 1.** En profundidad Rápido o si el usuario eligió "No", omitir esta sección y ejecutar directamente el script con datos reales.

- Generar `output/[ANALISIS_DIR]/scripts/test_*.py` con tests unitarios ANTES de ejecutar con datos reales
- Usar DataFrames mock con estructura similar a los datos reales
- Validar transformaciones, calculos y formatos de salida
- Ejecutar: `bash -c "source .venv/bin/activate && pytest output/[ANALISIS_DIR]/scripts/test_*.py -v"`
- Solo proceder si los tests pasan

### 6.6 Ejecucion con datos reales
```bash
bash -c "source .venv/bin/activate && python output/[ANALISIS_DIR]/scripts/mi_script.py"
```

### 6.7 Loop de iteracion

Tras revisar resultados iniciales, evaluar si requieren iteracion:

1. **Trigger**: Hallazgo contradice hipotesis, patron inesperado, o pregunta critica no prevista
2. **Accion**: Documentar hallazgo → formular nueva(s) pregunta(s) → queries MCP adicionales (6.2-6.3) → actualizar scripts
3. **Limite**: Max 2 iteraciones. Mas → documentar como analisis de seguimiento
4. **Registro**: Cada iteracion en reasoning: hipotesis → hallazgo → nueva hipotesis → resultado

### 6.8 Complexity Upgrade

Si durante la ejecucion se detecta un hallazgo que excede el alcance del nivel de complejidad actual:

**Triggers:**
- Anomalia: resultado difiere >30% del benchmark o de lo razonable para el dominio
- Inconsistencia: dos queries dan totales que no cuadran (diferencia >5%)
- Patron critico: concentracion Gini >0.8, caida/crecimiento >50% interperiodo, outlier en KPI principal

**Accion:**
1. Pausar la ejecucion normal
2. Informar al usuario siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md): "He detectado [descripcion del hallazgo]. Esto requiere investigacion adicional. ¿Quieres que profundice?" con opciones:
   - "Si, profundizar" → Escalar complejidad, activar fases adicionales (EDA completo, hipotesis sobre el hallazgo, visualizaciones de drill-down)
   - "No, solo documentar" → Registrar hallazgo en el chat y en reasoning como "area de investigacion futura"
3. El upgrade NO reinicia el analisis — extiende el analisis actual con fases adicionales

**Diferencia con el loop de iteracion (6.7):** El loop refina hipotesis dentro del mismo nivel de complejidad. El upgrade cambia el nivel (ej: Triage → Analisis) y activa capacidades adicionales (EDA, hipotesis formales, visualizaciones).

### 6.9 Generacion de deliverables

> **OBLIGATORIO si el usuario seleccionó formatos en el Bloque 1.** La profundidad del análisis (Rápido/Estándar/Profundo) NO afecta a este paso — si el usuario eligió formatos, todos se generan.

1. Cargar la skill `report`
2. Generar TODOS los formatos seleccionados (no omitir ninguno)
3. Verificar existencia de cada fichero con `ls -lh` antes de reportar al usuario (ver Fase 4, paso 10 de AGENTS.md)

### 6.10 Reasoning

Generar reasoning segun la profundidad (ver defaults en sec "Reasoning" de AGENTS.md):

- **Rapido**: No generar fichero. Las notas clave se incluyen en el reporte del chat (sec 7.1).
- **Estandar/Profundo**: Seguir la guia completa en [reasoning-guide.md](reasoning-guide.md). Generar solo `.md`.

Si el usuario solicito override de formatos, aplicar su preferencia.

### 6.11 Validacion de output final

Ejecutar validacion segun la profundidad (ver defaults en sec "Reasoning" de AGENTS.md):

- **Rapido**: Solo Bloque A (integridad de archivos). Reportar resultado en chat. No generar fichero.
- **Estandar**: Bloques A + B + C. Generar `validation/validation.md`. Reportar resumen en chat.
- **Profundo**: Bloques A + B + C + D. Generar `validation/validation.md`. Reportar resumen en chat.

Para detalle de cada bloque, umbrales y criterios PASS/WARNING/FAIL, ver [validation-guide.md](validation-guide.md).

Si el usuario solicito override de formatos, aplicar su preferencia.

## 7. Reporte Final

### 7.1 Estructura del reporte en chat

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

## 8. Memoria de Analisis (Confirmacion requerida)

Tras presentar el reporte final, preguntar al usuario (siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md)):

"¿Deseas guardar este analisis en la memoria persistente? Se actualizaran el registro de analisis (`ANALYSIS_MEMORY.md`) y la memoria de conocimiento (`MEMORY.md`)."
- **Si** → Continuar con los pasos 8.1, 8.2 y 8.3
- **No** → Saltar todos los pasos de escritura de memoria. Finalizar sin actualizar ningun fichero de memoria

Los pasos siguientes se ejecutan **solo si el usuario responde "Sí"**:

### 8.1 Crear fichero de detalle del analisis

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

### 8.2 Añadir entrada compacta al indice

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

### 8.3 Memoria de Conocimiento

Tras escribir en ANALYSIS_MEMORY.md, invocar la skill `/update-memory` para actualizar `output/MEMORY.md` con preferencias, patrones de datos y heuristicas descubiertas en este analisis.

## 9. Propuesta de Conocimiento (Opcional)

Tras presentar el reporte final, preguntar al usuario siguiendo la convencion de preguntas (sec "Interaccion con el Usuario" de AGENTS.md):
- **Si**: Analizar conversacion y proponer conocimiento al dominio
- **No**: Finalizar sin proponer

Si acepta, cargar la skill `propose-knowledge` con el dominio usado en este analisis.
Si rechaza, finalizar normalmente.

Este paso es SIEMPRE opcional. Nunca proponer automaticamente.
