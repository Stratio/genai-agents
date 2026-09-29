# Agente de Observabilidad y Evaluación

Agente que responde preguntas de usuario final sobre las trazas OpenTelemetry de la plataforma Stratio GenAI, consultando Grafana Tempo a través del proxy de datasources de Grafana. De solo lectura: únicamente peticiones `GET`, con las trazas como única fuente de datos.

## Estructura

```
observability-evaluation-agent/
├── AGENTS.md                          # Rol, flujo de trabajo, reglas de evidencia
├── opencode.json                      # Permisos (sin MCPs; allowlist granular de bash)
├── cowork-metadata.yaml               # Descripción + tags del bundle
├── USER_README.md                     # README de usuario final (pasa a ser el README.md del bundle)
└── skills/tempo-queries/              # Skill local: el recetario de queries
    ├── SKILL.md                       # Router + convenciones de query compartidas
    ├── references/vocabulary.md       # Mapa de servicios / spans / atributos / knobs
    └── tasks/
        ├── connect.md                 # Configuración del proxy de Grafana (una vez por sesión)
        ├── discover-schema.md         # Primitivas de tags / tag-values
        ├── cowork-usage.md            # Agentes usados, usuarios, sesiones por usuario
        ├── cowork-session.md          # Inspección de sesión + reconstrucción de conversación
        └── sql-chain.md               # Invocaciones de la chain SQL, errores, contenido de eval
```

## Configuración

| Variable de entorno | Propósito |
|---|---|
| `GRAFANA_URL` | URL base de Grafana (el agente pregunta al usuario y ofrece un default si no está definida) |
| `TEMPO_DATASOURCE_UID` | UID del datasource de Tempo (se descubre vía `/api/datasources` si no está definida) |

Sin MCPs y sin dependencias Python — las recetas usan `curl`, `jq` y `python3` de la imagen del sandbox.

## Empaquetado

```bash
bash pack_opencode.sh --agent observability-evaluation-agent [--lang es]
bash pack_stratio_cowork.sh --agent observability-evaluation-agent [--lang es]
```

## Notas para mantenedores

- Las recetas de queries se validaron en vivo contra un despliegue `grafana/otel-lgtm` (Tempo 2.x, Grafana 13). Detalles de la API de Tempo que tienden a cambiar: la ruta del proxy de datasources (`/api/datasources/proxy/uid/...` vs `.../resources/...`), el tope de rango del endpoint de métricas y el soporte de `select()` en TraceQL.
- `references/vocabulary.md` refleja las convenciones de instrumentación de la plataforma. Cuando la instrumentación cambie (atributos nuevos, la migración guiones→puntos completada, adopción de la semconv MCP), actualízalo — el agente tiene instrucciones de fiarse del esquema vivo por encima del mapa, pero el mapa guía sus primeras queries.
