# xlsx-writer

Shared skill que crea libros de Excel (`.xlsx`) con estructura intencional, y realiza operaciones estructurales sobre libros existentes. Cubre tres audiencias: (1) libros analíticos dirigidos por `/analyze` (portada/KPI + parámetros + detalle + apéndice), (2) libros de cobertura de calidad dirigidos por `quality-report` (estructura multi-hoja de auditoría per `quality-report-layout.md §6.6`), y (3) libros ad-hoc invocados directamente por el usuario (exports tabulares, catálogos, modelos cuantitativos, tablas de referencia).

La skill compañera `xlsx-reader` cubre ingest de entradas XLSX.

## Qué hace

- Autoría XLSX design-first vía `openpyxl` (sin clase builder): bandas KPI, Table objects nativos, formato condicional, freeze panes, anchos de columna, área de impresión y page setup
- Taxonomía de 6 categorías de libro (cover/KPI analítico, pivot, matriz de cobertura, export tabular, catálogo, modelo cuantitativo) como puntos de partida — no constreñidos por enum
- Theming vía referencia genérica a "centralized theming skill": paleta, tipografía, tamaños se alimentan de un bundle de tokens del tema; cae a `visual-craftsmanship.md` cuando no hay tema disponible
- Operaciones estructurales sobre ficheros XLSX existentes: merge hoja-a-hoja preservando estilos, split por hoja, buscar-y-reemplazar en texto de celda, extraer una hoja a CSV, convertir `.xls` binario legacy a `.xlsx`
- Helper de refresco de fórmulas (`scripts/refresh_formulas.py`) que fuerza un pase de recálculo con LibreOffice headless para escribir valores cacheados para visores que no auto-recalculan
- Pipeline de validación post-build (sanity estructural + refresco de fórmulas + export visual a PDF) para inspección pre-entrega

## Dependencias Python

- `openpyxl>=3.1`
- `pandas>=2.0` — opcional, usado por algunos snippets de operaciones estructurales para reshapes en bulk
- `pillow>=11.0` — embed de imágenes e inspección de tamaño cuando el libro incluye logos o figuras

Todas ya parte del `requirements.txt` baseline de los agentes Python que cargan esta skill.

## Dependencias de sistema (apt)

- `libreoffice` (o `libreoffice-calc`) — conversión `.xls` → `.xlsx` legacy, pase de refresco de fórmulas, renderizado de preview visual. Sin ello, la autoría sigue funcionando; solo se deshabilitan la conversión legacy, el refresco de fórmulas y el preview PDF.
- `poppler-utils` — `pdftoppm` rasteriza el PDF de preview visual a PNGs por página. Ya parte de las deps de sistema de `pdf-reader`.

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, revisa la sección "System dependencies" del `README.md` del monorepo.

## Skills compañeras

- `xlsx-reader` — la contraparte de ingesta (valores de celda / tablas / fórmulas / imágenes / metadatos). Comparte el stack `openpyxl` + `pandas`.
- `quality-report` — la skill que dispara el formato "Excel", materializando el libro multi-hoja de cobertura descrito en `quality-report-layout.md §6.6`.

## MCPs

Ninguno — la skill opera exclusivamente sobre ficheros locales.

## Guías compartidas

- `visual-craftsmanship.md` (vía `skill-guides`) — roles de paleta tonal y pairings tipográficos usados como fallback cuando no hay skill centralizada de theming que resolvió un tema.

## Assets empaquetados

- `assets/blank.xlsx` — libro vacío con una hoja sin estilo, usado como scaffold mínimo cuando la skill necesita arrancar un fichero desde cero en vez de construir desde `openpyxl.Workbook()`.
