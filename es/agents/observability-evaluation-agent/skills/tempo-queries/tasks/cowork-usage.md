# Task: preguntas de uso de Cowork

Responde preguntas de "quién usó qué" sobre Stratio Cowork a partir de trazas: qué agentes se usaron, qué usuarios estuvieron activos, cuántas sesiones tuvo cada usuario, qué proyectos/sandboxes se ejecutaron.

Todas las recetas necesitan `{PROXY}` (ver `tasks/connect.md`) y una ventana temporal:

```bash
NOW=$(date +%s); START=$((NOW - 86400))   # acuerda primero la ventana con el usuario
```

## Recetas

### 1. Qué agentes de Cowork se han usado

Cada turno de agente es un span `invoke_agent`; `gen_ai.agent.name` lleva el nombre del agente:

```bash
curl -sS -G "${PROXY}/api/v2/search/tag/span.gen_ai.agent.name/values" \
  --data-urlencode 'q={ span.gen_ai.operation.name = "invoke_agent" }' \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

> **Nota de honestidad — usados vs desplegados.** Las trazas muestran los agentes que *se ejecutaron* en la ventana. El inventario de agentes *desplegados* vive en el backend de administración de la plataforma, no en Tempo. Si el usuario pregunta "cuántos agentes hay desplegados", responde la pregunta de uso e indica esta limitación explícitamente.

### 2. Qué usuarios estuvieron activos en Cowork

`stratio.genai.user.id` lo estampa el **frontend web** (spans RUM con `stratio.genai.app = "cowork"`), no el runtime del agente:

```bash
curl -sS -G "${PROXY}/api/v2/search/tag/span.stratio.genai.user.id/values" \
  --data-urlencode 'q={ span.stratio.genai.app = "cowork" }' \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

> Los usuarios llegan a la plataforma por su navegador; un cliente headless que evite la UI web no deja spans RUM y es invisible para esta receta. Dilo si los totales parecen sospechosamente bajos.

### 3. Sesiones de un usuario

El puente usuario↔sesión también es el frontend: los spans del navegador llevan a la vez `stratio.genai.user.id` y `stratio.genai.opencode.session.id` (los spans del runtime del agente **no** llevan el id de usuario — ver el caveat de abajo):

```bash
USER_ID="<usuario>"
curl -sS -G "${PROXY}/api/v2/search/tag/span.stratio.genai.opencode.session.id/values" \
  --data-urlencode "q={ span.stratio.genai.user.id = \"${USER_ID}\" }" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

Cuenta los valores para "cuántas sesiones"; pasa cada id `ses_*` a `tasks/cowork-session.md` para "qué pasó en ellas".

Para **sesiones por usuario de todos los usuarios**, itera la receta 3 sobre los usuarios de la receta 2 (son pocos) — una llamada de tag-values filtrada por usuario es más barata y fiable que descargar trazas y agregar en cliente.

### 4. Qué proyectos / sandboxes se ejecutaron

Cowork ejecuta un sandbox por proyecto; sus spans llevan el id del proyecto:

```bash
curl -sS -G "${PROXY}/api/v2/search/tag/span.stratio.genai.project.id/values" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
```

La identidad del despliegue del sandbox también es visible como valores de `resource.service.instance.id` con prefijo `genai-project-`.

### 5. Conteos de turnos / tasas de actividad

- Ventanas pequeñas (≤ 3 h): el endpoint de métricas TraceQL puede agregar en servidor:

  ```bash
  curl -sS -G "${PROXY}/api/metrics/query_range" \
    --data-urlencode 'q={ span.gen_ai.operation.name = "invoke_agent" } | rate() by (span.gen_ai.agent.name)' \
    --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
  ```

  El backend rechaza rangos por encima de su máximo configurado (típicamente 3 h) — recurre a la siguiente opción cuando lo haga.

- Cualquier ventana: búsqueda con proyección y conteo en cliente:

  ```bash
  curl -sS -G "${PROXY}/api/search" \
    --data-urlencode 'q={ span.gen_ai.operation.name = "invoke_agent" } | select(span.gen_ai.agent.name, span.gen_ai.conversation.id, span.stratio.genai.opencode.turn.origin)' \
    --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
    --data-urlencode "limit=200" --data-urlencode "spss=10" | jq '[.traces[]] | length'
  ```

  Indica el `limit` usado; si el resultado lo alcanza, el conteo es una cota inferior — dilo.

## Caveats

- **Usuario↔turno no puede unirse dentro de una sola query TraceQL.** La traza del navegador (que conoce al usuario) y la traza del turno del agente son *trazas distintas*, cosidas por span links — no por parentesco. El puente fiable son los atributos compartidos (`stratio.genai.opencode.session.id`, `stratio.genai.message.id`) presentes en ambos lados, como en la receta 3.
- **Filtra los turnos lazy al contar actividad real de usuario**: los turnos con `stratio.genai.opencode.turn.origin = "lazy"` son mantenimiento interno del LLM (título/resumen/compactación), no mensajes del usuario. La proyección de la receta 5 incluye el atributo para poder separar los conteos.
- Las respuestas de tag-values son conjuntos deduplicados — buenos para "cuáles/cuántos distintos", inútiles para frecuencias. Usa la receta 5 para frecuencias.
