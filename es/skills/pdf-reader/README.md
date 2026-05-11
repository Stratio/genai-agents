# pdf-reader

Skill compartida que extrae texto, tablas, formularios, metadatos, imágenes y contenido mediante OCR de ficheros PDF aportados por el usuario. La usan los agentes que necesitan ingerir PDFs como parte de un análisis, una evaluación de calidad o un flujo de gobierno.

Diseñada como un flujo de tres fases: modo rápido (diagnóstico estructural), modo profundo (extracción determinista por herramienta) y modo OCR (para PDFs escaneados o compuestos solo por imágenes). La skill elige la fase en función de lo que el PDF contiene realmente, nunca por adelantado.

La skill compañera `pdf-writer` cubre la autoría ad-hoc de PDF y las operaciones estructurales (merge, split, watermark, cifrado, formularios).

## Qué hace

- Diagnóstico estructural (cifrado, corrupción, layout de páginas, presencia de capa de texto)
- Extracción de texto (fallback multi-motor: `pypdf`, `pdfplumber`, `pdfminer.six`, `pypdfium2`)
- Extracción de tablas preservando layout (`pdfplumber`)
- Inspección y volcado de campos de formulario (`pdftk` CLI)
- Extracción y rasterización de imágenes (`pdf2image` + Poppler)
- OCR para PDFs escaneados (`pytesseract`, `ocrmypdf` con Tesseract)
- Reparación de último recurso para PDFs corruptos (`ghostscript`)

## Dependencias Python

- `pypdf>=5.0`
- `pdfplumber>=0.11`
- `pdfminer.six>=20250000`
- `pypdfium2>=5.0`
- `pdf2image>=1.17` (requiere `poppler-utils`)
- `pytesseract>=0.3.10` (requiere `tesseract-ocr`)
- `ocrmypdf>=17.0` (requiere `ghostscript` + `tesseract-ocr` + `poppler-utils`)

La inspección de firmas digitales usa `pyhanko` bajo demanda (`pip install pyhanko`); intencionadamente no forma parte del baseline para que la imagen del sandbox quede ligera.

## Dependencias del sistema (apt)

- `poppler-utils` — `pdfinfo`, `pdftotext`, `pdftoppm`, `pdfimages`, `pdfdetach`, `pdffonts`
- `qpdf` — operaciones estructurales, reparación de PDFs corruptos
- `pdftk-java` — inspección de campos de formulario mediante `pdftk dump_data_fields`
- `tesseract-ocr` + `tesseract-ocr-eng` + `tesseract-ocr-spa` — motor OCR y datos de idioma
- `ghostscript` — reparación de PDF como último recurso y rasterización de fallback

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

## Guías compartidas

Ninguna.

## MCPs

Ninguno — la skill opera exclusivamente sobre ficheros PDF aportados por el usuario.
