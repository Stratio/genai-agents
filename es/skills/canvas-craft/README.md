# canvas-craft

Skill compartida que produce artefactos estáticos de página única como PDF o PNG: posters, portadas, certificados, one-pagers de marketing, infografías, resúmenes visuales. Complementa a `pdf-writer` (documentos tipográficos multipágina) y `web-craft` (HTML/JS interactivo). Comparte el guide `visual-craftsmanship.md` con ambas.

## Qué hace

- Autoría PDF de página única con `reportlab` (control total de coordenadas, sin flujo)
- Rasterización PNG desde el PDF generado vía `pdf2image` (requiere `poppler-utils`)
- Manipulación raster, resizing, transformaciones de color con `pillow`
- Heurísticas de paleta, pareado tipográfico y márgenes afinadas para piezas de display (ver `visual-craftsmanship.md`)

## Dependencias Python

- `reportlab>=4.4`
- `pdf2image>=1.17` (requiere `poppler-utils`)
- `pillow>=11.0`

## Dependencias del sistema (apt)

- `poppler-utils` — soporte de `pdf2image` para rasterizar PDF→PNG

En Stratio Cowork la imagen del sandbox (`genai-agents-sandbox`) provee todo lo anterior. En dev local, ver la sección "System dependencies" del `README.md` del monorepo.

## Guides compartidos

- `visual-craftsmanship.md` (declarado en `skill-guides`)

## MCPs

Ninguno — la skill produce artefactos visuales a partir de un brief más los tokens de tema.

## Activos empaquetados

Incluye **3 familias de fuentes OFL** bajo `fonts/` para que la tipografía de display esté disponible out-of-the-box:

- **Fraunces** — peso variable, serif con eje italic variable opcional (sirve tanto para display como para body).
- **Instrument Serif** — regular + italic, serif editorial refinado.
- **Archivo Black** — regular + italic, sans display de alto impacto para posters y portadas.

Cada familia ships con su texto de licencia OFL. El bundle es intencionadamente más pequeño que el de `pdf-writer` (que incluye 14 familias) porque canvas-craft se centra en piezas display de una sola página donde un puñado de tipografías idiosincráticas rinden más que una librería amplia.
