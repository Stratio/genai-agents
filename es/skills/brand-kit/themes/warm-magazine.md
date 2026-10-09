# Warm Magazine

Calidez editorial: una terracota sólida como anclaje, una display
condensada contra un serif clásico de cuerpo. Se lee como una pieza
larga de una revista mensual, no como un output corporativo. Construido
para storytelling, comunicaciones y contenido de marketing.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #8a3324 | títulos, reglas de sección, capitulares |
| ink | #1c1917 | texto cuerpo |
| muted | #78716c | captions, pull quotes, bylines |
| rule | #e7e5e4 | divisores y bordes finos |
| bg | #ffffff | página / superficie principal |
| bg_alt | #fafaf9 | sidebars, bloques de cita |
| accent | #d97706 | kickers, highlights, color de dateline |
| state_ok | #15803d | indicadores positivos |
| state_warn | #b45309 | alertas |
| state_danger | #991b1b | errores críticos |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #8a3324 | coincide con primary |
| 2 | #d97706 | coincide con accent |
| 3 | #047857 | teal profundo (complementario a los cálidos) |
| 4 | #1e40af | azul editorial |
| 5 | #7c2d12 | marrón quemado más profundo |
| 6 | #6b7280 | neutro de relleno |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Big Shoulders Display | 36 | Impact, Arial Black, sans-serif |
| h2 | Big Shoulders Display | 24 | Impact, Arial Black, sans-serif |
| body | Lora | 11 | Georgia, serif |
| caption | Lora Italic | 9 | Georgia, serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

## Optional extensions

- **Motion budget**: `expressive` (el tono de revista invita a
  movimiento considerado: reveals deliberados, no fundidos mecánicos)
- **Border radius**: `0px` (la geometría editorial tiene bordes duros)
- **Dark mode variant**: ver [Dark mode](#dark-mode)
- **Chart sequential**: color base `#8a3324`

## Dark mode

| Token | Hex |
|---|---|
| bg | #18100e |
| bg_alt | #261a16 |
| ink | #eae7e6 |
| muted | #908c89 |
| rule | #3c2b27 |
| primary | #cc6957 |
| accent | #d97706 |
| state_ok | #1b994a |
| state_warn | #d8650e |
| state_danger | #da5a5a |
| on_primary | #18100e |
| on_accent | #18100e |

Chart categorical: `#a8402e`, `#d97706`, `#047857`, `#2e56d7`, `#aa401c`, `#6b7280`

## Tone family

`warm-magazine`.

## Best used for

- Newsletters internos y briefings extensos
- Marketing y storytelling de marca
- Informes donde la narrativa importa tanto como los datos

## Anti-patterns

- No suavizar la display con letter-spacing ni pesos más ligeros —
  el tema se apoya en un titular condensado con cuerpo.
- No emparejar con fondos azules fríos; el anclaje cálido debe
  dominar.
- No usar para documentos legales o de compliance — la voz es
  demasiado narrativa para un tono regulado.
