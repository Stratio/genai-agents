# Task: download a file from Rocket

Bring a file from Rocket's File Browser — its HDFS or a configured S3 bucket — into the
sandbox workspace.

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `POST` |
| Path | `/fileBrowser/download` |
| Body | `{"pathHdfs": "<path>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Response | the raw file bytes (streamed) |

> The script uses the POST variant. The GET twin
> (`GET /fileBrowser/download?path=<p>[&filesystemId=&filesystemType=]`, also accepting
> the older `pathHdfs` name) exists so a browser can save a large file by navigating to
> it; it authorizes through the same actor message, so both grant exactly the same
> access. Either works — POST keeps the path out of access logs.

## Procedure

1. **Pre-check** — `ROCKET_API_URL` set and the client cert present (see `SKILL.md`
   prerequisites). If missing, stop and report which one.

2. **Filesystem** — use the one settled for this conversation; if none is yet, follow
   `tasks/filesystems.md` (list, use the only one or ask the user). The file is looked
   up in that filesystem only.

3. **Download**:

   ```bash
   python3 scripts/rocket_file_browser.py download \
     "<path>" "<local_dest>" --fs <id>:<type>
   ```

   - `<path>`: absolute path in that filesystem, e.g. `/data/kk/report.json` (on S3,
     relative to the bucket root: `/landing/a.csv`). A directory is
     downloaded as a zip built on the fly (subject to the server size limit).
   - `<local_dest>`: a local file path, or a directory (the remote basename is kept) —
     in the current task folder (or the workspace), not in `/tmp`.

## Expected output

```
Downloaded /data/kk/report.json [hdfs1.s000001-datastores:HDFS] -> /root/project/report.json (6521 bytes)
```

## Errors

- `401/403` — the user's certificate identity is not authorized for that path (Gosec;
  on S3 the check is against `/<bucket><path>`).
- Path not found or filesystem error — expect HTTP 500 rather than 404 (Rocket reports a
  missing path as 500; see `tasks/ls.md`). Check the filesystem before the path: the
  file may live on another one. Surface the HTTP code + body verbatim.
- Restricted roots (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
  `/mlProjectExecutionsArtifacts`) are refused client-side before the call.

See `guides/external-api-calls.md` §5 for reading common HTTP codes.
