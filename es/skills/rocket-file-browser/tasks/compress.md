# Tarea: comprimir ficheros HDFS en un archivo

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/compress` |
| Cuerpo | `{"files": ["<r1>", ...], "compressedFile": "<archivo>", "compressionCodec": "<codec>", "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

Desde ROCK #5384 el archivo se escribe **directo al filesystem, entrada a entrada** — no
se usa el disco del pod de Rocket, así que el límite práctico es el tamaño total de los
orígenes, no el espacio temporal del pod.

Codecs:

| Tipo | Codecs | Orígenes |
|---|---|---|
| Archivo (multi-fichero) | `Zip` (por defecto), `TarGz`, `TarZstd` | uno o varios ficheros/directorios |
| Flujo (un solo fichero) | `ZStandard`, `Lz4`, `Snappy`, `Gzip`, `Bzip2` | exactamente un **fichero** |

`TarZstd` es nuevo en esta versión. El script rechaza varios orígenes con un codec de
flujo antes de llamar.

> **Rocket añade la extensión del codec** a `compressedFile`: `out` + `TarZstd` →
> `out.tar.zst`. Pasa el nombre base sin extensión y usa el nombre completo resultante
> al extraer.

> **El destino no debe existir**: si existe, Rocket responde `Cannot compress file(s):
> Destination file <ruta> exits`. Su directorio padre se crea si falta.

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py compress "<archivo>" "<src1>" ["<src2>" ...] [--codec Zip] [--fs <id>:<type>]
   ```

## Errores

- `Destination file ... exits` — elige otro nombre o bórralo antes.
- `The total size is larger than the maximum allowed` — la suma de los orígenes supera
  `file-browser.max-content-length` (por defecto 5 GB).
- `There is no available compression method for this codec and number of source files` —
  se dio un directorio o varios orígenes a un codec de flujo; usa `Zip`/`TarGz`/`TarZstd`.
- `Codec not loaded` — el codec nativo no está disponible en ese Rocket (típicamente
  `ZStandard`); usa otro.
- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
