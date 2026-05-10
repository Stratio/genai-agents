# Industrial Utilitarian (draft v1)

Azul-gris pizarra sobre página neutra, ámbar para señalización, una
sans grotesca en todo. Se lee como funcional y desapasionado —
diseñado para informes de operaciones, dashboards de logística,
post-mortems de SRE y cualquier contenido donde el lenguaje visual
deba resonar con el lenguaje físico de salas de control y señalética.

> **Draft v1** — este tema se diseñó para este kit desde el tono
> `industrial-utilitarian` definido en `skills-guides/visual-craftsmanship.md`.
> Inspiración laxa tomada de la paleta base `corporate-formal` en el
> monorepo, pero el tono se desplaza deliberadamente hacia lo
> funcional / de señalización. Itérese según feedback de los primeros
> usos.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #37474f | cabeceras, reglas, marcas de sección |
| ink | #1f2933 | texto cuerpo |
| muted | #52606d | etiquetas secundarias |
| rule | #cbd2d9 | divisores, bordes |
| bg | #f5f7fa | página neutra clara (no blanco) |
| bg_alt | #e4e7eb | bloques de callout, barras de estado |
| accent | #f5a623 | ámbar de señalización — el color "atención" |
| state_ok | #3d7a3d | verde operativo |
| state_warn | #f5a623 | alertas (mismo tono que accent) |
| state_danger | #c62828 | errores críticos / incidentes |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #37474f | coincide con primary |
| 2 | #f5a623 | coincide con accent |
| 3 | #3d7a3d | verde operativo |
| 4 | #c62828 | rojo de incidente |
| 5 | #5c6ac4 | azul acero (diversidad categórica) |
| 6 | #6b7b80 | neutro de relleno |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | Inter | 28 weight 700 | Arial, sans-serif |
| h2 | Inter | 18 weight 600 | Arial, sans-serif |
| body | Inter | 10 | Arial, sans-serif |
| caption | Inter | 9 | Arial, sans-serif |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

Sans grotesca en todo. Tamaño de body menor (10 pt) porque el tono
acepta — y espera — información más densa por vista.

## Optional extensions

- **Motion budget**: `minimal`
- **Border radius**: `2px`
- **Dark mode variant**: `bg` = `#1f2933`, `ink` = `#e4e7eb`,
  `primary` = `#90a4ae`, mantener `accent`
- **Chart sequential**: color base `#37474f`

## Tone family

`industrial-utilitarian`.

## Best used for

- Dashboards de operaciones y logística, informes SRE
- Post-mortems de incidentes, ops reviews
- Informes de planta / instalaciones, documentos de estado de cadena
  de suministro
- Cualquier contexto donde la estética de señalética, sala de control
  y hardware industrial sea un eco apropiado

## Anti-patterns

- No usar para marketing, entregables a cliente ni narrativos — el
  tono es deliberadamente funcional y se lee como "herramienta interna".
- No sustituir el accent ámbar por un segundo azul; la señal cálida
  contra la base fría es el mecanismo del tema.
- No añadir iconografía decorativa ni formas redondeadas; el tema se
  inclina hacia bordes duros y geometría utilitaria.
