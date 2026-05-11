# Plugin Stratio Productivity

Plugin funcional skills-only que agrupa capacidades de I/O documental, crafting visual e identidad de marca. Enchufable en cualquier agente (Cowork o Claude) que necesite leer, crear o transformar documentos ofimáticos y output visual con diseño consistente.

## Qué incluye

| Skill | Propósito |
|---|---|
| [pdf-reader](../../skills/pdf-reader/) | Lectura y extracción de contenido de PDF. |
| [pdf-writer](../../skills/pdf-writer/) | Creación y manipulación de PDF: merge, split, watermark, encrypt, formularios, documentos tipográficos multi-página. |
| [docx-reader](../../skills/docx-reader/) | Lectura y extracción de contenido de DOCX. |
| [docx-writer](../../skills/docx-writer/) | Creación y manipulación de DOCX: merge, split, find-replace, `.doc` → `.docx`. |
| [pptx-reader](../../skills/pptx-reader/) | Lectura y extracción de contenido de PPTX. |
| [pptx-writer](../../skills/pptx-writer/) | Creación de PPTX: merge, split, reordenar, find-replace en diapositivas y notas, `.ppt` → `.pptx`. |
| [xlsx-reader](../../skills/xlsx-reader/) | Lectura y extracción de contenido de XLSX. |
| [xlsx-writer](../../skills/xlsx-writer/) | Creación de XLSX: workbooks analíticos, matrices pivot, exports tabulares, `.xls` → `.xlsx`, refresh de fórmulas. |
| [web-craft](../../skills/web-craft/) | Output frontend interactivo (HTML/CSS/JS, React, Vue): componentes, páginas, dashboards. |
| [canvas-craft](../../skills/canvas-craft/) | Artefactos visuales estáticos de una página (PDF/PNG): pósters, portadas, certificados, infografías. |
| [brand-kit](../../skills/brand-kit/) | Tokens centralizados de identidad visual (colores, tipografía, paletas de gráficos, tamaños, tono). Diez temas curados; los clientes pueden extender o reemplazar. |

## Plataformas soportadas

| Plataforma | Soportada | Notas |
|---|---|---|
| Stratio Cowork | sí | Los plugins skills-only se despliegan vía el endpoint `/v1/agents/skills/bundle/import` de `genai-api`. |
| Claude (claude-plugin) | sí | Genera un `.claude-plugin/plugin.json` consumible como plugin de marketplace de Claude Code. |

## Instalación

El plugin produce dos artefactos:

- `dist/stratio-productivity-stratio-cowork-{version}.zip` — bundle para Stratio Cowork.
- `dist/stratio-productivity-claude-{version}.zip` — plugin de marketplace para Claude.

Usa la task `upload-plugin` de la skill compartida [`cowork-api`](../../skills/cowork-api/) para desplegar la variante Cowork. Para la variante Claude, sigue el flujo estándar de instalación de plugins de Claude Code (`/plugin install` desde un marketplace).

## MCPs

Este plugin no requiere ningún MCP — sus skills operan sobre ficheros locales y generan output local.
