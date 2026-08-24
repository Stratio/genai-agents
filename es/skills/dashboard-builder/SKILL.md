---
name: dashboard-builder
description: "Crea o amplía dashboards nativos de GenAI a partir de conversaciones de Cowork, resultados de tools, datos tabulares materializados e imágenes del workspace. Usar cuando el usuario pida crear un dashboard, añadir cards, convertir un análisis en cards, visualizar resultados como cards de texto/datos/gráfico/imagen, incluir una imagen del File Browser o solicite una operación destructiva no soportada que deba rechazarse de forma segura."
argument-hint: "[petición o contenido del dashboard]"
---

# Constructor de Dashboards

Crea o amplía dashboards mediante las tools MCP de dashboards. Una petición
como «crea un dashboard» o «añade estas cards» autoriza esa mutación; no pidas
una segunda confirmación.

Antes de construir un payload de dashboard, lee
[`references/contract.md`](references/contract.md) de forma relativa al
directorio base de esta skill. Respeta exactamente sus nombres de campo,
anidamiento, campos obligatorios y valores permitidos. No redactes el payload
de memoria.

## Límite de seguridad: los dashboards existentes son append-only

Cowork permite crear un dashboard y añadir cards. No permite borrar, vaciar,
sustituir, editar, sobrescribir ni reordenar un dashboard o una card persistidos.

Cuando el efecto solicitado sea destructivo o modifique contenido existente:

1. No llames a ninguna tool de dashboard, incluido `list_dashboards`.
2. No delegues ni uses ficheros, comandos shell, HTTP/REST directo, PATCH o
   DELETE como alternativa.
3. No uses `create_dashboard` ni `add_dashboard_cards` para simular un borrado
   o el estado final deseado.
4. Responde una vez que borrar o editar dashboards y cards existentes no está
   disponible desde Cowork y debe hacerse manualmente en Dashboards; después,
   detente.

Si una petición mezcla cambios destructivos y aditivos, no realices ninguna
mutación. Explica el límite y pide al usuario que haga una petición separada
para la parte aditiva.

## Canal operacional obligatorio

Las mutaciones de dashboards se realizan únicamente mediante las tools MCP de
dashboards. Usa la tool disponible cuyo nombre sin prefijo sea
`create_dashboard`, `add_dashboard_cards` o `list_dashboards`; el runtime puede
añadirle el alias del servidor MCP.

- Nunca guardes el payload de un dashboard con tools de escritura de ficheros
  ni con shell.
- Nunca crees `created-dashboard.json`, un fichero de propuesta u otro JSON
  como sustituto de una llamada a una tool de dashboard.
- Nunca emitas un bloque `dashboard-skill-output`. El frontend no persiste
  acciones de dashboard desde el texto del asistente.
- Nunca invoques endpoints REST de dashboard mediante shell, HTTP o una tool
  que no sea MCP.
- Si las tools MCP de dashboards no están disponibles, indica que al proyecto
  le falta su configuración MCP de dashboards. No finjas que has creado el
  dashboard ni recurras a un fichero.

## Flujo de trabajo

1. Clasifica la petición actual como creación, adición, solo lectura o no
   soportada. Aplica inmediatamente el límite de seguridad a las peticiones
   destructivas. No arrastres a este turno una mutación no ejecutada de un turno
   anterior.
2. Recopila únicamente contenido respaldado por la conversación, los resultados
   de tools o los ficheros del workspace. Inspecciona los ficheros referenciados
   cuando las tools lo permitan.
3. Elige tipos de card nativos:
   - `text` para resúmenes, explicaciones y Markdown o HTML.
   - `data` para filas materializadas que deban seguir siendo tabulares.
   - `chart` para filas materializadas con una configuración de gráfico válida.
   - `image` para capturas, gráficos estáticos, diagramas y otros ficheros
     visuales. No incrustes imágenes en el HTML de una card de texto.
4. No añadas metadatos `source` a cards de texto, datos o gráfico porque no
   forman parte de su contenido persistido. Para un `@filename` o una imagen del
   File Browser, resuelve la ruta exacta bajo `/root/project` y usa únicamente
   una fuente `workspace_path`. Este flujo requiere actualmente configurar el
   servidor de dashboards como un MCP HTTP custom/direct cuya URL incluya
   `?projectId={env:PROJECT_ID}`. Un registro MCP de sistema nativo no transporta
   actualmente este contexto de proyecto.
5. Asigna cada elemento distinto solicitado a exactamente una card. Una petición
   singular de un texto, tabla, gráfico o imagen produce una card.
6. Valida los argumentos de la tool contra `references/contract.md`.
7. Llama a la tool MCP de dashboard adecuada con las cards canónicas.

## Persistencia operacional

- Para un dashboard nuevo, llama a `create_dashboard` con `title`, el
  `description` opcional y un array `cards` no vacío.
- Para añadir cards, usa un `dashboard_id` real cuando se conozca. En caso
  contrario, pasa el nombre exacto proporcionado por el usuario como
  `dashboard_title`; la API resuelve una única coincidencia exacta sin distinguir
  mayúsculas. Nunca inventes un ID.
- Añade solo las cards solicitadas en el turno aditivo actual. Nunca repitas
  cards ni trabajo incompleto de un turno anterior.
- Si una petición de adición no tiene un ID real ni un nombre de dashboard, pide
  una aclaración concisa antes de llamar a la tool.
- Tras un éxito, responde una vez con una confirmación concisa y sin enlace.
  Trata el `dashboardId` devuelto como metadato opaco del cliente: no lo repitas
  ni derives de él una ruta, URL, origen o host. La UI controla la navegación.
- Una mutación correcta completa la petición. No propongas una comprobación
  posterior ni continúes con otro paso de verificación.
- Tras un fallo, informa del error real. No afirmes que hubo éxito ni reintentes
  mediante un fichero o un bloque JSON del asistente.
- Para preguntas hipotéticas, documentación o ejemplos que no autoricen una
  mutación, responde normalmente sin llamar a una tool de dashboard.

Pide aclaración únicamente antes de la llamada a la tool cuando no sea posible
inferir el contenido obligatorio. No pidas al usuario que continúe después de
una operación completada.

## Reglas de contenido

- Nunca inventes IDs de dashboard, SQL, IDs de origen, rutas, mediciones ni filas.
- Materializa las filas de `data` y `chart` en el payload. No dependas de volver
  a ejecutar SQL para renderizar el dashboard.
- Incluye `sqlQuery` solo cuando exista una sentencia SQL real que se haya
  ejecutado correctamente.
- Usa `raw: null` en cards nuevas salvo que exista una respuesta raw compatible.
- Prefiere Markdown para borradores de texto; la API lo sanea y convierte a HTML.
- Para una imagen del File Browser, no copies sus bytes en la conversación ni
  pongas su mención en `src`. Resuelve la ruta absoluta exacta bajo
  `/root/project`, omite `src` y `projectId`, y proporciona
  `source: {"kind":"workspace_path","path":"/root/project/..."}`.
  Usa esta fuente únicamente cuando el MCP de dashboards sea un servidor HTTP
  custom/direct configurado con `?projectId={env:PROJECT_ID}`. Si ese transporte
  con contexto de proyecto no está disponible, indica que no se pueden importar
  imágenes del workspace; no pruebes con un MCP de sistema nativo ni inventes un
  ID de proyecto.
  La API lee y valida el fichero autorizado y persiste una Data URL Base64
  completa en `card_content.src`, haciendo que la card sea independiente del
  ciclo de vida del workspace.
- Usa una Data URL soportada y completa solo cuando ya sea el origen disponible;
  nunca fabriques ni trunques Base64.
- Usa por defecto `fit: "contain"` y `position: "center"` en imágenes.
- Omite el layout cuando sea suficiente la colocación automática. Cuando lo
  incluyas, respeta el grid de 12 columnas.
- Mantén los títulos de las cards concisos y apropiados para un dashboard.

## Comprobación final

Antes de llamar a la tool, comprueba:

- El payload contiene al menos una card y ningún campo desconocido.
- El número de cards coincide con los elementos distintos solicitados y no hay
  duplicados.
- Los metadatos del dashboard y el destino de la adición son suficientes.
- Cada card tiene contenido válido para su tipo.
- Los valores y campos del esquema concuerdan; las dimensiones y métricas del
  gráfico existen.
- El tipo de gráfico está soportado operacionalmente; nunca generes cards
  `heatmap`.
- Las referencias de imagen se pueden resolver y no se hacen pasar por cards
  de texto.
- Todo el contenido factual está respaldado por las fuentes disponibles.
