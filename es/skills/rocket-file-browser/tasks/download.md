# Tarea: descargar un fichero del HDFS de Rocket

Trae un fichero del File Browser HDFS de Rocket al workspace del sandbox.

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `POST` |
| Path | `/fileBrowser/download` |
| Cuerpo | `{"pathHdfs": "<ruta>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Respuesta | los bytes crudos del fichero (streaming) |

> Usa la variante POST, no `GET /fileBrowser/download?pathHdfs=` — el GET fuerza el
> filesystem interno y no puede apuntar a un datastore con nombre.

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y el cert cliente presente (ver
   prerrequisitos en `SKILL.md`). Si falta, para y di cuál.

2. **Resuelve el filesystem** si no lo conoces:

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   # p.ej. [{"id":"hdfs1.s000001-datastores","type":"HDFS","defaultPath":"/user/..."}]
   ```

   Cuando solo hay un filesystem el script lo elige solo, así que `--fs` es opcional.
   Pasa `--fs <id>:<type>` solo si hay varios.

3. **Descarga**:

   ```bash
   python3 scripts/rocket_file_browser.py download \
     "<ruta_hdfs>" "<destino_local>" [--fs <id>:<type>]
   ```

   - `<ruta_hdfs>`: ruta absoluta en HDFS, p.ej. `/data/kk/report.json`.
   - `<destino_local>`: ruta de fichero local, o un directorio (se conserva el nombre).

## Salida esperada

```
Downloaded /data/kk/report.json -> /root/project/report.json (6521 bytes)
```

## Errores

- `401/403` — la identidad del certificado no está autorizada para esa ruta (Gosec).
- `404`/`500` — ruta no encontrada o error de filesystem. Muestra el código HTTP + cuerpo verbatim.
- Raíces restringidas (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
  `/mlProjectExecutionsArtifacts`) se rechazan en cliente antes de la llamada.

Ver `guides/external-api-calls.md` §5 para leer los códigos HTTP habituales.
