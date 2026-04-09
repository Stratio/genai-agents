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
# Create a clean staging directory
AGENT_NAME="{name}"
STAGING=$(mktemp -d)

# Copy agent files to staging
cp output/$AGENT_NAME/AGENTS.md "$STAGING/"
cp output/$AGENT_NAME/README.md "$STAGING/"
cp output/$AGENT_NAME/opencode.json "$STAGING/"

# Copy internal skills (if they exist)
if [ -d "output/$AGENT_NAME/.opencode" ]; then
  cp -r "output/$AGENT_NAME/.opencode" "$STAGING/"
fi

# Copy any additional agent files (scripts, templates, etc.)
for item in output/$AGENT_NAME/scripts output/$AGENT_NAME/templates; do
  [ -d "$item" ] && cp -r "$item" "$STAGING/"
done

# Create the agent ZIP
(cd "$STAGING" && zip -r "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip" .)

# Clean up
rm -rf "$STAGING"
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
BUNDLE_DIR=$(mktemp -d)

# Copy components to bundle staging
cp "output/$AGENT_NAME/metadata.yaml" "$BUNDLE_DIR/"
cp "output/$AGENT_NAME/${AGENT_NAME}-opencode-agent.zip" "$BUNDLE_DIR/"

# Include shared skills ZIP only if it exists
if [ -f "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" ]; then
  cp "output/$AGENT_NAME/${AGENT_NAME}-shared-skills.zip" "$BUNDLE_DIR/"
fi

# Create the container ZIP
(cd "$BUNDLE_DIR" && zip -r "$OLDPWD/output/$AGENT_NAME/${AGENT_NAME}-stratio-cowork.zip" .)

# Clean up
rm -rf "$BUNDLE_DIR"
```

**Fallback**: If `zip` is not available, use `tar`:

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

After successful packaging, report:

1. **File path**: full path to the container ZIP
2. **File size**: human-readable size
3. **Bundle contents**: list the files inside the container ZIP
4. **Next steps**:
   - Upload the ZIP to the Stratio Cowork agent management interface
   - Configure MCP servers from the web interface (if the agent needs external tools)
   - Test the agent with the usage scenarios defined during design
