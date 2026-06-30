# Tarea: comprimir ficheros HDFS en un archivo

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/compress` |
| Cuerpo | `{"files": ["<r1>", ...], "compressedFile": "<archivo>", "compressionCodec": "<codec>", "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

Codecs válidos: `ZStandard`, `Lz4`, `Snappy`, `Gzip`, `Bzip2`, `Zip` (por defecto), `TarGz`.

> **Rocket añade la extensión del codec** a `compressedFile`. Pasar `out.zip` con codec
> `Zip` produce `out.zip.zip`. Pasa el nombre base sin extensión (p.ej. `out`) o cuenta
> con el sufijo — y usa el nombre completo resultante al extraer.

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py compress "<archivo>" "<src1>" ["<src2>" ...] [--codec Zip] [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
