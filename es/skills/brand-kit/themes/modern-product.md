# Modern Product

Lenguaje visual contemporáneo de producto tech: primary índigo, un
accent ámbar para el énfasis, superficies redondeadas y una sans
geométrica en todo. Construido para decks de lanzamiento de producto,
anuncios de features, material de pitch y documentación interna de
producto que requiere una voz contemporánea confiada.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #6366f1 | cabeceras, callouts de feature, toques de marca |
| ink | #0f172a | texto cuerpo |
| muted | #64748b | etiquetas secundarias, captions |
| rule | #e2e8f0 | divisores, bordes de tarjeta |
| bg | #ffffff | página / superficie principal |
| bg_alt | #f8fafc | fondos de sección, tarjetas |
| accent | #f59e0b | el único pop cálido contra el primary frío |
| state_ok | #10b981 | éxito, estados completados |
| state_warn | #f59e0b | alertas (mismo tono que accent; afinar según contexto) |
| state_danger | #ef4444 | errores críticos |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #6366f1 | coincide con primary |
| 2 | #f59e0b | coincide con accent |
| 3 | #10b981 | esmeralda |
| 4 | #06b6d4 | cian — complementario tech-producto |
| 5 | #ec4899 | rosa — diferenciación categórica |
| 6 | #8b5cf6 | violeta — tono cercano al primary, último en orden |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | DM Sans | 32 | Inter, system-ui, sans-serif |
| h2 | DM Sans | 22 | Inter, system-ui, sans-serif |
| body | DM Sans | 11 | Inter, system-ui, sans-serif |
| caption | DM Sans | 9 | Inter, system-ui, sans-serif |
| mono | JetBrains Mono | 10 | Consolas, monospace |

## Optional extensions

- **Motion budget**: `expressive` (los decks de producto permiten
  movimiento deliberado: reveals por fases, transiciones suaves,
  métricas animadas)
- **Border radius**: `12px` (superficies característicamente redondeadas)
- **Dark mode variant**: `bg` = `#0f172a`, `ink` = `#e2e8f0`,
  `primary` = `#818cf8`, `accent` = `#fbbf24`
- **Chart sequential**: color base `#6366f1`

## Tone family

`technical-minimal` (con ajustes más cálidos y expresivos).

## Best used for

- Decks de lanzamiento de producto y presentaciones de pitch
- Landings de marketing SaaS y anuncios de feature
- Documentos internos de equipo de producto (PRDs, roadmaps, retros)
  que requieren una voz pulida

## Anti-patterns

- No usar para documentos legales, de compliance o auditoría — el
  tono está demasiado orientado a marketing.
- No combinar con titulares serif; la sans geométrica es la voz.
- No saturar la paleta añadiendo más tonos vivos al chart categorical
  — los seis ya presionan el límite superior.
