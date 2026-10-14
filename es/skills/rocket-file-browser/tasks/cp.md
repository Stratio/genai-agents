# Tarea: copiar dentro de un filesystem

Copia un fichero/directorio a una ruta nueva **en el mismo filesystem** (HDFS o un bucket
S3). Rocket no tiene copia entre filesystems: para copiar de un filesystem a otro, sigue
`tasks/filesystems.md` §Mover datos entre filesystems (descarga + subida).

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/copy` |
| Cuerpo | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--fs` = el filesystem fijado con `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py cp "<src>" "<dst>" --fs <id>:<type>
   ```

## Errores

- `401/403` — no autorizado en src (lectura) o dst (escritura) (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
