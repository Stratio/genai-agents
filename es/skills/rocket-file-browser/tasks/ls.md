# Tarea: listar una ruta HDFS

Lista el contenido de un directorio (o stat de un fichero) en el HDFS de Rocket.

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `POST` |
| Path | `/fileBrowser/findByPath` |
| Cuerpo | `{"pathHdfs": "<ruta>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Respuesta | array JSON de `{name, type, size, owner, group, permissions, lastUpdated}` |

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y cert cliente presente (ver `SKILL.md`).
2. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py ls "<ruta_hdfs>" [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado para esa ruta (Gosec). Las raíces restringidas se rechazan en cliente.
- Muestra código HTTP + cuerpo verbatim en error (`guides/external-api-calls.md` §5).
