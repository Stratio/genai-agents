# Forensic Audit

Alto contraste, monospace-forward, casi probatorio. El tema se lee
como "este documento es un registro, no un pitch". Construido para
auditores, responsables de compliance e informes de seguridad donde
la precisión, la trazabilidad y la sobriedad pesan más que la calidez
visual.

## Color palette (core)

| Token | Hex | Rol |
|---|---|---|
| primary | #5a1c1c | títulos, cabeceras de hallazgo, marcas de clasificación |
| ink | #121212 | texto cuerpo |
| muted | #5a5550 | metadatos, footnotes, etiquetas de procedencia |
| rule | #cccccc | líneas divisorias, rejillas de tabla |
| bg | #ffffff | página / superficie principal |
| bg_alt | #ecebe8 | sidebar para bloques de chain-of-custody |
| accent | #b45309 | énfasis en hallazgos críticos |
| state_ok | #166534 | indicadores limpios / compliant |
| state_warn | #b45309 | observaciones que requieren atención |
| state_danger | #991b1b | hallazgos críticos / brechas |

## Chart categorical (5–8 colores ordenados)

| # | Hex | Notas |
|---|---|---|
| 1 | #5a1c1c | coincide con primary |
| 2 | #b45309 | coincide con accent |
| 3 | #374151 | slate forense |
| 4 | #65a30d | verde regulatorio |
| 5 | #7c2d12 | óxido más profundo |
| 6 | #111827 | casi negro de relleno |

## Typography

| Rol | Familia | Tamaño (pt) | Fallback |
|---|---|---|---|
| display (h1) | IBM Plex Sans | 24 | Arial, sans-serif |
| h2 | IBM Plex Sans | 16 | Arial, sans-serif |
| body | IBM Plex Mono | 10 | Consolas, monospace |
| caption | IBM Plex Mono | 9 | Consolas, monospace |
| mono | IBM Plex Mono | 10 | Consolas, monospace |

El body en monospace es deliberado: se lee como registro documental y
mantiene identificadores, hashes y strings de evidencia alineados y
legibles.

## Optional extensions

- **Motion budget**: `minimal` (sin transiciones decorativas; los
  documentos probatorios no animan)
- **Border radius**: `0px` (bordes duros)
- **Dark mode variant**: ver [Dark mode](#dark-mode)
- **Chart sequential**: color base `#5a1c1c`

## Dark mode

| Token | Hex |
|---|---|
| bg | #180e0e |
| bg_alt | #261616 |
| ink | #eae6e6 |
| muted | #908c88 |
| rule | #3c2727 |
| primary | #c66868 |
| accent | #d3630e |
| state_ok | #259851 |
| state_warn | #d3630e |
| state_danger | #da5a5a |
| on_primary | #180e0e |
| on_accent | #180e0e |

Chart categorical: `#aa3c3c`, `#b45309`, `#536177`, `#65a30d`, `#a63f1b`, `#486093`

## Tone family

`forensic-audit`.

## Best used for

- Informes de auditoría interna y externa
- Reporting regulatorio y de compliance
- Informes de incidentes de seguridad, registros de hallazgos
- Cadena de custodia, due diligence y documentos de investigación

## Anti-patterns

- No usar como default para informes de BI generales — el tono es
  demasiado severo y señala "se está investigando algo".
- No sustituir el body monospace por un serif o sans proporcional;
  la legibilidad probatoria es lo que define el tema.
- No añadir iconografía decorativa ni neutros cálidos.
