# Tarea: crear un directorio en HDFS

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `POST` |
| Path | `/fileBrowser/createDir` |
| Cuerpo | `{"pathHdfs": "<ruta>", "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py mkdir "<ruta_hdfs>" [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
