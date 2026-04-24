# Creador de Agentes

Agente experto en diseñar y generar agentes IA completos para la plataforma Stratio Cowork — desde la recogida de requisitos hasta un paquete ZIP desplegable, con todo lo intermedio revisado y aprobado por ti.

## Qué hace este agente

El Creador de Agentes te guía a través del ciclo completo de creación de un agente: entender qué debe hacer tu agente, diseñar su flujo de trabajo y skills, generar todos los ficheros de instrucciones y configuración, revisar la calidad contra un checklist de 26 puntos y empaquetar todo como un bundle ZIP `agents/v1` compatible con Stratio Cowork. Sigue patrones de diseño probados para asegurar que tu agente sea efectivo, bien estructurado y listo para desplegar.

El flujo es **iterativo y human-in-the-loop**: tú confirmas cada hito (requisitos, arquitectura, AGENTS.md, diseño de cada skill, ficheros ensamblados, revisión) antes de avanzar. Si algo necesita cambiar a mitad del flujo, el agente vuelve a la fase correspondiente en lugar de seguir adelante.

## Cómo funciona

1. **Triaje** — Entender si partes de cero, estás completando un agente parcial, revisando contenido existente, añadiendo una skill suelta o yendo directo al empaquetado.
2. **Recogida de requisitos** — Entrevista guiada (identidad, flujos de trabajo, comportamiento) para capturar qué debe hacer el agente y cómo debe comportarse.
3. **Diseño de arquitectura** — Fases del flujo de trabajo, tabla de triaje, mapa de skills, reglas de interacción. Se presenta para tu aprobación.
4. **Generación de AGENTS.md** — Escribe el fichero principal de instrucciones siguiendo patrones probados.
5. **Creación de skills** — Para cada skill, decide si referenciar una skill existente de la plataforma, crear una skill interna (específica de este agente) o crear una skill compartida (reutilizable por otros agentes). Las skills internas y compartidas se construyen delegando al motor de skill-creator.
6. **Ensamblaje de estructura** — Genera `README.md`, `opencode.json`, `metadata.yaml` y un manifiesto `mcps` opcional con los servidores MCP que el agente necesita en despliegue.
7. **Revisión** — Ejecuta el checklist de calidad de 26 puntos y te guía por los hallazgos. Puedes pedir cambios y el agente vuelve al paso correspondiente.
8. **Empaquetado** — Crea el bundle `agents/v1` (ver más abajo) listo para subir a Stratio Cowork.

Puedes entrar en cualquier fase. "Revisa este AGENTS.md" salta a la fase 7. "Empaqueta estos ficheros" salta a la 8. "Añade una skill a mi agente" entra a la fase 5 para esa skill concreta.

## Tipos de skill en tu agente

Al diseñar la arquitectura, cada capacidad se mapea a uno de estos tres tipos:

| Tipo | Comportamiento |
|---|---|
| **Skill de plataforma** | Ya existe en la plataforma Stratio Cowork — el agente la referencia por nombre en `AGENTS.md` y no lleva código para ella |
| **Skill interna** | Específica de este agente — se crea junto al agente y viaja dentro del ZIP del agente en `.opencode/skills/` |
| **Skill compartida** | Reutilizable entre agentes — se crea junto al agente y se empaqueta en un ZIP de shared-skills separado que acompaña al bundle |

## Estructura del paquete (agents/v1)

El entregable final es un ZIP contenedor con un layout predecible:

```
{name}-stratio-cowork.zip               # Bundle contenedor
├── metadata.yaml                       # Versión de formato agents/v1 y metadatos del agente
├── {name}-opencode-agent.zip           # Ficheros del agente (AGENTS.md, README.md, opencode.json, .opencode/skills/)
├── {name}-shared-skills.zip            # (Opcional) skills compartidas nuevas creadas para este agente
└── mcps                                # (Opcional) servidores MCP requeridos en despliegue
```

## Capacidades

- Diseñar agentes desde cero mediante entrevistas guiadas
- Completar agentes parciales (tú aportas algunas piezas, el agente completa el resto)
- Revisar `AGENTS.md` existentes contra un checklist de calidad de 26 puntos
- Generar `AGENTS.md` con fases de flujo de trabajo, tablas de triaje y reglas de interacción
- Crear skills internas para tu agente usando el motor de skill-creator
- Crear skills compartidas reutilizables por otros agentes
- Referenciar skills existentes en la plataforma por nombre
- Generar `README.md`, `opencode.json`, `metadata.yaml` y manifiesto `mcps` opcional
- Empaquetar como bundle ZIP `agents/v1` de Stratio Cowork

## Qué puedes preguntar

### Crear agentes
- "Crea un agente para gestionar evaluaciones de calidad de datos"
- "Necesito un agente que ayude con flujos de revisión de código"
- "Diseña un agente asistente de soporte al cliente"

### Trabajar con contenido existente
- "Revisa este AGENTS.md y sugiere mejoras" (pega tu contenido)
- "Tengo un agente parcial, ayúdame a completarlo"
- "Añade una skill a mi agente existente"
- "Mejora la tabla de triaje de mi agente"

### Empaquetado
- "Empaqueta mis ficheros de agente como ZIP de Stratio Cowork"
- "Mi agente está listo — genera el bundle agents/v1"

### Aprender sobre diseño de agentes
- "¿Qué hace un buen agente?"
- "¿Cómo debería estructurar el flujo de trabajo de un agente?"
- "¿Cuándo una capacidad debería ser una skill vs estar inline en AGENTS.md?"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/agent-designer` | Diseño de arquitectura de agentes: patrones de flujo de trabajo, plantillas de triaje, generación de AGENTS.md, checklist de calidad de 26 puntos |
| `/agent-packager` | Empaquetado agents/v1 de Stratio Cowork: estructura ZIP, `metadata.yaml`, manifiesto `mcps` opcional, validación |
| `/skill-creator` | Motor de creación de skills para generar ficheros `SKILL.md` (usado para crear las skills internas y compartidas del agente) |

## Cómo empezar

Inicia el agente y describe qué agente necesitas: "Crea un agente para [tu caso de uso]". El agente te guiará paso a paso por el proceso y esperará tu aprobación en cada hito.
