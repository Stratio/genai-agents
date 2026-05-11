# Canvas Craft — Set de fuentes

Familias OFL curadas que se incluyen con `canvas-craft`. Elegidas para artefactos visuales de una sola página: display editorial, display sans pesada y serif refinado para composiciones con tipografía-como-elemento.

## Familias

| Familia | Rol | Ficheros | Licencia | Origen | Commit SHA | Descargada |
|---|---|---|---|---|---|---|
| Fraunces (variable) | Serif editorial display con ejes de tamaño óptico, peso y wonk | `Fraunces-Variable.ttf`, `Fraunces-Italic-Variable.ttf` | OFL 1.1 | https://github.com/undercasetype/Fraunces (upstream); binario obtenido del mirror `googlefonts/fraunces` | `ad58030f7daa` | 2026-04-20 |
| Archivo Black | Sans display pesada para puntuar la composición visual | `Archivo-Black.ttf`, `Archivo-BlackItalic.ttf` | OFL 1.1 | https://github.com/Omnibus-Type/Archivo | `b5d63988ce19` | 2026-04-20 |
| Instrument Serif | Serif contemporáneo refinado para momentos display y anclajes | `InstrumentSerif-Regular.ttf`, `InstrumentSerif-Italic.ttf` | OFL 1.1 | https://github.com/Instrument/instrument-serif | `65c0ef225f38` | 2026-04-20 |

Cada familia va acompañada de su fichero de licencia (`{Family}-OFL.txt`). Redistribuir un artefacto que embeba estas fuentes requiere mantener el OFL de cada familia usada.

## Solape intencional con otras skills visuales

`Instrument Serif` aparece en más de una skill dentro del monorepo. El solape es deliberado — cada consumidor usa la familia para un propósito distinto (prosa body en un caso, cortes display sobre una composición en el otro). Mantener cada skill con su propia copia preserva el empaquetado standalone a un coste menor de duplicación (~140 KB).

Fuera de esta única familia, el set es disjunto con el de cualquier otra skill visual del monorepo, que tiran de serifs orientadas a body y una mono (Crimson Pro, IBM Plex Serif, Lora, Libre Baskerville, Work Sans, Young Serif, JetBrains Mono).

## Ampliar el set

Se pueden añadir más familias display cuando un artefacto concreto las pida — candidatas: Boldonse (Atipo Foundry), Redaction (Titl Brigade), Playfair Display, DM Serif Display. Descarga desde la distribución oficial del foundry, incluye el OFL.txt y registra la familia y el commit SHA en la tabla de arriba.

## No incluidas

- Space Grotesk — excluida a propósito. La familia está sobrerrepresentada en la salida generada por IA y se lee como una elección por defecto más que como una decisión.
- Inter, Roboto, Arial, system-ui — no se incluyen; si un brief requiere una sans genérica, intenta primero una alternativa distintiva.
