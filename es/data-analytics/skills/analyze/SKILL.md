---
name: analyze
description: "Análisis completo de datos BI/BA — descubrimiento de dominio, EDA y calidad de datos, planificación de métricas y KPIs con framework analítico, queries de datos vía MCP, análisis Python con pandas, visualizaciones, generación de informes multi-formato y documentación del razonamiento. Usar cuando el usuario necesite analizar datos de negocio, calcular KPIs, producir visualizaciones, generar resúmenes gráficos, obtener insights o responder preguntas analíticas sobre dominios gobernados. También se activa para comparaciones multi-métrica, resúmenes de KPIs, peticiones de entregables (informes, dashboards) o cualquier petición que requiera cruzar datos entre dimensiones."
argument-hint: "[pregunta o tema de análisis]"
---

# Skill: Análisis BI/BA Completo

Esta guía define el workflow completo para realizar un análisis de Business Intelligence / Business Analytics.

## 1. Parsear la Petición

- Extraer la pregunta de negocio principal del argumento: $ARGUMENTS
- Identificar sub-preguntas implicitas
- Detectar si menciona un dominio, tablas o métricas específicas
- Detectar si menciona un formato de salida preferido

### 1.1 Triage rápido

Si la petición se resuelve con una sola llamada MCP (ver Fase 0 del workflow (AGENTS.md)), responder directamente:
- Definiciones/conceptos → `search_domain_knowledge` → chat
- Estructura/columnas → `list_domain_tables` / `get_table_columns_details` → chat
- Dato puntual → `query_data` → chat
- En estos casos, NO continuar con el resto del workflow

Si la petición requiere análisis (cruce de datos, hipótesis, visualizaciones, múltiples métricas), continuar con sección 2.

## 2. Descubrimiento de Dominio

Si el dominio ya es conocido de la conversación (identificado y explorado en turnos previos), saltar esta sección y continuar con la sección 3. Usar el contexto de dominio y tablas ya establecido.

Leer y seguir `skills-guides/stratio-data-tools.md` sec 4 para los pasos de descubrimiento del dominio (buscar o listar dominios, seleccionar, explorar tablas, columnas y terminología).

## 3. EDA y Perfilado de Datos

Antes de preguntar al usuario sobre formatos y planificar métricas, entender la realidad de los datos en dos dimensiones complementarias: el **perfil estadístico** (EDA) y la **cobertura de calidad de gobernanza** ya definida para esas tablas. Ambas se lanzan en paralelo.

1. **Lanzamiento en paralelo** — Para las tablas clave identificadas en el paso 2, lanzar a la vez:
   - `profile_data` por tabla (perfilado estadístico — seguir la mecánica y umbrales adaptativos de `skills-guides/stratio-data-tools.md` sec 5)
   - `get_tables_quality_details(domain_name, [tablas])` (reglas de gobernanza existentes y su estado OK/KO/WARNING)

2. **Evaluar perfil estadístico (de `profile_data`)**:
   - **Completitud**: % de nulos por columna. Marcar columnas con >50% nulos como limitación
   - **Rango temporal**: Verificar que los datos cubren el periodo que el usuario necesita
   - **Outliers**: Identificar valores extremos (IQR) que podrían sesgar promedios o totales
   - **Distribuciones**: Sesgo en numéricas, desbalanceo en categóricas
   - **Correlaciones**: Relaciones fuertes entre variables (|r| > 0.7) — pueden indicar multicolinealidad o redundancia
   - **Cardinalidad**: Categóricas con >100 valores únicos son difíciles de visualizar o agrupar

3. **Evaluar cobertura de calidad de gobernanza (de `get_tables_quality_details`)**:
   - Contar reglas por tabla y en total
   - Clasificar por estado: OK, KO, WARNING, sin ejecutar
   - Para cada regla KO/WARNING, anotar la dimensión y la columna afectada
   - Identificar si alguna regla KO/WARNING afecta a una columna que el usuario va a usar para métricas, dimensiones o filtros en su petición
   - Este es un **chequeo ligero**: una evaluación completa de cobertura (catálogo de dimensiones, identificación de gaps, priorización) está fuera del alcance de esta skill. Si el usuario pide explícitamente una evaluación completa de cobertura en lugar de un análisis, parar aquí e indicarle que se requiere un flujo dedicado — el agente hará el routing según sus instrucciones

4. **Checklist de suficiencia** — Aplicar ANTES de preguntar formatos:

   | Criterio | Umbral mínimo | Si falla |
   |----------|---------------|----------|
   | Registros | >0 | STOP — reformular query |
   | Completitud temporal | ≥80% del periodo pedido | Ofrecer análisis del periodo disponible |
   | Nulos en vars clave | <30% | Alertar limitación severa, considerar imputación |
   | Tamaño para inferencia | n ≥ 30 | Reportar como exploratorio, sin tests estadísticos |
   | Tamaño para clustering | n ≥ 10 × features | Recomendar análisis descriptivo sin segmentación |
   | Variabilidad | std > 0 en numéricas clave | Excluir variable constante |
   | Granularidad | Nivel pedido disponible | Ofrecer agregacion al disponible |

5. **Data Profiling Score**: ALTO (80-100%), MEDIO (60-79%), BAJO (<60%) — derivado del perfil estadístico. Si BAJO, recomendar mejorar datos o reformular.

6. **Governance Quality Status**: Resumen derivado de `get_tables_quality_details`. Formato: `<N reglas definidas, X OK, Y KO, Z WARNING>` o `sin reglas de calidad definidas para estas tablas`. Si alguna regla KO/WARNING afecta a una columna relevante, marcarla con un ⚠️.

7. **Informar al usuario**: Generar mini-resumen combinado con ambas señales antes de preguntar sobre formato y estilo. Ejemplos:
   - "**Perfilado: ALTO (85%)** · Los datos cubren de enero 2023 a diciembre 2025. La columna `descuento` tiene 35% de nulos. 12 outliers en `importe_total` (>3 IQR). La distribución de `categoria_producto` está concentrada: 3 de 15 categorías representan el 80% de registros.
     **Gobernanza: 8 reglas definidas (6 OK, 1 KO, 1 WARNING)**. ⚠️ La regla KO `validez-fecha_factura` afecta a una columna que vas a usar para agregación temporal — tomar los resultados de esa dimensión con cautela."
   - "**Perfilado: MEDIO (72%)** · 30% nulos en `importe`, hueco de 3 meses en Q2 2024. **Gobernanza: sin reglas de calidad definidas para estas tablas** — el perfil estadístico es tu única señal de calidad."
   - "**Perfilado: ALTO (90%)** · sin issues significativos. **Gobernanza: 5 reglas definidas, todas OK**."

8. **Ajustar expectativas**: Si hay limitaciones serias (Data Profiling Score BAJO, reglas KO sobre columnas clave, cobertura temporal incompleta), advertir al usuario. Cuando una regla KO afecte a una columna central a la petición, preguntar si quiere:
   - Continuar el análisis dejando constancia de la limitación en el deliverable
   - Excluir esa columna/dimensión
   - Parar el análisis y solicitar una evaluación completa de cobertura (flujo dedicado fuera del alcance de esta skill)

## 4. Clasificación y Preguntas al Usuario

> **Nota**: Todas las preguntas con opciones de esta sección siguen la convención de preguntas (sec "Interacción con el Usuario" de AGENTS.md).

### 4.0 Triage vs Análisis

Las preguntas simples (datos puntuales, sin dimensiones de corte) se resuelven en Triage (Fase 0 del workflow) sin invocar esta skill. Todo lo demás es un análisis y sigue el flujo de bloques de preguntas descrito a continuación.

**Defaults generales:**
- Estilo visual: **Corporativo** (si el usuario no elige otro en Bloque 2)

### 4.1 Bloque 1 — Profundidad, Audiencia y Formato

Una sola interacción:

| # | Pregunta | Opciones (literales) | Selección | Condicion |
|---|----------|---------------------|-----------|-----------|
| 1 | ¿Qué profundidad de análisis prefieres? | **Rápido** · **Estándar** (Recomendado) · **Profundo** | Única | Siempre |
| 2 | ¿Para que audiencia es el análisis? | **C-level/Direccion** · **Manager/Responsable** · **Equipo técnico/Data** · **Mixta/General** | Única | Siempre |
| 3 | ¿En que formatos quieres los deliverables? | **Documento** (PDF + DOCX) · **Web** (HTML interactivo con Plotly) · **PowerPoint** (.pptx) | Múltiple | Siempre |
| 4 | ¿Quieres que se generen y ejecuten tests unitarios sobre el código Python? | **Sí** (Recomendado): mejora precisión y calidad, pero consume más tiempo, coste y contexto · **No**: ejecución directa sin tests | Única | Solo Estándar/Profundo |

**Regla adaptativa**: Si la petición del usuario ya especifica información que responde a alguna de estas preguntas, pre-rellenar esa respuesta y no volver a preguntarla. Por ejemplo: si el usuario dijo "dame un informe en PDF", pre-rellenar formato como Document; si dijo "análisis rápido", pre-rellenar profundidad como Quick; si dijo "dashboard ejecutivo", pre-rellenar audiencia como C-level/Executive y formato como Web. Solo preguntar aquello cuya respuesta no pueda inferirse de la petición.

- Los tests validan transformaciones y cálculos antes de ejecutar con datos reales. Mejoran la precisión pero consumen más tokens, tiempo y coste. **En profundidad Rápido, testing se desactiva automáticamente sin preguntar al usuario.**
- La pregunta de formato SIEMPRE permite selección múltiple
- Las opciones de formato son EXACTAMENTE 3: Documento (PDF + DOCX), Web, PowerPoint. No inventar, no omitir, no sustituir
- Si no selecciona formato → no hay deliverables, el análisis se entrega solo en chat + report.md automático
- **Si selecciona uno o más formatos → los deliverables SE GENERAN SIEMPRE, independientemente de la profundidad elegida. Rápido/Estándar/Profundo afecta al análisis, no a los entregables.**
- Requisitos adicionales vía opción "Other" (filtros temporales, segmentos, métricas obligatorias)

### 4.2 Bloque 2 — Estructura y Estilo (solo si seleccionó formato en Bloque 1)

Una sola interacción con 2 preguntas. Las opciones son literales — no inventar, no omitir, no sustituir:

| # | Pregunta | Opciones (literales) | Selección |
|---|----------|---------------------|-----------|
| 1 | ¿Qué estructura prefieres para el reporte? | **Scaffold base** (Recomendado): resumen ejecutivo → metodología → datos → análisis → conclusiones · **Al vuelo**: estructura libre según contexto | Única |
| 2 | ¿Qué estilo visual prefieres? | **Corporativo** (`corporate.css`, Recomendado): limpio, profesional · **Formal/académico** (`academic.css`): serif, márgenes amplios, estilo paper · **Moderno/creativo** (`modern.css`): colores, gradientes, visualmente atractivo | Única |

Si no seleccionó formato en Bloque 1 → Bloque 2 se omite completamente. Resultado: de 6 a 1-2 interacciones.

## 5. Planificación

Elaborar un plan detallado siguiendo el framework analítico (sec "Framework Analítico" de AGENTS.md):

### 5.0 Contexto histórico
Leer en paralelo (si existen):
- `output/ANALYSIS_MEMORY.md` — triage rápido: buscar entradas del mismo dominio. Si hay una entrada relevante, leer su fichero `analysis_memory.md` referenciado en el campo **Detalle** para obtener KPIs, insights y baselines de referencia
- `output/MEMORY.md` — sec "Patrones de Datos Conocidos" del dominio para anticipar problemas de datos conocidos

### 5.1 Librerias adicionales
Evaluar si `requirements.txt` necesita ampliarse

### 5.2 Enfoque analítico: descriptivo, segmentación o feature importance

Determinar si la pregunta requiere solo análisis descriptivo o también segmentación/clustering o feature importance:

| Escenario | Recomendación |
|-----------|---------------|
| Describir que paso y por qué | Análisis descriptivo (pandas, agrupaciones, comparativas) |
| Descubrir grupos/segmentos no predefinidos | Clustering (RFM, KMeans, DBSCAN). Ver [clustering-guide.md](clustering-guide.md) |
| Identificar factores influyentes (>5 variables) | Feature importance exploratoria. Ver [clustering-guide.md](clustering-guide.md) sec 7 |
| Proyección temporal | Proyección lineal + IC95%. Ver [advanced-analytics.md](advanced-analytics.md) |

**Detección automática**: Si la pregunta menciona "segmentar", "agrupar", "perfiles" → clustering. Si menciona "que factores influyen", "que explica" → feature importance. Si pide proyección temporal → proyección lineal (no ML). Inferir el tipo de la pregunta y los datos, no preguntar al usuario.

### 5.3 Hipótesis
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

### 5.4 Métricas y KPIs

Para cada KPI, documentar:

| Campo | Descripción |
|-------|-------------|
| Nombre | Identificador claro |
| Fórmula | Cálculo exacto |
| Granularidad | Temporal: diario/semanal/mensual/trimestral |
| Dimensiones | Ejes de corte (región, producto, segmento) |
| Benchmark | Objetivo, media del sector, o periodo anterior |
| Fuente | Tabla(s) y columna(s) del dominio |
| Test estadístico | Si requiere IC o comparación entre grupos (ver [advanced-analytics.md](advanced-analytics.md)) |

**Benchmark Discovery** — Escala según profundidad (ver matriz de activación en AGENTS.md sec 2):
- **Rápido**: No buscar activamente. Usar comparación temporal natural si la query ya incluye dimensión tiempo
- **Estándar**: Best-effort silencioso:
  1. `search_domain_knowledge("target/objetivo de [nombre_KPI]", domain)`
  2. Query MCP adicional para mismo KPI en periodo T-1
  3. Si no hay referencia externa: media/mediana como referencia interna
  Sin benchmark → reportar el dato normalmente, documentar en reasoning
- **Profundo**: Pasos 1-3 + tendencia si >6 puntos temporales + preguntar al usuario

Documentar el benchmark en el campo "Benchmark" del KPI. Los datos sin benchmark se reportan con normalidad — la ausencia solo se marca como limitación en profundidad Profundo.

### 5.5 Preguntas de datos
Lista de preguntas en lenguaje natural para `query_data`. NUNCA escribir SQL.

Para buenas prácticas de formulación y estrategia de queries (orden de planificación, ejecución en paralelo), ver `skills-guides/stratio-data-tools.md` sec 9.

### 5.6 Visualizaciones

Leer y seguir `skills-guides/visualization.md` para selección de gráficas y principios de visualización.

Para cada visualización del plan, definir:
- **Pregunta analítica** que responde
- **Tipo de gráfica**: Seleccionar según tabla en `skills-guides/visualization.md` sec 1
- **Variables**: Que va en cada eje, agrupaciones, filtros
- **Título**: Formulado como insight, no como descripción
- **Datos fuente**: Query MCP que alimenta la visualización

### 5.7 Técnicas analíticas avanzadas

Activar según la profundidad seleccionada (ver matriz de activación en AGENTS.md sec 2):
- **Estándar**: Consultar [advanced-analytics.md](advanced-analytics.md) cuando sea relevante
- **Profundo**: Consultar [advanced-analytics.md](advanced-analytics.md) sistemáticamente

Cubre: rigor estadístico (tests, IC, effect sizes), análisis prospectivo (escenarios, Monte Carlo), root cause analysis, detección de anomalías.

### 5.8 Patrones analíticos adicionales

Implementación detallada de patrones cuyo trigger está en sec "Patrones analíticos operacionalizados" de AGENTS.md (Lorenz/Gini, mix, indexación, desviación vs referencia, gap).

Cuando un patrón se active: consultar [analytical-patterns.md](analytical-patterns.md) para query MCP, Python e interpretación.

### 5.9 Segmentación y clustering

Para guía completa de segmentación (RFM, clustering, validación, profiling), ver [clustering-guide.md](clustering-guide.md).

Usar cuando el usuario pida segmentación, agrupación de clientes/productos, o descubrimiento de perfiles. La guía cubre:
- Tabla de decisión (cuando usar rule-based, RFM, KMeans o DBSCAN)
- RFM con quintiles y etiquetas de negocio
- Clustering básico con elbow + silhouette
- Validación de clusters y profiling obligatorio

Para feature importance como complemento a la segmentación o al análisis descriptivo, ver [clustering-guide.md](clustering-guide.md) sec 7.

### 5.10 Estructura del deliverable
Secciones, contenido de cada una, formato. Aplicar principios de data storytelling (sección 7.1)

### 5.11 Presentar plan
Presentar plan completo al usuario y solicitar aprobación antes de ejecutar.

Al final de la presentación del plan, incluir una nota breve:
> Si dispones de documentación adicional, benchmarks de referencia, informes previos o datos complementarios que puedan enriquecer el análisis, puedes compartirlos ahora.

No convertir esta nota en pregunta bloqueante. Es una invitación, no un paso obligatorio. Si el usuario no aporta nada, continuar sin esperar respuesta adicional más allá de la aprobación del plan.

## 6. Ejecución

### 6.0 Determinar carpeta del análisis
Generar nombre `YYYY-MM-DD_HHMM_nombre_descriptivo` (minusculas, sin tildes, guiones bajos, max 30 chars en el nombre). Declarar en chat. Crear subdirectorios: `output/[ANALISIS_DIR]/scripts/`, `output/[ANALISIS_DIR]/data/`, `output/[ANALISIS_DIR]/assets/`. Si profundidad >= Estándar, crear también `output/[ANALISIS_DIR]/reasoning/` y `output/[ANALISIS_DIR]/validation/`.

Persistir el plan aprobado en `output/[ANALISIS_DIR]/plan.md`.
Escribir el plan tal como fue formulado en la Fase 3 (sección 5) y aprobado por el usuario:
hipótesis, métricas/KPIs, queries de datos, visualizaciones, estructura del deliverable,
complejidad, profundidad, formatos y estilo.

### 6.1 Setup del entorno
```bash
bash setup_env.sh
```
Si hay librerías adicionales, actualizar `requirements.txt` y re-ejecutar setup.

### 6.2 Obtención de datos
- Usar `query_data(data_question=..., domain_name=..., output_format="dict")` para cada pregunta de datos. **Lanzar en paralelo** todas las queries independientes definidas en el plan (paso 5.5). Solo serializar si una query necesita el resultado de otra para formularse
- Seguir todas las reglas de `skills-guides/stratio-data-tools.md` (MCP-first, output_format, no SQL manual, ejecución en paralelo)
- Guardar datos intermedios en `output/[ANALISIS_DIR]/data/` como CSV si son necesarios para scripts posteriores

### 6.3 Validación post-query (obligatorio)
Aplicar las 7 validaciones de `skills-guides/stratio-data-tools.md` sec 7 a cada resultado recibido. Cuando se lanzan queries en paralelo, validar cada resultado conforme llega. Si alguna falla: reformular la pregunta al MCP, informar al usuario, ajustar el plan.

### 6.4 Desarrollo de scripts
- Escribir scripts en `output/[ANALISIS_DIR]/scripts/` con nombres descriptivos que incluyan contexto del análisis
- Cada script debe:
  - Leer datos de `output/[ANALISIS_DIR]/data/` (CSVs guardados previamente) o recibir datos como parámetro
  - Realizar transformaciones y cálculos
  - Generar visualizaciones en `output/[ANALISIS_DIR]/assets/`
  - Producir outputs en `output/[ANALISIS_DIR]/`
- **Datasets grandes (>100k filas)**: Usar muestreo estratificado para desarrollo rápido, datos completos para la versión final

### 6.5 Testing

> **Solo si la profundidad es Estándar/Profundo Y el usuario eligió "Sí" en la pregunta de testing del Bloque 1.** En profundidad Rápido o si el usuario eligió "No", omitir esta sección y ejecutar directamente el script con datos reales.

- Generar `output/[ANALISIS_DIR]/scripts/test_*.py` con tests unitarios ANTES de ejecutar con datos reales
- Usar DataFrames mock con estructura similar a los datos reales
- Validar transformaciones, cálculos y formatos de salida
- Ejecutar: `bash -c "source .venv/bin/activate && pytest output/[ANALISIS_DIR]/scripts/test_*.py -v"`
- Solo proceder si los tests pasan

### 6.6 Ejecución con datos reales
```bash
bash -c "source .venv/bin/activate && python output/[ANALISIS_DIR]/scripts/mi_script.py"
```

### 6.7 Loop de iteración

Tras revisar resultados iniciales, evaluar si requieren iteración:

1. **Trigger**: Hallazgo contradice hipótesis, patrón inesperado, o pregunta crítica no prevista
2. **Acción**: Documentar hallazgo → formular nueva(s) pregunta(s) → queries MCP adicionales (6.2-6.3) → actualizar scripts
3. **Limite**: Max 2 iteraciones. Más → documentar como análisis de seguimiento
4. **Registro**: Cada iteración en reasoning: hipótesis → hallazgo → nueva hipótesis → resultado

### 6.8 Complexity Upgrade

Si durante la ejecución se detecta un hallazgo que excede el alcance del nivel de complejidad actual:

**Triggers:**
- Anomalía: resultado difiere >30% del benchmark o de lo razonable para el dominio
- Inconsistencia: dos queries dan totales que no cuadran (diferencia >5%)
- Patrón crítico: concentración Gini >0.8, caida/crecimiento >50% interperiodo, outlier en KPI principal

**Acción:**
1. Pausar la ejecución normal
2. Informar al usuario siguiendo la convención de preguntas (sec "Interacción con el Usuario" de AGENTS.md): "He detectado [descripción del hallazgo]. Esto requiere investigación adicional. ¿Quieres que profundice?" con opciones:
   - "Sí, profundizar" → Escalar complejidad, activar fases adicionales (EDA completo, hipótesis sobre el hallazgo, visualizaciones de drill-down)
   - "No, solo documentar" → Registrar hallazgo en el chat y en reasoning como "área de investigación futura"
3. El upgrade NO reinicia el análisis — extiende el análisis actual con fases adicionales

**Diferencia con el loop de iteración (6.7):** El loop refina hipótesis dentro del mismo nivel de complejidad. El upgrade cambia el nivel (ej: Triage → Análisis) y activa capacidades adicionales (EDA, hipótesis formales, visualizaciones).

### 6.9 Generación de deliverables

> **OBLIGATORIO si el usuario seleccionó formatos en el Bloque 1.** La profundidad del análisis (Rápido/Estándar/Profundo) NO afecta a este paso — si el usuario eligió formatos, todos se generan.

1. Cargar la skill `report`
2. Generar TODOS los formatos seleccionados (no omitir ninguno)
3. Verificar existencia de cada fichero con `ls -lh` antes de reportar al usuario (ver Fase 4, paso 10 de AGENTS.md)

### 6.10 Reasoning

Generar reasoning según la profundidad (ver defaults en sec "Reasoning" de AGENTS.md):

- **Rápido**: No generar fichero. Las notas clave se incluyen en el reporte del chat (sec 7.1).
- **Estándar/Profundo**: Seguir la guía completa en [reasoning-guide.md](reasoning-guide.md). Generar solo `.md`.

Si el usuario solicitó override de formatos, aplicar su preferencia.

### 6.11 Validación de output final

Ejecutar validación según la profundidad (ver defaults en sec "Reasoning" de AGENTS.md):

- **Rápido**: Solo Bloque A (integridad de archivos). Reportar resultado en chat. No generar fichero.
- **Estándar**: Bloques A + B + C. Generar `validation/validation.md`. Reportar resumen en chat.
- **Profundo**: Bloques A + B + C + D. Generar `validation/validation.md`. Reportar resumen en chat.

Para detalle de cada bloque, umbrales y criterios PASS/WARNING/FAIL, ver [validation-guide.md](validation-guide.md).

Si el usuario solicitó override de formatos, aplicar su preferencia.

## 7. Reporte Final

### 7.1 Estructura del reporte en chat

Al presentar hallazgos en la conversación, seguir esta estructura:

1. **Hook**: El hallazgo más impactante primero
2. Resumen ejecutivo (3-5 bullets con "so what")
3. Insights con datos concretos y contexto comparativo (vs anterior, vs objetivo)
4. Recomendaciones accionables priorizadas (alto impacto + alta confianza primero)
5. Limitaciones y caveats
6. Rutas de archivos generados
7. Sugerencias de análisis de seguimiento

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

Para principios de data storytelling y mapping hallazgos → narrativa, leer `skills-guides/visualization.md` secciones 3 y 4.

## 8. Memoria de Análisis (Confirmación requerida)

Tras presentar el reporte final, preguntar al usuario (siguiendo la convención de preguntas (sec "Interacción con el Usuario" de AGENTS.md)):

"¿Deseas guardar este análisis en la memoria persistente? Se actualizarán el registro de análisis (`ANALYSIS_MEMORY.md`) y la memoria de conocimiento (`MEMORY.md`)."
- **Si** → Continuar con los pasos 8.1, 8.2 y 8.3
- **No** → Saltar todos los pasos de escritura de memoria. Finalizar sin actualizar ningún fichero de memoria

Los pasos siguientes se ejecutan **solo si el usuario responde "Sí"**:

**Idioma**: Redactar todo el contenido de memoria (fichero de detalle, entradas del índice) en el idioma del usuario.

### 8.1 Crear fichero de detalle del análisis

Crear `output/[ANALISIS_DIR]/analysis_memory.md` con el contenido completo:

```markdown
# Memoria del Análisis: Título Descriptivo

- **Dominio**: nombre_exacto_dominio
- **Pregunta**: "Pregunta original del usuario"
- **Carpeta**: `output/YYYY-MM-DD_HHMM_nombre/`
- **Reporte**: `output/YYYY-MM-DD_HHMM_nombre/report.md`
- **KPIs**: KPI1: valor (periodo), KPI2: valor (periodo)
- **Insights**: Hallazgo 1 (confianza), Hallazgo 2 (confianza)
- **Data Profiling Score**: ALTO/MEDIO/BAJO (N%)
```

### 8.2 Añadir entrada compacta al índice

Añadir entrada al final de `output/ANALYSIS_MEMORY.md` con solo los campos de triage:

```markdown
---

## YYYY-MM-DD HH:MM — Título Descriptivo

- **Dominio**: nombre_exacto_dominio
- **Resumen**: Pregunta + hallazgo principal en 1 frase (max ~120 chars)
- **Detalle**: `output/YYYY-MM-DD_HHMM_nombre/analysis_memory.md`

---
```

Si `output/ANALYSIS_MEMORY.md` no existe, inicialízalo a partir del template antes de añadir la entrada:

```bash
mkdir -p output
cp templates/memory/ANALYSIS_MEMORY.md output/ANALYSIS_MEMORY.md
```

Luego añade la entrada al final (cronológicas).

### 8.3 Memoria de Conocimiento

Tras escribir en ANALYSIS_MEMORY.md, invocar la skill `/update-memory` para actualizar `output/MEMORY.md` con preferencias, patrones de datos y heurísticas descubiertas en este análisis.

## 9. Propuesta de Conocimiento (Opcional)

Tras presentar el reporte final, preguntar al usuario siguiendo la convención de preguntas (sec "Interacción con el Usuario" de AGENTS.md):
- **Si**: Analizar conversación y proponer conocimiento al dominio
- **No**: Finalizar sin proponer

Si acepta, cargar la skill `propose-knowledge` con el dominio usado en este análisis.
Si rechaza, finalizar normalmente.

Este paso es SIEMPRE opcional. Nunca proponer automáticamente.
