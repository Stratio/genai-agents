# Task: upload a file to Rocket's HDFS

Push a local sandbox file into a Rocket HDFS directory.

Since Rocket 4.x (ROCK #5384) this is a **single request**, handled by the script:

`POST /fileBrowser/upload?path=<hdfs_dir>[&filesystemId=<id>&filesystemType=<type>]`
with the file in the `binary` multipart part.

- The write is **authorized before any byte is accepted**, so a caller without
  permission over `path` is refused without having transferred the file.
- The bytes are **streamed straight into the filesystem** — nothing is written to the
  Rocket pod's disk any more.
- The file is stored under `path` with the name the multipart part carries, and the
  request is **refused when that name is already taken** (no overwrite). Delete or
  rename first, or upload under a different name.
- The response is `200` with the stored path.

The legacy two-request flow (`POST /fileBrowser/uploadLocalFile` →
`POST /fileBrowser/putLocalFileToHdfs`, with its HTTP 420 retry) still exists for
compatibility. The script falls back to it automatically when the server answers
404/405 to the one-shot route, and `--legacy` forces it.

## Procedure

1. **Pre-check** — `ROCKET_API_URL` set and the client cert present (see `SKILL.md`).

2. **Resolve the filesystem** if unknown (`--fs` optional when only one exists):

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   ```

3. **Upload**:

   ```bash
   python3 scripts/rocket_file_browser.py upload \
     "<local_src>" "<hdfs_dir>" [--fs <id>:<type>] [--legacy]
   ```

   - `<local_src>`: existing local file in the sandbox.
   - `<hdfs_dir>`: target HDFS **directory** (absolute); the file keeps its basename.

## Expected output

```
Uploaded /root/project/Screenshot.png -> /data/kk/LoadDocument/Screenshot.png
```

With the legacy fallback, a `Phase 1 OK: staged at /tmp/uploads/...` line precedes it.

## Notes & errors

- Max upload size is the server's `file-browser.max-content-length` (default 5 GB);
  very large files may still hit timeouts — surface the body verbatim if so.
- `Target <path> already exists` — the destination name is taken; the upload is refused
  before the transfer.
- A relative `<hdfs_dir>` is refused (Rocket only accepts absolute File Browser paths).
- A file name HDFS or S3 cannot hold (a colon, braces) is refused before the transfer.
- `401/403` — not authorized for that target directory (Gosec).
- `420` only appears in the legacy flow — a concurrent upload kept the slot busy; the
  script retries with backoff and reports if it never clears.
- Restricted roots are refused client-side before the call.

See `guides/external-api-calls.md` §5 for reading common HTTP codes.
