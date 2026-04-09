# Creador de Agentes

Agente experto en diseñar y generar agentes IA completos para la plataforma Stratio Cowork — desde la recogida de requisitos hasta un paquete ZIP desplegable.

## Qué hace este agente

El Creador de Agentes te guía a través del ciclo completo de creación de un agente: entender qué debe hacer tu agente, diseñar su flujo de trabajo y skills, generar todos los ficheros de instrucciones y configuración, revisar la calidad y empaquetar todo como un ZIP compatible con Stratio Cowork. Sigue patrones de diseño probados para asegurar que tu agente sea efectivo, bien estructurado y listo para desplegar.

## Capacidades

- Diseñar agentes desde cero mediante entrevistas guiadas
- Generar AGENTS.md con fases de flujo de trabajo, tablas de triaje y reglas de interacción
- Crear skills internas para tu agente usando el motor de skill-creator
- Crear skills compartidas reutilizables por otros agentes
- Referenciar skills existentes en la plataforma por nombre
- Generar README.md, opencode.json y metadata.yaml
- Revisar agentes contra un checklist de calidad de 26 puntos
- Empaquetar como bundle ZIP agents/v1 de Stratio Cowork

## Qué puedes preguntar

**Crear agentes:**
- "Crea un agente para gestionar evaluaciones de calidad de datos"
- "Necesito un agente que ayude con flujos de revisión de código"
- "Diseña un agente asistente de soporte al cliente"

**Trabajar con contenido existente:**
- "Revisa este AGENTS.md y sugiere mejoras" (pega tu contenido)
- "Tengo un agente parcial, ayúdame a completarlo"
- "Añade una skill a mi agente existente"

**Aprender sobre diseño de agentes:**
- "¿Qué hace un buen agente?"
- "¿Cómo debería estructurar el flujo de trabajo de un agente?"
- "Empaqueta mis ficheros de agente como ZIP de Stratio Cowork"

## Skills disponibles

| Comando | Descripción |
|---------|-------------|
| `/agent-designer` | Diseño de arquitectura de agentes: patrones de flujo de trabajo, plantillas de triaje, generación de AGENTS.md, checklist de calidad |
| `/agent-packager` | Empaquetado agents/v1 de Stratio Cowork: estructura ZIP, metadatos, validación |
| `/skill-creator` | Motor de creación de skills para generar ficheros SKILL.md (usado para skills internas y compartidas) |

## Cómo empezar

Inicia el agente y describe qué agente necesitas: "Crea un agente para [tu caso de uso]". El agente te guiará paso a paso por todo el proceso.
