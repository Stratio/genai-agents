# Task: create a directory

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `POST` |
| Path | `/fileBrowser/createDir` |
| Body | `{"pathHdfs": "<path>", "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--fs` = the filesystem settled with `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py mkdir "<path>" --fs <id>:<type>
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- On S3 a directory is a key prefix: the "directory" exists as an empty marker until a
  file is written under it.
- Surface HTTP code + body verbatim on failure.
