# Stratio MCP Response Patterns

Companion to `stratio-data-tools.md` (data MCPs) and `stratio-semantic-layer-tools.md` (governance MCPs). Read alongside whichever of those you have loaded — this guide documents two response patterns that can occur on any MCP tool listed there: polling for long-running tasks and handling outputs that exceed the host environment's response limit. Both are orthogonal to the specific tool and to which server it lives on.

## 1. Long-Running Task Polling

Any MCP tool may take longer than expected to complete. When this happens, the MCP server returns a response carrying a `task_id` instead of the data the tool would normally produce. This is not an error — the operation continues in the background and the result can be retrieved later.

**Before polling, verify both:**

- **Origin** — the response comes **directly** from a Stratio MCP tool call. A `task_id` nested in a subagent's `result`, a hook output or any other non-MCP envelope belongs to the host runtime, not to the MCP. Typical false positive: a subagent that fails and returns an empty `result` with its own id like `ses_xxxxxxxx` — treat as a subagent failure, do not poll.
- **Prefix** — a Stratio `task_id` **always starts with `mcp-ckpt-`** (followed by 16 hex chars, e.g. `mcp-ckpt-7c3e1f0a9b224e3d`). Values like `ses_*`, bare UUIDs or `task_*` are not Stratio task_ids — do **not** call `get_mcp_task_result` with them.

If either check fails, do not poll: process the response as-is or handle the upstream failure.

**Protocol when both checks pass:**

1. Call `get_mcp_task_result(task_id=<the received task_id>)` on the **same MCP server that issued the `task_id`**. If the host environment exposes more than one server (e.g. `gov` and `sql`), mixing servers will return `not_found` even for valid ids. Do not introduce explicit waits between calls — issue the next poll as soon as you have processed the previous response.
2. Inspect the `status` field:
   - `"pending"` — still running. Call again immediately. Repeat until the status changes
   - `"done"` — the `result` field contains the original tool response. Parse and use it as if the tool had returned it directly
   - `"error"` — read `error` and apply the calling guide's retry strategy (e.g. simplify, split, reformulate) or inform the user
   - `"not_found"` — the task_id expired or is unknown. Retry the original tool call from scratch

Applies to ALL MCP tools on every Stratio MCP server.

## 2. Large Tool Outputs — Truncated and Saved to File

When a tool's inline output would exceed the host environment's response limit, the response is replaced by a truncation notice plus a file path where the full content was written. The data is already there — the tool succeeded — but it is no longer inline. This is **distinct from §1** (where the response is a `task_id` because the tool is still running): here the work is done; there it is still pending.

**Detection** (any of):
- The response contains an explicit truncation marker (e.g. `…N bytes truncated…`, "output was truncated", "Full output saved to ...") and a file path
- The response carries a saved-file path with no `task_id` field

**Protocol** (apply in order):
1. **Never read the full saved file directly into your own context.** It will trigger the same limit that caused the truncation.
2. **Delegate the file inspection to the runtime's subagent** (e.g. OpenCode's `explore` via the Task tool) to preserve your own context. The subagent has NO view of the parent conversation — it only sees the prompt you write. The prompt MUST contain:
   - **The full saved file path, copied literally from the truncation notice.** Do not paraphrase. Do not ask the subagent to find it with Glob — if it has to guess, it can fail and surface an error to you. Paste the absolute path exactly as it appeared in the runtime's hint.
   - **The extraction goal**: what to extract (inventory, topical subset, specific record) and what to return (e.g. a markdown list of table names matching X).
   - **A reminder to return only the extracted fragment**, not the full file.
   - **If the saved file is a JSON payload minified on a single line** — the usual shape for Stratio MCP outputs — say so explicitly to the subagent and tell it that line-based tools (`Grep` counts matches per line, `Read` truncates each line to a fixed character cap that is not configurable in OpenCode) won't help. Direct it to use a structural parser via Bash: `jq` for one-shot queries (e.g. `jq '.tables | length'`, `jq '.tables[:20] | .[].name'`), or a short Python script for richer extraction (the sandbox ships Python with `json` in the standard library — the subagent can run an inline `python -c '...'` or save a small script).

   Leave the rest of the *how* to the subagent — it is a file-search specialist and will pick the right primitives within the constraints above. Do not embed regex patterns beyond what is needed to convey the goal.

   Good prompt example:
   > "Inspect the saved file at `<full-path-from-truncation-notice>`. The file is a JSON payload minified on a single line, so use `jq` (or a short inline Python script) via Bash rather than line-based tools. Extract a topical subset: only the table entries whose name contains 'customer'. Return a markdown list of the matching names — do not return the file content."

3. **If the subagent returns "file not found" or "permission denied"** on the saved path, do NOT retry and do NOT delegate again. Process the file yourself in this conversation with strict caps: `Grep` for targeted patterns first, then `Read` with `offset` and a small `limit` (≤ 200 lines per call). Never read end-to-end in a single call.
4. **If `Grep`/`Read` in the main session also fails**, surface the limitation to the user and reformulate the MCP query with a narrower scope (additional filters, `domain_type`, narrower keyword) instead of looping. Never ask the user the same question twice.
5. **Iterate by need**: first pass extracts an inventory (identifiers, names, counts); subsequent passes retrieve full records on demand. Stop as soon as the user's question is answered.

**Typical extraction goals** for list-style payloads (express these to the subagent or apply them in the fallback):
- _Inventory_: identifiers / names / count of entries.
- _Topical subset_: only entries matching the user's keywords.
- _Specific record_: a single entry by identifier, with surrounding context if useful.
- _Sample_: first N entries to inspect the structure before deciding the goal.

Applies to any tool that may return large payloads. On the data side, common cases include `list_domain_tables`, `list_domains`, `get_tables_details` over many tables, and `query_data` over wide/long results. On the governance side, common cases include `list_business_views`, `list_technical_domain_concepts`, `search_data_dictionary` and any `*_details` tool over large catalogs.
