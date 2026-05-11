# cowork-api

Skill compartida que envuelve la API REST de gestión de Stratio Cowork (`genai-api`) para que otras skills y agentes puedan registrar, desplegar y gestionar skills y agentes directamente desde dentro del sandbox de Stratio sin el rodeo manual de descargar y subir vía la UI web.

Diseñada como **router**: un `SKILL.md` mínimo lista las capacidades disponibles y apunta a un fichero autocontenido por capacidad bajo `tasks/`. Los nuevos endpoints se añaden creando un fichero más en esa carpeta — el índice crece linealmente sin inflar el punto de entrada.

## Qué hace

Hoy:

- **Subir un bundle de skill** — `POST /v1/agents/skills/bundle/import` con un ZIP multipart. Soporta estrategias de `on_conflict` (`new_version`, `overwrite`, `fail`) y una versión semántica explícita opcional.
- **Subir un bundle de agente** — `POST /v1/agents/bundle/import` con un ZIP contenedor `agents/v1` multipart. Lee `name` del `metadata.yaml` del bundle. Soporta las mismas estrategias de `on_conflict`.

Mañana (puntos de extensión): listar/exportar versiones, publicar versiones draft, gestionar proyectos, registrar servidores MCP, grupos de modelos — cualquier cosa que la superficie REST de `genai-api` exponga.

## Cuándo usar

Carga esta skill cuando el agente necesite **llamar al plano de gestión de Cowork** desde dentro del sandbox de Stratio: registrar una skill o un agente recién empaquetado, consultar o mutar su ciclo de vida, etc.

Esta skill **no** es para acceso a datos en runtime (eso son las MCPs `stratio_data` / `stratio_gov`) **ni** para llamadas a modelos vía LiteLLM (eso pasa por el proxy interno en `127.0.0.1:3002`, no por `genai-api`).

## Guías compartidas

- `external-api-calls.md` — declarada en `guides`. Cubre las env vars (`GENAI_API_URL`, `USER_CERT_PATH`, `USER_KEY_PATH`, `CA_CERT_PATH`), el pre-check estándar y las plantillas curl/Python sobre las que se apoya esta skill. Cada sub-fichero bajo `tasks/` la referencia para los aspectos transversales (mTLS, manejo de errores).

## MCPs

Ninguno. Esta skill habla directamente con `genai-api` por HTTPS con mTLS — no interviene ningún servidor MCP.

## Dependencias Python

Ninguna para las plantillas que se entregan (todo es bash + curl). Si un caller prefiere Python, las plantillas en `external-api-calls.md` usan `requests` o `httpx`, ambos ya presentes en `/opt/venv` dentro del sandbox.

## Dependencias del sistema

- `curl` — presente en la imagen del sandbox.
- `~/.curlrc` se autogenera al arrancar el sandbox con el cert/key del cliente, así que un `curl` plano ya negocia mTLS; aun así esta skill añade `--cert`, `--key` y `--cacert` explícitamente para que el mismo script funcione también fuera del sandbox si las env vars están definidas.

## Notas

- Todos los endpoints son relativos a `${GENAI_API_URL%/}`. La skill espera que esa variable esté definida; si no, el pre-check detiene la llamada con elegancia.
- La autenticación es solo mTLS. La identidad del certificado del usuario también dirige la autorización RBAC/whitelist en el servidor — una respuesta 401/403 significa que el rol del usuario no permite la operación; muestra el cuerpo tal cual para que el rol que falta sea visible.
- Esta skill nunca reintenta en silencio. Una llamada fallida se reporta al caller con código HTTP y cuerpo; decidir si se reintenta es responsabilidad del caller.
