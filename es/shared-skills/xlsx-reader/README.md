# xlsx-reader

Shared skill que extrae valores de celdas, tablas, fórmulas, imágenes, metadatos y estructura de hojas de libros de Excel aportados por el usuario (`.xlsx`, `.xlsm` y `.xls` legacy vía conversión con LibreOffice). Usada por agentes que necesitan ingerir entradas de hoja de cálculo como parte de un análisis, un flujo de gobernanza, o al leer especificaciones en forma tabular.

Diseñada como un flujo de dos fases: modo rápido (extracción one-shot con cadena de fallback multi-motor) y modo profundo (extracción determinista por motor con diagnóstico previo). La skill elige la fase según lo que el libro contiene realmente, nunca a priori.

## Qué hace

- Diagnóstico estructural (inventario de partes vía `unzip -l`, listado de hojas con estado de visibilidad, inventario de nombres definidos)
- Extracción de celdas y tablas con fallback multi-motor: `openpyxl` (read-only) → `pandas` (backend openpyxl) → walk XML en crudo sobre `zipfile`
- Inspección de fórmulas (`data_only=False`) e inspección de valores cacheados (`data_only=True`) como dos pases distintos
- Lectura selectiva de columnas y filas para datasets grandes (`usecols`, `nrows`, `--max-rows`)
- Extracción de imágenes (walk del ZIP hacia `xl/media/*`)
- Metadatos core y extendidos (autor, título, fechas de creación/modificación, nombres definidos, hoja activa, visibilidad de hojas)
- Conversión de `.xls` legacy a `.xlsx` (`soffice --headless --convert-to xlsx`)
- Conversión de `.xlsb` a `.xlsx` por el mismo pase de LibreOffice
- Fallback a CSV/TSV cuando el "fichero de Excel" que adjuntó el usuario es en realidad texto plano

## Dependencias Python

- `openpyxl>=3.1`
- `pandas>=2.0` (usa openpyxl como motor XLSX)
- `lxml` (transitiva de openpyxl)

Opcional:

- `xlrd<2` — soporte `.xls` legacy en solo lectura cuando LibreOffice no está disponible

Todas las dependencias listadas arriba ya forman parte del `requirements.txt` baseline de los agentes Python que cargan esta skill.

## Dependencias de sistema (apt)

- `libreoffice` (o `libreoffice-calc`) — conversión de `.xls` legacy y `.xlsb`. Solo se necesita cuando la entrada es un `.xls` binario pre-2007 o un `.xlsb` binario 2007+.

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, revisa la sección "System dependencies" del `README.md` del monorepo para comandos de instalación.

## Degradación elegante

La skill funciona solo con `openpyxl` + `pandas` + `lxml` para `.xlsx` y `.xlsm` modernos. LibreOffice habilita `.xls` y `.xlsb` legacy. Sin LibreOffice y sin `xlrd<2`, los binarios legacy no se pueden abrir — la skill reporta un diagnóstico claro en lugar de fallar en silencio.
