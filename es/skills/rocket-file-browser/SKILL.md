---
name: rocket-file-browser
description: "Gestiona ficheros en el File Browser de Rocket desde el sandbox de Stratio, en cualquier filesystem que exponga Rocket — su HDFS y los buckets S3 configurados en él: descargar, subir, listar, copiar, mover/renombrar, borrar, mkdir, comprimir, extraer y elegir o cambiar de filesystem. Úsala cuando el usuario quiera operar sobre el HDFS o el S3 de Rocket — frases como 'baja este fichero de Rocket', 'sube este archivo al HDFS', 'súbelo al bucket', 'lista la carpeta de S3', 'borra/copia/mueve en HDFS', 'comprime estos ficheros', 'cambia al otro filesystem', 'descarga del file browser', 'sube a Rocket'. Llama a la API mutual-TLS de Rocket (/fileBrowser/*) con el certificado cliente del sandbox, así que opera con los permisos propios del usuario en Rocket."
argument-hint: "[download|upload|ls|cp|mv|rm|mkdir|compress|extract] [rutas...]"
---

# Skill: Rocket File Browser (HDFS y S3)

Skill router. Cada capacidad vive en su propio fichero bajo `tasks/`. **Este fichero es
deliberadamente mínimo** — al ejecutar una tarea, carga y sigue el sub-fichero
correspondiente entero. No improvises la petición desde este índice.

Todas las operaciones las sirve un único cliente Python, `scripts/rocket_file_browser.py`,
que gestiona el mTLS, el filesystem destino, la subida en una sola petición
(`POST /fileBrowser/upload`) y su repliegue al flujo antiguo de dos peticiones con
reintento del HTTP 420 en versiones de Rocket anteriores.

## Varios filesystems — leer antes de cualquier operación

Un Rocket puede navegar **varios filesystems**: el interno (HDFS, o S3 si Rocket corre
sobre S3) más cada **bucket S3** que haya configurado un administrador. Rocket no guarda
un filesystem actual — cada llamada nombra el suyo — y una ruta designa un fichero
distinto en cada filesystem. Por tanto:

- Fija el filesystem **antes de la primera operación** con `tasks/filesystems.md`:
  lístalos, usa el único o **pregunta al usuario** cuando haya varios y la petición no
  nombre uno. Nunca adivines.
- Pasa el elegido como `--fs <id>:<type>` en **todas** las llamadas de la conversación,
  y cámbialo solo cuando el usuario lo pida (dilo en una línea).
- Nombra el filesystem siempre que informes de una ruta o pidas una confirmación
  ("`/landing/a.csv` en el bucket `sales-landing`"), no solo la ruta.
- Las operaciones nunca cruzan filesystems: copiar/mover entre ellos = descarga + subida
  (`tasks/filesystems.md` §Mover datos entre filesystems).

## Prerrequisitos — leer primero

La autenticación es **solo mTLS**, mismo modelo que `guides/external-api-calls.md`
(§1 entorno, §3/§4 plantillas, §5 tabla de errores). Diferencias respecto a esa guía:

- La URL base es **`ROCKET_API_URL`** (no `GENAI_API_URL`). Es el **host:puerto** del
  listener **mutual-TLS** de Rocket (puerto 7777), **sin path** — la skill llama a
  `/fileBrowser/...` directamente. Usa el nombre corto de servicio en-cluster (resuelto
  por el search domain del pod), p.ej. `https://<rocket-instance>.<rocket-namespace>:7777`
  (p.ej. `https://rocket.s000001-rocket:7777`). El ingress
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
| Elegir / cambiar filesystem | Primera operación de la conversación, varios filesystems, el usuario nombra un bucket o "el otro filesystem", o hay que llevar datos de un filesystem a otro. | `tasks/filesystems.md` |
| Descargar un fichero | Traer un fichero de Rocket (HDFS o S3) al workspace del sandbox. | `tasks/download.md` |
| Subir un fichero | Empujar un fichero local del sandbox a un directorio de Rocket (HDFS o S3). | `tasks/upload.md` |
| Listar una ruta | Mostrar el contenido de un directorio. | `tasks/ls.md` |
| Copiar | Copiar un fichero/directorio a una ruta nueva en el mismo filesystem. | `tasks/cp.md` |
| Mover / renombrar | Mover o renombrar un fichero/directorio en el mismo filesystem (confirma antes). | `tasks/mv.md` |
| Borrar | Eliminar ficheros/directorios (destructivo — confirma antes). | `tasks/rm.md` |
| Crear directorio | Crear un directorio. | `tasks/mkdir.md` |
| Comprimir | Comprimir ficheros en un archivo. | `tasks/compress.md` |
| Extraer | Extraer un archivo. | `tasks/extract.md` |

## Reglas de enrutado

1. Identifica la capacidad por la intención del usuario. Si no encaja en ninguna entrada
   del índice (p.ej. publicar vistas, consultar datos), esta skill no puede ayudar — dilo.
2. Ejecuta el pre-check de arriba. Si falla, para y repórtalo.
3. Si el filesystem de esta conversación aún no está fijado, sigue antes
   `tasks/filesystems.md`.
4. Carga el sub-fichero correspondiente y síguelo de principio a fin.
5. Tras la llamada, muestra el resultado (o el código HTTP + cuerpo verbatim si falla)
   al usuario, según `guides/external-api-calls.md` §5.

## Uso de esta skill dentro del flujo de un agente

- **Las descargas van a la carpeta de trabajo de la tarea actual.** Si el agente mantiene
  una carpeta por tarea (de análisis o de informe), descarga ahí — no en la raíz del
  workspace — para que el fichero quede junto al trabajo que lo usa.
- **Nunca publiques por iniciativa propia.** Sube, copia o mueve a Rocket solo cuando el
  usuario lo pida. Generar un entregable en local no implica subirlo.
- **Nunca adivines el destino de una subida.** Si el usuario no nombró el directorio,
  pregúntaselo (nunca uses el `defaultPath` por defecto); si lo propusiste tú, espera un
  sí explícito. Indica siempre el filesystem, el directorio y el nombre final. La subida
  se rechaza si ese nombre ya existe, así que compruébalo con `ls` y pregunta al usuario
  cómo seguir (otro nombre con `--name`, o borrar el antiguo con `rm`) en lugar de
  borrar por tu cuenta — `tasks/upload.md` paso 3.
- **Las operaciones destructivas siempre requieren confirmación explícita** — `rm` y `mv`
  (mover o renombrar rompe toda ruta que apuntaba al original), enumerando las rutas
  exactas y el filesystem en que están.

## Añadir una nueva capacidad

Crea un `tasks/<capacidad>.md` (cuándo usarla, la invocación exacta de
`rocket_file_browser.py`, salida esperada, casos de error), añade un subcomando al script,
añade una fila al índice y replica ambos ficheros en `skills/rocket-file-browser/` (inglés).
