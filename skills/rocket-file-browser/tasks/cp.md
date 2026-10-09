# Task: copy within a filesystem

Copy a file/directory to a new path **in the same filesystem** (HDFS or an S3 bucket).
Rocket has no cross-filesystem copy: to copy from one filesystem to another, follow
`tasks/filesystems.md` §Moving data between filesystems (download + upload).

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/copy` |
| Body | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--fs` = the filesystem settled with `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py cp "<src>" "<dst>" --fs <id>:<type>
   ```

## Errors

- `401/403` — not authorized for src (read) or dst (write) (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
