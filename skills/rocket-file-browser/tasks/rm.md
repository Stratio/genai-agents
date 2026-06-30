# Task: delete HDFS files/directories

Delete one or more paths in Rocket's HDFS. **Destructive — confirm with the user first.**

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `DELETE` |
| Path | `/fileBrowser/delete` |
| Body | `{"files": [{"path": "<p1>"}, ...], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Confirm** the exact paths with the user — this cannot be undone.
3. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py rm "<hdfs_path>" ["<hdfs_path2>" ...] [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
