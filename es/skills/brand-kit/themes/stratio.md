# Stratio

El aspecto propio de Stratio, el mismo que ya tiene GenAI UI: títulos en Deep
Navy y Stratio Blue (action-7) para lo que se puede pulsar y las cifras que importan,
sobre blanco y las superficies frías space-1 en modo claro; el fondo space-17 y
las superficies space-14 de GenAI UI en modo oscuro. Todos los colores salen de
las escalas SDS (space, action, turquoise, peach, coral, lavender). El tema por
defecto cuando nadie pide otro aspecto.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #0f1b27 | títulos, reglas superiores, acentos de portada (Deep Navy, space-17) |
| ink | #27323d | texto cuerpo (space-13) |
| muted | #566574 | captions, notas al pie (space-8) |
| rule | #cdd6df | divisores finos y bordes sutiles (space-3) |
| bg | #ffffff | página / superficie principal |
| bg_alt | #f3f6f8 | bandas de tabla, rellenos de callout (space-1) |
| accent | #0059b8 | CTAs, enlaces, cifras clave (action-7: el Stratio Blue sobre el que se lee texto blanco) |
| state_ok | #006466 | indicadores positivos (turquoise-8) |
| state_warn | #8a5403 | alertas (peach-9) |
| state_danger | #c92822 | errores críticos (coral-7) |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #0076df | Stratio Blue (action-6) |
| 2 | #008c8a | turquoise-7 |
| 3 | #b0740c | peach-8, el dorado de marca con contraste para marcas |
| 4 | #ef4034 | coral-6 |
| 5 | #823eff | lavender-6 |
| 6 | #566574 | space-8 (relleno para series largas) |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Inter | 28 weight 700 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| h2 | Inter | 18 weight 600 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| body | Inter | 11 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| caption | Inter | 9 | system-ui, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif |
| mono | Roboto Mono | 10 | SF Mono, Menlo, Consolas, monospace |

Inter y Roboto Mono son las fuentes de la marca. Donde no están instaladas, la
sans del sistema (San Francisco, Segoe UI, Roboto) mantiene el aspecto.

## Optional extensions

- **Motion budget**: `restrained` (transiciones web-craft, animaciones pptx)
- **Border radius**: `4px` (web-craft)
- **Dark mode variant**: ver [Dark mode](#dark-mode)
- **Chart sequential**: `#0076df` (la escala action de SDS, de action-0 `#e6f3ff` a action-9 `#002d6b`)

## Print variant (para pdf-writer)

| Token | Hex | Notas |
|---|---|---|
| paper | #ffffff | blanco, como los documentos de la marca |
| ink | #0f1b27 | el texto en Deep Navy imprime más nítido que space-13 |
| rule | #cdd6df | space-3 |
| accent | #0059b8 | sin cambios |

## Dark mode

| Token | Hex |
|---|---|
| bg | #0f1b27 |
| bg_alt | #212c38 |
| ink | #f3f6f8 |
| muted | #aab7c4 |
| rule | #3d4a57 |
| primary | #ffffff |
| accent | #6db3f3 |
| state_ok | #41ccbc |
| state_warn | #fdbd2b |
| state_danger | #ff998a |
| on_primary | #0f1b27 |
| on_accent | #0f1b27 |

Chart categorical: `#399aef`, `#1fbfb2`, `#fdbd2b`, `#fc7060`, `#be8fff`, `#9aa9b8`

## Tone family

`technical-minimal` (ver `guides/visual-craftsmanship.md`).

## Best used for

- Cualquier entregable cuando nadie pide otro aspecto
- Informes, dashboards y documentos que se comparten fuera con la marca Stratio
- Páginas que conviven con GenAI UI y deben parecer parte de ella

## Anti-patterns

- Stratio Blue solo para lo que se puede pulsar, cifras clave y la primera
  serie; los títulos van en Deep Navy.
- El blanco sobre Stratio Blue `#0076df` da 4,45:1, por debajo de 4,5: botones
  y enlaces usan action-7 `#0059b8` (el accent); `#0076df` queda para series de
  gráficos y marcas grandes.
- No cambiar los grises space por grises neutros: su sesgo azul es la marca.
