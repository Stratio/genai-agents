# Tarea: borrar ficheros/directorios

Borra una o varias rutas en un filesystem de Rocket (HDFS o un bucket S3). **Destructivo —
confirma con el usuario antes.**

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `DELETE` |
| Path | `/fileBrowser/delete` |
| Cuerpo | `{"files": [{"path": "<r1>"}, ...], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Confirma** las rutas exactas **y el filesystem** con el usuario — no se puede
   deshacer, y la misma ruta puede existir en otro filesystem.
3. **Ejecuta** (`--fs` = el filesystem fijado con `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py rm "<ruta>" ["<ruta2>" ...] --fs <id>:<type>
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
