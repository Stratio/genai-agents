---
name: cowork-api
description: "Capabilities exposed by the Stratio Cowork management REST API (`genai-api`): registering new skills, registering new agent bundles, and any future operation against that API. Use when the agent needs to call the Cowork management plane to deploy or manage skills/agents from inside the Stratio sandbox."
---

# Skill: Stratio Cowork management API (`genai-api`)

Router skill. Each capability lives in its own file under `tasks/`. **This file is intentionally minimal** — when the agent needs to perform a specific task, it must load and follow the corresponding sub-file in full. Do not improvise the request from this index.

## Prerequisites — read first

Before any call, follow `skills-guides/external-api-calls.md`:

- §1 lists the environment variables and certificate paths the sandbox provides.
- §2 has the standard pre-check (`preflight_external_api`). Run it; if it fails, stop and inform the user that the operation requires running inside the Stratio sandbox.
- §3 and §4 are the curl / Python templates. Each task below picks one and only adds the endpoint-specific bits (path, multipart field, query params).
- §5 is the error table to use when surfacing failures back to the user.

`GENAI_API_URL` (env var) is the base URL of the API. All endpoints below are relative to it.

## Capability index

| Capability | When to use | Sub-file to load |
|---|---|---|
| Upload a skill bundle | The user has packaged a skill into a ZIP and wants it registered in Stratio Cowork. | `tasks/upload-skill.md` |
| Upload an agent bundle | The user has packaged an agent (`agents/v1` container ZIP) and wants it registered in Stratio Cowork. | `tasks/upload-agent.md` |

## Routing rules

1. Identify the capability from the user's intent. If none of the entries above matches, this skill cannot help — say so.
2. Run the pre-check from `skills-guides/external-api-calls.md` §2. If it fails, stop and report.
3. Load the matching sub-file and follow it end-to-end. Do not blend instructions across sub-files.
4. After the call, surface the HTTP code and response body to the user as described in `skills-guides/external-api-calls.md` §5.

## Adding a new capability

To extend this skill with a new operation against `genai-api`:

1. Create `tasks/<capability>.md` with: when to use, endpoint (method + path + content type), required and optional parameters, ready-to-run command, expected response, error cases specific to this endpoint.
2. Add an entry to the **Capability index** above.
3. Mirror both files under `es/shared-skills/cowork-api/`.

The sub-file is the source of truth for its capability. The index above is just routing.
