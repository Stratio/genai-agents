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
- Surface HTTP code + body verbatim on failure (`guides/external-api-calls.md` §5).
