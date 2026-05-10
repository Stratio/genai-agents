# Plugin Stratio Productivity

Plugin funcional skills-only que agrupa capacidades de I/O documental, crafting visual y autoría de skills. Enchufable en cualquier agente (Cowork o Claude) que necesite leer, crear o transformar documentos ofimáticos y output visual.

## Qué incluye

| Skill | Propósito |
|---|---|
| [pdf-reader](../../shared-skills/pdf-reader/) | Lectura y extracción de contenido de PDF. |
| [pdf-writer](../../shared-skills/pdf-writer/) | Creación y manipulación de PDF: merge, split, watermark, encrypt, formularios, documentos tipográficos multi-página. |
| [docx-reader](../../shared-skills/docx-reader/) | Lectura y extracción de contenido de DOCX. |
| [docx-writer](../../shared-skills/docx-writer/) | Creación y manipulación de DOCX: merge, split, find-replace, `.doc` → `.docx`. |
| [pptx-reader](../../shared-skills/pptx-reader/) | Lectura y extracción de contenido de PPTX. |
| [pptx-writer](../../shared-skills/pptx-writer/) | Creación de PPTX: merge, split, reordenar, find-replace en diapositivas y notas, `.ppt` → `.pptx`. |
| [xlsx-reader](../../shared-skills/xlsx-reader/) | Lectura y extracción de contenido de XLSX. |
| [xlsx-writer](../../shared-skills/xlsx-writer/) | Creación de XLSX: workbooks analíticos, matrices pivot, exports tabulares, `.xls` → `.xlsx`, refresh de fórmulas. |
| [skill-creator](../../shared-skills/skill-creator/) | Diseña y genera nuevas skills de agente (guía de autoría de SKILL.md, checklist de calidad). |
| [web-craft](../../shared-skills/web-craft/) | Output frontend interactivo (HTML/CSS/JS, React, Vue): componentes, páginas, dashboards. |
| [canvas-craft](../../shared-skills/canvas-craft/) | Artefactos visuales estáticos de una página (PDF/PNG): pósters, portadas, certificados, infografías. |

## Plataformas soportadas

| Plataforma | Soportada | Notas |
|---|---|---|
| Stratio Cowork | sí | Los plugins skills-only se despliegan vía el endpoint `/v1/agents/skills/bundle/import` de `genai-api`. |
| Claude (claude-plugin) | sí | Genera un `.claude-plugin/plugin.json` consumible como plugin de marketplace de Claude Code. |

## Instalación

El plugin produce dos artefactos:

- `dist/stratio-productivity-stratio-cowork-{version}.zip` — bundle para Stratio Cowork.
- `dist/stratio-productivity-claude-{version}.zip` — plugin de marketplace para Claude.

Usa la task `upload-plugin` de la skill compartida [`cowork-api`](../../shared-skills/cowork-api/) para desplegar la variante Cowork. Para la variante Claude, sigue el flujo estándar de instalación de plugins de Claude Code (`/plugin install` desde un marketplace).

## MCPs

Este plugin no requiere ningún MCP — sus skills operan sobre ficheros locales y generan output local. Skills como `web-craft` y `canvas-craft` pueden recibir datos de cualquier MCP que tenga configurado el agente consumidor, pero el plugin en sí no impone ningún requisito de MCP.

## Solape con otros plugins

`web-craft` y `canvas-craft` también aparecen en `stratio-data-storytelling`. Es intencional: una skill puede pertenecer a varios plugins, porque los plugins son unidades aditivas de composición, no particiones exclusivas del catálogo de skills.
