# pptx-reader

Skill compartida que ingiere presentaciones PowerPoint (`.pptx`, y `.ppt` legacy vía conversión con LibreOffice). Cubre extracción de texto, bullets, tablas, notas del presentador, comentarios, datos de charts OOXML nativos, medios embebidos y metadatos. Soporta dos modos: un one-shot `quick_extract.py` que devuelve Markdown estructurado, y un workflow profundo documentado en `SKILL.md` para decks complejos (dashboards con datos, slides ocultos, ficheros cifrados, contenido mixto).

La skill complementaria `pptx-writer` cubre la creación y las operaciones estructurales sobre ficheros PPT.

## Qué hace

- Extracción one-shot de texto + bullets + tablas + notas del presentador vía `scripts/quick_extract.py`, emitiendo Markdown
- Rasterización por slide vía `scripts/rasterize_slides.py` (PPTX → PDF → PNG) para pasar a un modelo de visión
- Extracción de datos de charts OOXML nativos desde `ppt/charts/chart*.xml` sin OCR
- Extracción de notas del presentador desde `ppt/notesSlides/notesSlide*.xml`
- Extracción de comentarios del revisor desde `ppt/comments/comment*.xml`
- Detección de slides ocultos e inclusión opcional
- Conversión de `.ppt` legacy vía `libreoffice --headless --convert-to pptx`
- Metadatos (autor, título, creado/modificado, revisión) vía `python-pptx`

## Dependencias de Python

- `python-pptx>=1.0`
- `lxml` (transitiva de `python-pptx`) — necesaria para el fallback por XML y el parseo de datos de charts

Ambas ya forman parte del baseline `requirements.txt` de los agentes Python que cargan esta skill.

Opcional:
- `msoffcrypto-tool` — solo necesaria para descifrar `.pptx` protegidos con contraseña. Instalar bajo demanda cuando el usuario proporciona la contraseña.
- `Pillow` — solo si post-procesas los PNG rasterizados (redimensionar, componer). Ya en el baseline.

## Dependencias del sistema (apt)

- `libreoffice` (o `libreoffice-impress`) — necesario para (a) convertir `.ppt` legacy a `.pptx`, (b) el pipeline de rasterización (PPTX → PDF). Sin él, la extracción de texto de `.pptx` modernos sigue funcionando; solo se deshabilitan conversión y rasterización.
- `poppler-utils` — `pdftoppm` rasteriza el PDF intermedio a PNG por slide. Ya es dependencia del sistema de `pdf-reader`, así que normalmente ya está presente.

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee ambos pre-instalados. En entorno local de desarrollo, ver la sección "System dependencies" del `README.md` del monorepo.

### Instalar en Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y libreoffice-impress poppler-utils
```

### Instalar en macOS

```bash
brew install --cask libreoffice
brew install poppler
```

## Guías compartidas

Ninguna en esta iteración.

## Assets incluidos

Ninguno. La skill depende de `python-pptx` y del LibreOffice del sistema; no se incluyen fuentes ni plantillas.
