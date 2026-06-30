# Tarea: borrar ficheros/directorios HDFS

Borra una o varias rutas en el HDFS de Rocket. **Destructivo — confirma con el usuario antes.**

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `DELETE` |
| Path | `/fileBrowser/delete` |
| Cuerpo | `{"files": [{"path": "<r1>"}, ...], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Confirma** las rutas exactas con el usuario — no se puede deshacer.
3. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py rm "<ruta_hdfs>" ["<ruta_hdfs2>" ...] [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
