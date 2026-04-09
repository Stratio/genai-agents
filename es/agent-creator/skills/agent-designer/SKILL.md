---
name: agent-designer
description: "Diseñar la arquitectura de un agente IA para Stratio Cowork. Usar cuando el usuario necesita planificar el flujo de trabajo, tabla de triaje, skills y estructura de ficheros de un agente antes de generar ficheros."
argument-hint: "[descripción o requisitos del agente]"
---

# Skill: Diseñador de Arquitectura de Agentes

Referencia para diseñar agentes IA efectivos para la plataforma Stratio Cowork. Usar esta skill siempre que se diseñe un nuevo agente o se revise/mejore uno existente.

## 1. Anatomía de un Agente para Stratio Cowork

Un agente para Stratio Cowork consta de estos ficheros:

| Fichero | Propósito | Obligatorio |
|---------|-----------|-------------|
| `AGENTS.md` | Instrucciones del agente: identidad, flujo de trabajo, triaje, skills, reglas de interacción | Sí |
| `README.md` | Documentación para el usuario: qué hace el agente, cómo interactuar, ejemplos | Sí |
| `opencode.json` | Configuración de plataforma: referencia al fichero de instrucciones, permisos | Sí |
| `.opencode/skills/{nombre}/SKILL.md` | Skills internas: instrucciones operativas detalladas para tareas específicas | Opcional |

### Tipos de skills

Las skills extienden las capacidades del agente. Hay tres categorías:

| Tipo | Dónde reside | Cuándo usarla |
|------|-------------|---------------|
| **Skill interna** | Dentro del agent ZIP en `.opencode/skills/{nombre}/SKILL.md` | Específica de este agente — no reutilizable por otros |
| **Skill compartida (nueva)** | ZIP separado junto al agente | El usuario quiere que esté disponible para otros agentes también |
| **Skill de plataforma (existente)** | Ya disponible en la plataforma | Se referencia por nombre en AGENTS.md — la plataforma la carga en runtime |

Las skills internas y compartidas se crean usando la skill `/skill-creator`. Las skills de plataforma solo se referencian.

## 2. Escribir un AGENTS.md Efectivo

El AGENTS.md es el fichero más importante — define cómo piensa y actúa el agente. Seguir estos principios:

### Estructura

Todo AGENTS.md debe tener estas secciones en orden:

1. **Descripción y Rol** — Identidad, capacidades, limitaciones, estilo de comunicación
2. **Flujo de Trabajo Obligatorio** — Tabla de triaje + fases numeradas
3. **[Secciones específicas del dominio]** — Reglas, tablas de referencia, docs de herramientas (0 o más)
4. **Interacción con el Usuario** — Convención de preguntas, idioma, progreso, iteración

### Diseño de la tabla de triaje

La tabla de triaje es siempre la Fase 0. Enruta la intención del usuario a la acción correcta.

**Proceso de diseño:**
1. Listar todas las cosas distintas que un usuario podría pedir al agente
2. Para cada una, decidir: ¿se puede resolver con 1-2 acciones directas (llamada a herramienta, respuesta en chat), o necesita un flujo de múltiples pasos?
3. Acciones directas → resolver inline. Flujos de múltiples pasos → cargar una skill o activar la secuencia completa de fases

Usar el formato del Patrón de Triaje de `agents-md-patterns.md`.

### Diseño de fases del flujo de trabajo

Diseñar las fases a partir de los requisitos de flujo de trabajo del usuario (recogidos en la Fase 1 del creador de agentes):

1. Mapear cada escenario de flujo a una secuencia de pasos
2. Agrupar pasos relacionados en fases (3-6 fases es lo típico)
3. Para cada fase, definir:
   - **Condición de entrada**: qué activa esta fase
   - **Pasos**: lista numerada de acciones
   - **Condición de salida**: qué debe ser cierto antes de avanzar
4. Identificar fases que necesitan human-in-the-loop (cualquier fase que modifique sistemas externos o cree artefactos)

### Implementación de human-in-the-loop

Para fases con efectos secundarios, usar el Patrón Human-in-the-Loop de `agents-md-patterns.md`. Reglas clave:

- Presentar el plan completo ANTES de ejecutar
- Esperar confirmación explícita (nunca proceder ante respuestas ambiguas)
- Manejar rechazo, aprobación parcial e iteración
- Usar `**CRÍTICO**: NUNCA [acción] sin confirmación explícita del usuario` para las restricciones más fuertes

### Activación de skills

Cuando el triaje enruta a una skill, usar este patrón exacto en el flujo de trabajo:

```
Cargar `/nombre-skill` como referencia autoritativa para [tema].
```

Y en la sección de triaje:

```
**Activación de skills**: Cargar la skill correspondiente ANTES de continuar con el flujo de trabajo.
La skill contiene el detalle operativo necesario.
```

### Referencias a guides

Si el agente usa ficheros de guía externos dentro de skills, referenciarlos con:

```
Todas las reglas para [tema] están en `skills-guides/[nombre-guia].md`. Seguir TODAS las reglas definidas ahí.
```

### Calidad de las instrucciones

Aplicar estas reglas a cada instrucción del AGENTS.md:

- **Explicar POR QUÉ**: "Validar el SQL antes de ejecutar porque una consulta mal formada puede devolver resultados parciales silenciosamente" es mejor que solo "Validar el SQL"
- **Voz imperativa**: "Presentar el plan al usuario" no "El plan debería presentarse"
- **Tablas para decisiones**: Usar tablas markdown para routing, no párrafos de prosa
- **Formulación positiva**: "Haz X" es mejor que "No hagas Y" (decir qué HACER, no qué evitar)
- **Específico antes que vago**: "Consultar mediante la herramienta MCP `search_domains`" es mejor que "Buscar la información"

### Guías de longitud

| Complejidad del agente | Longitud objetivo del AGENTS.md | Estrategia |
|------------------------|--------------------------------|------------|
| Simple (1-2 skills, flujo lineal) | < 150 líneas | Todo inline |
| Medio (3-5 skills, flujo con ramas) | 150-300 líneas | Extraer detalle operativo a skills |
| Complejo (6+ skills, múltiples dominios) | 300-500 líneas | Extraer agresivamente; las skills llevan el detalle |

Si el AGENTS.md excede 500 líneas, dividir el contenido operativo en skills o guides.

## 3. Patrones de Diseño

El catálogo completo de patrones probados está en `agents-md-patterns.md`. Los más importantes:

1. **Triaje** — Enrutar intención del usuario antes de activar flujos (obligatorio)
2. **Fases secuenciales** — Estructurar el trabajo como etapas numeradas con condiciones de entrada/salida
3. **Activación de skills** — Cargar detalle operativo bajo demanda
4. **Human-in-the-loop** — Confirmar antes de efectos secundarios
5. **Convención de preguntas** — Estandarizar interacción con el usuario mediante `{{TOOL_QUESTIONS}}`
6. **Idioma** — Responder siempre en el idioma del usuario

## 4. Plantilla

La plantilla esqueleto para un nuevo AGENTS.md está en `agents-md-template.md`. Usarla como punto de partida y personalizar según el diseño del agente.

## 5. Checklist de Calidad

Ejecutar este checklist antes de finalizar cualquier agente. Presentar resultados como ítems ✅/❌:

**A. Calidad del AGENTS.md:**

1. ✅ Tiene sección de identidad con rol, capacidades, limitaciones y estilo de comunicación
2. ✅ Tiene flujo de trabajo obligatorio con fases numeradas
3. ✅ La Fase 0 es una tabla de triaje que enruta la intención del usuario a acciones o skills
4. ✅ Cada fase tiene condiciones claras de entrada y salida
5. ✅ Existen gates human-in-the-loop para acciones con efectos secundarios
6. ✅ Las reglas de activación de skills usan el patrón: "Cargar /nombre-skill ANTES de continuar"
7. ✅ Sección de Interacción con el Usuario define: idioma, convención de preguntas (`{{TOOL_QUESTIONS}}`), reporte de progreso
8. ✅ Las skills no contienen referencias directas a `AGENTS.md` o `CLAUDE.md` — usan frases genéricas
9. ✅ Usa voz imperativa
10. ✅ Usa tablas para routing de decisiones (no prosa)
11. ✅ Las instrucciones clave explican POR QUÉ, no solo QUÉ
12. ✅ Longitud apropiada (< 300 líneas para agentes simples, extraer a skills si es más largo)
13. ✅ Incluye instrucción de idioma: "Responder SIEMPRE en el mismo idioma que el usuario usa"
14. ✅ Tiene al menos un ejemplo de interacción esperada o referencia de uso

**B. Calidad de la estructura de ficheros:**

15. ✅ `opencode.json` es JSON válido con `"instructions": ["AGENTS.md"]`
16. ✅ Los permisos de `opencode.json` corresponden a las herramientas que el agente realmente usa
17. ✅ `README.md` tiene todas las secciones: qué hace, capacidades, ejemplos, tabla de skills, cómo empezar
18. ✅ Todas las skills internas tienen frontmatter YAML válido con `name` y `description`
19. ✅ Las descripciones de skills empiezan con verbo de acción e incluyen "Usar cuando..." para activación
20. ✅ No hay referencias a ficheros huérfanos (todos los ficheros referenciados existen)
21. ✅ Las skills son autocontenidas: no dependen de conocimiento externo no verificable

**C. Calidad del empaquetado:**

22. ✅ `metadata.yaml` tiene `format_version: "agents/v1"` y `name`
23. ✅ `metadata.yaml` `agent_zip` referencia el nombre de fichero correcto
24. ✅ El ZIP del agente contiene `AGENTS.md` en la raíz
25. ✅ El ZIP del agente contiene `.opencode/skills/` con las skills internas
26. ✅ Si hay shared skills, `skills_zip` está declarado y el ZIP contiene `{nombre-skill}/SKILL.md` por cada una
