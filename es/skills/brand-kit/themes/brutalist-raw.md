# Brutalist Raw (draft v1)

Sin pulir, alto contraste, intencionalmente sin ornamento. Superficie
casi negra sobre blanco roto, un naranja industrial saturado como
accent, monospace en todo. El tema se lee como "aquí están los datos
expuestos" — construido para informes exploratorios sin procesar,
documentos orientados a desarrollo, volcados de datos y cualquier
entregable donde la pulcritud resultaría deshonesta.

> **Draft v1** — este tema se diseñó para este kit desde el tono
> `brutalist-raw` definido en `skills-guides/visual-craftsmanship.md`. No hay
> precedente directo en el monorepo. Itérese según feedback de los
> primeros usos.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #111111 | todo lo estructural — cabeceras, reglas, bordes |
| ink | #111111 | texto cuerpo (igual que primary — tema de un solo croma) |
| muted | #525252 | etiquetas secundarias, comentarios |
| rule | #111111 | reglas gruesas (para usar a 2–3 pt de grosor) |
| bg | #fafafa | página blanco roto |
| bg_alt | #ededed | bloques, bandas de tabla |
| accent | #ff3d00 | el único pop saturado — solo para énfasis crítico |
| state_ok | #16a34a | indicadores positivos |
| state_warn | #ff8c00 | alertas (coherentes con la calidez del accent) |
| state_danger | #dc2626 | errores críticos |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #111111 | coincide con primary |
| 2 | #ff3d00 | coincide con accent |
| 3 | #525252 | gris medio |
| 4 | #16a34a | verde industrial |
| 5 | #ff8c00 | segundo cálido |
| 6 | #737373 | neutro de relleno |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | IBM Plex Sans | 34 weight 700 | Arial Black, sans-serif |
| h2 | IBM Plex Sans | 22 weight 700 | Arial Black, sans-serif |
| body | IBM Plex Mono | 10 | Consolas, monospace |
| caption | IBM Plex Mono | 9 | Consolas, monospace |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

Sans pesada para titulares, monospace para todo lo demás. El
contraste de pesos (display en bold contra monospace en regular) es
la firma tipográfica del tema.

## Optional extensions

- **Motion budget**: `minimal` (el brutalismo no anima)
- **Border radius**: `0px` (bordes duros, siempre)
- **Dark mode variant**: `bg` = `#111111`, `ink` = `#fafafa`,
  mantener `primary` y `accent`
- **Chart sequential**: color base `#111111`

## Tone family

`brutalist-raw`.

## Best used for

- Informes de análisis exploratorio de datos (primera pasada,
  hallazgos en bruto)
- Documentación orientada a desarrolladores y post-mortems de
  ingeniería
- Volcados de datos, análisis de logs, informes de debug
- Cualquier artefacto donde "pulido" se leería como deshonesto sobre
  el estado del contenido

## Anti-patterns

- No suavizar con esquinas redondeadas, sombras o gradientes — eso
  contradice el tono directamente.
- No usar para entregables a cliente o ejecutivos.
- No expandir el accent a superficies grandes; el naranja saturado
  es una luz de advertencia, no un envoltorio de marca.
