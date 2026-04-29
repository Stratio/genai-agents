---
name: agent-packager
description: "Package an agent as a Stratio Cowork agents/v1 ZIP bundle. Use when the agent's files are ready and need to be assembled into a deployable ZIP with metadata."
argument-hint: "[agent-name]"
---

# Skill: Stratio Cowork Agent Packager

Step-by-step instructions for packaging an agent into the Stratio Cowork `agents/v1` bundle format.

## 1. Bundle Structure

A Stratio Cowork bundle is a ZIP file containing:

```
{name}-stratio-cowork.zip              # Container ZIP
  metadata.yaml                        # Bundle manifest (agents/v1)
  {name}-opencode-agent.zip            # Agent files (without shared skills)
  {name}-shared-skills.zip             # Shared skills (optional, only if new shared skills exist)
```

## 2. Generate the Agent ZIP

The agent ZIP contains all files needed to run the agent.

### Staging directory convention

All staging during packaging happens under `output/<agent-name>/.pack-staging/` (workdir-local, hidden). **Do not use `/tmp/` or `mktemp -d`** — in some execution environments (e.g. the Stratio sandbox) those paths are not writable, and silent improvisation leaks staging dirs into the final bundle. The cleanup of `.pack-staging/` happens **once, at the end of section 5**, after the container ZIP is built.

### Files to include

| File/Directory | Required | Notes |
|---------------|----------|-------|
| `AGENTS.md` | Yes | Agent instructions — must be at the ZIP root |
| `README.md` | Yes | User-facing documentation |
| `opencode.json` | Yes | Platform config with permissions |
| `.opencode/skills/` | If skills exist | Internal skills: `.opencode/skills/{name}/SKILL.md` |
| `scripts/` | Optional | Helper scripts used by the agent |
| `templates/` | Optional | Output templates used by the agent |
| Other files | Optional | Any additional files the agent needs |

### Files to NOT include

- `cowork-metadata.yaml` — description goes directly in `metadata.yaml`
- `shared-skills` manifest — shared skill references go in `metadata.yaml`
- `_shared-skills/` directory — these go in the separate shared-skills ZIP
- Temporary files, build artifacts, `dist/`, `.git/`

### Commands

```bash
# Staging dir lives under the agent workdir (hidden, workdir-local)
AGENT_NAME="{name}"
STAGING="output/$AGENT_NAME/.pack-staging/agent"
mkdir -p "$STAGING"

# Copy agent files to staging
cp "output/$AGENT_NAME/AGENTS.md"     "$STAGING/"
cp "output/$AGENT_NAME/README.md"     "$STAGING/"
cp "output/$AGENT_NAME/opencode.json" "$STAGING/"

# Copy internal skills (if they exist)
if [ -d "output/$AGENT_NAME/.opencode" ]; then
  cp -r "output/$AGENT_NAME/.opencode" "$STAGING/"
fi

# Copy any additional agent files (scripts, templates, etc.)
for item in "output/$AGENT_NAME/scripts" "output/$AGENT_NAME/templates"; do
  [ -d "$item" ] && cp -r "$item" "$STAGING/"
done

# Create the agent ZIP (destination lives outside the staging dir)
(cd "$STAGING" && zip -rq "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip" .)

# IMPORTANT: do NOT delete .pack-staging here. Section 5 owns the cleanup
# after the container ZIP is built, so the bundle staging can reuse the same
# parent dir without a race.
```

## 3. Generate the Shared Skills ZIP

Only create this if the agent has **new** shared skills (created during the workflow). Skills that already exist on the platform are NOT included — they are loaded at runtime.

### Structure

```
{skill-name-1}/
  SKILL.md
  [supporting-file-1.md]
  [supporting-file-2.md]
{skill-name-2}/
  SKILL.md
```

Each skill is a directory named after the skill, containing at minimum a `SKILL.md`.

### Path substitutions

If any SKILL.md references `skills-guides/filename.md`, and the guide file is embedded alongside the SKILL.md, replace the path to just `filename.md` (remove the `skills-guides/` prefix).

### Commands

```bash
AGENT_NAME="{name}"
SHARED_DIR="output/$AGENT_NAME/_shared-skills"

if [ -d "$SHARED_DIR" ] && [ "$(ls -A "$SHARED_DIR")" ]; then
  (cd "$SHARED_DIR" && zip -r "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" .)
fi
```

## 4. Generate metadata.yaml

The manifest describes the bundle contents.

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `format_version` | string | Always `"agents/v1"` |
| `name` | string | Agent name in kebab-case (e.g., `"my-agent"`) |
| `agent_zip` | string | Filename of the agent ZIP (e.g., `"my-agent-opencode-agent.zip"`) |
| `description` | string | One-sentence description of what the agent does |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `skills_zip` | string | Filename of the shared skills ZIP (only if it exists) |
| `external_version` | string | Semantic version (e.g., `"1.0.0"`) |

### Example

```yaml
format_version: "agents/v1"
name: "my-agent"
agent_zip: "my-agent-opencode-agent.zip"
skills_zip: "my-agent-shared-skills.zip"
description: "Expert agent for analyzing data quality coverage and creating quality rules."
```

Without shared skills:

```yaml
format_version: "agents/v1"
name: "my-agent"
agent_zip: "my-agent-opencode-agent.zip"
description: "Expert agent for analyzing data quality coverage and creating quality rules."
```

### Commands

```bash
AGENT_NAME="{name}"
DESCRIPTION="{agent description}"
METADATA="output/$AGENT_NAME/metadata.yaml"

cat > "$METADATA" <<EOF
format_version: "agents/v1"
name: "$AGENT_NAME"
agent_zip: "${AGENT_NAME}-opencode-agent.zip"
EOF

# Add skills_zip only if shared skills exist
if [ -f "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" ]; then
  echo "skills_zip: \"${AGENT_NAME}-shared-skills.zip\"" >> "$METADATA"
fi

echo "description: \"$DESCRIPTION\"" >> "$METADATA"
```

## 5. Create the Container ZIP

Assemble the final bundle:

```bash
AGENT_NAME="{name}"
BUNDLE_DIR="output/$AGENT_NAME/.pack-staging/bundle"
mkdir -p "$BUNDLE_DIR"

# Copy components to bundle staging
cp "output/$AGENT_NAME/metadata.yaml"                       "$BUNDLE_DIR/"
cp "output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip"    "$BUNDLE_DIR/"

# Include shared skills ZIP only if it exists
if [ -f "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" ]; then
  cp "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" "$BUNDLE_DIR/"
fi

# Create the container ZIP (destination lives outside the staging dir)
(cd "$BUNDLE_DIR" && zip -rq "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.zip" .)

# Cleanup ALL packaging staging in one shot (covers section 2 and section 5)
rm -rf "output/$AGENT_NAME/.pack-staging"
```

**Fallback**: If `zip` is not available, use `tar` (run before the cleanup above so `$BUNDLE_DIR` still exists):

```bash
(cd "$BUNDLE_DIR" && tar -czf "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.tar.gz" .)
```

### Integrity verification

After creating the container ZIP, verify:

1. `metadata.yaml` exists in the container ZIP
2. `metadata.yaml` contains `format_version: "agents/v1"`
3. The agent ZIP referenced by `agent_zip` exists in the container
4. The agent ZIP contains `AGENTS.md` at the root
5. If `skills_zip` is declared, the shared skills ZIP exists in the container
6. If shared skills ZIP exists, each skill has a `SKILL.md`

```bash
AGENT_NAME="{name}"
BUNDLE="output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.zip"

# List contents
echo "Bundle contents:"
unzip -l "$BUNDLE"

# Verify metadata
unzip -p "$BUNDLE" metadata.yaml

# Verify AGENTS.md in agent ZIP
unzip -p "$BUNDLE" "${AGENT_NAME}-opencode-agent.zip" | funzip | unzip -l /dev/stdin 2>/dev/null | grep AGENTS.md
```

## 6. Deliver to the User

### Pre-delivery check

Before reporting to the user, ensure `output/<agent-name>/` is in a clean state.

**Must be present** (open list — the exact contents depend entirely on the agent's design):

- The agent's source files and directories generated during the workflow. At minimum: `AGENTS.md`, `README.md`, `opencode.json`. Beyond that, **anything** the design defines — `.opencode/`, `scripts/`, `templates/`, internal data dirs, prompt libraries, additional docs, custom subfolders, etc. There is no fixed list: any file or folder that the agent legitimately needs is valid.
- `metadata.yaml`
- `<name>-opencode-agent.zip`
- `<name>-stratio-cowork.zip`
- Optional: `<name>-shared-skills.zip` (only if new shared skills were created)

**Must NOT be present** (this is a closed list — these are forbidden artefacts):

- `.pack-staging/` — packaging staging from sections 2 and 5. The cleanup at the end of section 5 should have removed it; if it still exists, the cleanup did not run.
- `_pack_tmp/` — legacy staging name from earlier improvisations. Should never be created by the current flow, but clean it defensively if found.
- Partial or temporary files left by failed runs (e.g. half-built ZIPs, `.tmp` suffixes).

If any forbidden artefact is present, remove it before reporting. The directory must be clean enough that the user — or the sandbox-export mechanism — can identify the deliverable unambiguously.

```bash
AGENT_NAME="{name}"
ls -la "output/$AGENT_NAME/"
[ -d "output/$AGENT_NAME/.pack-staging" ] && rm -rf "output/$AGENT_NAME/.pack-staging"
[ -d "output/$AGENT_NAME/_pack_tmp" ]     && rm -rf "output/$AGENT_NAME/_pack_tmp"
```

### Report

After successful packaging, report:

1. **File path**: full path to the container ZIP
2. **File size**: human-readable size
3. **Bundle contents**: list the files inside the container ZIP
4. **Next steps**:
   - Proceed to section 7 (deployment to Stratio Cowork) — that is the next step of the workflow.
   - For reference: the artifact identified as the deployable unit is `<name>-stratio-cowork.zip` (the container ZIP). If a manual upload is ever needed, that is the file to use — do NOT use the agent ZIP, the shared-skills ZIP, or the workdir folder.
   - After deployment, configure MCP servers from the web interface (if the agent needs external tools).
   - Test the agent with the usage scenarios defined during design.

## 7. Deploy the bundle to Stratio Cowork

This is a **mandatory step** of the packaging workflow, not an option. Load the `/cowork-api` skill and run `tasks/upload-agent.md` end-to-end. That sub-file owns: the pre-check (via `skills-guides/external-api-calls.md` §2), the question to the user about `on_conflict`, the curl invocation against `/v1/agents/bundle/import`, and how to surface the HTTP code and JSON response.

The ZIP path to pass is `output/<agent-name>/<agent-name>-stratio-cowork.zip` (the container ZIP produced in section 5).

The `metadata.yaml` generated in section 4 already carries `name`, so the API reads it from the bundle — `cowork-api` does not need to ask for or pass it.

The pre-check inside `cowork-api` is an **environment health check** (env vars, certificates), not a sandbox detector. The host agent always runs inside the Stratio sandbox; if the pre-check reports missing prerequisites (e.g. `GENAI_API_URL`, `USER_CERT_PATH`, `USER_KEY_PATH`, `CA_CERT_PATH`), surface the missing pieces to the user as an environment incident — do NOT silence the failure and do NOT refuse with a generic "I can't". The bundle is already packaged correctly; only the deployment step did not complete, and the user can decide how to proceed.
