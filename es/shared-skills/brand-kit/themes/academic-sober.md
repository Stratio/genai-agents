# Academic Sober

El aspecto de un journal académico — márgenes generosos, un serif
clásico en todo el documento, croma restringida y jerarquía tipográfica
cuidada. Construido para papers de investigación, whitepapers y
documentos de política largos donde la forma refleja las convenciones
académicas establecidas.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #312e81 | título, cabecera de página, marcas de sección |
| ink | #1f2937 | texto cuerpo |
| muted | #6b7280 | captions, notas al pie, referencias |
| rule | #d4d4d8 | divisores, rejillas de tabla |
| bg | #ffffff | página / superficie principal |
| bg_alt | #fafafa | abstract, bloques de cita, pull quotes |
| accent | #312e81 | igual que primary — el tema resiste los pops |
| state_ok | #166534 | indicadores positivos |
| state_warn | #92400e | alertas |
| state_danger | #991b1b | errores críticos |

Nota: `accent` colapsa en `primary` deliberadamente. La escritura
académica no destaca cosas con un segundo color — destaca con
itálicas, citas y jerarquía.

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #312e81 | coincide con primary |
| 2 | #525252 | tono gris neutro |
| 3 | #0e7490 | teal |
| 4 | #92400e | ocre |
| 5 | #6b21a8 | violeta atenuado |
| 6 | #166534 | verde profundo |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Libre Baskerville | 22 | Georgia, serif |
| h2 | Libre Baskerville | 16 | Georgia, serif |
| body | Libre Baskerville | 11 | Georgia, serif |
| caption | Libre Baskerville Italic | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

La tipografía de una sola familia es tradicional en publicaciones
académicas. La itálica de la misma familia asume el rol de captions y
referencias.

## Optional extensions

- **Motion budget**: `minimal`
- **Border radius**: `0px`
- **Dark mode variant**: no incluido
- **Chart sequential**: color base `#312e81`

## Print variant (para pdf-writer)

El papel académico se beneficia de una referencia clásica de stock de
papel cálido en vez de blanco puro:

| Token | Hex | Notas |
|---|---|---|
| paper | #f9f6f0 | blanco roto cálido académico clásico |
| ink | #1f1f1f | casi negro cálido (ligeramente más cálido que el ink de pantalla) |
| rule | #d6d3cc | tinte de hairline coordinado con paper |
| accent | #312e81 | sin cambios — índigo profundo imprime bien como marca contenida |

Los márgenes en ediciones impresas deberían ser generosos (≥ 2,5 cm).

## Tone family

`editorial-serious` (variante académica — nota: el guide
visual-craftsmanship no lista un tono académico; este tema hereda
de editorial-serious con la tipografía serif clásica como rasgo
distintivo).

## Best used for

- Papers académicos, tesis, working papers
- Whitepapers con aparato formal de citación
- Análisis de política y publicaciones extensas de think-tank

## Anti-patterns

- No introducir una segunda familia tipográfica — la austeridad de
  un solo serif es el tono.
- No usar para marketing de producto ni comunicaciones a cliente.
- No apretar márgenes para encajar contenido; la página académica
  debe respirar.
