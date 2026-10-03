# Task: move/rename within HDFS

Move or rename an HDFS file/directory (move semantics). **Confirm with the user first** —
every path that pointed at the original stops resolving.

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/update` |
| Body | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Confirm** the exact source and destination with the user.
3. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py mv "<src>" "<dst>" [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
