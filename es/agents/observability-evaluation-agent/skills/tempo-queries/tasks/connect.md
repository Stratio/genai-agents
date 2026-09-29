# Task: conectar a Grafana Tempo

Construye la URL base que usan todas las demás tasks. Las trazas viven en **Grafana Tempo** (típicamente parte de un despliegue `grafana/otel-lgtm`). El puerto propio de Tempo no está expuesto; se llega a él a través del **proxy de datasources de Grafana**. No hay autenticación configurada — no envíes credenciales.

## Entradas

| Variable | Descripción |
|---|---|
| `GRAFANA_URL` | URL base de Grafana. Si no está definida, propón el default de abajo y confírmalo con el usuario. |
| `TEMPO_DATASOURCE_UID` | UID del datasource de Tempo (opcional — descúbrelo si no está definida). |

Backend por defecto a ofrecer: `http://lgtm.s000001-genaiobserv:3000`

## Procedimiento (una vez por sesión)

1. **Resuelve la URL de Grafana**:
   - Tómala de `GRAFANA_URL`, o de la petición del usuario si la dio ahí.
   - Si no hay ninguna de las dos, **pregunta al usuario antes de conectar** (convención de preguntas): ofrece el default de arriba y deja que lo confirme o aporte otra. No conectes al default en silencio y nunca inventes una tercera URL propia.

2. **Health check**:

   ```bash
   GRAFANA_URL="${GRAFANA_URL%/}"
   curl -sS --connect-timeout 5 --max-time 15 "${GRAFANA_URL}/api/health"
   ```

   Esperado: JSON con `"database": "ok"`. Si falla, informa del fallo y pide al usuario confirmar la URL en lugar de reintentar variaciones.

3. **Resuelve el UID del datasource de Tempo**:
   - Si `TEMPO_DATASOURCE_UID` está definida, úsala.
   - En caso contrario:

     ```bash
     curl -sS --connect-timeout 5 --max-time 15 "${GRAFANA_URL}/api/datasources" \
       | jq -r '.[] | select(.type == "tempo") | .uid'
     ```

   - Si vuelven varios UIDs, pregunta al usuario cuál usar. Si ninguno, informa de que esa instancia de Grafana no tiene datasource de Tempo y para.

4. **Construye la base del proxy** y reutilízala toda la sesión:

   ```bash
   PROXY="${GRAFANA_URL}/api/datasources/proxy/uid/${UID}"
   ```

5. **Prueba de humo** (confirma además que la ruta del proxy funciona en esta versión de Grafana):

   ```bash
   NOW=$(date +%s); START=$((NOW - 3600))
   curl -sS -G "${PROXY}/api/v2/search/tags" \
     --data-urlencode "scope=resource" \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
   ```

   Esperado: una lista JSON `scopes` que contenga `service.name`.

## Rutas de la API de Tempo (se añaden a `{PROXY}` sin cambios)

```
GET {PROXY}/api/v2/search/tags?scope=<resource|span>&start=&end=
GET {PROXY}/api/v2/search/tag/{scope.tag}/values?q=&start=&end=
GET {PROXY}/api/search?q={TraceQL}&start=&end=&limit=&spss=
GET {PROXY}/api/traces/{traceID}
GET {PROXY}/api/metrics/query_range?q=&start=&end=
```

## Gestión de errores

| Síntoma | Significado / acción |
|---|---|
| `401` o una redirección a una página de login | El acceso anónimo no está habilitado en este Grafana. Infórmalo y para — esta skill no envía credenciales. |
| `404` / `405` en la ruta del proxy | Prueba la ruta alternativa `{GRAFANA_URL}/api/datasources/uid/{UID}/resources/{path}` — existen ambas formas según la versión de Grafana. |
| Conexión rechazada / timeout | URL incorrecta o network policy. Muestra el error exacto y pide al usuario confirmar la URL. |
| `response larger than the max` en `/api/traces/{id}` | La traza supera el límite de mensaje gRPC del backend — un asunto de tuning del backend, no un error de la query. Infórmalo y recurre a `search` + proyecciones `select()` para esa traza. |

Muestra siempre al usuario el código HTTP y el cuerpo de la respuesta literal cuando una llamada falle.
