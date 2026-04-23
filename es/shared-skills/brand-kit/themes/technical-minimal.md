# Technical Minimal

Superficie funcional de baja croma anclada en un primary azul nítido,
con un accent ámbar reservado para lo único que el lector debe notar.
Construido para dashboards, documentación de ingeniería y runbooks —
contenido donde los datos son la historia y el tema debe apartarse.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #0369a1 | títulos de sección, reglas primarias, highlights de KPI |
| ink | #111827 | texto cuerpo |
| muted | #4b5563 | captions, etiquetas secundarias |
| rule | #e5e7eb | divisores, bordes de tabla |
| bg | #ffffff | página / superficie principal |
| bg_alt | #f9fafb | bandas de tabla, rellenos de callout |
| accent | #f59e0b | el único color "mira aquí" |
| state_ok | #047857 | indicadores positivos |
| state_warn | #b45309 | alertas |
| state_danger | #b91c1c | errores críticos |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #0369a1 | coincide con primary |
| 2 | #f59e0b | coincide con accent |
| 3 | #059669 | teal-verde |
| 4 | #dc2626 | rojo (usar con moderación, coherente con state_danger) |
| 5 | #8b5cf6 | violeta para diversidad categórica |
| 6 | #6b7280 | gris muted |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | IBM Plex Sans | 28 | Inter, Arial, sans-serif |
| h2 | IBM Plex Sans | 20 | Inter, Arial, sans-serif |
| body | IBM Plex Sans | 11 | Inter, Arial, sans-serif |
| caption | IBM Plex Sans | 9 | Inter, Arial, sans-serif |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

## Optional extensions

- **Motion budget**: `minimal` (transiciones ajustadas, sin movimiento decorativo)
- **Border radius**: `4px`
- **Dark mode variant**: no incluido (derivar con `bg` = `#0b1220`,
  `ink` = `#e5e7eb`, manteniendo primary y accent)
- **Chart sequential**: color base `#0369a1`

## Tone family

`technical-minimal`.

## Best used for

- Dashboards de ingeniería, herramientas internas, docs SRE / ops
- Runbooks, API docs, especificaciones técnicas
- Vistas densas de datos donde el chrome debe apartarse

## Anti-patterns

- No añadir superficies de fondo cálidas — la baja croma es el punto.
- No usar tamaños de display mayores a los de arriba; este tema
  susurra, no anuncia.
- No emparejar con iconografía ornamental o fondos texturizados.
