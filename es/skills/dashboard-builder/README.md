# dashboard-builder

Crea dashboards nativos de GenAI y añade cards a dashboards existentes desde
una conversación de Cowork. Convierte contenido respaldado por la conversación,
resultados de tools, datos tabulares materializados e imágenes del workspace en
cards canónicas de tipo `text`, `data`, `chart` e `image`.

## Qué hace

- Llama directamente al MCP de dashboards; no usa la respuesta del asistente ni
  ficheros de propuesta como canal de persistencia.
- Crea dashboards y añade cards tratando el contenido existente como append-only.
- Valida los payloads de cards contra el contrato canónico de
  `references/contract.md`.
- Resuelve imágenes del File Browser mediante una ruta exacta del workspace. La
  API guarda una copia autorizada como Data URL Base64 para que el dashboard no
  dependa del ciclo de vida del workspace del proyecto.
- Trata el identificador de dashboard devuelto como metadato opaco de la UI y
  nunca inventa URLs de despliegue.

## Cuándo usarla

- Crear un dashboard a partir de un análisis o conversación de Cowork.
- Añadir una o varias cards a un dashboard existente.
- Representar información respaldada como cards nativas de texto, datos,
  gráfico o imagen.
- Añadir una imagen del workspace referenciada desde File Browser o mediante
  `@filename`.
- Rechazar de forma segura peticiones de borrado o edición de dashboards o cards;
  esas operaciones deben realizarse manualmente en Dashboards.

## Dependencias

### MCP

El agente host debe exponer tools con estos nombres sin prefijo:

- `create_dashboard`
- `add_dashboard_cards`
- `list_dashboards`

El runtime puede añadirles el alias de su servidor MCP.

Las imágenes del workspace requieren además configurar el servidor de
dashboards como un MCP HTTP custom/direct cuya URL incluya
`?projectId={env:PROJECT_ID}`. Un registro MCP de sistema nativo no transporta
actualmente el contexto de proyecto necesario para resolver rutas bajo
`/root/project`. Sin este transporte con contexto, la skill puede seguir creando
cards de texto, datos, gráficos e imágenes mediante URL o Data URL, pero no puede
importar imágenes del File Browser.

### Otras skills

Ninguna.

### Python y paquetes de sistema

Ninguno. Es una skill compuesta únicamente por instrucciones. La validación de
imágenes del workspace y su conversión a Base64 son responsabilidad de la
implementación del MCP de dashboards.

## Referencias incluidas

- `references/contract.md` — argumentos canónicos de las tools, esquemas de
  cards, reglas de fuentes e imágenes, layout del grid, configuración de
  gráficos, ejemplos y lista de validación.

## Modelo de seguridad

Las mutaciones de dashboards desde Cowork son intencionadamente append-only. La
skill puede crear un dashboard o añadir cards, pero no borrar, sustituir, editar,
sobrescribir, vaciar ni reordenar dashboards o cards persistidos. Tampoco simula
peticiones destructivas recreando el contenido.
