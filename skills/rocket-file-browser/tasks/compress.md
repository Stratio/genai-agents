# Task: compress HDFS files into an archive

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/compress` |
| Body | `{"files": ["<p1>", ...], "compressedFile": "<archive>", "compressionCodec": "<codec>", "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

Valid codecs: `ZStandard`, `Lz4`, `Snappy`, `Gzip`, `Bzip2`, `Zip` (default), `TarGz`.

> **Rocket appends the codec extension** to `compressedFile`. Passing `out.zip` with
> codec `Zip` produces `out.zip.zip`. Pass the base name without extension (e.g. `out`)
> or expect the suffix — and use the resulting full name when extracting.

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py compress "<archive>" "<src1>" ["<src2>" ...] [--codec Zip] [--fs <id>:<type>]
   ```

## Errors

- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
