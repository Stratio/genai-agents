# Task: actividad de la chain SQL

Responde preguntas sobre la chain SQL de "habla con tus datos" a partir de trazas: invocaciones, errores, latencia, llamadas a servicios de plataforma y contenido de turnos para evaluación.

Necesita `{PROXY}` (ver `tasks/connect.md`) y una ventana:

```bash
NOW=$(date +%s); START=$((NOW - 86400))
```

Las chains se ejecutan como servicios trazados propios. La chain SQL agrega bajo `resource.service.name = "genai-chain-sql"` independientemente de cuántos despliegues existan; cada despliegue se distingue por `resource.service.instance.id` (el id de despliegue de la chain). Antes de nada, confirma que la señal existe en la ventana (`tasks/discover-schema.md`, primitiva 1) — que falte el servicio significa que la chain estuvo ociosa o su trazado está apagado, no que las recetas estén mal.

## Recetas

### 1. Invocaciones de la chain (los turnos de evaluación de la chain)

Un span `invoke_workflow` por invocación de la chain — el equivalente del lado chain al `invoke_agent` de Cowork:

```bash
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode 'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" } | select(span.gen_ai.workflow.name, span.gen_ai.conversation.id, span.stratio.genai.chat.id)' \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
  --data-urlencode "limit=100" --data-urlencode "spss=5"
```

- `gen_ai.conversation.id` = el id de chat — **presente solo cuando la invocación pertenece a una conversación**; la plataforma nunca fabrica un id de relleno, así que las invocaciones sueltas carecen de él legítimamente.
- Restringe a un despliegue con `&& resource.service.instance.id = "<id de despliegue de la chain>"`.

### 2. Una conversación de punta a punta

El id de chat vive en dos familias de atributos: `stratio.genai.chat.id` (spans del frontend y de la chain) y `gen_ai.conversation.id` (spans de operación GenAI). Consulta ambas para obtener el camino completo:

```bash
CHAT="<chat_id>"
curl -sS -G "${PROXY}/api/search" \
  --data-urlencode "q={ span.stratio.genai.chat.id = \"${CHAT}\" || span.gen_ai.conversation.id = \"${CHAT}\" }" \
  --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" --data-urlencode "limit=100"
```

Solo el subconjunto del lado GenAI: `{ span.gen_ai.conversation.id = "<chat_id>" }`. Los spans del hub backend en esas trazas no llevan id de chat — solo atributos con guiones de usuario/tenant/request (ver la nota puntos-vs-guiones en `references/vocabulary.md`) — así que los filtros por usuario sobre spans del hub necesitan la grafía con guiones.

### 3. Errores y latencia

```bash
# invocaciones fallidas
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" && status = error }'
# invocaciones lentas
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" && duration > 10s }'
```

Profundiza en una traza coincidente (`{PROXY}/api/traces/<traceID>`) para localizar *dónde* se fue el tiempo o dónde surgió el error: los spans hijos de servicios de plataforma se llaman `<servicio>.<operación>` (`governance.get_glossary_items`, `virtualizer.run_sql_command`, `opensearch.search_filter_values`, ...) con `peer.service` fijado, más spans cliente httpx hacia el gateway LLM.

### 4. Invocaciones de la chain por reentrada MCP

Cuando la chain se usa como tool MCP (por un agente) en lugar de vía chat, la ejecución de la tool es el padre del workflow:

```bash
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "execute_tool" } | select(span.gen_ai.tool.name)'
```

### 5. Contenido de turnos para evaluación

Mismo mecanismo que los turnos de Cowork — el contenido vive en el span `invoke_workflow` cuando la captura de contenido de evaluación está encendida en el despliegue de la chain:

```bash
'q={ resource.service.name = "genai-chain-sql" && span.gen_ai.operation.name = "invoke_workflow" && span.gen_ai.conversation.id = "<chat_id>" } | select(span.gen_ai.input.messages, span.gen_ai.output.messages)'
```

Atributos de contenido ausentes ⇒ la captura está apagada en ese despliegue (tabla de knobs en `references/vocabulary.md`); informa del esqueleto y dilo.

## Caveats

- **Señal dependiente del despliegue.** El trazado de las chains tiene su propio gate en cada despliegue de chain; los spans de nodo de LangChain/LangGraph y las trazas de refresco en segundo plano están además gateados por knob y **apagados por defecto**. Su ausencia es lo esperado, no un hallazgo — consulta la tabla de knobs antes de reportar un hueco.
- **La identidad del usuario vive en el server span** de la invocación de la chain (`stratio.genai.user.id` en spans tipo `POST /invoke`), no en el propio `invoke_workflow`; los server spans del hub backend en la misma traza llevan las variantes con guiones.
- **Las filas de `query_result` no se capturan nunca** en spans, por diseño. El texto SQL puede aparecer en el contenido capturado; los valores de datos no deberían — márcalo si los ves.
- Las trazas con la instrumentación de LangChain habilitada pueden superar los 300 spans; usa proyecciones `select()` en lugar de descargar esas trazas enteras cuando solo necesites atributos.
