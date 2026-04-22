# docx-writer

Skill compartida que crea documentos Word (`.docx`) con diseño intencional y realiza operaciones estructurales sobre los existentes. Cubre dos públicos: (1) documentos genéricos dominados por prosa (cartas, memos, contratos, notas de política, informes multipágina) autorizados con un flujo *design-first*, y (2) operaciones estructurales sobre `.docx` ya existentes (fusionar, dividir, buscar-y-reemplazar, convertir `.doc` → `.docx`, previsualización visual).

La skill hermana `docx-reader` cubre la ingesta de DOCX de entrada. Para informes analíticos dentro de `data-analytics`, la skill `analyze` mantiene su propio `DOCXGenerator` opinado con un esqueleto analítico (resumen ejecutivo / metodología / análisis / conclusiones). `docx-writer` es la herramienta de autoría de propósito general.

## Qué hace

- Autoría DOCX *design-first* con una clase primitiva `DOCXBuilder` (portadas, encabezados, párrafos, tablas, figuras, callouts, listas, bloques de código, bloques markdown)
- Tamaño de página configurable (A4 / Letter) y orientación (retrato / apaisado)
- Aplicación de estilo mediante `aesthetic_direction` (tono, override de paleta, par tipográfico)
- Composición de tablas con anchos DXA correctos, márgenes de celda y `ShadingType.CLEAR` para evitar fallos entre visores
- Operaciones estructurales sobre `.docx` existentes: merge, split, find-replace (consciente de runs)
- Conversión `.doc` heredado → `.docx` vía `libreoffice --headless --convert-to docx`
- Pipeline de previsualización visual (DOCX → PDF → PNG por página) para que el agente inspeccione el layout antes de entregar

## Dependencias Python

- `python-docx>=1.1`
- `lxml` (transitiva de `python-docx`)
- `markdown>=3.6` — lo usa `add_markdown_block` para plegar markdown a primitivas docx
- `beautifulsoup4>=4.12` — parsea el HTML inline que produce markdown para renderizado fiel en docx
- `pillow>=11.0` — inserción de figuras e inspección de tamaño de imagen

Todas ya forman parte del `requirements.txt` base de los agentes Python que cargan esta skill.

## Dependencias del sistema (apt)

- `libreoffice` (o `libreoffice-writer`) — conversión de `.doc` heredado y renderizado del preview visual. Sin él, la creación y todas las operaciones estructurales puras de Python siguen funcionando; solo se deshabilitan la conversión `.doc` y la previsualización.
- `poppler-utils` — `pdftoppm` rasteriza el PDF de preview a PNGs por página. Ya forma parte de las dependencias de `pdf-reader`.

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) aporta todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

## Guías compartidas

- `visual-craftsmanship.md` (vía `skill-guides`)

## Activos empaquetados

Ninguno en esta iteración. DOCX depende de las fuentes instaladas en la máquina del lector; la skill recomienda Calibri / Aptos / Arial como fallback seguro y documenta el embedding de fuentes para los casos donde la distribución lo exige.
