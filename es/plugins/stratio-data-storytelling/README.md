# Plugin Stratio Data Storytelling

Plugin funcional skills-only enfocado a narrar historias con datos gobernados de Stratio. Agrupa las reglas de acceso a datos, los tokens de identidad visual y las skills de output visual para que cualquier agente consumidor pueda ir desde la query hasta el artefacto pulido y con marca.

## Qué incluye

| Skill | Propósito |
|---|---|
| [stratio-data](../../shared-skills/stratio-data/) | Reglas obligatorias y patrones de uso de los MCPs de datos de Stratio (`query_data`, `list_domains`, `search_domains`, `generate_sql`, `profile_data`, etc.). |
| [brand-kit](../../shared-skills/brand-kit/) | Tokens de identidad visual centralizados (colores, tipografías, paletas de gráficos, tamaños, tono). Diez temas curados; los clientes pueden extender o sustituir. |
| [web-craft](../../shared-skills/web-craft/) | Output frontend interactivo (HTML/CSS/JS, React, Vue): dashboards, reportes web narrativos, componentes. |
| [canvas-craft](../../shared-skills/canvas-craft/) | Artefactos estáticos de una página (PDF/PNG): pósters, infografías, portadas, certificados. |

## MCPs requeridos

Este plugin necesita los siguientes MCPs configurados en el agente consumidor:

| MCP | Usado por | Propósito |
|---|---|---|
| `Stratio_Data` | `stratio-data` | Expone `query_data`, `list_domains`, `search_domains`, `generate_sql`, `execute_sql`, `profile_data` y el resto de la superficie de MCPs de datos. |

El endpoint `/v1/agents/skills/bundle/import` de `genai-api` no configura MCPs — deben existir ya en el agente que consuma estas skills, o añadirse a su `metadata.yaml` después. La futura API `plugins/v1` (fase 2) permitirá que el manifest del plugin los configure server-side.

## Plataformas soportadas

| Plataforma | Soportada | Notas |
|---|---|---|
| Stratio Cowork | sí | Los plugins skills-only se despliegan vía el endpoint `/v1/agents/skills/bundle/import` de `genai-api`. |
| Claude (claude-plugin) | sí | Genera un `.claude-plugin/plugin.json` consumible como plugin de marketplace de Claude Code. |

## Instalación

El plugin produce dos artefactos:

- `dist/stratio-data-storytelling-stratio-cowork-{version}.zip` — bundle para Stratio Cowork.
- `dist/stratio-data-storytelling-claude-{version}.zip` — plugin de marketplace para Claude.

Usa la task `upload-plugin` de la skill compartida [`cowork-api`](../../shared-skills/cowork-api/) para desplegar la variante Cowork. Para la variante Claude, sigue el flujo estándar de instalación de plugins de Claude Code.

## Solape con otros plugins

`web-craft` y `canvas-craft` también aparecen en `stratio-productivity`. Es intencional: una skill puede pertenecer a varios plugins, porque los plugins son unidades aditivas de composición, no particiones exclusivas del catálogo de skills.
