# Editorial Serious

Tipografía con serif dominante sobre una página casi blanca, navy
profundo como anclaje y una terracota cálida como único pop
intencional. Transmite gravedad institucional sin ornamento — el tono
de un documento de política extenso o de un informe analítico
multipágina.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #0a2540 | títulos, reglas superiores, acentos de portada |
| ink | #1f2937 | texto cuerpo |
| muted | #6b7280 | captions, notas al pie |
| rule | #d1d5db | divisores finos y bordes sutiles |
| bg | #ffffff | página / superficie principal |
| bg_alt | #f3f4f6 | bandas de tabla, rellenos de callout |
| accent | #b84c2c | CTAs, highlights, pops intencionales |
| state_ok | #047857 | indicadores positivos |
| state_warn | #b45309 | alertas |
| state_danger | #b91c1c | errores críticos |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #0a2540 | coincide con primary |
| 2 | #b84c2c | coincide con accent |
| 3 | #047857 | verde (balancea el rojo del accent) |
| 4 | #6366f1 | índigo (amplia separación de tono) |
| 5 | #b45309 | ámbar (se lee como cálido diferenciado) |
| 6 | #6b7280 | gris muted (relleno para series largas) |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Instrument Serif | 32 | Georgia, serif |
| h2 | Instrument Serif | 22 | Georgia, serif |
| body | Crimson Pro | 11 | Georgia, serif |
| caption | Crimson Pro | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

## Optional extensions

- **Motion budget**: `restrained` (transiciones web-craft, animaciones pptx)
- **Border radius**: `2px` (web-craft)
- **Dark mode variant**: ver [Dark mode](#dark-mode)
- **Chart sequential**: no incluido

## Print variant (para pdf-writer)

Sobre papel, la paleta de pantalla necesita un blanco roto cálido en
vez de blanco puro y un casi negro cálido en vez del ink regular:

| Token | Hex | Notas |
|---|---|---|
| paper | #faf8f4 | blanco roto cálido para página |
| ink | #1a1a1a | casi negro cálido para texto cuerpo |
| rule | #e5e0d8 | tinte de hairline coordinado con paper |
| accent | #b84c2c | sin cambios — la terracota imprime bien |

Tamaños de fuente y tipografía iguales que en el bloque core.

## Dark mode

| Token | Hex |
|---|---|
| bg | #0e1318 |
| bg_alt | #161e26 |
| ink | #e6e8ea |
| muted | #868a92 |
| rule | #27323c |
| primary | #3f88d1 |
| accent | #d06747 |
| state_ok | #07986f |
| state_warn | #d8650e |
| state_danger | #df5757 |
| on_primary | #0e1318 |
| on_accent | #0e1318 |

Chart categorical: `#2365a7`, `#b84c2c`, `#047857`, `#6366f1`, `#b45309`, `#6b7280`

## Tone family

`editorial-serious` (ver `guides/visual-craftsmanship.md`).

## Best used for

- Informes analíticos y de BI multipágina (5+ páginas)
- Documentos legales, de política, prosa larga
- Entregables institucionales y para steering committees

## Anti-patterns

- No emparejar con transiciones agresivas o degradados en PPTX.
- Evitar como hero de landing de producto tech.
- No sustituir el accent por un segundo primary azul — el único pop
  cálido es lo que hace que el tema se lea como editorial y no como
  corporativo-anónimo.
