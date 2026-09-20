# Task: compress HDFS files into an archive

## Endpoint (handled by the script)

| | |
|---|---|
| Method | `PUT` |
| Path | `/fileBrowser/compress` |
| Body | `{"files": ["<p1>", ...], "compressedFile": "<archive>", "compressionCodec": "<codec>", "targetFilesystem": {...}}` |
| Response | boolean / `OK` |

Since ROCK #5384 the archive is written **straight into the filesystem, one entry at a
time** — the Rocket pod's disk is not used, so the practical limit is the total source
size, not the pod's scratch space.

Codecs:

| Kind | Codecs | Sources |
|---|---|---|
| Archive (multi-file) | `Zip` (default), `TarGz`, `TarZstd` | one or many files/directories |
| Stream (single file) | `ZStandard`, `Lz4`, `Snappy`, `Gzip`, `Bzip2` | exactly one **file** |

`TarZstd` is new in this version. The script refuses several sources with a stream codec
before calling.

> **Rocket appends the codec extension** to `compressedFile`: `out` + `TarZstd` →
> `out.tar.zst`. Pass the base name without extension and use the resulting full name
> when extracting.

> **The destination must not exist**: Rocket answers `Cannot compress file(s):
> Destination file <path> exits` otherwise. Its parent directory is created if missing.

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **Run** (`--fs` optional when only one filesystem exists):

   ```bash
   python3 scripts/rocket_file_browser.py compress "<archive>" "<src1>" ["<src2>" ...] [--codec Zip] [--fs <id>:<type>]
   ```

## Errors

- `Destination file ... exits` — pick another name or delete it first.
- `The total size is larger than the maximum allowed` — sum of the sources exceeds
  `file-browser.max-content-length` (default 5 GB).
- `There is no available compression method for this codec and number of source files` —
  a stream codec was given a directory or several sources; use `Zip`/`TarGz`/`TarZstd`.
- `Codec not loaded` — the native codec is unavailable on this Rocket (typically
  `ZStandard`); use another one.
- `401/403` — not authorized (Gosec). Restricted roots refused client-side.
- Surface HTTP code + body verbatim on failure.
