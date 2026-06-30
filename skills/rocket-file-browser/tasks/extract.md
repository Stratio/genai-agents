# Task: extract an HDFS archive

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/extract` |
| Body | `{"files": [{"path": "<archive>", "newPath": "<dest?>"}], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--dest` and `--fs` optional):

   ```bash
   python3 scripts/rocket_file_browser.py extract "<archive>" [--dest "<hdfs_dir>"] [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
