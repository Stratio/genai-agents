# Corporate Formal

La paleta tradicional de oficina — un navy corporativo profundo, un
azul de negocio más brillante para énfasis secundario, tipografía
system-safe que renderiza idéntica en cualquier máquina. Construido
para steering committees, packets de consejo y reporting regulado
donde el entregable debe sentirse institucional y universalmente
legible.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #1a365d | cabeceras, pies, bloques de portada |
| ink | #1a202c | texto cuerpo |
| muted | #4a5568 | captions, notas al pie |
| rule | #e2e8f0 | divisores, bordes de tabla |
| bg | #ffffff | página / superficie principal |
| bg_alt | #f7fafc | bandas de tabla, callouts |
| accent | #3182ce | énfasis secundario, enlaces, highlights de chart |
| state_ok | #38a169 | indicadores positivos |
| state_warn | #d69e2e | alertas |
| state_danger | #e53e3e | errores críticos |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #1a365d | coincide con primary |
| 2 | #3182ce | coincide con accent |
| 3 | #38a169 | verde de negocio |
| 4 | #d69e2e | ámbar corporativo |
| 5 | #805ad5 | violeta (diversidad categórica) |
| 6 | #e53e3e | rojo (usar con moderación, coherente con state_danger) |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Calibri | 24 | Aptos, Arial, sans-serif |
| h2 | Calibri | 16 | Aptos, Arial, sans-serif |
| body | Calibri | 11 | Aptos, Arial, sans-serif |
| caption | Calibri | 9 | Aptos, Arial, sans-serif |
| mono | Consolas | 10 | Courier New, monospace |

La elección system-safe (Calibri / Aptos / Arial) es deliberada: los
informes corporativos deben renderizar idéntico en cualquier máquina,
incluidas instalaciones de Office sin fuentes custom embebidas.

## Optional extensions

- **Motion budget**: `minimal` (el contenido corporativo no anima)
- **Border radius**: `2px`
- **Dark mode variant**: no incluido
- **Chart sequential**: color base `#1a365d`

## Print variant (para pdf-writer)

Los documentos corporativos impresos se benefician de un papel
ligeramente más cálido y un casi negro más suave para evitar la
sensación clínica de blanco puro + negro puro:

| Token | Hex | Notas |
|---|---|---|
| paper | #fafaf8 | casi blanco, con calidez muy sutil |
| ink | #1a1a1a | casi negro cálido (más suave que el negro puro) |
| rule | #dcdfe4 | tinte de hairline, ligeramente más cálido que el rule de pantalla |
| accent | #3182ce | sin cambios — el azul de negocio imprime bien |

Tamaños de fuente y tipografía iguales que en el bloque core.

## Tone family

`editorial-serious` (variante corporativa con tipografía system-safe).

## Best used for

- Packets de consejo e informes para steering committees
- Filings regulatorios, informes anuales, revisiones trimestrales
- Memos internos y documentos de política corporativa
- Cualquier entregable donde "debe renderizar igual en todos los
  portátiles" sea una restricción dura

## Anti-patterns

- No sustituir las fuentes system-safe por una familia custom — el
  sentido del tema es la renderización universal.
- No añadir accents cálidos o vivos; la paleta debe quedarse dentro
  del rango azul corporativo.
- No usar para marketing orientado a consumidor, donde se lee como
  anticuado y genérico.
