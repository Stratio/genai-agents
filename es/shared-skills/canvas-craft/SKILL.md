---
name: canvas-craft
description: "Crea artefactos visuales de una sola página — pósters, portadas, certificados, one-pagers de marketing, infografías — como PDF o PNG. Produce piezas en las que la composición domina sobre la prosa: la tipografía se convierte en elemento visual, la imagen y la forma cargan el significado. Úsala cuando el usuario pida una pieza visual más que un documento o una interfaz."
argument-hint: "[poster|portada|certificado|infografia|one-pager] [brief]"
---

# Skill: Canvas Craft

Guía para producir artefactos visuales de una sola página renderizados como PDF o PNG. El artefacto es estático, visualmente protagonista, y trata la tipografía como parte de la composición en lugar de como vehículo para prosa larga.

**Alcance**: esta skill gestiona piezas de una sola página en las que aproximadamente el setenta por ciento o más de la superficie es composición visual — color, forma, tipografía como forma. Para documentos tipográficos multi-página (informes analíticos, contratos, facturas, zines) la salida es un documento y pertenece a otra herramienta. Para artefactos interactivos de navegador (componentes, páginas, dashboards) el artefacto vive en un navegador y también pertenece a otra herramienta. Cuando haya duda, consulta `skills-guides/visual-craftsmanship.md` para el criterio de selección.

## 1. Lee la base

Lee y sigue `skills-guides/visual-craftsmanship.md`. Define los principios compartidos, anti-patrones, roles de paleta, filosofía de emparejamiento tipográfico y checklist de artesanía usados en todas las skills visuales del monorepo. Esta skill añade encima el workflow específico de canvas.

## 2. Workflow de dos pasos

Los artefactos de canvas se hacen en dos pases: un manifiesto breve que fija la intención visual, y luego la pieza en sí.

### Paso A — Declara la filosofía visual

Escribe un manifiesto estético corto (3–5 párrafos) que nombre el mundo visual en el que vive el artefacto. El manifiesto es privado a la sesión — no es el output — pero disciplina cada decisión posterior. Guárdalo como fichero `.md` junto al artefacto final para trazabilidad.

El manifiesto debe incluir:
- **Un nombre de movimiento** (una o dos palabras inventadas por ti — por ejemplo *Tinta Granito*, *Señal Lenta*, *Plancha Erosionada*, *Arquitectura Callada*, *Impreso con Sol*). No reutilices nombres de otras fuentes.
- **Forma y espacio**: cómo respira la composición, dónde vive la densidad, cómo es el esqueleto del artefacto.
- **Color y materia**: la paleta, la textura de la superficie (grano de papel, misregistro de risografía, cuatricromía brillante, metal grabado, tinta aguada), y qué se le pide a cada color.
- **Escala y ritmo**: qué elementos son enormes, cuáles recedan, cómo se siente el pacing de un vistazo frente a en detalle.
- **Tipografía como elemento**: cómo participa el tipo en la composición — como bloque display, como anclaje de caption, como marca espacial, como textura.

Mantenlo lo bastante específico para descartar las elecciones equivocadas y lo bastante abierto para que la composición emerja. Un manifiesto bien escrito permite producir más tarde un artefacto hermano con sensación de familia coherente.

### Paso B — Expresa la filosofía en el canvas

Con el manifiesto en mano, construye la pieza. Trabaja estas decisiones explícitamente:

- **Tamaño de página**: A4, A3, A2, Letter, Tabloid, cuadrado (1080×1080 para social). Comprométete antes de componer — redimensionar después destruye decisiones espaciales.
- **Márgenes y zona segura**: márgenes generosos; nada toca el borde salvo que la composición quiera sangrar. Deja aire.
- **Rejilla y anclaje**: incluso sin reglas visibles, una rejilla de tres o cinco columnas mantiene la composición deliberada. Un elemento que rompa la rejilla por página basta.
- **Jerarquía**: como mucho tres niveles focales (hero, secundario, anclaje). Todo lo demás sirve a estos.
- **Tipografía**: normalmente dos fuentes, a veces una, rara vez tres. Al menos una aparece como elemento visual — grande, recortada, interactuando con formas.
- **Imagen y forma**: formas originales, abstracciones, patrones. Si usas fotografía, recorta con audacia o reduce a silueta. Evita estéticas de stock.
- **Densidad de texto**: mínima. Un título, un subtítulo, un pequeño conjunto de cadenas de anclaje. Ningún párrafo. Si la pieza necesita párrafos, probablemente no sea un artefacto de canvas.

## 3. Tooling

Los artefactos de canvas en este monorepo se construyen en Python:

- **PDF**: `reportlab`. Registra las fuentes personalizadas de `fonts/` al principio de cada script usando `TTFont` y `registerFontFamily`.
- **PNG**: renderiza antes el PDF con reportlab y conviértelo a PNG a 300 DPI con `pdf2image` (que envuelve Poppler). Una sola fuente de verdad para ambos formatos.

```python
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

FONTS_DIR = Path(__file__).parent / "fonts"

def register_fonts():
    pdfmetrics.registerFont(TTFont("Fraunces", FONTS_DIR / "Fraunces-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Fraunces-Bold", FONTS_DIR / "Fraunces-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Fraunces-It", FONTS_DIR / "Fraunces-Italic.ttf"))
    registerFontFamily("Fraunces", normal="Fraunces", bold="Fraunces-Bold",
                       italic="Fraunces-It")
    # registra solo las familias que vas a usar de verdad
```

Para producir un PNG junto al PDF:

```python
from pdf2image import convert_from_path

images = convert_from_path("output.pdf", dpi=300)
images[0].save("output.png", "PNG")
```

Nunca te apoyes en la Helvetica integrada de reportlab para artefactos finales. Esas fuentes producen el aspecto por defecto plano al que esta skill se resiste activamente.

### Paleta específica para canvas

Los valores concretos de la paleta vienen del tema, no de esta skill.

- **Si el agente tiene disponible una skill de theming centralizada** (una skill tipo brand-kit que aporta un catálogo de temas más un flujo para que el usuario elija o defina uno), ejecuta ese flujo ANTES de codear. Mapea los tokens `primary` / `ink` / `accent` / `bg` del tema a los cuatro colores como mucho que tolera esta superficie.
- **Si no hay tal skill disponible**, improvisa siguiendo los roles de paleta tonal en `skills-guides/visual-craftsmanship.md`.

Los artefactos renderizados para impresión se benefician de:
- Neutros profundos que no son `#000` (café oscuro cálido, índigo frío, azul-negro).
- Blancos rotos como fondos en lugar del `#fff` puro. Hueso, crema, papel, arcilla.
- Saturación que sobreviva a la compresión de impresión. Los pastel tienden a desvaírse; los tonos más profundos aguantan.

Declara RGB en floats `0–1` para reportlab (`colors.Color(<r>, <g>, <b>)`). Mantén la paleta en cuatro colores declarados o menos — el canvas tiene espacio solo para el dominante, el neutro profundo, el neutro claro y un accent.

## 4. Pipeline combinada: portada + cuerpo

Cuando el brief es un informe con portada diseñada, esta skill produce solo la portada. El cuerpo multi-página lo ensambla la herramienta de documento tipográfico (consulta `skills-guides/visual-craftsmanship.md` para el criterio de selección). Merge final con `pypdf`:

```python
from pypdf import PdfWriter
writer = PdfWriter()
writer.append("cover.pdf")
writer.append("body.pdf")
writer.write("final.pdf")
```

Mantén consistentes los márgenes de la última página de la portada con los de la primera página del cuerpo para una transición limpia.

## 5. Fuentes

Usa las familias OFL curadas que se incluyen en `fonts/`. El set cubre un serif editorial display, una sans display pesada y un serif contemporáneo refinado — rango suficiente para composiciones con tipografía-como-elemento. Amplía el set cuando un brief necesite una mono o una display lúdica (ver `fonts/README.md` §"Ampliar el set").

Consulta `fonts/README.md` para ver la lista de familias, origen, fecha de descarga y commit SHA. Cada familia va acompañada de su `OFL.txt`. Para redistribuir un artefacto que use estas fuentes en contextos externos, incluye el OFL.txt de cada familia usada.

No mezcles más de tres familias. Dos suelen ser suficientes.

## 6. Pase final

Trabaja el checklist de artesanía de `visual-craftsmanship.md` antes de dar por terminado:
- Los márgenes respetan la rejilla. Nada se sale de página. Nada se solapa sin querer.
- La pieza se lee de un vistazo: el momento hero aparece primero, la información secundaria lo apoya, el texto de anclaje es legible sin esfuerzo.
- La tipografía aparece con los pesos y estilos elegidos; ningún peso por defecto se ha colado en un titular.
- La paleta aparece en las proporciones declaradas — el acento no se está esparciendo al fondo.
- Ninguna pauta de stock, ninguna imagen placeholder, nada de Lorem.
- La composición se siente deliberada a un metro de distancia y recompensa la observación cercana.

**Pulido sobre adición.** Si el instinto pide añadir otra forma o floritura tipográfica, refina en su lugar lo que ya está en la página.

Cuando se pidan varias páginas, trata cada una como una pieza emparentada dentro del mismo mundo visual — el manifiesto debe llevarse a través, y cada página ofrece una composición distinta en lugar de una variación de plantilla.
