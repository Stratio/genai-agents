# Task: connect to Grafana Tempo

Build the base URL used by every other task. Traces live in **Grafana Tempo** (typically part of a `grafana/otel-lgtm` deployment). Tempo's own port is not exposed; you reach it through **Grafana's datasource proxy**. No authentication is configured — send no credentials.

## Inputs

| Variable | Description |
|---|---|
| `GRAFANA_URL` | Grafana base URL. If unset, propose the default below and confirm with the user. |
| `TEMPO_DATASOURCE_UID` | Tempo datasource UID (optional — discover it if unset). |

Default backend to offer: `http://lgtm.s000001-genaiobserv:3000`

## Procedure (once per session)

1. **Resolve the Grafana URL**:
   - Take it from `GRAFANA_URL`, or from the user's request if they gave one there.
   - If neither is present, **ask the user before connecting** (question convention): offer the default above and let them confirm it or supply a different one. Do not connect to the default silently, and never invent a third URL of your own.

2. **Health check**:

   ```bash
   GRAFANA_URL="${GRAFANA_URL%/}"
   curl -sS --connect-timeout 5 --max-time 15 "${GRAFANA_URL}/api/health"
   ```

   Expected: JSON with `"database": "ok"`. If it fails, report the failure and ask the user to confirm the URL rather than retrying variations of it.

3. **Resolve the Tempo datasource UID**:
   - If `TEMPO_DATASOURCE_UID` is set, use it.
   - Otherwise:

     ```bash
     curl -sS --connect-timeout 5 --max-time 15 "${GRAFANA_URL}/api/datasources" \
       | jq -r '.[] | select(.type == "tempo") | .uid'
     ```

   - If several UIDs come back, ask the user which one to use. If none, report that the Grafana instance has no Tempo datasource and stop.

4. **Build the proxy base** and reuse it for the whole session:

   ```bash
   PROXY="${GRAFANA_URL}/api/datasources/proxy/uid/${UID}"
   ```

5. **Smoke test** (also confirms the proxy route works on this Grafana version):

   ```bash
   NOW=$(date +%s); START=$((NOW - 3600))
   curl -sS -G "${PROXY}/api/v2/search/tags" \
     --data-urlencode "scope=resource" \
     --data-urlencode "start=${START}" --data-urlencode "end=${NOW}"
   ```

   Expected: a JSON `scopes` list containing `service.name`.

## Tempo API paths (appended to `{PROXY}` unchanged)

```
GET {PROXY}/api/v2/search/tags?scope=<resource|span>&start=&end=
GET {PROXY}/api/v2/search/tag/{scope.tag}/values?q=&start=&end=
GET {PROXY}/api/search?q={TraceQL}&start=&end=&limit=&spss=
GET {PROXY}/api/traces/{traceID}
GET {PROXY}/api/metrics/query_range?q=&start=&end=
```

## Error handling

| Symptom | Meaning / action |
|---|---|
| `401` or a redirect to a login page | Anonymous access is not enabled on this Grafana. Report it and stop — this skill sends no credentials. |
| `404` / `405` on the proxy route | Try the alternative route `{GRAFANA_URL}/api/datasources/uid/{UID}/resources/{path}` — both forms exist depending on the Grafana version. |
| Connection refused / timeout | Wrong URL or network policy. Surface the exact error and ask the user to confirm the URL. |
| `response larger than the max` on `/api/traces/{id}` | The trace exceeds the backend's gRPC message limit — a backend tuning issue, not a query mistake. Report it and fall back to `search` + `select()` projections for that trace. |

Always show the user the HTTP status and the response body verbatim when a call fails.
