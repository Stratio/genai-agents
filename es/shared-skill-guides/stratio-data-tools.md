# Guia de Uso de MCPs Stratio

## 1. Regla Fundamental

**NUNCA escribas SQL manualmente.** El sistema MCP tiene un motor sofisticado de generacion de queries que entiende el dominio gobernado, sus reglas de negocio, relaciones entre tablas y restricciones. Siempre delega la generacion y ejecucion de queries al MCP.

## 2. Herramientas MCP Disponibles

| Paso | Herramienta MCP | Proposito |
|------|----------------|-----------|
| 1a | `search_domains(search_text, domain_type?, refresh?)` | **Preferir sobre `list_domains`**. Buscar dominios por texto libre (nombre o descripcion). Resultados ordenados por relevancia. Usar cuando se conoce parte del nombre o tema del dominio. `domain_type`: `'business'` (dominios semanticos publicados, con nombres de negocio), `'technical'` (dominios de datos crudos, con identificadores de base de datos) o `'both'` (defecto — todos). `refresh`: bypass de cache |
| 1b | `list_domains(domain_type?, refresh?)` | Listar todos los dominios disponibles. Usar solo cuando se necesita ver todos los dominios sin filtro o cuando `search_domains` no devuelve resultados. Mismos parametros `domain_type` y `refresh` que `search_domains` |
| 2 | `list_domain_tables` | Conocer tablas del dominio |
| 3 | `get_tables_details` | Entender reglas de negocio y contexto |
| 4 | `get_table_columns_details` | Conocer columnas, tipos y significado |
| 5 | `search_domain_knowledge` | Entender terminologia y definiciones |
| 6 | `query_data` | **Obtener datos** (pregunta en lenguaje natural -> datos) |
| 7 | `generate_sql` | Ver el SQL antes de ejecutar (opcional, para revision) |
| 8 | `execute_sql` | Re-ejecutar SQL generado por el MCP (nunca SQL manual) |
| 9 | `profile_data` | EDA estadistico rapido |
| 10 | `propose_knowledge` | Proponer terminos de negocio descubiertos |

## 3. Reglas Estrictas

- **INMUTABILIDAD de `domain_name`**: El parametro `domain_name` en TODAS las llamadas MCP debe ser **exactamente** el valor devuelto por `list_domains` o `search_domains`. NUNCA traducirlo, interpretarlo, parafrasearlo ni inferirlo. Si el dominio se llama `semantic_AnaliticaBanca`, usar `"semantic_AnaliticaBanca"` — no `"Banca Particulares"`, no `"Analítica Banca"`, no `"banca"`. Si hay duda sobre el nombre exacto, volver a llamar a `search_domains` o `list_domains` para confirmarlo
- NUNCA escribas queries SQL directamente. Siempre usa `query_data` o `generate_sql`
- Para agregaciones simples (totales, promedios, conteos): `query_data` directamente
- Para analisis avanzados: intentar siempre resolver con `query_data` (el MCP soporta joins, agregaciones, window functions, subconsultas). Usar Python/pandas solo cuando el calculo no sea expresable en SQL (tests estadisticos, segmentacion, transformaciones iterativas, logica procedural). En ese caso, obtener los datos con `output_format="dict"` y procesarlos en pandas
- **MCP-first**: Resolver siempre en el MCP todo lo que pueda expresarse como query SQL. El MCP genera SQL que entiende el dominio gobernado, sus relaciones y reglas de negocio. Usar Python/pandas SOLO para lo que SQL no puede resolver: tests estadisticos, segmentacion, transformaciones iterativas, logica procedural, o preparacion de datos para visualizacion. Para multiples datasets:
  - **Una query MCP** cuando: el resultado requiere datos de varias tablas relacionadas (el MCP genera los JOINs), o agregaciones con filtros complejos. Siempre intentar esto primero
  - **Multiples queries independientes** cuando: se necesitan cortes ortogonales de los datos (ej: una query temporal + una query por segmento + una query de ranking). Lanzar en paralelo
  - **Combinar en pandas** solo cuando: se necesitan calculos que SQL no puede resolver (estadistica, segmentacion) sobre datos de varias queries, o transformaciones iterativas sobre el detalle transaccional
  - **Inconsistencias**: Si dos queries dan totales diferentes, verificar granularidad y filtros. Reformular con `additional_context` para alinear
- Puedes proporcionar `additional_context` al MCP para guiar la generacion (ej: definiciones de negocio, filtros especificos)
- **`output_format` es un string**: Los valores validos son `"dict"`, `"csv"` o `"markdown"`. Es opcional (default: `"dict"`). NUNCA pasar un booleano (`true`/`false`). Si no necesitas un formato especifico, omitir el parametro
- Si una query falla o da resultados inesperados: reformular la pregunta en lenguaje natural, no intentar escribir SQL
- **Profiling (`profile_data`)**: Requiere SQL como parametro — generarla SIEMPRE con `generate_sql`, nunca escribirla manualmente. NUNCA anadir LIMIT a la SQL; usar el parametro `limit` de la tool
- **Ejecucion en paralelo**: Cuando el plan define multiples preguntas de datos independientes (ninguna necesita el resultado de otra para formularse), lanzar TODAS las llamadas a `query_data` en una sola respuesta para que se ejecuten en paralelo. Aplica tambien a llamadas de metadata (`get_table_columns_details`, `profile_data`, etc.). Solo serializar cuando una query depende del resultado de otra (ej: necesitas un valor de la query A para formular la query B)

## 4. Workflow de Descubrimiento de Dominio

Pasos para explorar un dominio gobernado y entender sus datos antes de un analisis.

### 4.1 Descubrir Dominios

**Preferir buscar sobre listar** — `search_domains` devuelve resultados relevantes sin cargar la lista completa (que puede ser muy extensa).

Si el usuario proporciona un dominio o da pistas sobre el tema:
- Ejecutar `search_domains(nombre_o_pista)` para buscar coincidencias
- Si coincide con un resultado → usarlo directamente e ir al paso 4.2
- Si no hay coincidencias → ejecutar `list_domains()` como fallback y preguntar al usuario

Si no hay dominio claro, preguntar al usuario cual le interesa. Si el usuario no da pistas, ejecutar `list_domains()` para mostrar todos los dominios disponibles (presentar como opciones seleccionables).

Si un dominio recien publicado o creado no aparece, reintentar con `refresh=true` (bypass de cache).

### 4.2 Explorar Tablas

1. `list_domain_tables(domain_name)` para listar todas las tablas del dominio
2. Presentar las tablas con sus descripciones en formato tabla markdown

### 4.3 Detalle de Tablas

Para las tablas de interes:
1. `get_tables_details(domain_name, table_names)` para obtener:
   - Descripcion completa
   - Contexto de negocio
   - Terminos de negocio asociados
   - Reglas de negocio
   - Comportamientos SQL
2. Presentar la informacion de forma estructurada

### 4.4 Columnas

Para cada tabla de interes:
1. `get_table_columns_details(domain_name, table_name)` para obtener nombre, tipo y descripcion de negocio
2. Presentar en tabla markdown ordenada logicamente

**Lanzar en paralelo** los pasos 4.3 y 4.4 cuando sean sobre tablas independientes. Tambien lanzar paso 4.5 en paralelo si ya se conocen los terminos a buscar.

### 4.5 Terminologia de Negocio

`search_domain_knowledge(question, domain_name)` para buscar:
- Definiciones de terminos de negocio
- Reglas de calculo
- Politicas de datos
- Glosario del dominio

## 5. Perfilado Estadistico

Para las reglas de uso de `profile_data` (generar SQL con `generate_sql`, nunca SQL manual, usar parametro `limit` en vez de LIMIT en SQL), ver sec 3.

Umbrales adaptativos de profiling segun tamano estimado:

| Filas estimadas | Estrategia | Parametro limit |
|----------------|------------|-----------------|
| <100K | Completo | No configurar (default) |
| 100K - 1M | Muestreo | `limit=100000` |
| >1M | Muestreo + alerta | `limit=100000` + informar al usuario |

Documentar en reasoning si se uso muestreo.

## 6. Respuestas de Aclaracion del MCP

`query_data` y `generate_sql` pueden responder con una solicitud de aclaracion
en lugar de datos (ej: "¿A que periodo te refieres?", "¿'Activos' incluye usuarios con compra
en 30 o 90 dias?"). Esto no es un error — es el motor pidiendo contexto adicional.

Protocolo en cascada (seguir en orden):
1. **Buscar en el dominio**: Llamar a `search_domain_knowledge` con el termino ambiguo.
   Si se encuentra la definicion, rellamar con `additional_context` incluyendo la definicion
2. **Inferir del plan**: Si el plan de analisis ya define el termino o periodo, anadirlo
   directamente a `additional_context` y rellamar
3. **Preguntar al usuario**: Solo si los pasos 1-2 no resuelven la ambiguedad. Presentar
   la pregunta con opciones concretas (nunca texto libre si hay opciones claras)
4. **Reformular**: Si persiste la ambiguedad, reformular la pregunta de datos con mayor
   especificidad (fechas explicitas, definiciones incrustadas en el texto)
5. **Informar y continuar**: Si el MCP no puede responder tras estos pasos, documentar
   la limitacion y continuar el analisis con los datos disponibles

Maximo 2 iteraciones de aclaracion por query. Si tras ambas iteraciones no hay datos,
informar al usuario y omitir esa metrica del analisis.

## 7. Validacion Post-Query

Cada resultado de `query_data` debe pasar estas 7 validaciones antes de usarse en el analisis. Cuando se lanzan queries en paralelo, validar cada resultado conforme se recibe:
1. **Dataset no vacio** (>0 filas). Si vacio: reformular pregunta o alertar al usuario
2. **Columnas esperadas presentes**. Si faltan: revisar formulacion de la pregunta
3. **Tipos de datos coherentes** (fechas son fechas, numericos son numericos)
4. **Rango temporal** cubre el periodo solicitado
5. **Proporcion de nulos** en columnas clave (<50%). Si excede: documentar limitacion
6. **Valores en rangos razonables** (no hay edades de 500 anos, importes negativos inesperados)
7. **Sanity check de negocio**: Verificar que los resultados tienen sentido:
   - Magnitudes razonables (crecimiento del 500% MoM es probablemente error de datos)
   - Consistencia con conocimiento del dominio (`search_domain_knowledge`)
   - Si un hallazgo parece "demasiado bueno/malo", investigar antes de reportar

Si alguna validacion falla: reformular la pregunta al MCP, informar al usuario de la limitacion, y ajustar el plan si es necesario.

## 8. Timeouts y Reintentos

Si el MCP tarda demasiado o devuelve error:
1. **Simplificar la pregunta**: Reducir dimensiones o periodo temporal
2. **Dividir la query**: Partir una pregunta compleja en varias mas simples
3. **Reformular**: Expresar la misma pregunta de forma diferente
4. No reintentar la misma pregunta mas de 2 veces — si persiste, informar al usuario

## 9. Buenas Practicas para Formular Preguntas

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

Este orden es para **planificar** las preguntas. En **ejecucion**, lanzar en paralelo todas las queries independientes — tipicamente las categorias 1, 2 y 3 se pueden ejecutar simultaneamente. Solo las de categoria 4 (validacion cruzada) pueden requerir resultados previos.
