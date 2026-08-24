# Contrato canónico v1 de las tools de dashboards

## Entrega obligatoria

Pasa las cards canónicas directamente a la tool MCP de dashboards. No emitas el
payload en el texto del asistente ni lo guardes en un fichero. El frontend no
persiste acciones de dashboard.

## Límite de seguridad append-only

Cowork puede crear un dashboard nuevo, añadir cards y listar dashboards. No
puede borrar, eliminar, vaciar, sustituir, editar, sobrescribir ni reordenar un
dashboard o una card existentes.

Ante una petición destructiva, no llames a una tool de dashboard, no delegues ni
uses comandos shell o peticiones REST/PATCH/DELETE directas. Nunca uses
`create_dashboard` ni `add_dashboard_cards` para simular un borrado o un estado
final deseado. Responde que la operación no está disponible desde Cowork y debe
realizarse manualmente en Dashboards; después, detente. Si una petición mezcla
trabajo destructivo y aditivo, no realices ninguna mutación y pide la parte
aditiva por separado.

## Contenido

1. Llamadas a tools
2. Campos compartidos de las cards
3. Contenido por tipo de card
4. Fuentes e imágenes
5. Layout
6. Configuración de gráficos
7. Ejemplos completos
8. Lista de validación

## 1. Llamadas a tools

Usa el esquema exacto de la tool que presenta el runtime. Los argumentos
lógicos son:

- `create_dashboard(title, cards, description?)`
- `add_dashboard_cards(cards, dashboard_id?, dashboard_title?)`
- `list_dashboards(page?, page_size?)`

`cards` debe contener al menos una card canónica. Para operaciones de adición,
proporciona un `dashboard_id` real o el `dashboard_title` exacto del destino. No
añadas a una llamada campos de envoltorio de acción como `version`, `operation`,
`targetDashboardId` o `dashboard`.

`add_dashboard_cards` es estrictamente append-only: incrementa el conjunto de
cards existente y nunca representa el estado final deseado. No puede eliminar,
sustituir ni editar cards existentes. Incluye únicamente las cards solicitadas
explícitamente en el turno aditivo actual; nunca repitas cards anteriores ni
peticiones incompletas.

Una creación o adición correcta devuelve únicamente
`{"dashboardId":"<id>"}`. Trata el ID como metadato opaco del cliente: no lo
repitas ni construyas a partir de él una ruta, URL, origen o host. La UI crea la
navegación con su propio router y base de despliegue.

## 2. Campos compartidos de las cards

```json
{
  "type": "text | data | chart | image",
  "title": "Título conciso opcional",
  "layout": { "x": 0, "y": 0, "w": 12, "h": 4 },
  "card_content": {}
}
```

Solo `type` y `card_content` son siempre obligatorios. `title` y `layout` son
opcionales. Los borradores operacionales usan `source` únicamente para una
imagen copiada del workspace; no añadas metadatos de origen a cards de texto,
datos o gráfico porque su modelo de persistencia no los conserva.

## 3. Contenido por tipo de card

### Texto

Proporciona al menos uno de `markdown` o `html`. Prefiere Markdown. No incluyas
markup de imagen cuando pueda representarse con una card de imagen.

```json
{
  "type": "text",
  "title": "Resumen ejecutivo",
  "card_content": {
    "markdown": "## Resultado\nLos ingresos aumentaron un 12%.",
    "raw": null
  }
}
```

### Datos

`data` y `querySchema` son arrays obligatorios. Cada fila de datos es un objeto
cuyas celdas pueden contener cualquier valor JSON válido: string, número,
booleano, null, array u objeto. Usa el tipo de esquema correspondiente para cada
columna y define `nullable` de forma coherente con los valores materializados.
Cada entrada del esquema requiere `name`, `type`, `nullable` y `metadata`.

```json
{
  "type": "data",
  "title": "Ingresos por año",
  "card_content": {
    "data": [
      { "year": 2025, "revenue": 1200000, "audited": true },
      { "year": 2026, "revenue": 1450000, "audited": null }
    ],
    "querySchema": [
      { "name": "year", "type": "integer", "nullable": false, "metadata": {} },
      { "name": "revenue", "type": "double", "nullable": false, "metadata": {} },
      { "name": "audited", "type": "boolean", "nullable": true, "metadata": {} }
    ],
    "raw": null
  }
}
```

Tipos de esquema permitidos: `string`, `boolean`, `integer`, `double`, `float`,
`long`, `decimal`, `date`, `datetime`, `timestamp`, `object`, `array` y `json`.

Usa `object` para columnas con objetos, `array` para columnas con arrays y
`json` cuando una columna contenga intencionadamente estructuras JSON
heterogéneas. Añade `sqlQuery` solo cuando sea una sentencia SQL real producida
correctamente en el contexto actual.

### Gráfico

El contenido de un gráfico requiere `data`, `querySchema`, `chartType` y
`chartConfig`. Las reglas de datos y esquema son las mismas que para una card de
datos.

```json
{
  "type": "chart",
  "title": "Evolución de ingresos",
  "layout": { "w": 12, "h": 6 },
  "card_content": {
    "data": [
      { "year": 2025, "revenue": 1200000 },
      { "year": 2026, "revenue": 1450000 }
    ],
    "querySchema": [
      { "name": "year", "type": "integer", "nullable": false, "metadata": {} },
      { "name": "revenue", "type": "double", "nullable": false, "metadata": {} }
    ],
    "chartType": "bar",
    "chartConfig": {
      "graph.dimensions": ["year"],
      "graph.metrics": ["revenue"]
    },
    "raw": null
  }
}
```

Tipos de gráfico soportados operacionalmente: `bar`, `line`, `area`,
`waterfall`, `pie`, `histogram`, `radar`, `bubble`, `scatter`, `progress`,
`gauge`, `map`, `pinmap` y `table`. No generes `heatmap`: el modelo de transporte
todavía reconoce el valor legacy, pero la UI actual de dashboards no lo renderiza.

### Imagen

Proporciona una referencia de imagen resoluble: `src` o una fuente
`workspace_path`. Este flujo requiere actualmente un MCP HTTP custom/direct
configurado con `?projectId={env:PROJECT_ID}`. Un registro MCP de sistema nativo
no transporta ese contexto de proyecto. Con el transporte directo y consciente
del proyecto, la API lee y valida un fichero autorizado del workspace y después
codifica y persiste una Data URL Base64 completa directamente en
`card_content.src`; el modelo no debe transportar el binario por la conversación.
La card persistida sigue funcionando aunque el proyecto se pare o se elimine.
Los MIME soportados son PNG, JPEG, GIF y WebP, con un tamaño máximo decodificado
de 5 MB. `raw` debe ser `null`.

```json
{
  "type": "image",
  "title": "Gráfico generado",
  "source": {
    "kind": "workspace_path",
    "path": "/root/project/output/chart.png"
  },
  "card_content": {
    "alt": "Gráfico de ingresos generado durante el análisis",
    "caption": "Ingresos por año",
    "fit": "contain",
    "position": "center",
    "raw": null
  }
}
```

`fit` puede ser `contain`, `cover` o `fill`; su valor por defecto es `contain`.
El valor por defecto de `position` es `center`.

## 4. Fuentes e imágenes

La única forma de fuente operacional es:

- `{"kind":"workspace_path","path":"/root/project/output/chart.png"}` requiere
  una ruta exacta. Úsala solo en una card de imagen y omite `projectId` del
  payload de la tool. La URL del MCP custom/direct debe incluir
  `?projectId={env:PROJECT_ID}` para que la API reciba el proyecto actual fuera
  de los argumentos generados por el modelo e incruste el fichero validado como
  Base64.

No emitas `source` para cards de texto, datos o gráfico. No emitas fuentes
`chat_message`, `tool_result` ni `generated` en borradores operacionales; sus
metadatos no forman parte del contrato persistido. La fuente de imagen puede
estar en la card o en `card_content.source`, pero nunca en ambos lugares.

Para `src`, usa una URL HTTP(S) válida o una Data URL completa
`data:image/<type>;base64,<payload>`. Para imágenes del File Browser, omite
`src`; nunca pases ahí `@filename`. Nunca emitas Base64 de relleno ni un payload
truncado.

## 5. Layout

El grid tiene 12 columnas:

- `x`: entero entre 0 y 11.
- `y`: entero no negativo.
- `w`: entero entre 1 y 12.
- `h`: entero entre 1 y 12.
- Cuando ambos estén presentes, `x + w` no puede superar 12.

Todos los campos de layout son opcionales. Valores recomendados cuando importe
un layout explícito:

- texto: `{ "w": 12, "h": 4 }`
- datos: `{ "w": 12, "h": 7 }`
- gráfico: `{ "w": 6, "h": 6 }`
- imagen: `{ "w": 6, "h": 5 }`

Prefiere omitir `x` e `y`; la capa de persistencia coloca las cards nuevas sin
colisiones.

## 6. Configuración de gráficos

Referencia únicamente columnas presentes en `data` y `querySchema`.

- `bar`, `line`, `area`, `waterfall`, `scatter`:
  `{"graph.dimensions":["dimension"],"graph.metrics":["metric"]}`
- `bubble`: añade `"scatter.bubble":"sizeColumn"`.
- `pie`: `{"pie.dimension":"dimension","pie.measure":"metric"}`
- `progress`: `{"progress.goal":100}`
- `gauge`: `{"gauge.segments":[{"min":0,"max":50,"label":"Low"}]}`
- `radar`: `{"radar.metrics":["metric"],"radar.dimension":["dimension"]}`
- `map`:
  `{"map.metric":"metric","map.dimension":"region","map.region":"world_countries","map.type":"region"}`
- `pinmap`: `{"map.latitude_column":"latitude","map.longitude_column":"longitude"}`
- `histogram`: `{"counts":[2,5,3],"bin_edges":[0,10,20,30]}`

Usa `table` solo cuando el runtime ya proporcione una configuración de gráfico
compatible y conocida; en caso contrario, usa una card `data`.

Para `map.region`, usa exactamente uno de estos valores: `Spain-communities`,
`Spain-provinces`, `world_countries` o `United States`. Se distingue entre
mayúsculas y minúsculas. No generes `heatmap` hasta que la UI de dashboards lo
soporte.

## 7. Ejemplos completos

### Argumentos de `create_dashboard`

```json
{
  "title": "Analítica de clientes",
  "description": "Generado a partir del análisis actual de Cowork",
  "cards": [
    {
      "type": "text",
      "title": "Resumen",
      "card_content": {
        "markdown": "Los ingresos aumentaron de 1,2 M a 1,45 M.",
        "raw": null
      }
    },
    {
      "type": "chart",
      "title": "Ingresos por año",
      "card_content": {
        "data": [
          { "year": 2025, "revenue": 1200000 },
          { "year": 2026, "revenue": 1450000 }
        ],
        "querySchema": [
          { "name": "year", "type": "integer", "nullable": false, "metadata": {} },
          { "name": "revenue", "type": "double", "nullable": false, "metadata": {} }
        ],
        "chartType": "bar",
        "chartConfig": {
          "graph.dimensions": ["year"],
          "graph.metrics": ["revenue"]
        },
        "raw": null
      }
    }
  ]
}
```

### Argumentos de `add_dashboard_cards` usando el nombre de destino

```json
{
  "dashboard_title": "Arquitectura",
  "cards": [
    {
      "type": "image",
      "title": "Diagrama de arquitectura",
      "card_content": {
        "src": "https://example.com/architecture.png",
        "alt": "Diagrama de arquitectura generado en Cowork",
        "fit": "contain",
        "position": "center",
        "raw": null
      }
    }
  ]
}
```

## 8. Lista de validación

- Usa únicamente los campos documentados y la escritura camelCase exacta.
- No incluyas `id`, `created_at` ni `updated_at` en los borradores.
- No emitas un array `cards` vacío.
- No inventes un ID de destino ni SQL.
- No llames a una tool de dashboard ante una petición destructiva.
- No incluyas cards arrastradas de un turno anterior.
- Mantén `querySchema` como array JSON, no como string JSON serializado.
- Asegúrate de que cada valor de fila sea JSON válido y concuerde con el esquema
  declarado.
- Haz coincidir cada configuración de gráfico con su tipo y columnas reales.
- Usa cards de imagen para ficheros visuales y rutas exactas del workspace.
- Mantén las imágenes inline completas, soportadas y dentro del límite de 5 MB.
