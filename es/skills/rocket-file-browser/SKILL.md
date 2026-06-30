---
name: rocket-file-browser
description: "Gestiona ficheros en el File Browser HDFS de Rocket desde el sandbox de Stratio: descargar, subir, listar, copiar, mover/renombrar, borrar, mkdir, comprimir y extraer. Úsala cuando el usuario quiera operar sobre el HDFS de Rocket — frases como 'baja este fichero de Rocket', 'sube este archivo al HDFS', 'lista la carpeta', 'borra/copia/mueve en HDFS', 'comprime estos ficheros', 'descarga del file browser', 'sube a Rocket'. Llama a la API mutual-TLS de Rocket (/rocket/fileBrowser/*) con el certificado cliente del sandbox, así que opera con los permisos propios del usuario en Rocket."
argument-hint: "[download|upload|ls|cp|mv|rm|mkdir|compress|extract] [rutas...]"
---

# Skill: Rocket File Browser (subir/bajar de HDFS)

Skill router. Cada capacidad vive en su propio fichero bajo `tasks/`. **Este fichero es
deliberadamente mínimo** — al ejecutar una tarea, carga y sigue el sub-fichero
correspondiente entero. No improvises la petición desde este índice.

Todas las operaciones las sirve un único cliente Python, `scripts/rocket_file_browser.py`,
que gestiona el mTLS, la subida en dos fases y el reintento del HTTP 420.

## Prerrequisitos — leer primero

La autenticación es **solo mTLS**, mismo modelo que `guides/external-api-calls.md`
(§1 entorno, §3/§4 plantillas, §5 tabla de errores). Diferencias respecto a esa guía:

- La URL base es **`ROCKET_API_URL`** (no `GENAI_API_URL`). Debe incluir el prefijo
  `/rocket` y apuntar al listener **mutual-TLS** de Rocket (puerto 7777), p.ej.
  `https://<rocket-instance>.<rocket-namespace>:7777/rocket` (nombre corto de servicio
  en-cluster, resuelto por el search domain del pod — p.ej.
  `https://rocket.s000001-rocket:7777/rocket`). El ingress
  público (443) es solo oauth2/cookie y **no** acepta el certificado.
- El cert cliente (`/vault/secrets/cert.crt`, CN = el usuario que opera) es la
  identidad con la que Rocket autoriza. Sin token, sin impersonación — las llamadas
  van con los permisos propios del usuario en el File Browser.

**Pre-check antes de cualquier llamada:**

1. `ROCKET_API_URL` está definida (si no, el script para limpiamente y lo indica).
2. `USER_CERT_PATH` / `USER_KEY_PATH` existen (defaults `/vault/secrets/cert.{crt,key}`).

Si falta un prerrequisito, para y di al usuario exactamente cuál — no rehúses con un
mensaje genérico.

## Índice de capacidades

| Capacidad | Cuándo usarla | Sub-fichero a cargar |
|---|---|---|
| Descargar un fichero | Traer un fichero del HDFS de Rocket al workspace del sandbox. | `tasks/download.md` |
| Subir un fichero | Empujar un fichero local del sandbox a un directorio HDFS de Rocket. | `tasks/upload.md` |
| Listar una ruta | Mostrar el contenido de un directorio HDFS. | `tasks/ls.md` |
| Copiar | Copiar un fichero/directorio HDFS a una ruta nueva. | `tasks/cp.md` |
| Mover / renombrar | Mover o renombrar un fichero/directorio HDFS. | `tasks/mv.md` |
| Borrar | Eliminar ficheros/directorios HDFS (destructivo — confirma antes). | `tasks/rm.md` |
| Crear directorio | Crear un directorio HDFS. | `tasks/mkdir.md` |
| Comprimir | Comprimir ficheros HDFS en un archivo. | `tasks/compress.md` |
| Extraer | Extraer un archivo HDFS. | `tasks/extract.md` |

Ayudante (sin sub-fichero): lista los filesystems con
`python3 scripts/rocket_file_browser.py filesystems` para descubrir el `id`/`type`
que pasar en `--fs`. El script auto-resuelve el filesystem cuando solo hay uno.

## Reglas de enrutado

1. Identifica la capacidad por la intención del usuario. Si no encaja en ninguna entrada
   del índice (p.ej. publicar vistas, consultar datos), esta skill no puede ayudar — dilo.
2. Ejecuta el pre-check de arriba. Si falla, para y repórtalo.
3. Carga el sub-fichero correspondiente y síguelo de principio a fin.
4. Tras la llamada, muestra el resultado (o el código HTTP + cuerpo verbatim si falla)
   al usuario, según `guides/external-api-calls.md` §5.

## Añadir una nueva capacidad

Crea un `tasks/<capacidad>.md` (cuándo usarla, la invocación exacta de
`rocket_file_browser.py`, salida esperada, casos de error), añade un subcomando al script,
añade una fila al índice y replica ambos ficheros en `skills/rocket-file-browser/` (inglés).
