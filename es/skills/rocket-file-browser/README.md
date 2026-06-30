# rocket-file-browser

Skill compartida que mueve ficheros entre el sandbox de Stratio y el **File Browser
HDFS de Rocket** (`/rocket/fileBrowser/*`), para que un agente pueda traerse un
dataset/documento de Rocket al workspace o empujar un fichero generado de vuelta a
HDFS — sin el roundtrip manual por la UI web de Rocket.

Diseñada como **router** (igual que `cowork-api`): un `SKILL.md` mínimo indexa las
capacidades y apunta a un fichero autocontenido bajo `tasks/` por capacidad. Un único
cliente Python, `scripts/rocket_file_browser.py`, hace el trabajo HTTP.

## Qué hace

- **download** — `POST /fileBrowser/download`, streaming de los bytes a una ruta local.
- **upload** — dos fases: `POST /fileBrowser/uploadLocalFile` (multipart) y luego
  `POST /fileBrowser/putLocalFileToHadoopFs`, con reintento automático del HTTP 420.
- **ls** — `POST /fileBrowser/findByPath` (listado de directorio / stat de fichero).
- **cp** / **mv** — `PUT /fileBrowser/copy` / `PUT /fileBrowser/update`.
- **rm** — `DELETE /fileBrowser/delete` (una o varias rutas).
- **mkdir** — `POST /fileBrowser/createDir`.
- **compress** / **extract** — `PUT /fileBrowser/compress` (codecs: ZStandard, Lz4,
  Snappy, Gzip, Bzip2, Zip, TarGz) / `PUT /fileBrowser/extract`.
- **filesystems** (ayudante) — `GET /fileBrowser/getFilesystems` para descubrir `id`/`type`.

## Autenticación e identidad

Solo mTLS. Rocket corre en `Oauth2Mutual` y expone un listener mutual-TLS en el puerto
7777; el certificado cliente montado en el sandbox (`/vault/secrets/cert.crt`, CN = el
usuario que opera, p.ej. `s000001-user`) es la identidad con la que Rocket autoriza vía
Gosec. **Sin token, sin impersonación** — la skill opera con los permisos propios del
usuario en el File Browser, los mismos que ve en la UI de Rocket.

El ingress público (`:443`) es solo oauth2/cookie e ignora el certificado. Apunta
`ROCKET_API_URL` al listener **mutual** (host:puerto, **sin path** — la skill llama a
`/fileBrowser/...`), alcanzable en-cluster por el nombre corto de servicio (resuelto por
el search domain del pod): `https://<rocket-instance>.<rocket-namespace>:7777`
(p.ej. `https://rocket.s000001-rocket:7777`).

## Variables de entorno

| Variable | Requerida | Default | Propósito |
|---|---|---|---|
| `ROCKET_API_URL` | sí | — | Host:puerto del listener mutual 7777 (sin path), p.ej. `https://rocket.s000001-rocket:7777` |
| `USER_CERT_PATH` | sí | `/vault/secrets/cert.crt` | Cert cliente (mTLS) |
| `USER_KEY_PATH` | sí | `/vault/secrets/cert.key` | Clave cliente |
| `CA_CERT_PATH` | al verificar | `/stratio/certs/ca.crt` | CA para validar el cert servidor |
| `ROCKET_TLS_VERIFY` | no | `false` | `true` para verificar el cert servidor; si no, se omite (el SAN del cert del 7777 no suele cubrir el nombre de servicio — mismo motivo que el `NODE_TLS_REJECT_UNAUTHORIZED=0` de OpenCode) |

## Guías compartidas

- `external-api-calls.md` — declarada en `guides`. Rutas de cert, el pre-check, las
  plantillas curl/Python y la tabla de errores. Esta skill reutiliza todo; el único
  delta es `ROCKET_API_URL` (vs `GENAI_API_URL`) sobre el puerto mutual-TLS.

## Dependencias Python

- `requests` — ya presente en el `/opt/venv` del sandbox.

## Dependencias de sistema

- Ninguna más allá del venv. El script lee las rutas del cert del entorno y negocia el
  mTLS él mismo.

## Notas

- Nunca reintenta en silencio salvo el HTTP 420 en la fase de confirmación de la subida
  (Rocket señala subida concurrente). Cualquier otro fallo se muestra con código HTTP +
  cuerpo verbatim.
- Las raíces reservadas (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
  `/mlProjectExecutionsArtifacts`) se rechazan en cliente antes de cualquier llamada.
- `download` usa la variante POST (soporta datastores con nombre); la forma
  `GET ...?pathHdfs=` fuerza el filesystem interno y no se usa.
