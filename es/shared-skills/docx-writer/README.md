# docx-writer

Skill compartida que crea documentos Word (`.docx`) con diseño intencional y realiza operaciones estructurales sobre los existentes. Cubre dos públicos: (1) documentos genéricos dominados por prosa (cartas, memos, contratos, notas de política, whitepapers, newsletters, manuales, informes multipágina) autorizados con un flujo *design-first*, y (2) operaciones estructurales sobre `.docx` ya existentes (fusionar, dividir, buscar-y-reemplazar, convertir `.doc` → `.docx`, previsualización visual).

La skill hermana `docx-reader` cubre la ingesta de DOCX de entrada. Para informes analíticos dentro de `data-analytics`, la skill `analyze` mantiene su propio `DOCXGenerator` opinado con un esqueleto analítico (resumen ejecutivo / metodología / análisis / conclusiones). `docx-writer` es la herramienta de autoría de propósito general.

## Qué hace

- Autoría DOCX design-first directa con `python-docx` (sin clase builder): portadas, encabezados, párrafos, tablas con override de estilo, figuras, callouts, listas, bloques de código, markdown/HTML vía helpers inline
- Tamaño de página (A4 / Letter) y orientación (portrait / landscape) configurables
- Taxonomía de 7 categorías de documento (nota de política, contrato/legal, carta/memo, newsletter, manual, informe multipágina, académico) como puntos de partida — no enum-constrained
- Seis paletas de referencia (editorial-serio, corporativo-formal, técnico-minimalista, cálido-revista, sobrio-legal, académico-sobrio) como semillas `DESIGN` inline
- Operaciones estructurales sobre DOCX existentes: fusionar, dividir por encabezado o salto de página, buscar-reemplazar (run-aware), conversión `.doc` → `.docx` heredada
- Pipeline de previsualización visual (DOCX → PDF → PNG por página) para inspección de layout previa a entrega

## Dependencias Python

- `python-docx>=1.1`
- `lxml` (transitiva de `python-docx`)
- `pillow>=11.0` — embedido de figuras e inspección de tamaño de imagen

Todas ya forman parte del `requirements.txt` base de los agentes Python que cargan esta skill.

## Dependencias de sistema (apt)

- `libreoffice` (o `libreoffice-writer`) — conversión de `.doc` heredado → `.docx` y renderizado del preview visual. Sin él, la creación y las ops estructurales puras en Python siguen funcionando; solo se deshabilitan la conversión `.doc` y el preview PDF.
- `poppler-utils` — `pdftoppm` rasteriza el PDF del preview visual a PNGs por página. Ya forma parte de las dependencias de sistema de `pdf-reader`.

En Stratio Cowork, la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

## Guías compartidas

- `visual-craftsmanship.md` (vía `skill-guides`)

## Assets empaquetados

Ninguno en esta iteración. DOCX depende de las fuentes presentes en la máquina del lector; la skill recomienda Calibri / Aptos / Arial / Times New Roman como fallbacks seguros y documenta el embedding de fuentes en `REFERENCE.md` §Embedding de fuentes para los casos en que la distribución requiera fidelidad exacta.
