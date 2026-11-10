# Task: descubrir el esquema de trazas

Lista qué servicios, nombres de span y atributos existen realmente en el backend para una ventana temporal. Ejecuta esto antes de asumir cualquier convención de atributos, y siempre que una query devuelva vacío inesperadamente.

## Queries

Todas requieren `start`/`end` (segundos Unix). **Sin rango temporal Tempo responde solo con los bloques recientes y el resultado parece completo sin serlo** — no te fíes nunca de una query de tags sin rango.

```bash
NOW=$(date +%s); START=$((NOW - 86400))   # ajusta la ventana a la pregunta
```

1. **Qué servicios están emitiendo**:

   ```bash
   curl -sS -G "${PROXY}/api/v2/search/tag/resource.service.name/values" \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" | jq -r '.tagValues[].value'
   ```

2. **Qué atributos existen** (por scope):

   ```bash
   curl -sS -G "${PROXY}/api/v2/search/tags" \
     --data-urlencode "scope=span" \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
   # scope=resource para atributos de resource
   ```

3. **Valores de un atributo**, opcionalmente filtrados por una condición TraceQL (`q`) — es la primitiva de agregación más barata disponible; úsala antes de escribir bucles de búsqueda:

   ```bash
   curl -sS -G "${PROXY}/api/v2/search/tag/span.gen_ai.operation.name/values" \
     --data-urlencode 'q={ resource.service.name = "genai-litellm" }' \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
   ```

   El tag de la ruta va con scope (`resource.x` o `span.x`). El filtro `q` restringe los valores a spans que cumplan la condición.

4. **Muestreo de spans con atributos proyectados** (para ver valores reales lado a lado):

   ```bash
   curl -sS -G "${PROXY}/api/search" \
     --data-urlencode 'q={ resource.service.name = "<svc>" } | select(span.gen_ai.operation.name, name)' \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}" \
     --data-urlencode "limit=20" --data-urlencode "spss=5"
   ```

## Interpretación

- **Indica la convención que encontraste.** La plataforma mezcla varias: semconv GenAI de OTel (`gen_ai.*`), atributos de plataforma (`stratio.genai.*`), atributos vendor (`litellm.*`), más la semconv HTTP. `references/vocabulary.md` mapea quién emite qué — fíate del esquema vivo por encima del mapa cuando discrepen.
- **Espera ruido de tags del gateway LLM**: `genai-litellm` aporta cientos de tags de span de la forma `llm.request.functions.<N>.*` y `gen_ai.tool.<N>.*` (uno por slot de tool por petición). Ignóralos a efectos de esquema.
- **Un resultado vacío tiene cuatro explicaciones candidatas** — compruébalas en este orden antes de concluir "no se ejecutó": (1) ventana incorrecta, (2) grafía del atributo incorrecta (ver la nota puntos-vs-guiones del vocabulario), (3) un knob de captura/señal apagado en el despliegue observado (tabla de knobs del vocabulario), (4) el código realmente nunca se ejecutó.
- Los listados de tags son datos, no garantías: un tag aparece si al menos un span de la ventana lo lleva — no dice nada de qué servicio lo emitió. Confirma la propiedad con una query de valores filtrada (primitiva 3) o un muestreo de búsqueda (primitiva 4).
