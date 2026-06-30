# Task: copy within HDFS

Copy an HDFS file/directory to a new path (both within the same filesystem).

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/copy` |
| Body | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py cp "<src>" "<dst>" [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized for src (read) or dst (write) (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
