# docx-reader

Skill compartida que extrae texto, tablas, imágenes, metadatos y marcas de cambios rastreados de documentos Word aportados por el usuario (`.docx` y `.doc` heredado). La usan los agentes que necesitan ingerir DOCX como parte de un análisis, un flujo de gobierno o cuando construyen una capa semántica a partir de especificaciones de negocio.

Diseñada como un flujo en dos fases: modo rápido (extracción de un solo paso con cadena de motores de respaldo) y modo profundo (extracción determinista por herramienta, con diagnóstico previo). La skill elige la fase según lo que realmente contiene el documento, no a priori.

La skill compañera `docx-writer` cubre la autoría ad-hoc de DOCX y las operaciones estructurales (merge, split, buscar-reemplazar, conversión de `.doc` heredado).

## Qué hace

- Diagnóstico estructural (inventario de partes vía `unzip -l`, detección de `word/comments.xml`, `word/media/`, `word/footnotes.xml`)
- Extracción de texto con cadena multimotor: `pandoc` → `python-docx` → recorrido XML crudo sobre `zipfile`
- Extracción de tablas con fidelidad celda a celda (`python-docx` `Document.tables`)
- Extracción de imágenes (recorrido ZIP en `word/media/*`)
- Metadatos core y extendidos (autor, título, fechas de creación/modificación, número de revisiones, aplicación)
- Visibilidad de cambios rastreados (informe solo-lectura de `<w:ins>` / `<w:del>` presentes en `document.xml`)
- Conversión `.doc` (heredado) → `.docx` (`soffice --headless --convert-to docx`)

## Dependencias Python

- `python-docx>=1.1`
- `lxml` (transitiva de `python-docx`)

Ambas ya forman parte del `requirements.txt` de base de los agentes Python que cargan esta skill.

## Dependencias del sistema (apt)

- `pandoc` — extractor principal para documentos dominados por prosa (buen manejo de notas al pie, cambios rastreados, listas). Sin él la skill cae a `python-docx`.
- `libreoffice` (o `libreoffice-writer`) — conversión de `.doc` heredado a `.docx`. Solo se necesita cuando la entrada es un `.doc` binario anterior a 2007.

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) aporta todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo para los comandos de instalación.

## Degradación elegante

La skill funciona solo con `python-docx` + `lxml`. `pandoc` y `libreoffice` mejoran la calidad de extracción y desbloquean el soporte de `.doc` heredado, pero no son obligatorias.

## Guías compartidas

Ninguna.

## MCPs

Ninguno — la skill opera exclusivamente sobre ficheros DOCX aportados por el usuario.
