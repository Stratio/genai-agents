# Tarea: subir un fichero al HDFS de Rocket

Empuja un fichero local del sandbox a un directorio HDFS de Rocket.

Desde Rocket 4.x (ROCK #5384) es una **sola petición**, gestionada por el script:

`POST /fileBrowser/upload?path=<dir_hdfs>[&filesystemId=<id>&filesystemType=<type>]`
con el fichero en la parte multipart `binary`.

- La escritura se **autoriza antes de aceptar un solo byte**, así que a quien no tenga
  permiso sobre `path` se le rechaza sin haber transferido el fichero.
- Los bytes van **en streaming directo al filesystem** — ya no se escribe nada en el
  disco del pod de Rocket.
- El fichero se guarda bajo `path` con el nombre que lleva la parte multipart, y la
  petición se **rechaza si ese nombre ya existe** (no sobrescribe). Borra o renombra
  antes, o sube con otro nombre.
- La respuesta es `200` con la ruta donde quedó almacenado.

El flujo antiguo de dos peticiones (`POST /fileBrowser/uploadLocalFile` →
`POST /fileBrowser/putLocalFileToHdfs`, con su reintento del HTTP 420) sigue existiendo
por compatibilidad. El script repliega a él automáticamente si el servidor responde
404/405 a la ruta de una sola petición, y `--legacy` lo fuerza.

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y el cert cliente presente (ver `SKILL.md`).

2. **Resuelve el filesystem** si no lo conoces (`--fs` opcional si solo hay uno):

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   ```

3. **Sube**:

   ```bash
   python3 scripts/rocket_file_browser.py upload \
     "<origen_local>" "<dir_hdfs>" [--fs <id>:<type>] [--legacy]
   ```

   - `<origen_local>`: fichero local existente en el sandbox.
   - `<dir_hdfs>`: **directorio** HDFS destino (absoluto); el fichero conserva su nombre.

## Salida esperada

```
Uploaded /root/project/Screenshot.png -> /data/kk/LoadDocument/Screenshot.png
```

Con el repliegue antiguo, antes aparece una línea `Phase 1 OK: staged at /tmp/uploads/...`.

## Notas y errores

- El tamaño máximo de subida es el `file-browser.max-content-length` del servidor
  (por defecto 5 GB); los ficheros muy grandes pueden dar timeout — muestra el cuerpo
  verbatim si pasa.
- `Target <ruta> already exists` — el nombre destino ya está ocupado; la subida se
  rechaza antes de la transferencia.
- Un `<dir_hdfs>` relativo se rechaza (Rocket solo acepta rutas absolutas en el File
  Browser).
- Un nombre de fichero que HDFS o S3 no admiten (dos puntos, llaves) se rechaza antes de
  la transferencia.
- `401/403` — no autorizado para ese directorio destino (Gosec).
- El `420` solo aparece en el flujo antiguo — una subida concurrente mantuvo el slot
  ocupado; el script reintenta con backoff y avisa si no se libera.
- Las raíces restringidas se rechazan en cliente antes de la llamada.

Ver `guides/external-api-calls.md` §5 para leer los códigos HTTP habituales.
