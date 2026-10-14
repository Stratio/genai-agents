# Tarea: elegir (o cambiar) el filesystem

El File Browser de Rocket puede acceder a **varios filesystems a la vez**. Todas las demás
tareas operan sobre exactamente uno de ellos, así que fija cuál antes de la primera
operación y mantenlo explícito en cada llamada.

## Qué expone Rocket

`GET /fileBrowser/getFilesystems` (script: `filesystems`) devuelve una lista de
`{"id", "type", "defaultPath"}`:

| Entrada | `type` | `id` | Cuándo aparece |
|---|---|---|---|
| Filesystem interno de metadatos — el `fs.defaultFS` de Hadoop del propio Rocket, siempre el primero | `HDFS`, `S3` o `HadoopFs` | HDFS: el host del namenode / nameservice. S3: el bucket | Salvo con `fileBrowser.internalMetadataFilesystemEnabled=false` |
| Filesystems configurados — los añade un administrador de Rocket | `S3` (el único tipo configurable hoy) | El **nombre del bucket** | Uno por bucket configurado |

Ejemplo:

```json
[
  {"id": "hdfs1.s000001-datastores", "type": "HDFS", "defaultPath": "/"},
  {"id": "sales-landing", "type": "S3", "defaultPath": "/landing"}
]
```

Hechos que justifican las reglas de abajo:

- **Rocket no guarda un filesystem "actual".** Cada petición lleva su propio
  `targetFilesystem` (`{"id", "type"}`; en `upload`, los parámetros de query
  `filesystemId` / `filesystemType`). Cambiar de filesystem = enviar otro.
- **Una petición sin `targetFilesystem` va al filesystem interno**, en silencio. Por eso
  el script lo envía siempre explícito — nunca depende de ese comportamiento por defecto.
- **Las rutas son relativas a la raíz del filesystem elegido.** En S3 esa raíz es el
  bucket: `/landing/a.csv` en `sales-landing` es `s3a://sales-landing/landing/a.csv`.
  La misma ruta en dos filesystems designa dos ficheros distintos.
- **Toda operación se queda dentro de un filesystem.** `cp`, `mv`, `compress` y
  `extract` reciben un único `targetFilesystem`; no hay copia ni movimiento entre
  filesystems en el servidor.
- `defaultPath` es donde la UI de Rocket abre ese filesystem — el punto de partida
  natural para un `ls` cuando el usuario no da ruta.

## Procedimiento

1. **Pre-check** — ver `SKILL.md`.
2. **Lista** los filesystems una vez por conversación (y de nuevo si una llamada dice
   que el filesystem no está disponible):

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   ```

3. **Elige uno:**
   - **Solo hay uno** → úsalo; di al usuario cuál en una línea.
   - **Hay varios y la petición ya nombra uno sin ambigüedad** (un nombre de bucket,
     "el HDFS", "S3" cuando solo hay una entrada S3) → usa ese y dilo.
   - **Hay varios en otro caso** → pregunta al usuario, siguiendo la convención de
     preguntas al usuario, mostrando de cada opción el `id`, el `type` y el
     `defaultPath`. Nunca adivines ni tomes por defecto el primero (el interno).
   - **No hay ninguno** → para: el File Browser no tiene ningún filesystem habilitado en
     este Rocket (interno deshabilitado y ningún bucket configurado). Díselo al usuario;
     no hay nada que reintentar.
4. **Recuerda la elección** el resto de la conversación y pásala como
   `--fs <id>:<type>` en **todas** las llamadas, aunque solo haya un filesystem, para que
   cada comando (y su línea de salida, que termina en `[<id>:<type>]`) diga dónde actuó.
5. **Cambia** solo cuando el usuario lo pida ("ahora en el bucket X", "lo mismo en el
   HDFS"), o cuando una petición nombre otro filesystem. Anuncia el cambio en una línea y
   usa el nuevo `--fs` a partir de ahí.

El script valida `--fs` contra el listado antes de actuar: un `id` desconocido, o un
`type` que no coincide (se compara sin distinguir mayúsculas), se detiene mostrando las
opciones válidas.

## Mover datos entre filesystems

No existe `cp` / `mv` entre filesystems. Para llevar un fichero de un filesystem a otro
(HDFS → S3, bucket → bucket), pasa por el sandbox:

```bash
python3 scripts/rocket_file_browser.py download "<ruta_origen>" "<dir_tmp>" --fs <id_origen>:<type_origen>
python3 scripts/rocket_file_browser.py upload "<dir_tmp>/<nombre>" "<dir_destino>" --fs <id_destino>:<type_destino>
```

- Es una subida al destino: aplican las reglas de subida (lo pidió el usuario, destino
  confirmado, el nombre no debe existir).
- Un "mover" entre filesystems además borra el origen con `rm` — solo después de que la
  subida haya ido bien y con confirmación explícita del usuario.
- Un directorio se descarga como zip; súbelo y haz `extract` en el filesystem destino si
  el usuario quiere el árbol y no el archivo.
- Usa una carpeta temporal para `<dir_tmp>` y borra la copia local al terminar salvo que
  el usuario quiera conservarla.

## Comportamiento distinto en S3

- **Permisos** — Gosec autoriza una ruta S3 con el bucket delante (`/landing/a.csv` en
  `sales-landing` se comprueba como `/sales-landing/landing/a.csv`). Un `401/403` en S3
  cuando la misma ruta funciona en otro filesystem suele significar que la política del
  usuario no cubre ese prefijo de bucket.
- **Los directorios son emulados** (prefijos de clave, con un objeto marcador si están
  vacíos): los tamaños, propietarios y permisos de `ls` no tienen el significado de HDFS.
- **`mv` es copia + borrado**, no un renombrado atómico — lento en árboles grandes, y un
  movimiento interrumpido puede dejar ambas copias. Confirma antes de mover directorios
  grandes.
- **`S3 filesystem not found in classpath`** — a este Rocket le falta el conector S3
  necesario para abrir buckets configurados; repórtalo, el agente no puede arreglarlo.
- `Filesystem with id '<id>' and type '<type>' not found` — el bucket se quitó de la
  configuración de Rocket después del listado; vuelve a listar y pregunta al usuario.

Las raíces restringidas (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
`/mlProjectExecutionsArtifacts`) se rechazan en todos los filesystems, S3 incluido.
