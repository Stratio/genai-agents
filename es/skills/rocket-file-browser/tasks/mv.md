# Tarea: mover/renombrar dentro de un filesystem

Mueve o renombra un fichero/directorio **en el mismo filesystem** (semántica de move).
**Confirma con el usuario antes** — toda ruta que apuntaba al original deja de resolverse.

Rocket no tiene movimiento entre filesystems: mover de un filesystem a otro es descarga +
subida + `rm` del origen, según `tasks/filesystems.md` §Mover datos entre filesystems.
En S3 un move es copia + borrado, no un renombrado atómico: lento en árboles grandes, y un
movimiento interrumpido puede dejar ambas copias — dilo al confirmar un directorio grande.

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/update` |
| Cuerpo | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Confirma** el origen, el destino y el filesystem exactos con el usuario.
3. **Ejecuta** (`--fs` = el filesystem fijado con `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py mv "<src>" "<dst>" --fs <id>:<type>
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
