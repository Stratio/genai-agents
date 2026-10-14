# Tarea: descargar un fichero de Rocket

Trae un fichero del File Browser de Rocket — su HDFS o un bucket S3 configurado — al
workspace del sandbox.

## Endpoint (lo gestiona el script)

| | |
|---|---|
| Método | `POST` |
| Path | `/fileBrowser/download` |
| Cuerpo | `{"pathHdfs": "<ruta>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Respuesta | los bytes crudos del fichero (streaming) |

> El script usa la variante POST. El gemelo GET
> (`GET /fileBrowser/download?path=<r>[&filesystemId=&filesystemType=]`, que además
> sigue aceptando el nombre antiguo `pathHdfs`) existe para que un navegador pueda
> guardar un fichero grande navegando a él; autoriza con el mismo mensaje de actor, así
> que ambos dan exactamente el mismo acceso. Sirven los dos — POST mantiene la ruta
> fuera de los logs de acceso.

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y el cert cliente presente (ver
   prerrequisitos en `SKILL.md`). Si falta, para y di cuál.

2. **Filesystem** — usa el fijado para esta conversación; si aún no hay ninguno, sigue
   `tasks/filesystems.md` (listar, usar el único o preguntar al usuario). El fichero se
   busca solo en ese filesystem.

3. **Descarga**:

   ```bash
   python3 scripts/rocket_file_browser.py download \
     "<ruta>" "<destino_local>" --fs <id>:<type>
   ```

   - `<ruta>`: ruta absoluta en ese filesystem, p.ej. `/data/kk/report.json` (en S3,
     relativa a la raíz del bucket: `/landing/a.csv`). Un directorio se descarga como zip construido al vuelo (sujeto al límite de tamaño del servidor).
   - `<destino_local>`: ruta de fichero local, o un directorio (se conserva el nombre
     remoto) — en la carpeta de la tarea actual (o en el workspace), no en `/tmp`.

## Salida esperada

```
Downloaded /data/kk/report.json [hdfs1.s000001-datastores:HDFS] -> /root/project/report.json (6521 bytes)
```

## Errores

- `401/403` — la identidad del certificado no está autorizada para esa ruta (Gosec; en
  S3 se comprueba contra `/<bucket><ruta>`).
- Ruta no encontrada o error de filesystem — espera HTTP 500 más que 404 (Rocket informa
  de una ruta inexistente como 500; ver `tasks/ls.md`). Revisa el filesystem antes que la
  ruta: el fichero puede estar en otro. Muestra el código HTTP + cuerpo verbatim.
- Raíces restringidas (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
  `/mlProjectExecutionsArtifacts`) se rechazan en cliente antes de la llamada.

Ver `guides/external-api-calls.md` §5 para leer los códigos HTTP habituales.
