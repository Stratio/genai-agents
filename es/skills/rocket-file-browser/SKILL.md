---
name: rocket-file-browser
description: "Sube y baja ficheros entre el sandbox de Stratio y el File Browser HDFS de Rocket. Úsala cuando el usuario quiera mover un fichero hacia o desde el HDFS de Rocket — frases como 'baja este fichero de Rocket', 'sube este archivo al HDFS', 'descarga del file browser', 'sube a Rocket', 'get/put de un fichero en HDFS'. Llama a la API mutual-TLS de Rocket (/rocket/fileBrowser/*) con el certificado cliente del sandbox, así que opera con los permisos propios del usuario en Rocket."
argument-hint: "[download|upload] [rutas...]"
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
  `https://rocket.<tenant>-rocket.svc.<cluster-domain>:7777/rocket`. El ingress
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

Ayudante (sin sub-fichero): lista los filesystems con
`python3 scripts/rocket_file_browser.py filesystems` para descubrir el `id`/`type`
que pasar en `--fs`. El script auto-resuelve el filesystem cuando solo hay uno.

## Reglas de enrutado

1. Identifica la capacidad por la intención del usuario. Si no es download ni upload,
   este MVP no puede ayudar — dilo (la cobertura completa del File Browser es una
   extensión planificada).
2. Ejecuta el pre-check de arriba. Si falla, para y repórtalo.
3. Carga el sub-fichero correspondiente y síguelo de principio a fin.
4. Tras la llamada, muestra el resultado (o el código HTTP + cuerpo verbatim si falla)
   al usuario, según `guides/external-api-calls.md` §5.

## Añadir una nueva capacidad

Crea un `tasks/<capacidad>.md` (cuándo usarla, la invocación exacta de
`rocket_file_browser.py`, salida esperada, casos de error), añade una fila al índice y
replica ambos ficheros en `skills/rocket-file-browser/` (inglés). El alcance completo
planificado añade `ls`, `cp`, `mv`, `rm`, `mkdir`, `compress`, `extract`.
