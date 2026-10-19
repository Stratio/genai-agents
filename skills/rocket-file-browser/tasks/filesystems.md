# Task: choose (or switch) the filesystem

Rocket's File Browser can reach **several filesystems at once**. Every other task runs
against exactly one of them, so settle which one before the first operation and keep it
explicit on every call.

## What Rocket exposes

`GET /fileBrowser/getFilesystems` (script: `filesystems`) returns a list of
`{"id", "type", "defaultPath"}`:

| Entry | `type` | `id` | When it is listed |
|---|---|---|---|
| Internal metadata filesystem — Rocket's own Hadoop `fs.defaultFS`, always first | `HDFS`, `S3` or `HadoopFs` | HDFS: the namenode / nameservice host. S3: the bucket | Unless `fileBrowser.internalMetadataFilesystemEnabled=false` |
| Configured filesystems — added by a Rocket admin | `S3` (the only configurable type today) | The **bucket name** | One per configured bucket |

Example:

```json
[
  {"id": "hdfs1.s000001-datastores", "type": "HDFS", "defaultPath": "/"},
  {"id": "sales-landing", "type": "S3", "defaultPath": "/landing"}
]
```

Facts that drive the rules below:

- **Rocket keeps no "current" filesystem.** Each request carries its own
  `targetFilesystem` (`{"id", "type"}`; on `upload`, the `filesystemId` /
  `filesystemType` query parameters). Switching filesystem = sending another one.
- **A request without `targetFilesystem` goes to the internal filesystem**, silently. The
  script therefore always sends it explicitly — it never relies on that fallback.
- **Paths are relative to the root of the chosen filesystem.** On S3 that root is the
  bucket: `/landing/a.csv` on `sales-landing` is `s3a://sales-landing/landing/a.csv`.
  The same path on two filesystems names two different files.
- **Every operation stays inside one filesystem.** `cp`, `mv`, `compress` and `extract`
  take a single `targetFilesystem`; there is no server-side copy or move across
  filesystems.
- `defaultPath` is where the Rocket UI opens that filesystem — the natural starting
  point for an `ls` when the user gives no path.

## Procedure

1. **Pre-check** — see `SKILL.md`.
2. **List** the filesystems once per conversation (and again if a call says the
   filesystem is not available):

   ```bash
   python3 scripts/rocket_file_browser.py filesystems
   ```

3. **Pick one:**
   - **Exactly one listed** → use it; tell the user which one in one line.
   - **Several listed and the request already names one unambiguously** (a bucket name,
     "the HDFS", "S3" when only one S3 entry exists) → use that one and say so.
   - **Several listed otherwise** → ask the user, following the user question
     convention, showing for each option the `id`, the `type` and the `defaultPath`.
     Never guess and never default to the first (internal) one.
   - **None listed** → stop: the File Browser has no filesystem enabled for this Rocket
     (internal one disabled and no bucket configured). Tell the user; nothing to retry.
4. **Remember the choice** for the rest of the conversation and pass it as
   `--fs <id>:<type>` on **every** call, even when only one filesystem exists, so each
   command (and its output line, which ends in `[<id>:<type>]`) states where it acted.
5. **Switch** only when the user asks ("now in the bucket X", "the same in HDFS"), or
   when a request names a different filesystem. Say the switch out loud in one line and
   use the new `--fs` from then on.

The script validates `--fs` against the listing before acting: an unknown `id`, or a
`type` that does not match (matched case-insensitively), stops with the valid options.

## Moving data between filesystems

There is no cross-filesystem `cp` / `mv`. To bring a file from one filesystem to another
(HDFS → S3, bucket → bucket), go through the sandbox:

```bash
python3 scripts/rocket_file_browser.py download "<src_path>" "<tmp_dir>" --fs <src_id>:<src_type>
python3 scripts/rocket_file_browser.py upload "<tmp_dir>/<name>" "<dst_dir>" --fs <dst_id>:<dst_type>
```

- It is an upload into the destination: the upload rules apply (the user asked for it,
  destination confirmed, the name must not exist).
- A "move" across filesystems additionally deletes the source with `rm` — only after
  the upload succeeded and with the user's explicit confirmation.
- A directory downloads as a zip; upload it and `extract` it on the destination
  filesystem if the user wants the tree, not the archive.
- Use a scratch folder for `<tmp_dir>` and remove the local copy afterwards unless the
  user wants to keep it.

## Behaviour that differs on S3

- **Permissions** — Gosec authorizes an S3 path with the bucket prepended
  (`/landing/a.csv` on `sales-landing` is checked as `/sales-landing/landing/a.csv`). A
  `401/403` on S3 when the same path works elsewhere usually means the user's policy
  does not cover that bucket prefix.
- **Directories are emulated** (key prefixes, with a marker object for an empty one):
  `ls` sizes, owners and permissions do not carry the HDFS meaning.
- **`mv` is copy + delete**, not an atomic rename — slow on large trees, and an
  interrupted move can leave both copies. Confirm before moving big directories.
- **`S3 filesystem not found in classpath`** — this Rocket lacks the S3 connector
  needed to open configured buckets; report it, the agent cannot fix it.
- `Filesystem with id '<id>' and type '<type>' not found` — the bucket was removed from
  Rocket's configuration after the listing; list again and ask the user.

The restricted roots (`/extensions`, `/mockData`, `/backups`, `/mlProjectModelArtifacts`,
`/mlProjectExecutionsArtifacts`) are refused on every filesystem, S3 included.
