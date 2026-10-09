# Tarea: mover/renombrar dentro de HDFS

Mueve o renombra un fichero/directorio HDFS (semántica de move). **Confirma con el usuario
antes** — toda ruta que apuntaba al original deja de resolverse.

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `PUT` |
| Path | `/fileBrowser/update` |
| Cuerpo | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Respuesta | boolean / `OK` |

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Confirma** el origen y el destino exactos con el usuario.
3. **Ejecuta** (`--fs` opcional si solo hay un filesystem):

   ```bash
   python3 scripts/rocket_file_browser.py mv "<src>" "<dst>" [--fs <id>:<type>]
   ```

## Errores

- `401/403` — no autorizado (Gosec). Raíces restringidas rechazadas en cliente.
- Muestra código HTTP + cuerpo verbatim en error.
