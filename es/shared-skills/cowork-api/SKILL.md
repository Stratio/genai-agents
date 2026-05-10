---
name: cowork-api
description: "Sube, importa, despliega, publica, registra o envía bundles de agentes, skills o plugins a Stratio Cowork (`genai-api`). Úsala cuando el usuario pida subir/importar/desplegar/publicar/registrar el ZIP empaquetado de un agente, skill o plugin a Cowork — incluyendo frases como 'súbelo', 'deploy this', 'impórtalo', 'publica el agente', 'regístralo en Cowork', 'sube el plugin'. Llama a `/v1/agents/bundle/import` y `/v1/agents/skills/bundle/import` (los plugins reparten en ambos)."
---

# Skill: API de gestión de Stratio Cowork (`genai-api`)

Skill router. Cada capacidad vive en su propio fichero bajo `tasks/`. **Este fichero es deliberadamente mínimo** — cuando el agente necesite realizar una tarea concreta, debe cargar y seguir el sub-fichero correspondiente íntegro. No improvises la petición a partir de este índice.

## Prerrequisitos — leer primero

Antes de cualquier llamada, sigue `skills-guides/external-api-calls.md`:

- §1 lista las variables de entorno y rutas de certificados que provee el sandbox.
- §2 contiene el pre-check estándar (`preflight_external_api`). Ejecútalo; si falla, detente y reporta al usuario qué prerequisites faltan (variables de entorno o rutas de certificados) — la operación no puede continuar sin un entorno saludable. Traslada las piezas faltantes de forma explícita; no rechaces con un mensaje genérico.
- §3 y §4 son las plantillas de curl / Python. Cada tarea de abajo elige una y solo añade los detalles específicos del endpoint (path, campo multipart, query params).
- §5 es la tabla de errores que se debe usar al reportar fallos al usuario.

`GENAI_API_URL` (env var) es la URL base de la API. Todos los endpoints de abajo son relativos a ella.

## Índice de capacidades

| Capacidad | Cuándo usar | Sub-fichero a cargar |
|---|---|---|
| Subir un bundle de skill | El usuario tiene una skill empaquetada en ZIP y quiere registrarla en Stratio Cowork. | `tasks/upload-skill.md` |
| Subir un bundle de agente | El usuario tiene un agente empaquetado (ZIP contenedor `agents/v1`) y quiere registrarlo en Stratio Cowork. | `tasks/upload-agent.md` |
| Subir un bundle de plugin | El usuario tiene un plugin funcional empaquetado (ZIP envoltorio que contiene sub-ZIPs de agente y/o skill más un `plugin.yaml` agregado) y quiere registrarlo en Stratio Cowork. | `tasks/upload-plugin.md` |

## Reglas de routing

1. Identifica la capacidad a partir de la intención del usuario. Si ninguna entrada de arriba encaja, esta skill no puede ayudar — díselo.
2. Ejecuta el pre-check de `skills-guides/external-api-calls.md` §2. Si falla, detente y reporta.
3. Carga el sub-fichero que corresponda y síguelo de principio a fin. No mezcles instrucciones de varios sub-ficheros.
4. Tras la llamada, muestra al usuario el código HTTP y el cuerpo de la respuesta como se describe en `skills-guides/external-api-calls.md` §5.

## Añadir una nueva capacidad

Para extender esta skill con una nueva operación contra `genai-api`:

1. Crea `tasks/<capacidad>.md` con: cuándo usar, endpoint (método + path + content type), parámetros requeridos y opcionales, comando listo para ejecutar, respuesta esperada, casos de error específicos de ese endpoint.
2. Añade una entrada en el **Índice de capacidades** de arriba.
3. Replica ambos ficheros bajo `shared-skills/cowork-api/` (en su versión en inglés, raíz del repo).

El sub-fichero es la fuente de verdad de su capacidad. El índice de arriba solo enruta.
