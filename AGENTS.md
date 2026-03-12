# genai-agents — Monorepo

Monorepo con agentes de IA generativa para analisis de datos de negocio.

## Estructura

```
genai-agents/
  shared-skills/           # Skills compartidas entre agentes (autocontenidas o casi)
    propose-knowledge/
    explore-data/
    stratio-data/
  shared-skill-guides/     # Guides compartidos (no son skills; copiados a skills-guides/ en el output)
    stratio-data-tools.md
  data-analytics/          # Agente completo (analisis + informes multi-formato)
    shared-skills          # Lista de shared skills que incluye este agente
    shared-guides          # Lista de shared-skill-guides que AGENTS.md referencia directamente
  data-analytics-light/    # Agente ligero (analisis en chat)
    shared-skills
    shared-guides
```

## Instrucciones de desarrollo

- Cada agente tiene su propio `AGENTS.md` con instrucciones especificas. Trabajar siempre desde la carpeta del agente correspondiente
- Skills propias de cada agente en `skills/`; skills compartidas en `shared-skills/` (raiz del monorepo)
- Guides compartidos en `shared-skill-guides/` (raiz del monorepo); guides locales en `skills-guides/` del agente
- Cada agente declara que shared skills necesita en `shared-skills` (una linea por skill) y que guides directos en `shared-guides`
- Cada shared skill puede declarar que guides de `shared-skill-guides/` necesita en un fichero `skill-guides` dentro de su carpeta
- Si un agente tiene en `skills/` una skill con el mismo nombre que una shared skill → la version local tiene prioridad
- Scripts de empaquetado genericos en la raiz del monorepo: `pack_claude_code.sh` y `pack_opencode.sh` (cualquier agente)
- Scripts de empaquetado especificos de plataforma en `data-analytics-light/` (`pack_claude_project.sh`, `pack_claude_plugin.sh`, `pack_claude_cowork.sh`)
- El `.gitignore` raiz cubre ambos agentes

## Resumen de agentes

### data-analytics
Agente completo de BI/BA: consulta de datos gobernados via MCP, analisis con Python (pandas, scipy, scikit-learn), visualizaciones (matplotlib, seaborn, plotly), generacion de informes (PDF, DOCX, web, PowerPoint), documentacion del razonamiento, validacion, gestion de la memoria entre sesiones.

### data-analytics-light
Agente ligero de BI/BA: mismo motor analitico pero orientado a conversacion. Sin generacion de informes formales — el output principal es el chat. Incluye scripts de empaquetado para Claude Projects, Claude Plugin y Claude Cowork.

## Scripts de empaquetado (raiz)

Scripts genericos que funcionan con cualquier agente del monorepo:

| Script | Plataforma destino | Output |
|--------|-------------------|--------|
| `pack_claude_code.sh` | Claude Code CLI | `{agente}/claude_code/{nombre}/` |
| `pack_opencode.sh` | OpenCode | `{agente}/opencode/{nombre}/` |
| `pack_shared_skills.sh` | Todas (skills sueltas) | `dist/shared-skills.zip` o `dist/{skill}.zip` |

Uso: `bash pack_claude_code.sh --agent <ruta-agente> [--name <nombre-kebab>]`

## Skills compartidas

### Crear una shared skill

1. Crear `shared-skills/<nombre>/SKILL.md` con el contenido de la skill
2. Si la skill necesita guides externos, crear los ficheros en `shared-skill-guides/` y listarlos en `shared-skills/<nombre>/skill-guides` (texto plano, una linea por fichero)
3. Declarar la skill en los agentes que la usen añadiendo su nombre al fichero `<agente>/shared-skills`
4. Si el AGENTS.md del agente referencia el guide directamente, añadirlo tambien a `<agente>/shared-guides`

**Reglas de contenido del SKILL.md:**
- No referenciar `AGENTS.md` ni `CLAUDE.md` directamente — usar formulaciones genericas como "segun las instrucciones del agente" o "siguiendo la convencion de preguntas al usuario". Los pack scripts sustituyen estos nombres segun la plataforma destino, pero una referencia directa puede quedar mal en alguna plataforma
- No depender de herramientas Python, estilos, templates ni rutas especificas de un agente concreto — si la skill necesita eso, debe ser local
- Las referencias a `output/MEMORY.md` son aceptables si estan condicionadas a la existencia del fichero (`si existe`) — agentes sin memoria simplemente la ignoran
- Las referencias a guides en el SKILL.md deben usar la ruta `skills-guides/<fichero>` (sin prefijo de plataforma) — los pack scripts genéricos copian cada guide **dentro** de la carpeta de la skill y reescriben las referencias para que sean locales (autocontenida). Los guides declarados en `shared-guides` del agente se copian además a `skills-guides/` para que `AGENTS.md` los referencie

### Usar una shared skill en un agente

Añadir el nombre de la skill al fichero `<agente>/shared-skills` (una linea por skill). Si el AGENTS.md referencia directamente algun guide de `shared-skill-guides/`, añadirlo a `<agente>/shared-guides`. Todos los pack scripts leen estos manifiestos automaticamente.

Si el agente ya tiene en `skills/` una skill con el mismo nombre, la version local tiene prioridad y la shared se omite.

## Añadir un nuevo agente

La guía completa de creación está en `README.md` (sección "Crear un agente nuevo"). Checklist de integración en el monorepo:

1. Crear carpeta `mi-agente/` con estructura mínima:
   - `AGENTS.md` — rol, workflow, reglas del agente
   - `opencode.json` — MCPs y permisos para OpenCode (si usa OpenCode)
   - `skills/` — opcional; si el agente tiene skills propias, formato canónico `skills/<nombre>/SKILL.md`
   - `shared-skills` — opcional; lista de shared skills del monorepo a incluir (una linea por skill)
   - `shared-guides` — opcional; lista de shared-skill-guides que AGENTS.md referencia directamente
2. Añadir `mi-agente` al fichero `release-modules` (una línea por agente) para que `make package` lo incluya
3. Actualizar la tabla de agentes en `README.md`
