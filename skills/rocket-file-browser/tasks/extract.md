# Task: extract an HDFS archive

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/extract` |
| Body | `{"files": [{"path": "<archive>", "newPath": "<dest>"}], "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

Since ROCK #5384 extraction streams entry by entry into the filesystem, with no local
disk on the Rocket pod. What that changes for the caller:

- **The archive kind is detected by content, not by name** — a `.tar.zst`, a `.tar.gz`,
  a plain `.gz`, a `.zip` or an extension-less file are all read for what they are.
  Zip, tar, tar+gzip and tar+zstd are handled as archives; a single stream-compressed
  file (`.gz`, `.bz2`, `.zst`, `.snappy`, `.lz4`) is decompressed to its name without
  the extension.
- **Empty directories inside a zip are now recreated** (they used to be lost).
- An entry whose name would write **outside the destination** (`../…`, absolute names)
  aborts the extraction.
- A failed extraction **rolls back only what it created**; pre-existing content in the
  destination is left alone.
- `newPath` is **mandatory** server-side. The script defaults it to the archive's own
  directory and says so; pass `--dest` to choose another. The destination is created if
  it does not exist, and must be a directory.

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--dest` and `--fs` optional):

   ```bash
   python3 scripts/rocket_file_browser.py extract "<archive>" [--dest "<hdfs_dir>"] [--fs <id>:<type>]
   ```

## Errors

- `Compressed file ... has a size larger than the maximum allowed` — the archive exceeds
  `file-browser.max-content-length` (default 5 GB).
- `Destination ... must be a directory` / `Source file ... cannot be a directory`.
- `the archive holds an entry whose name would write it outside <dest>` — refused as a
  path-traversal archive.
- `Unsupported file extension and codec` — the file is neither an archive nor something
  a filesystem codec can decompress.
- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
