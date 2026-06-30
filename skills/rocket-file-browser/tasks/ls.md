# Task: list an HDFS path

List the contents of a directory (or stat a file) in Rocket's HDFS.

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `POST` |
| Path | `/fileBrowser/findByPath` |
| Body | `{"pathHdfs": "<path>", "targetFilesystem": {"id": "...", "type": "..."}}` |
| Response | JSON array of `{name, type, size, owner, group, permissions, lastUpdated}` |

## Procedure

1. **Pre-check** — `ROCKET_API_URL` set and client cert present (see `SKILL.md`).
2. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py ls "<hdfs_path>" [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized for that path (Gosec). Restricted roots are refused client-side.
- Surface HTTP code + body verbatim on failure (`guides/external-api-calls.md` §5).
