# Task: list a path

List the contents of a directory (or stat a file) in one Rocket filesystem (HDFS or an S3
bucket).

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `POST` |
| Path | `/fileBrowser/findByPath` |
| Body | `{"pathHdfs": "<path>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Response | JSON array of `{name, type, size, owner, group, permissions, lastUpdated}` |

## Procedure

1. **Pre-check** — `ROCKET_API_URL` set and client cert present (see `SKILL.md`).
2. **Run** (`--fs` = the filesystem settled with `tasks/filesystems.md`). With no path from the user, start at that
   filesystem's `defaultPath` (from the `filesystems` listing):

   ```bash
   python3 scripts/rocket_file_browser.py ls "<path>" --fs <id>:<type>
   ```

## Errors

- `401/403` — not authorized for that path (Gosec). On S3 the check is against
  `/<bucket><path>`. Restricted roots are refused client-side.
- **Path not found** — Rocket answers **HTTP 500, not 404**, with `errorCode` `1463`
  ("Error obtaining HDFS content of provided path", on S3 too). The `exception` shows
  where it looked — `No such file or directory: s3a://<bucket>/<path>` on S3,
  `File <path> does not exist.` on HDFS — so check the filesystem before the path: the
  file may live on another one.
- Surface HTTP code + body verbatim on failure (`guides/external-api-calls.md` §5).
