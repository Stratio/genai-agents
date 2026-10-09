# Tarea: listar una ruta

Lista el contenido de un directorio (o stat de un fichero) en un filesystem de Rocket
(HDFS o un bucket S3).

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `POST` |
| Path | `/fileBrowser/findByPath` |
| Cuerpo | `{"pathHdfs": "<ruta>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Respuesta | array JSON de `{name, type, size, owner, group, permissions, lastUpdated}` |

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y cert cliente presente (ver `SKILL.md`).
2. **Ejecuta** (`--fs` = el filesystem fijado con `tasks/filesystems.md`). Si el usuario no da ruta, empieza por
   el `defaultPath` de ese filesystem (del listado de `filesystems`):

   ```bash
   python3 scripts/rocket_file_browser.py ls "<ruta>" --fs <id>:<type>
   ```

## Errores

- `401/403` — no autorizado para esa ruta (Gosec). En S3 se comprueba contra
  `/<bucket><ruta>`. Las raíces restringidas se rechazan en cliente.
- Muestra código HTTP + cuerpo verbatim en error (`guides/external-api-calls.md` §5).
