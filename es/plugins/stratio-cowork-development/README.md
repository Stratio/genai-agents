# Plugin Stratio Cowork Development

Vertical de desarrollo de agentes AI para Stratio Cowork. Empaqueta los dos agentes constructores que permiten a los usuarios diseñar y generar nuevos agentes y skills directamente desde la plataforma.

## Qué incluye

| Agente | Propósito |
|---|---|
| [agent-creator](../../agents/agent-creator/) | Diseña y genera agentes AI completos para Stratio Cowork. Flujo interactivo: recogida de requisitos → diseño de arquitectura (fases del workflow, triage tables, descomposición de skills) → generación de AGENTS.md → creación de skills → revisión de calidad (checklist de 26 puntos) → empaquetado en ZIP `agents/v1`. |
| [skill-creator](../../agents/skill-creator/) | Diseña y genera skills de agente AI de alta calidad (ficheros SKILL.md). Flujo interactivo: recogida de requisitos → diseño de skill siguiendo principios probados → generación de SKILL.md con ficheros de soporte → revisión de calidad → empaquetado ZIP. |

Ambos agentes importan la shared-skill `skill-creator` vía su manifest `imported-skills`. La shared-skill `cowork-api` (usada por los agentes para subir bundles generados a Cowork) **no** se empaqueta aquí — Cowork ya la provee de forma nativa en runtime.

## Plataformas soportadas

| Plataforma | Soportada | Notas |
|---|---|---|
| Stratio Cowork | sí | Desplegable como bundle envoltorio `agents/v1`. |
| Claude (claude-plugin) | **no** | Los plugins del marketplace de Claude no soportan agentes. |

## Instalación

El plugin produce un artefacto:

- `dist/stratio-cowork-development-stratio-cowork-{version}.zip` — Bundle envoltorio para Stratio Cowork.

Usa la task `upload-plugin` de la shared-skill [`cowork-api`](../../skills/cowork-api/) para desplegarlo.
