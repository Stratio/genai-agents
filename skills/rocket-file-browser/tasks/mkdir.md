# Task: create a directory in HDFS

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `POST` |
| Path | `/fileBrowser/createDir` |
| Body | `{"pathHdfs": "<path>", "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py mkdir "<hdfs_path>" [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
