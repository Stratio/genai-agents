# Tarea: crear un directorio

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `POST` |
| Path | `/fileBrowser/createDir` |
| Cuerpo | `{"pathHdfs": "<ruta>", "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--fs` = el filesystem fijado con `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py mkdir "<ruta>" --fs <id>:<type>
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- En S3 un directorio es un prefijo de clave: el "directorio" existe como marcador vacío
  hasta que se escribe un fichero dentro.
- Muestra código HTTP + cuerpo verbatim en error.
