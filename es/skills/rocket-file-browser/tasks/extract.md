# Tarea: extraer un archivo HDFS

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/extract` |
| Cuerpo | `{"files": [{"path": "<archivo>", "newPath": "<dest?>"}], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--dest` y `--fs` opcionales):

   ```bash
   python3 scripts/rocket_file_browser.py extract "<archivo>" [--dest "<dir_hdfs>"] [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
