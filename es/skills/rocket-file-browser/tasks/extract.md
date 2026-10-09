# Tarea: extraer un archivo HDFS

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/extract` |
| Cuerpo | `{"files": [{"path": "<archivo>", "newPath": "<destino>"}], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

Desde ROCK #5384 la extracción va en streaming entrada a entrada al filesystem, sin
disco local en el pod de Rocket. Lo que cambia para quien llama:

- **El tipo de archivo se detecta por contenido, no por nombre** — un `.tar.zst`, un
  `.tar.gz`, un `.gz` simple, un `.zip` o un fichero sin extensión se leen por lo que
  son. Zip, tar, tar+gzip y tar+zstd se tratan como archivos; un fichero comprimido de
  flujo (`.gz`, `.bz2`, `.zst`, `.snappy`, `.lz4`) se descomprime a su nombre sin la
  extensión.
- **Los directorios vacíos dentro de un zip ahora se recrean** (antes se perdían).
- Una entrada cuyo nombre escribiría **fuera del destino** (`../…`, nombres absolutos)
  aborta la extracción.
- Una extracción fallida **deshace solo lo que creó**; el contenido previo del destino
  se respeta.
- `newPath` es **obligatorio** en el servidor. El script lo pone por defecto al
  directorio del propio archivo y lo indica; usa `--dest` para elegir otro. El destino
  se crea si no existe y debe ser un directorio.

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--dest` y `--fs` opcionales):

   ```bash
   python3 scripts/rocket_file_browser.py extract "<archivo>" [--dest "<dir_hdfs>"] [--fs <id>:<type>]
   ```

## Errores

- `Compressed file ... has a size larger than the maximum allowed` — el archivo supera
  `file-browser.max-content-length` (por defecto 5 GB).
- `Destination ... must be a directory` / `Source file ... cannot be a directory`.
- `the archive holds an entry whose name would write it outside <destino>` — rechazado
  como archivo con path traversal.
- `Unsupported file extension and codec` — el fichero no es un archivo ni algo que un
  codec del filesystem pueda descomprimir.
- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
