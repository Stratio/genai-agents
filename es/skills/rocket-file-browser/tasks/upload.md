# Tarea: subir un fichero al HDFS de Rocket

Empuja un fichero local del sandbox a un directorio HDFS de Rocket. Es una operación
en **dos fases**, ambas gestionadas por el script:

1. `POST /fileBrowser/uploadLocalFile` (multipart, campo `binary`) → deja el fichero en
   una ruta temporal del pod de Rocket y devuelve `/tmp/uploads/<uuid>/<nombre>`.
2. `POST /fileBrowser/putLocalFileToHadoopFs` con `{"pathHdfs": "<dir>", "dockerPath":
   "<temp>", "targetFilesystem": {...}}` → lo confirma en HDFS. Puede responder
   **HTTP 420** ("subida en curso") — el script reintenta con backoff.

## Procedimiento

1. **Pre-check** — `ROCKET_API_URL` definida y el cert cliente presente (ver `SKILL.md`).

2. **Resuelve el filesystem** si no lo conoces (`--fs` opcional si solo hay uno):

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   ```

3. **Sube**:

   ```bash
   python3 scripts/rocket_file_browser.py upload \
     "<origen_local>" "<dir_hdfs>" [--fs <id>:<type>]
   ```

   - `<origen_local>`: fichero local existente en el sandbox.
   - `<dir_hdfs>`: **directorio** HDFS destino; el fichero conserva su nombre.

## Salida esperada

```
Phase 1 OK: staged at /tmp/uploads/8b2afa0f-.../Screenshot.png
Uploaded /root/project/Screenshot.png -> /data/kk/LoadDocument/Screenshot.png
```

## Notas y errores

- El tamaño máximo de subida es grande (default servidor 5 GB) pero finito; ficheros
  muy grandes pueden dar timeout — muestra el cuerpo verbatim si pasa.
- Los temporales del pod se auto-limpian (~30 min); una confirmación correcta saca el
  fichero antes de eso.
- `401/403` — no autorizado para ese directorio destino (Gosec). `420` tras todos los
  reintentos — una subida concurrente al mismo destino mantuvo el slot ocupado; reintenta luego.
- Las raíces restringidas se rechazan en cliente antes de la llamada.

Ver `guides/external-api-calls.md` §5 para leer los códigos HTTP habituales.
