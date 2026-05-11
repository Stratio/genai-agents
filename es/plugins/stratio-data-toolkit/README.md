# Plugin Stratio Data Toolkit

Plugin de marketplace de Claude que expone las skills core de datos de Stratio como un bundle conectable, para usuarios que tienen los MCPs de datos y gobierno de Stratio configurados y prefieren trabajar desde Claude Code.

## Qué incluye

| Skill | Propósito |
|---|---|
| [stratio-data](../../skills/stratio-data/) | Reglas y patrones de uso obligatorios para los MCPs de datos de Stratio (`query_data`, `list_domains`, `search_domains`, `generate_sql`, `profile_data`, etc.). |
| [explore-data](../../skills/explore-data/) | Workflow guiado para descubrir dominios gobernados, tablas, columnas y terminología antes de cualquier análisis. |
| [propose-knowledge](../../skills/propose-knowledge/) | Captura mejoras del data dictionary detectadas durante el análisis y las envía como propuestas de gobierno. |
| [assess-quality](../../skills/assess-quality/) | Evalúa la cobertura de calidad de un dominio, tabla o columna; identifica gaps en las ocho dimensiones de calidad. |

## MCPs requeridos

| MCP | Usado por | Propósito |
|---|---|---|
| `Stratio_Data` | `stratio-data`, `explore-data` | Consultar y perfilar dominios gobernados. |
| `Stratio_Gov` | `propose-knowledge`, `assess-quality` | Leer el data dictionary, proponer actualizaciones de conocimiento, e inspeccionar reglas y cobertura de calidad. |

Ambos MCPs deben estar configurados en tu agente Claude antes de instalar este plugin. El manifest del plugin los declara para que aparezcan en el resumen de instalación, pero el marketplace no auto-configura MCPs.

## Plataformas soportadas

| Plataforma | Soportada | Notas |
|---|---|---|
| Claude (claude-plugin) | sí | Genera un `.claude-plugin/plugin.json` consumible como plugin de marketplace de Claude Code. |
| Stratio Cowork | **no** | Los usuarios de Cowork ya disponen de estas skills a través de los plugins con agentes (`stratio-data`, `stratio-governance`), que las empaquetan dentro de los bundles de agente. |

## Instalación

El plugin produce un artefacto:

- `dist/plugin-stratio-data-toolkit-claude-{version}.zip` — plugin de marketplace para Claude.

Instala con el flujo estándar de plugins de Claude Code (`/plugin install` desde un marketplace que exponga este plugin).

## Composición de output

Para generar informes (PDF, DOCX, PPTX, XLSX, páginas web, pósters) a partir de los datos y la evaluación de calidad que este toolkit te da, instala también el plugin [`stratio-productivity`](../stratio-productivity/). Los dos están diseñados para componerse: este toolkit cubre el **input** (acceso a datos + evaluación de calidad), `stratio-productivity` cubre el **output** (autoría de documentos y visuales con identidad de marca).
