# Task: upload a file to Rocket's HDFS

Push a local sandbox file into a Rocket HDFS directory. This is a **two-phase**
operation, both handled by the script:

1. `POST /fileBrowser/uploadLocalFile` (multipart, field `binary`) → stages the file on
   the Rocket pod and returns a temp path `/tmp/uploads/<uuid>/<name>`.
2. `POST /fileBrowser/putLocalFileToHadoopFs` with `{"pathHdfs": "<dir>", "dockerPath":
   "<temp>", "targetFilesystem": {...}}` → commits it into HDFS. May answer **HTTP 420**
   ("upload already in progress") — the script retries with backoff.

## Procedure

1. **Pre-check** — `ROCKET_API_URL` set and the client cert present (see `SKILL.md`).

2. **Resolve the filesystem** if unknown (`--fs` optional when only one exists):

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   ```

3. **Upload**:

   ```bash
   python3 scripts/rocket_file_browser.py upload \
     "<local_src>" "<hdfs_dir>" [--fs <id>:<type>]
   ```

   - `<local_src>`: existing local file in the sandbox.
   - `<hdfs_dir>`: target HDFS **directory**; the file keeps its basename.

## Expected output

```
Phase 1 OK: staged at /tmp/uploads/8b2afa0f-.../Screenshot.png
Uploaded /root/project/Screenshot.png -> /data/kk/LoadDocument/Screenshot.png
```

## Notes & errors

- Max upload size is large (server default 5 GB) but finite; very large files may hit
  timeouts — surface the body verbatim if so.
- Staged temp files on the pod are auto-cleaned (~30 min); a successful commit moves the
  file out before then.
- `401/403` — not authorized for that target directory (Gosec). `420` after all retries —
  a concurrent upload to the same target kept the slot busy; retry later.
- Restricted roots are refused client-side before the call.

See `guides/external-api-calls.md` §5 for reading common HTTP codes.
