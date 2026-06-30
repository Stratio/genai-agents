# Tarea: copiar dentro de HDFS

Copia un fichero/directorio HDFS a una ruta nueva (ambas en el mismo filesystem).

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/copy` |
| Cuerpo | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py cp "<src>" "<dst>" [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado en src (lectura) o dst (escritura) (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
