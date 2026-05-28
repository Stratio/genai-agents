# Patrones de Respuesta de los MCPs de Stratio

Compañera de `stratio-data-tools.md` (MCPs de datos) y `stratio-semantic-layer-tools.md` (MCPs de gobierno). Leerla junto con la que tengas cargada — este documento describe dos patrones de respuesta que pueden ocurrir en cualquier tool MCP de las listadas allí: polling de tareas de larga duración y manejo de salidas que superan el límite de respuesta del entorno anfitrión. Ambos son ortogonales a la tool específica y al servidor donde vive.

## 1. Polling de Tareas de Larga Duración

Cualquier tool MCP puede tardar más de lo esperado en completarse. Cuando esto ocurre, el servidor MCP devuelve una respuesta con un `task_id` en lugar de los datos que la tool produciría en su modo normal. Esto no es un error — la operación sigue ejecutándose en segundo plano y el resultado se puede obtener después.

**Antes de hacer polling, verificar ambas cosas:**

- **Origen** — la respuesta viene **directamente** de una llamada a una tool MCP de Stratio. Un `task_id` anidado dentro del `result` de un subagente, en la salida de un hook o en cualquier otro envoltorio que no sea MCP pertenece al runtime del host, no al MCP. Falso positivo típico: un subagente que falla y devuelve un `result` vacío con su propio id tipo `ses_xxxxxxxx` — tratar como fallo del subagente, no hacer polling.
- **Prefijo** — un `task_id` de Stratio **siempre empieza por `mcp-ckpt-`** (seguido de 16 caracteres hex, p. ej. `mcp-ckpt-7c3e1f0a9b224e3d`). Valores como `ses_*`, UUIDs pelados o `task_*` no son task_ids de Stratio — **no** llamar a `get_mcp_task_result` con ellos.

Si falla cualquiera de los dos checks, no hacer polling: procesar la respuesta tal cual o manejar el fallo upstream.

**Protocolo cuando ambos checks pasan:**

1. Llamar a `get_mcp_task_result(task_id=<el task_id recibido>)` en el **mismo servidor MCP que emitió el `task_id`**. Si el entorno anfitrión expone más de un servidor (p. ej. `gov` y `sql`), mezclar servidores devolverá `not_found` incluso para task ids válidos. No introducir esperas explícitas entre llamadas — emitir el siguiente poll en cuanto se haya procesado la respuesta anterior.
2. Inspeccionar el campo `status`:
   - `"pending"` — la tarea sigue ejecutándose. Llamar de nuevo inmediatamente. Repetir hasta que el estado cambie
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
1. **Nunca leas el fichero guardado completo en tu propio contexto.** Disparará el mismo límite que provocó la truncación.
2. **Delega la inspección del fichero al subagente del runtime** (p. ej. `explore` de OpenCode vía la tool Task) para preservar tu propio contexto. El subagente NO ve la conversación padre — solo ve el prompt que tú escribes. El prompt DEBE incluir:
   - **La ruta completa del fichero guardado, copiada literalmente del aviso de truncación.** No parafrasees. No pidas al subagente que busque el fichero con `Glob` — si tiene que adivinar, puede fallar y devolverte un error. Pega la ruta absoluta exactamente como aparece en el hint del runtime.
   - **El objetivo de extracción**: qué extraer (inventario, subconjunto temático, registro concreto) y qué devolver (p. ej. una lista markdown de nombres de tablas que coinciden con X).
   - **Un recordatorio de devolver solo el fragmento extraído**, no el fichero completo.
   - **Si el fichero guardado es un payload JSON minificado en una sola línea** — la forma habitual de los outputs de los MCPs de Stratio — dile explícitamente al subagente que las herramientas line-based (`Grep` cuenta matches por línea, `Read` trunca cada línea a un tope fijo de caracteres no configurable en OpenCode) no le servirán. Indícale que use un parser estructural vía Bash: `jq` para consultas one-shot (p. ej. `jq '.tables | length'`, `jq '.tables[:20] | .[].name'`), o un script Python corto para extracciones más ricas (el sandbox lleva Python con la librería estándar `json` — el subagente puede ejecutar un `python -c '...'` inline o guardar un script breve).

   Deja el resto del *cómo* al subagente — es un especialista en búsqueda de ficheros y elegirá las primitivas adecuadas dentro de los límites de arriba. No embebas patrones regex más allá de lo necesario para transmitir el objetivo.

   Ejemplo de prompt bueno:
   > "Inspecciona el fichero guardado en `<ruta-completa-del-aviso-de-truncación>`. El fichero es un payload JSON minificado en una sola línea, así que usa `jq` (o un script Python corto inline) vía Bash en lugar de herramientas line-based. Extrae un subconjunto temático: solo las entradas de tabla cuyo nombre contenga 'customer'. Devuelve una lista markdown con los nombres coincidentes — no devuelvas el contenido del fichero."

3. **Si el subagente devuelve "file not found" o "permission denied"** sobre la ruta guardada, NO reintentes y NO vuelvas a delegar. Procesa el fichero tú mismo en esta conversación con topes estrictos: primero `Grep` para patrones concretos, luego `Read` con `offset` y `limit` pequeño (≤ 200 líneas por llamada). Nunca leas de extremo a extremo en una sola llamada.
4. **Si `Grep`/`Read` en la sesión principal también fallan**, comunica la limitación al usuario y reformula la query MCP con un alcance más estrecho (filtros adicionales, `domain_type`, palabra clave más acotada) en lugar de entrar en bucle. Nunca preguntes lo mismo al usuario dos veces.
5. **Iterar por necesidad**: la primera pasada extrae un inventario (identificadores, nombres, conteos); pasadas posteriores recuperan registros completos bajo demanda. Para en cuanto la pregunta del usuario quede respondida.

**Objetivos típicos de extracción** para payloads tipo listado (formula uno de estos al subagente, o aplícalo en el fallback):
- _Inventario_: identificadores / nombres / conteo de entradas.
- _Subconjunto temático_: solo entradas que coincidan con las palabras clave del usuario.
- _Registro concreto_: una sola entrada por identificador, con contexto alrededor si es útil.
- _Muestra_: primeras N entradas para inspeccionar la estructura antes de decidir el objetivo.

Aplica a cualquier tool que pueda devolver payloads grandes. En el lado de datos, los casos comunes incluyen `list_domain_tables`, `list_domains`, `get_tables_details` sobre muchas tablas y `query_data` sobre resultados anchos/largos. En el lado de gobierno, los casos comunes incluyen `list_business_views`, `list_technical_domain_concepts`, `search_data_dictionary` y cualquier tool `*_details` sobre catálogos grandes.
