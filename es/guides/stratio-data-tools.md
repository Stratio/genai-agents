# Guía de Uso de MCPs Stratio

> **Guía compañera.** Para polling de `task_id` y truncación de salidas grandes — ambos pueden ocurrir en cualquier tool MCP de las listadas más abajo — ver `stratio-mcp-response-patterns.md`. Referencia rápida en §9.

## 1. Regla Fundamental

**NUNCA escribas SQL manualmente.** El sistema MCP tiene un motor sofisticado de generación de queries que entiende el dominio gobernado, sus reglas de negocio, relaciones entre tablas y restricciones. Siempre delega la generación y ejecución de queries al MCP.

## 2. Herramientas MCP Disponibles

| Paso | Herramienta MCP | Propósito |
|------|----------------|-----------|
| 1a | `search_domains(search_text, domain_type?, refresh?, prefer_semantic?)` | **Preferir sobre `list_domains`**. Buscar dominios por texto libre (nombre o descripción). Resultados ordenados por relevancia. Usar cuando se conoce parte del nombre o tema del dominio. `domain_type`: `'business'` (dominios semánticos publicados, con nombres de negocio), `'technical'` (dominios de datos crudos, con identificadores de base de datos) o `'both'` (defecto — todos). `refresh`: bypass de cache. `prefer_semantic` (defecto `false`, solo aplica cuando `domain_type='both'`): deduplica los resultados por colección, devolviendo la entrada business/semántica cuando existe y cayendo al técnico en caso contrario |
| 1b | `list_domains(domain_type?, refresh?, prefer_semantic?)` | Listar todos los dominios disponibles. Usar solo cuando se necesita ver todos los dominios sin filtro o cuando `search_domains` no devuelve resultados. Mismos parámetros `domain_type`, `refresh` y `prefer_semantic` que `search_domains` |
| 2 | `list_domain_tables` | Conocer tablas del dominio |
| 3 | `get_tables_details` | Entender reglas de negocio y contexto |
| 4 | `get_table_columns_details` | Conocer columnas, tipos y significado |
| 5 | `search_domain_knowledge` | Entender terminología y definiciones |
| 6 | `query_data` | **Obtener datos** (pregunta en lenguaje natural -> datos) |
| 7 | `generate_sql` | Ver el SQL antes de ejecutar (opcional, para revisión) |
| 8 | `execute_sql` | Re-ejecutar SQL generado por el MCP (nunca SQL manual) |
| 9 | `profile_data` | EDA estadístico rápido |
| 10 | `get_tables_quality_details` | Cobertura de reglas de calidad de gobierno por tabla (OK/KO/WARNING/not-executed) |
| 11 | `propose_knowledge` | Proponer términos de negocio descubiertos |
| — | `get_mcp_task_result(task_id)` | Obtener el resultado de una tool de larga duración que sigue ejecutándose en segundo plano. Se llama cuando cualquier tool devuelve solo un `task_id` — ver §9 y `stratio-mcp-response-patterns.md` §1 |

## 3. Reglas Estrictas

- **INMUTABILIDAD de `domain_name`**: El parámetro `domain_name` en TODAS las llamadas MCP debe ser **exactamente** el valor devuelto por `list_domains` o `search_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo. Si el dominio se llama `semantic_AnaliticaBanca`, usar `"semantic_AnaliticaBanca"` — no `"Banca Particulares"`, no `"Analítica Banca"`, no `"banca"`. Si hay duda sobre el nombre exacto, volver a llamar a `search_domains` o `list_domains` para confirmarlo
- NUNCA escribas queries SQL directamente. Siempre usa `query_data` o `generate_sql`
- Para agregaciones simples (totales, promedios, conteos): `query_data` directamente
- Para análisis avanzados: intentar siempre resolver con `query_data` (el MCP soporta joins, agregaciones, window functions, subconsultas). Usar Python/pandas solo cuando el cálculo no sea expresable en SQL (tests estadísticos, segmentación, transformaciones iterativas, lógica procedural). En ese caso, obtener los datos con `output_format="dict"` y procesarlos en pandas
- **MCP-first**: Resolver siempre en el MCP todo lo que pueda expresarse como query SQL. El MCP genera SQL que entiende el dominio gobernado, sus relaciones y reglas de negocio. Usar Python/pandas SOLO para lo que SQL no puede resolver: tests estadísticos, segmentación, transformaciones iterativas, lógica procedural, o preparación de datos para visualización. Para múltiples datasets:
  - **Una query MCP** cuando: el resultado requiere datos de varias tablas relacionadas (el MCP genera los JOINs), o agregaciones con filtros complejos. Siempre intentar esto primero
  - **Múltiples queries independientes** cuando: se necesitan cortes ortogonales de los datos (ej: una query temporal + una query por segmento + una query de ranking). Lanzar en paralelo
  - **Combinar en pandas** solo cuando: se necesitan cálculos que SQL no puede resolver (estadística, segmentación) sobre datos de varias queries, o transformaciones iterativas sobre el detalle transaccional
  - **Inconsistencias**: Si dos queries dan totales diferentes, verificar granularidad y filtros. Reformular con `additional_context` para alinear
- Puedes proporcionar `additional_context` al MCP para guiar la generación (ej: definiciones de negocio, filtros específicos)
- **`output_format` es un string**: Los valores válidos son `"dict"`, `"csv"` o `"markdown"`. Es opcional (default: `"dict"`). NUNCA pasar un booleano (`true`/`false`). Si no necesitas un formato específico, omitir el parámetro
- Si una query falla o da resultados inesperados: reformular la pregunta en lenguaje natural, no intentar escribir SQL
- **Profiling (`profile_data`)**: Requiere SQL como parámetro — generarla SIEMPRE con `generate_sql`, nunca escribirla manualmente. NUNCA añadir LIMIT a la SQL; usar el parámetro `limit` de la tool
- **Ejecución en paralelo**: Cuando el plan define múltiples preguntas de datos independientes (ninguna necesita el resultado de otra para formularse), lanzar TODAS las llamadas a `query_data` en una sola respuesta para que se ejecuten en paralelo. Aplica también a llamadas de metadata (`get_table_columns_details`, `profile_data`, etc.). Solo serializar cuando una query depende del resultado de otra (ej: necesitas un valor de la query A para formular la query B). **"En paralelo" aquí significa emitir múltiples tool calls en la MISMA respuesta para que el runtime las ejecute concurrentemente — NO crear subtareas, sub-sesiones, ni invocar la tool Task. Nunca delegues llamadas MCP a un subagente.**

## 4. Mostrar resultados de queries al usuario

Siempre que el usuario pida ver el resultado de una query — señales explícitas o implícitas: *muéstrame*, *enséñame*, *show me*, *dame*, *top N*, *primeras N*, *no veo los resultados*, *preview*, *validación*, *una muestra*, *los datos*, *los resultados*, *qué devuelve* — renderizar el resultado en línea en chat como tabla Markdown con **todas** las columnas devueltas. El agente nunca sustituye el resultado por un resumen, ni muestra solo "una fila representativa".

Aplica a `query_data`, `execute_sql` y a cualquier otro flujo que devuelva datos tabulares al usuario.

### Reglas de presentación de filas

- **Cap por defecto (sin N explícito)**: renderizar hasta **10 filas** en chat. La query puede haber usado un `LIMIT` distinto internamente — el cap solo controla qué se pinta al usuario.
- **N explícito del usuario**: cuando el usuario pidió un número concreto (`top 50`, `primeras 25`, `muéstrame 100`, `dame 30`), respetar esa intención hasta un **techo absoluto de 50 filas** pintadas en chat. Por encima de 50, aplicar el cap y reportar el total en la línea de cierre.
- **Línea de cierre** (una línea breve en cursiva justo después de la tabla):
  - `N_devueltas ≤ pintadas`: sin línea de cierre. Solo la tabla.
  - `N_devueltas > pintadas`: añadir `_Mostrando {pintadas} de {N_devueltas} filas — query ejecutada con LIMIT {LIMIT_query}_` (en el idioma del usuario).
  - `N_devueltas == 0`: no pintar tabla. Emitir un mensaje breve `_La query no devolvió filas._` (en el idioma del usuario).
- **Cabeceras**: incluir todas las columnas devueltas por la tool, en el orden devuelto. No abreviar ni ocultar columnas.

### Fuera de scope

Esta regla rige **solo la presentación final al usuario en chat**. Los datos que se pasan a otra skill (p. ej. una skill writer que producirá un artefacto PDF/DOCX/PPTX/XLSX/web, o una skill de gráficos) son intermedios y no están sujetos al cap.

## 5. Workflow de Descubrimiento de Dominio

Pasos para explorar un dominio gobernado y entender sus datos antes de un análisis.

### 5.1 Descubrir Dominios

**Preferir buscar sobre listar** — `search_domains` devuelve resultados relevantes sin cargar la lista completa (que puede ser muy extensa).

Si el usuario proporciona un dominio o da pistas sobre el tema:
- Ejecutar `search_domains(nombre_o_pista)` para buscar coincidencias
- Si coincide con un resultado → usarlo directamente e ir al paso 5.2
- Si no hay coincidencias → ejecutar `list_domains()` como fallback y preguntar al usuario

Si no hay dominio claro, preguntar al usuario cuál le interesa. Si el usuario no da pistas, ejecutar `list_domains()` para mostrar todos los dominios disponibles (presentar como opciones seleccionables).

Si un dominio recién publicado o creado no aparece, reintentar con `refresh=true` (bypass de cache).

Cuando una colección está expuesta en ambas capas (semántica + técnica), `domain_type='both'` devuelve ambas entradas por defecto. Si solo necesitas una entrada por colección y prefieres el nombre semántico (business) cuando exista, cayendo al técnico en caso contrario, pasar `prefer_semantic=true`.

### 5.2 Explorar Tablas

1. `list_domain_tables(domain_name)` para listar todas las tablas del dominio
2. **Si la salida está truncada** (ver §9 y `stratio-mcp-response-patterns.md` §2): delegar la inspección del fichero al subagente del runtime (p. ej. `explore` de OpenCode vía Task). En el prompt incluye tanto la ruta literal del fichero guardado, tal como aparece en el aviso de truncación, **como el objetivo de extracción** (inventario de nombres de tablas, subconjunto temático, etc.); NO pidas al subagente que encuentre el fichero con `Glob`. Si el subagente devuelve un error, recurre a `Grep` + `Read` con `limit` en esta conversación (≤ 200 líneas por llamada). Extraer los nombres de tablas y sus descripciones — o un subconjunto temático que coincida con la pregunta del usuario — sin ingerir el fichero completo
3. Presentar las tablas y sus descripciones en una tabla markdown. Si el inventario sigue siendo demasiado grande para renderizar de forma útil (caso de truncación, o lista plana muy por encima del tamaño presentable en chat): mostrar solo el subconjunto relevante para la pregunta del usuario, indicar el total y explicar el criterio de filtrado — p. ej. *"El dominio tiene 312 tablas; mostrando las 9 que coinciden con `<tema>`. Avisa si quieres otro recorte."*

### 5.3 Detalle de Tablas

Para las tablas de interés:
1. `get_tables_details(domain_name, table_names)` para obtener:
   - Descripción completa
   - Contexto de negocio
   - Términos de negocio asociados
   - Reglas de negocio
   - Comportamientos SQL
2. Presentar la información de forma estructurada

### 5.4 Columnas

Para cada tabla de interés:
1. `get_table_columns_details(domain_name, table_name)` para obtener nombre, tipo y descripción de negocio
2. Presentar en tabla markdown ordenada lógicamente

**Lanzar en paralelo** los pasos 5.3 y 5.4 cuando sean sobre tablas independientes. También lanzar paso 5.5 en paralelo si ya se conocen los términos a buscar.

### 5.5 Terminología de Negocio

`search_domain_knowledge(question, domain_name)` para buscar:
- Definiciones de términos de negocio
- Reglas de cálculo
- Políticas de datos
- Glosario del dominio

## 6. Observación de Datos: Perfilado y Cobertura de Calidad

Dos tools complementarias caracterizan las tablas seleccionadas antes de un análisis — una aporta señal estadística, la otra muestra la cobertura de reglas de gobierno. Lanzar ambas **en paralelo** cuando el alcance cubre el mismo conjunto de tablas.

### 6.1 Perfilado Estadístico — `profile_data`

Para las reglas de uso de `profile_data` (generar SQL con `generate_sql`, nunca SQL manual, usar parámetro `limit` en vez de LIMIT en SQL), ver sec 3.

Umbrales adaptativos de profiling según tamaño estimado:

| Filas estimadas | Estrategia | Parámetro limit |
|----------------|------------|-----------------|
| <100K | Completo | No configurar (default) |
| 100K - 1M | Muestreo | `limit=100000` |
| >1M | Muestreo + alerta | `limit=100000` + informar al usuario |

Documentar en reasoning si se usó muestreo.

### 6.2 Cobertura de Calidad de Gobierno — `get_tables_quality_details`

`get_tables_quality_details(domain_name, table_names=[...])` devuelve las reglas de calidad de gobierno actualmente definidas para las tablas indicadas y su último estado de ejecución.

Se devuelve para cada tabla:
- Reglas registradas sobre la tabla, con dimensión (completitud, unicidad, validez, consistencia, etc.) y columna afectada
- Estado de ejecución por regla: `OK`, `KO`, `WARNING` o `not-executed`

Cuándo usarla:
- Chequeo ligero de gobierno durante la exploración de datos o la fase EDA de un análisis
- No reemplaza una evaluación completa de calidad — para análisis de brechas y remediación, usar la skill `assess-quality`

Patrón de ejecución: lanzar en paralelo con `profile_data` sobre el mismo conjunto de tablas. El profiling revela anomalías estadísticas; los detalles de calidad revelan cuáles de esas anomalías ya están cubiertas por una regla de gobierno (y cuáles no).

## 7. Respuestas de Aclaración del MCP

`query_data` y `generate_sql` pueden responder con una solicitud de aclaración
en lugar de datos (ej: "¿A que periodo te refieres?", "¿'Activos' incluye usuarios con compra
en 30 o 90 días?"). Esto no es un error — es el motor pidiendo contexto adicional.

Protocolo en cascada (seguir en orden):
1. **Buscar en el dominio**: Llamar a `search_domain_knowledge` con el término ambiguo.
   Si se encuentra la definición, rellamar con `additional_context` incluyendo la definición
2. **Inferir del plan**: Si el plan de análisis ya define el término o periodo, añadirlo
   directamente a `additional_context` y rellamar
3. **Preguntar al usuario**: Solo si los pasos 1-2 no resuelven la ambigüedad. Presentar
   la pregunta con opciones concretas (nunca texto libre si hay opciones claras)
4. **Reformular**: Si persiste la ambigüedad, reformular la pregunta de datos con mayor
   especificidad (fechas explícitas, definiciones incrustadas en el texto)
5. **Informar y continuar**: Si el MCP no puede responder tras estos pasos, documentar
   la limitación y continuar el análisis con los datos disponibles

Máximo 2 iteraciones de aclaración por query. Si tras ambas iteraciones no hay datos,
informar al usuario y omitir esa métrica del análisis.

## 8. Validación Post-Query

Cada resultado de `query_data` debe pasar estas 7 validaciones antes de usarse en el análisis. Cuando se lanzan queries en paralelo, validar cada resultado conforme se recibe:
1. **Dataset no vacío** (>0 filas). Si vacío: reformular pregunta o alertar al usuario
2. **Columnas esperadas presentes**. Si faltan: revisar formulación de la pregunta
3. **Tipos de datos coherentes** (fechas son fechas, numéricos son numéricos)
4. **Rango temporal** cubre el periodo solicitado
5. **Proporción de nulos** en columnas clave (<50%). Si excede: documentar limitación
6. **Valores en rangos razonables** (no hay edades de 500 años, importes negativos inesperados)
7. **Sanity check de negocio**: Verificar que los resultados tienen sentido:
   - Magnitudes razonables (crecimiento del 500% MoM es probablemente error de datos)
   - Consistencia con conocimiento del dominio (`search_domain_knowledge`)
   - Si un hallazgo parece "demasiado bueno/malo", investigar antes de reportar

Si alguna validación falla: reformular la pregunta al MCP, informar al usuario de la limitación, y ajustar el plan si es necesario.

## 9. Patrones de Respuesta del MCP

Dos patrones de respuesta pueden ocurrir en **cualquier** tool MCP de las listadas en §2. Los protocolos están en `stratio-mcp-response-patterns.md` — aplicarlos siempre que aparezca el disparador.

| Disparador | Sección compañera |
|------------|-------------------|
| La respuesta contiene únicamente un campo `task_id` (sin datos, sin error) | `stratio-mcp-response-patterns.md` §1 — Polling de Tareas de Larga Duración |
| La respuesta sustituida por un aviso de truncación + ruta de fichero guardado, sin `task_id` | `stratio-mcp-response-patterns.md` §2 — Salidas de Tools de Gran Tamaño Truncadas |

## 10. Optimización de Queries en Errores/Timeouts

Si el MCP tarda demasiado o devuelve error:
1. **Simplificar la pregunta**: Reducir dimensiones o periodo temporal
2. **Dividir la query**: Partir una pregunta compleja en varias más simples
3. **Reformular**: Expresar la misma pregunta de forma diferente
4. No reintentar la misma pregunta más de 2 veces — si persiste, informar al usuario

## 11. Buenas Prácticas para Formular Preguntas

- **Ser específico con periodos**: "ventas mensuales del último año" en vez de "ventas"
- **Incluir dimensiones**: "por región y categoría de producto"
- **Especificar métricas**: "total de ingresos y número de transacciones"
- **Usar additional_context**: Para definiciones no obvias (ej: "Clientes activos = al menos 1 compra en 90 días")
- **Una pregunta = un dataset**: No mezclar preguntas no relacionadas
- **Pensar en granularidad**: Necesito datos agregados o detalle transaccional?

**Estrategia de queries** — orden de PLANIFICACIÓN (pensar de lo general a lo específico):
1. **Contexto general**: Totales, conteos básicos → entender la magnitud del dataset
2. **Queries dimensionales**: Por tiempo, segmento, región → encontrar patrones y tendencias
3. **Queries de detalle**: Top/bottom N, outliers → profundizar en los hallazgos
4. **Queries de validación**: Cruces de datos, checks de consistencia → asegurar fiabilidad

Este orden es para **planificar** las preguntas. En **ejecución**, lanzar en paralelo todas las queries independientes — típicamente las categorías 1, 2 y 3 se pueden ejecutar simultáneamente. Solo las de categoría 4 (validación cruzada) pueden requerir resultados previos.

## 12. Fallback por Indisponibilidad de OpenSearch

`search_domains` consulta OpenSearch internamente. OpenSearch puede no estar disponible en todos los entornos (despliegues on-premise, entornos aislados, incidencias de infraestructura). Esta sección define el fallback cuando la tool no está disponible — distinto del fallback por *resultado vacío* ya descrito en §5.1.

### 12.1 Detección del caso

| Situación | Indicador | Ruta de fallback |
|-----------|-----------|------------------|
| Resultado vacío (ya documentado) | La tool devuelve una respuesta bien formada con cero coincidencias | §5.1 — llamar a `list_domains()` y preguntar al usuario |
| Indisponibilidad (nuevo) | Respuesta de error que menciona OpenSearch / index / connection / timeout, **o** dos reintentos sucesivos según §10 siguen fallando (no un `task_id` pendiente según §9 y `stratio-mcp-response-patterns.md` §1) | §12.2 |

### 12.2 Fallback determinístico

| Tool OpenSearch | Alternativa determinística | Cobertura |
|-----------------|----------------------------|-----------|
| `search_domains(search_text, domain_type?)` | `list_domains(domain_type?)` + filtro local de substring sobre `name` y `description` | Dataset completo; sin ranking por relevancia |

Procedimiento:
1. Al detectarse la indisponibilidad por primera vez en la sesión, avisar al usuario una sola vez — p. ej. *"La búsqueda de dominios no está disponible ahora; usaré el listado completo de dominios."* No repetir en llamadas posteriores dentro de la misma sesión.
2. Invocar la alternativa determinística.
3. Continuar el workflow con normalidad (non-blocking).
4. Parar únicamente si la alternativa no cubre la necesidad del usuario (el listado es demasiado grande para que el usuario elija, o se requiere realmente una búsqueda free-text). En ese caso, pedir al usuario que acote el alcance manualmente.
5. Registrar la degradación en cualquier reasoning o resumen producido al final del turno.
