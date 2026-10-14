# Task: move/rename within a filesystem

Move or rename a file/directory **in the same filesystem** (move semantics). **Confirm
with the user first** — every path that pointed at the original stops resolving.

Rocket has no cross-filesystem move: moving from one filesystem to another is download +
upload + `rm` of the source, per `tasks/filesystems.md` §Moving data between filesystems.
On S3 a move is copy + delete, not an atomic rename: slow on big trees, and an
interrupted move can leave both copies — say so when confirming a large directory.

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/update` |
| Body | `{"files": [{"path": "<src>", "newPath": "<dst>"}], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Confirm** the exact source, destination and filesystem with the user.
3. **Run** (`--fs` = the filesystem settled with `tasks/filesystems.md`):

   ```bash
   python3 scripts/rocket_file_browser.py mv "<src>" "<dst>" --fs <id>:<type>
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
