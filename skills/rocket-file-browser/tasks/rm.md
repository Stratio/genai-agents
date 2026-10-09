# Task: delete files/directories

Delete one or more paths in one Rocket filesystem (HDFS or an S3 bucket). **Destructive —
confirm with the user first.**

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `DELETE` |
| Path | `/fileBrowser/delete` |
| Body | `{"files": [{"path": "<p1>"}, ...], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Confirm** the exact paths **and the filesystem** with the user — this cannot be
   undone, and the same path may exist on another filesystem.
3. **Run** (`--fs` = the filesystem settled with `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py rm "<path>" ["<path2>" ...] --fs <id>:<type>
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
