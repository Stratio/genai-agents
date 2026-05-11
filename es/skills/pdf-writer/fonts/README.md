# Fuentes incluidas

Todas las fuentes de este directorio se distribuyen bajo la **SIL Open Font
License 1.1** (OFL). Puedes usarlas, modificarlas y redistribuirlas
como parte de los PDFs generados por esta skill, incluso con fines comerciales.

Los textos de licencia por familia se encuentran en los archivos `*-OFL.txt`.

## Inventario de fuentes

### Fuentes serif para cuerpo de texto — lectura de forma larga

- **Crimson Pro** — serif literaria moderna, excelente en pantalla e impresión
- **Lora** — serif contemporánea cálida, ligeramente caligráfica
- **Libre Baskerville** — serif clásica refinada, documentos formales
- **IBM Plex Serif** — serif técnica neutra (parte de la superfamilia IBM Plex)

### Fuentes sans-serif — UI, display, documentación técnica

- **Instrument Sans** — sans geométrica con calidez humanista sutil
- **Work Sans** — sans versátil y robusta
- **Outfit** — sans moderna redondeada, aspecto accesible

### Fuentes de display — titulares, títulos, carteles

- **Instrument Serif** — serif editorial de alto contraste, hermosa en tamaños grandes
- **Big Shoulders** — sans condensada de display, fuerte presencia editorial
- **Italiana** — didona aérea, tono ceremonial y lujoso
- **Young Serif** — serif amigable y llamativa, adecuada para titulares cálidos

### Monoespaciadas — cifras, código, datos tabulares

- **JetBrains Mono** — monoespaciada favorita de desarrolladores, gran legibilidad
- **IBM Plex Mono** — monoespaciada complementaria de la familia IBM Plex
- **DM Mono** — monoespaciada geométrica, limpia y discreta

## Notas de licencia

- La mayoría de las fuentes incluyen su archivo `*-OFL.txt` junto a los TTF.
- La **familia IBM Plex** (Serif y Mono) es publicada por IBM bajo OFL 1.1.
  El texto de licencia canónico está publicado en
  https://github.com/IBM/plex y reproducido en `OFL.txt` en la raíz
  de este directorio `fonts/` cuando está presente.
- **Instrument Serif** se incluye sin un archivo OFL separado porque
  se publicó originalmente junto a Instrument Sans bajo la misma
  concesión OFL — el archivo `InstrumentSans-OFL.txt` aplica a ambas familias.

## Combinaciones recomendadas

| Contexto | Display | Cuerpo | Monoespaciada |
|---|---|---|---|
| Informe literario | Instrument Serif | Crimson Pro | IBM Plex Mono |
| Documento financiero | Instrument Sans Bold | IBM Plex Serif | IBM Plex Mono |
| Factura / recibo | Instrument Sans Bold | Instrument Sans | JetBrains Mono |
| Newsletter | Big Shoulders | Lora | — |
| Certificado formal | Italiana | Libre Baskerville | — |
| Documento técnico | Outfit Bold | IBM Plex Serif | IBM Plex Mono |
| Informe amigable | Young Serif | Lora | DM Mono |

## Registrar fuentes en reportlab

Consulta el `SKILL.md` principal para ver el patrón completo. Ejemplo mínimo:

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

FONTS = Path(__file__).parent / "fonts"
pdfmetrics.registerFont(TTFont("Body", FONTS / "CrimsonPro-Regular.ttf"))
```

Registra solo las variantes que vayas a usar — cada registro incrusta
los datos de la fuente en el PDF de salida.

## Añadir más fuentes

Para ampliar esta biblioteca con fuentes OFL adicionales:

1. Descarga los archivos TTF desde la fuente oficial de la fuente (Google
   Fonts, GitHub, etc.).
2. Copia los TTF en este directorio.
3. Copia el texto de licencia como `<NombreFamilia>-OFL.txt` junto a ellos.
4. Añade una entrada a este README en la categoría correspondiente.

Usa únicamente fuentes con licencia OFL o licencias equivalentemente permisivas.
Las fuentes comerciales de fundiciones requieren licencia por uso y no pueden
incluirse aquí.
