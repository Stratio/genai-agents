# Patrones de Respuesta de los MCPs de Stratio

Compañera de `stratio-data-tools.md` (MCPs de datos) y `stratio-semantic-layer-tools.md` (MCPs de gobierno). Leerla junto con la que tengas cargada — este documento describe dos patrones de respuesta que pueden ocurrir en cualquier tool MCP de las listadas allí: polling de tareas de larga duración y manejo de salidas que superan el límite de respuesta del entorno anfitrión. Ambos son ortogonales a la tool específica y al servidor donde vive.

## 1. Polling de Tareas de Larga Duración

Cualquier tool MCP puede tardar más de lo esperado en completarse. Cuando esto ocurre, el servidor MCP devuelve una respuesta con un `task_id` en lugar de los datos que la tool produciría en su modo normal. Esto no es un error — la operación sigue ejecutándose en segundo plano y el resultado se puede obtener después.

**Antes de hacer polling, verificar ambas cosas:**

- **Origen** — la respuesta viene **directamente** de una llamada a una tool MCP de Stratio. Un `task_id` anidado dentro del `result` de un subagente, en la salida de un hook o en cualquier otro envoltorio que no sea MCP pertenece al runtime del host, no al MCP. Falso positivo típico: un subagente que falla y devuelve un `result` vacío con su propio id tipo `ses_xxxxxxxx` — tratar como fallo del subagente, no hacer polling.
- **Prefijo** — un `task_id` de Stratio **siempre empieza por `mcp-ckpt-`** (seguido de 16 caracteres hex, p. ej. `mcp-ckpt-7c3e1f0a9b224e3d`). Valores como `ses_*`, UUIDs pelados o `task_*` no son task_ids de Stratio — **no** llamar a `get_mcp_task_result` con ellos.

Si falla cualquiera de los dos checks, no hacer polling: procesar la respuesta tal cual o manejar el fallo upstream.

**Protocolo cuando ambos checks pasan:**

1. Esperar **5 segundos**
2. Llamar a `get_mcp_task_result(task_id=<el task_id recibido>)` en el **mismo servidor MCP que emitió el `task_id`**. Si el entorno anfitrión expone más de un servidor (p. ej. `gov` y `sql`), mezclar servidores devolverá `not_found` incluso para task ids válidos.
3. Inspeccionar el campo `status`:
   - `"pending"` — la tarea sigue ejecutándose. Esperar **10 segundos** y llamar de nuevo. Repetir hasta que el estado cambie
   - `"done"` — el campo `result` contiene la respuesta original de la tool. Parsear y usar como si la tool la hubiera devuelto directamente
   - `"error"` — leer `error` y aplicar la estrategia de reintento que indique la guía que invoca este patrón (p. ej. simplificar, dividir, reformular) o informar al usuario
   - `"not_found"` — el task_id ha expirado o es desconocido. Reintentar la llamada original a la tool desde cero

Aplica a TODAS las tools MCP de cualquier servidor de Stratio.

## 2. Salidas de Tools de Gran Tamaño — Truncadas y Guardadas en Fichero

Cuando la salida inline de una tool superaría el límite de respuesta del entorno anfitrión, la respuesta se sustituye por un aviso de truncación y la ruta de un fichero donde se escribió el contenido completo. Los datos están ahí — la tool tuvo éxito — pero ya no son inline. Esto es **distinto de §1** (donde la respuesta es un `task_id` porque la tool sigue ejecutándose): aquí el trabajo ya está hecho; allí sigue pendiente.

**Detección** (cualquiera de):
- La respuesta contiene un marcador de truncación explícito (p. ej. `…N bytes truncated…`, "output was truncated", "Full output saved to ...") y una ruta de fichero
- La respuesta lleva una ruta de fichero guardado y no hay campo `task_id`

**Protocolo** (aplicar en orden):
1. **Nunca leas el fichero guardado completo en tu propio contexto.** Disparará el mismo límite que provocó la truncación
2. **Preferir delegar la inspección del fichero a un subagente** cuando el entorno anfitrión exponga uno (p. ej. un subagente Explore / Task). Indícale al subagente la ruta del fichero y la extracción concreta a realizar, y pídele que devuelva solo el fragmento que necesitas — no el contenido del fichero
3. **Si no hay delegación a subagente disponible**, inspecciona el fichero tú mismo con topes estrictos: primero `Grep` para patrones concretos, luego `Read` con `offset` y `limit` pequeño (≤ 200 líneas por llamada). Nunca leas de extremo a extremo en una sola llamada
4. **Iterar por necesidad**: una primera pasada suele extraer un inventario (identificadores, nombres, conteos); pasadas posteriores recuperan registros completos bajo demanda. Para en cuanto la pregunta del usuario quede respondida

**Patrones típicos de extracción** para payloads tipo listado:
- _Inventario_: `Grep` por la clave JSON que delimita cada entrada (p. ej. `"name":`) y cuenta / lista las coincidencias
- _Subconjunto temático_: `Grep` por palabras clave de la pregunta del usuario sobre el fichero guardado
- _Registro concreto_: `Grep` por el identificador, luego `Read` ±N líneas alrededor de la coincidencia para obtener el contexto
- _Muestra_: `Read` con `offset=0`, `limit=200` para inspeccionar la estructura antes de lanzar lecturas más dirigidas

Aplica a cualquier tool que pueda devolver payloads grandes. En el lado de datos, los casos comunes incluyen `list_domain_tables`, `list_domains`, `get_tables_details` sobre muchas tablas y `query_data` sobre resultados anchos/largos. En el lado de gobierno, los casos comunes incluyen `list_business_views`, `list_technical_domain_concepts`, `search_data_dictionary` y cualquier tool `*_details` sobre catálogos grandes.
