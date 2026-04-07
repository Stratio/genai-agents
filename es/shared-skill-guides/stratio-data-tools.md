# Guía de Uso de MCPs Stratio

## 1. Regla Fundamental

**NUNCA escribas SQL manualmente.** El sistema MCP tiene un motor sofisticado de generación de queries que entiende el dominio gobernado, sus reglas de negocio, relaciones entre tablas y restricciones. Siempre delega la generación y ejecución de queries al MCP.

## 2. Herramientas MCP Disponibles

| Paso | Herramienta MCP | Propósito |
|------|----------------|-----------|
| 1a | `search_domains(search_text, domain_type?, refresh?)` | **Preferir sobre `list_domains`**. Buscar dominios por texto libre (nombre o descripción). Resultados ordenados por relevancia. Usar cuando se conoce parte del nombre o tema del dominio. `domain_type`: `'business'` (dominios semánticos publicados, con nombres de negocio), `'technical'` (dominios de datos crudos, con identificadores de base de datos) o `'both'` (defecto — todos). `refresh`: bypass de cache |
| 1b | `list_domains(domain_type?, refresh?)` | Listar todos los dominios disponibles. Usar solo cuando se necesita ver todos los dominios sin filtro o cuando `search_domains` no devuelve resultados. Mismos parámetros `domain_type` y `refresh` que `search_domains` |
| 2 | `list_domain_tables` | Conocer tablas del dominio |
| 3 | `get_tables_details` | Entender reglas de negocio y contexto |
| 4 | `get_table_columns_details` | Conocer columnas, tipos y significado |
| 5 | `search_domain_knowledge` | Entender terminología y definiciones |
| 6 | `query_data` | **Obtener datos** (pregunta en lenguaje natural -> datos) |
| 7 | `generate_sql` | Ver el SQL antes de ejecutar (opcional, para revisión) |
| 8 | `execute_sql` | Re-ejecutar SQL generado por el MCP (nunca SQL manual) |
| 9 | `profile_data` | EDA estadístico rápido |
| 10 | `propose_knowledge` | Proponer términos de negocio descubiertos |

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
- **Ejecución en paralelo**: Cuando el plan define múltiples preguntas de datos independientes (ninguna necesita el resultado de otra para formularse), lanzar TODAS las llamadas a `query_data` en una sola respuesta para que se ejecuten en paralelo. Aplica también a llamadas de metadata (`get_table_columns_details`, `profile_data`, etc.). Solo serializar cuando una query depende del resultado de otra (ej: necesitas un valor de la query A para formular la query B)

## 4. Workflow de Descubrimiento de Dominio

Pasos para explorar un dominio gobernado y entender sus datos antes de un análisis.

### 4.1 Descubrir Dominios

**Preferir buscar sobre listar** — `search_domains` devuelve resultados relevantes sin cargar la lista completa (que puede ser muy extensa).

Si el usuario proporciona un dominio o da pistas sobre el tema:
- Ejecutar `search_domains(nombre_o_pista)` para buscar coincidencias
- Si coincide con un resultado → usarlo directamente e ir al paso 4.2
- Si no hay coincidencias → ejecutar `list_domains()` como fallback y preguntar al usuario

Si no hay dominio claro, preguntar al usuario cuál le interesa. Si el usuario no da pistas, ejecutar `list_domains()` para mostrar todos los dominios disponibles (presentar como opciones seleccionables).

Si un dominio recién publicado o creado no aparece, reintentar con `refresh=true` (bypass de cache).

### 4.2 Explorar Tablas

1. `list_domain_tables(domain_name)` para listar todas las tablas del dominio
2. Presentar las tablas con sus descripciones en formato tabla markdown

### 4.3 Detalle de Tablas

Para las tablas de interés:
1. `get_tables_details(domain_name, table_names)` para obtener:
   - Descripción completa
   - Contexto de negocio
   - Términos de negocio asociados
   - Reglas de negocio
   - Comportamientos SQL
2. Presentar la información de forma estructurada

### 4.4 Columnas

Para cada tabla de interés:
1. `get_table_columns_details(domain_name, table_name)` para obtener nombre, tipo y descripción de negocio
2. Presentar en tabla markdown ordenada lógicamente

**Lanzar en paralelo** los pasos 4.3 y 4.4 cuando sean sobre tablas independientes. También lanzar paso 4.5 en paralelo si ya se conocen los términos a buscar.

### 4.5 Terminología de Negocio

`search_domain_knowledge(question, domain_name)` para buscar:
- Definiciones de términos de negocio
- Reglas de cálculo
- Políticas de datos
- Glosario del dominio

## 5. Perfilado Estadístico

Para las reglas de uso de `profile_data` (generar SQL con `generate_sql`, nunca SQL manual, usar parámetro `limit` en vez de LIMIT en SQL), ver sec 3.

Umbrales adaptativos de profiling según tamaño estimado:

| Filas estimadas | Estrategia | Parámetro limit |
|----------------|------------|-----------------|
| <100K | Completo | No configurar (default) |
| 100K - 1M | Muestreo | `limit=100000` |
| >1M | Muestreo + alerta | `limit=100000` + informar al usuario |

Documentar en reasoning si se usó muestreo.

## 6. Respuestas de Aclaración del MCP

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

## 7. Validación Post-Query

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

## 8. Timeouts y Reintentos

Si el MCP tarda demasiado o devuelve error:
1. **Simplificar la pregunta**: Reducir dimensiones o periodo temporal
2. **Dividir la query**: Partir una pregunta compleja en varias más simples
3. **Reformular**: Expresar la misma pregunta de forma diferente
4. No reintentar la misma pregunta más de 2 veces — si persiste, informar al usuario

## 9. Buenas Prácticas para Formular Preguntas

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
