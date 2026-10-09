# Tarea: subir un fichero a Rocket

Empuja un fichero local del sandbox a un directorio de un filesystem de Rocket — su HDFS
o un bucket S3 configurado.

Desde Rocket 4.x (ROCK #5384) es una **sola petición**, gestionada por el script:

`POST /fileBrowser/upload?path=<dir>&filesystemId=<id>&filesystemType=<type>`
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
`POST /fileBrowser/putLocalFileToHadoopFs`, con su reintento del HTTP 420; también
lleva el `targetFilesystem`) sigue existiendo
por compatibilidad. El script repliega a él automáticamente si el servidor responde
404/405 a la ruta de una sola petición, y `--legacy` lo fuerza.

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y el cert cliente presente (ver `SKILL.md`).

2. **Filesystem** — usa el fijado para esta conversación; si aún no hay ninguno, sigue
   `tasks/filesystems.md`. Si hay varios y el usuario no dijo dónde, pregunta: subir al
   bucket equivocado es publicar en el sitio equivocado. Incluye el filesystem en el
   destino que confirmas con el usuario.

3. **Sube**:

   ```bash
   python3 scripts/rocket_file_browser.py upload \
     "<origen_local>" "<dir>" --fs <id>:<type> [--legacy]
   ```

   - `<origen_local>`: fichero local existente en el sandbox.
   - `<dir>`: **directorio** destino (absoluto, en ese filesystem; en S3 relativo a la
     raíz del bucket); el fichero conserva su nombre.
     Si no existe, Rocket lo crea, directorios intermedios incluidos — no hace falta
     `mkdir` previo, pero una errata en la ruta crea en silencio un árbol nuevo.

## Salida esperada

```
Uploaded /root/project/Screenshot.png -> /data/kk/LoadDocument/Screenshot.png [hdfs1.s000001-datastores:HDFS]
```

Con el repliegue antiguo, antes aparece una línea `Phase 1 OK: staged at /tmp/uploads/...`.

## Notas y errores

- El tamaño máximo de subida es el `file-browser.max-content-length` del servidor
  (por defecto 5 GB); los ficheros muy grandes pueden dar timeout — muestra el cuerpo
  verbatim si pasa.
- `Target <ruta> already exists` — el nombre destino ya está ocupado; la subida se
  rechaza antes de la transferencia. Rocket lo devuelve como HTTP 500, no 409.
- Un `<dir>` relativo se rechaza (Rocket solo acepta rutas absolutas en el File
  Browser).
- Un nombre de fichero que HDFS o S3 no admiten (dos puntos, llaves) se rechaza antes de
  la transferencia.
- `401/403` — no autorizado para ese directorio destino (Gosec; en S3 se comprueba
  contra `/<bucket><dir>`).
- El `420` solo aparece en el flujo antiguo — una subida concurrente mantuvo el slot
  ocupado; el script reintenta con backoff y avisa si no se libera.
- Las raíces restringidas se rechazan en cliente antes de la llamada.

Ver `guides/external-api-calls.md` §5 para leer los códigos HTTP habituales.
