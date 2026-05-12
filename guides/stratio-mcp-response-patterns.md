# Stratio MCP Response Patterns

Companion to `stratio-data-tools.md` (data MCPs) and `stratio-semantic-layer-tools.md` (governance MCPs). Read alongside whichever of those you have loaded — this guide documents two response patterns that can occur on any MCP tool listed there: polling for long-running tasks and handling outputs that exceed the host environment's response limit. Both are orthogonal to the specific tool and to which server it lives on.

## 1. Long-Running Task Polling

Any MCP tool may take longer than expected to complete. When this happens, the MCP server returns a response carrying a `task_id` instead of the data the tool would normally produce. This is not an error — the operation continues in the background and the result can be retrieved later.

**Before polling, verify both:**

- **Origin** — the response comes **directly** from a Stratio MCP tool call. A `task_id` nested in a subagent's `result`, a hook output or any other non-MCP envelope belongs to the host runtime, not to the MCP. Typical false positive: a subagent that fails and returns an empty `result` with its own id like `ses_xxxxxxxx` — treat as a subagent failure, do not poll.
- **Prefix** — a Stratio `task_id` **always starts with `mcp-ckpt-`** (followed by 16 hex chars, e.g. `mcp-ckpt-7c3e1f0a9b224e3d`). Values like `ses_*`, bare UUIDs or `task_*` are not Stratio task_ids — do **not** call `get_mcp_task_result` with them.

If either check fails, do not poll: process the response as-is or handle the upstream failure.

**Protocol when both checks pass:**

1. Wait **5 seconds**
2. Call `get_mcp_task_result(task_id=<the received task_id>)` on the **same MCP server that issued the `task_id`**. If the host environment exposes more than one server (e.g. `gov` and `sql`), mixing servers will return `not_found` even for valid ids.
3. Inspect the `status` field:
   - `"pending"` — still running. Wait **10 seconds** and call again. Repeat until the status changes
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
1. **Never read the full saved file directly into your own context.** It will trigger the same limit that caused the truncation
2. **Prefer delegating the file inspection to a subagent** when the host environment exposes one (e.g. an Explore / Task subagent). Brief it with the file path and the specific extraction it should perform, and ask it to return only the fragment you need — not the file contents
3. **If subagent delegation is not available**, inspect the file yourself with strict caps: `Grep` for targeted patterns first, then `Read` with `offset` and a small `limit` (≤ 200 lines per call). Never read end-to-end in a single call
4. **Iterate by need**: a first pass typically extracts an inventory (identifiers, names, counts); subsequent passes retrieve full records on demand. Stop as soon as the user's question is answered

**Typical extraction patterns** for list-style payloads:
- _Inventory_: `Grep` for the JSON key that delimits each entry (e.g. `"name":`) and count / list the matches
- _Topical subset_: `Grep` for keywords from the user's question over the saved file
- _Specific record_: `Grep` for the identifier, then `Read` ±N lines around the match for the surrounding context
- _Sample_: `Read` with `offset=0`, `limit=200` to inspect the structure before issuing more targeted reads

Applies to any tool that may return large payloads. On the data side, common cases include `list_domain_tables`, `list_domains`, `get_tables_details` over many tables, and `query_data` over wide/long results. On the governance side, common cases include `list_business_views`, `list_technical_domain_concepts`, `search_data_dictionary` and any `*_details` tool over large catalogs.
