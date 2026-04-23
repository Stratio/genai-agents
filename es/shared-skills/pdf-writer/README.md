# pdf-writer

Skill compartida que crea, transforma y asegura documentos PDF. Cubre dos audiencias: (1) documentos tipográficos multipágina y páginas únicas dominadas por prosa (informes analíticos, facturas, contratos, fanzines) y (2) operaciones estructurales (combinar, dividir, rotar, marca de agua, cifrar, aplanar, rellenar formularios).

La skill compañera `canvas-craft` cubre artefactos estáticos de página única (posters, portadas, certificados); `web-craft` cubre output interactivo HTML/JS; `quality-report` cubre el informe de calidad de plantilla fija. `pdf-writer` es la herramienta general para autoría de PDF.

## Qué hace

- Autoría PDF multipágina con `reportlab` (texto, tablas, figuras, flujo)
- Conversión SVG→PDF con `svglib` (fijada por debajo de 1.6 para evitar traer `pycairo`, que no tiene wheels manylinux)
- Incrustación y manipulación de imágenes con `pillow`
- Fusión, división, rotación, extracción de páginas vía `pypdf` (librería) o `qpdf` (CLI, reparación estructural)
- Relleno, inspección y aplanado de campos de formulario vía `pdftk-java`
- Marca de agua, cifrado, conversión PDF/A-1 vía `ghostscript`

## Dependencias Python

- `reportlab>=4.4`
- `svglib>=1.5,<1.6` — fijada por debajo de 1.6 porque 1.6+ arrastra `rlPyCairo` → `pycairo`, y `pycairo` no tiene wheels manylinux en PyPI; compilar desde fuente requeriría `libcairo2-dev` + un toolchain C que el sandbox purga tras el build.
- `pillow>=11.0`
- `pypdf>=5.0`
- `pdfplumber` — solo al reutilizar tablas de PDFs fuente; compartido con `pdf-reader`.

## Dependencias del sistema (apt)

- `qpdf` — operaciones estructurales y reparación como fallback CLI
- `pdftk-java` — inspección y aplanado de formularios (`pdftk`, vía update-alternatives); ver `FORMS.md`
- `ghostscript` — conversión PDF/A y aplanado como último recurso
- `poppler-utils` — `pdfinfo`, `pdftotext` para inspeccionar PDFs fuente; compartido con `pdf-reader`

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

### Instalar en Debian / Ubuntu

```bash
sudo apt update && sudo apt install -y poppler-utils qpdf pdftk ghostscript
pip install 'reportlab>=4.4' 'pypdf>=5.0' pdfplumber 'svglib>=1.5,<1.6' 'pillow>=11.0'
```

### Instalar en macOS

```bash
brew install poppler qpdf pdftk-java ghostscript
pip install 'reportlab>=4.4' 'pypdf>=5.0' pdfplumber 'svglib>=1.5,<1.6' 'pillow>=11.0'
```

### Qué proporciona cada dependencia

| Paquete | Propósito |
|---|---|
| `reportlab` | Motor principal para generar PDFs desde cero |
| `pypdf` | Combinar, dividir, rotar, marcas de agua, cifrar, rellenar formularios |
| `pdfplumber` | Leer tablas de PDFs fuente cuando se reutiliza su contenido |
| `svglib` | Incrustar gráficos vectoriales SVG en PDFs de reportlab |
| `pillow` | Gestión de imágenes para los flowables `Image()` |
| `qpdf` | Operaciones estructurales CLI, más rápido que pypdf para archivos grandes |
| `pdftk` | `FORMS.md`: aplanado robusto de formularios rellenos, inspección de campos |
| `ghostscript` | Conversión a PDF/A, aplanado de último recurso |
| `poppler-utils` | `pdfinfo`, `pdftotext` para inspeccionar PDFs fuente |

## Guides compartidos

- `visual-craftsmanship.md` (declarado en `skill-guides`)

## Activos empaquetados

Incluye un bundle de 14 familias de fuentes OFL (display y body) bajo `fonts/` para que los PDFs generados se vean consistentes entre entornos sin depender del descubrimiento de fuentes del sistema. Registradas directamente desde ese directorio por la skill — no hace falta instalación adicional de fuentes. Ver `fonts/README.md` (cuando exista) para la lista completa y las notas de licencia.
