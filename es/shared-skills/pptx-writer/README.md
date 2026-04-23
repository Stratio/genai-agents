# pptx-writer

Skill compartida que crea decks de PowerPoint (`.pptx`) con diseño intencional, y realiza operaciones estructurales sobre ficheros existentes. Cubre dos audiencias: (1) decks genéricos fuera del pipeline analítico (pitches, briefings ejecutivos, formación, académicos, ventas, town-hall), y (2) operaciones estructurales sobre ficheros `.pptx` existentes (merge, split, reordenar, borrar slides, find-replace en texto de slide y notas del presentador, conversión `.ppt` legacy → `.pptx`, rasterización de slides, exportación a PDF).

La skill complementaria `pptx-reader` cubre la ingesta de entradas PPTX. Para reports analíticos dentro de `data-analytics`, la skill `/analyze` mantiene su propio pipeline de PPT opinionado en `skills/analyze/report/tools/pptx_layout.py` con safe-area fija 4:3; `pptx-writer` es la herramienta general de autoría para todo lo demás.

## Qué hace

- Autoría de PPT design-first siguiendo un workflow de 5 pasos (clasificar → tono → emparejamiento tipográfico → paleta → ritmo), con una taxonomía de decks y un scaffold canónico en `SKILL.md`
- Aspect ratio por defecto 16:9 (10 × 5.625 pulgadas) vía scaffold blank incluido (`assets/blank.pptx`); 4:3 disponible cargando una plantilla del usuario
- Primitivas de slide como snippets copy-paste en `REFERENCE.md`: portada, agenda, divisor de sección, título+contenido, bullets, dos columnas, imagen-con-texto, KPI, tabla con override de estilo, charts OOXML nativos, cita, conclusión
- Autoría de charts OOXML nativos (bar / column / line / pie / area / scatter / radar / bubble) para que el usuario pueda editar los datos subyacentes en PowerPoint
- Operaciones estructurales sobre PPT existentes: merge, split (por sección o por N slides), reordenar, borrar, find-replace (en texto de slide y/o notas del presentador), conversión `.ppt` legacy → `.pptx` vía LibreOffice
- Pipeline de preview visual (PPTX → PDF → PNG por slide) para que el modelo inspeccione el layout antes de la entrega
- Exportación a PDF en una línea vía LibreOffice headless

## Dependencias de Python

- `python-pptx>=1.0`
- `lxml` (transitiva de `python-pptx`) — usada por los snippets de operaciones estructurales para manipulación de XML (`_sldIdLst`, find-replace cross-slide)
- `pillow>=11.0` — solo cuando los snippets post-procesan imágenes antes de embeberlas (redimensionar, componer)

Todas ya forman parte del baseline `requirements.txt` de los agentes Python que cargan esta skill.

## Dependencias del sistema (apt)

- `libreoffice` (o `libreoffice-impress`) — necesario para (a) conversión `.ppt` legacy → `.pptx`, (b) el pipeline de preview visual, (c) exportación a PDF. Sin él, la creación de decks y todas las operaciones estructurales pure-Python siguen funcionando; solo se deshabilitan esas tres features.
- `poppler-utils` — `pdftoppm` rasteriza el PDF de preview a PNG por slide. Ya es dependencia de `pptx-reader` y `pdf-reader`.

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee ambos pre-instalados (mismo patrón que `docx-writer` y `pdf-writer`). En entorno local de desarrollo, ver la sección "System dependencies" del `README.md` del monorepo.

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

- `visual-craftsmanship.md` (vía `skill-guides`) — principios de diseño compartidos entre la familia visual-craftsmanship (`web-craft`, `canvas-craft`, `pdf-writer`, `docx-writer`, `pptx-writer`).

## Assets incluidos

- `assets/blank.pptx` — un scaffold limpio 16:9 (10 × 5.625 pulgadas) con un único layout Blank y un tema neutro. Unos 30 KB. Cárgalo con `Presentation(ruta_al_blank_pptx)` como punto de partida de cada nuevo deck, salvo que el usuario provea una plantilla corporativa.

No se incluyen fuentes. PPT usa las fuentes del sistema del lector salvo que se embeban explícitamente, y el embedding es poco fiable entre Office / LibreOffice / Web Office. La skill recomienda Calibri / Aptos / Inter / Arial como defaults seguros y documenta el trade-off en `SKILL.md` §Fonts.
