# Task: download a file from Rocket's HDFS

Bring a file from Rocket's HDFS File Browser into the sandbox workspace.

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `POST` |
| Path | `/fileBrowser/download` |
| Body | `{"pathHdfs": "<path>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Response | the raw file bytes (streamed) |

> Use the POST variant, not `GET /fileBrowser/download?pathHdfs=` — the GET form forces
> the internal filesystem and cannot target a named datastore.

## Procedure

1. **Pre-check** — `ROCKET_API_URL` set and the client cert present (see `SKILL.md`
   prerequisites). If missing, stop and report which one.

2. **Resolve the filesystem** if you don't know it:

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   # e.g. [{"id":"hdfs1.s000001-datastores","type":"HDFS","defaultPath":"/user/..."}]
   ```

   When exactly one filesystem exists the script picks it automatically, so `--fs`
   is optional. Pass `--fs <id>:<type>` only when several exist.

3. **Download**:

   ```bash
   python3 scripts/rocket_file_browser.py download \
     "<hdfs_path>" "<local_dest>" [--fs <id>:<type>]
   ```

   - `<hdfs_path>`: absolute path in HDFS, e.g. `/data/kk/report.json`.
   - `<local_dest>`: a local file path, or a directory (the HDFS basename is kept).

## Expected output

```
Downloaded /data/kk/report.json -> /root/project/report.json (6521 bytes)
```

## Errors

- `401/403` — the user's certificate identity is not authorized for that path (Gosec).
- `404`/`500` — path not found or filesystem error. Surface the HTTP code + body verbatim.
- Restricted roots (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
  `/mlProjectExecutionsArtifacts`) are refused client-side before the call.

See `guides/external-api-calls.md` §5 for reading common HTTP codes.
