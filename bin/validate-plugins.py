#!/usr/bin/env python3
"""validate-plugins.py — Validator for plugins/<name>/plugin.yaml manifests.

Validates each plugin against the schema and the monorepo state.

Usage:
  bin/validate-plugins.py                # validate all plugins/
  bin/validate-plugins.py --plugin NAME  # validate one plugin
  bin/validate-plugins.py --strict       # treat warnings as errors

Exit code: 0 if OK, 1 if any error (or any warning under --strict).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
SHARED_SKILLS_DIR = REPO_ROOT / "shared-skills"

KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")
DESCRIPTION_MAX = 1024
VALID_PLATFORMS = {"stratio-cowork", "claude"}

# Optional top-level keys in plugin.yaml. Anything else is rejected to catch typos.
ALLOWED_KEYS = {"name", "version", "description", "tags", "contents", "mcps", "platforms"}
ALLOWED_CONTENTS_KEYS = {"agents", "skills"}


class Issue:
    __slots__ = ("level", "plugin", "message")

    def __init__(self, level: str, plugin: str, message: str) -> None:
        self.level = level  # "error" or "warn"
        self.plugin = plugin
        self.message = message

    def __str__(self) -> str:
        prefix = "ERROR" if self.level == "error" else "WARN"
        return f"[{prefix}] {self.plugin}: {self.message}"


def _agent_exists(name: str) -> bool:
    """An agent is a top-level monorepo directory containing an AGENTS.md file."""
    candidate = REPO_ROOT / name
    return candidate.is_dir() and (candidate / "AGENTS.md").is_file()


def _skill_exists(name: str) -> bool:
    return (SHARED_SKILLS_DIR / name / "SKILL.md").is_file()


def _collect_known_mcps() -> set[str]:
    """Read every <agent>/mcps file in the monorepo and collect declared MCP names."""
    known: set[str] = set()
    for mcps_file in REPO_ROOT.glob("*/mcps"):
        # Only count agent-owned mcps files (sibling of AGENTS.md).
        if not (mcps_file.parent / "AGENTS.md").is_file():
            continue
        for raw in mcps_file.read_text().splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                known.add(line)
    return known


def _validate_plugin(plugin_dir: Path, known_mcps: set[str]) -> list[Issue]:
    issues: list[Issue] = []
    name_from_dir = plugin_dir.name

    def err(msg: str) -> None:
        issues.append(Issue("error", name_from_dir, msg))

    def warn(msg: str) -> None:
        issues.append(Issue("warn", name_from_dir, msg))

    manifest_path = plugin_dir / "plugin.yaml"
    if not manifest_path.is_file():
        err(f"missing plugin.yaml at {manifest_path.relative_to(REPO_ROOT)}")
        return issues

    try:
        data = yaml.safe_load(manifest_path.read_text()) or {}
    except yaml.YAMLError as exc:
        err(f"invalid YAML: {exc}")
        return issues

    if not isinstance(data, dict):
        err("plugin.yaml must be a mapping at the top level")
        return issues

    extra_keys = set(data.keys()) - ALLOWED_KEYS
    if extra_keys:
        err(f"unknown top-level keys: {sorted(extra_keys)} (allowed: {sorted(ALLOWED_KEYS)})")

    # name
    declared_name = data.get("name")
    if not isinstance(declared_name, str) or not declared_name:
        err("'name' is required and must be a non-empty string")
    else:
        if not KEBAB_RE.match(declared_name):
            err(f"'name' must be kebab-case (got '{declared_name}')")
        if declared_name != name_from_dir:
            err(f"'name' ({declared_name!r}) must match parent directory ({name_from_dir!r})")

    # version (optional)
    version = data.get("version")
    if version is not None:
        if not isinstance(version, str) or not SEMVER_RE.match(version):
            err(f"'version' must be a semver-like string (got {version!r})")

    # description
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        err("'description' is required and must be a non-empty string")
    elif len(description) > DESCRIPTION_MAX:
        err(f"'description' exceeds {DESCRIPTION_MAX} chars (got {len(description)})")

    # tags (optional)
    tags = data.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            err("'tags' must be a list of strings")

    # contents
    contents = data.get("contents") or {}
    if not isinstance(contents, dict):
        err("'contents' must be a mapping")
        contents = {}
    extra_contents_keys = set(contents.keys()) - ALLOWED_CONTENTS_KEYS
    if extra_contents_keys:
        err(f"unknown 'contents' keys: {sorted(extra_contents_keys)} (allowed: {sorted(ALLOWED_CONTENTS_KEYS)})")

    agents = contents.get("agents") or []
    if agents and not (isinstance(agents, list) and all(isinstance(a, str) for a in agents)):
        err("'contents.agents' must be a list of strings")
        agents = []
    skills = contents.get("skills") or []
    if skills and not (isinstance(skills, list) and all(isinstance(s, str) for s in skills)):
        err("'contents.skills' must be a list of strings")
        skills = []

    if not agents and not skills:
        err("plugin must declare at least one agent or one skill in 'contents'")

    for agent in agents:
        if not _agent_exists(agent):
            err(f"agent '{agent}' not found in monorepo (expected directory with AGENTS.md)")
    for skill in skills:
        if not _skill_exists(skill):
            err(f"skill '{skill}' not found at shared-skills/{skill}/SKILL.md")

    # mcps (optional, only in skills-only plugins)
    mcps = data.get("mcps")
    if mcps is not None:
        if agents:
            err("'mcps' is only allowed in skills-only plugins (no 'contents.agents')")
        elif not isinstance(mcps, list) or not all(isinstance(m, str) and m for m in mcps):
            err("'mcps' must be a list of non-empty strings")
        else:
            for mcp in mcps:
                if mcp not in known_mcps:
                    warn(
                        f"MCP '{mcp}' not declared in any <agent>/mcps file in the monorepo "
                        f"(known: {sorted(known_mcps)}) — possible typo"
                    )

    # platforms (optional)
    platforms = data.get("platforms")
    if platforms is not None:
        if not isinstance(platforms, list) or not all(isinstance(p, str) for p in platforms):
            err("'platforms' must be a list of strings")
        else:
            invalid = [p for p in platforms if p not in VALID_PLATFORMS]
            if invalid:
                err(f"invalid platforms: {invalid} (valid: {sorted(VALID_PLATFORMS)})")
            if agents and "claude" in platforms:
                err(
                    "Claude does not support agents in plugins; remove 'claude' from "
                    "'platforms' or split the plugin into a skills-only one"
                )

    # README.md is required (user-facing documentation)
    if not (plugin_dir / "README.md").is_file():
        err("missing README.md")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plugin", help="Validate only this plugin (directory name)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    if not PLUGINS_DIR.is_dir():
        print(f"==> No plugins/ directory at {PLUGINS_DIR.relative_to(REPO_ROOT)} — nothing to validate")
        return 0

    if args.plugin:
        targets = [PLUGINS_DIR / args.plugin]
        if not targets[0].is_dir():
            print(f"ERROR: plugin '{args.plugin}' not found at {targets[0].relative_to(REPO_ROOT)}", file=sys.stderr)
            return 2
    else:
        targets = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))

    if not targets:
        print("==> No plugins to validate")
        return 0

    known_mcps = _collect_known_mcps()
    print(f"==> Validating {len(targets)} plugin(s); known MCPs: {sorted(known_mcps) or 'none'}")

    all_issues: list[Issue] = []
    for plugin_dir in targets:
        issues = _validate_plugin(plugin_dir, known_mcps)
        all_issues.extend(issues)
        n_err = sum(1 for i in issues if i.level == "error")
        n_warn = sum(1 for i in issues if i.level == "warn")
        status = "OK" if n_err == 0 and (not args.strict or n_warn == 0) else "FAIL"
        print(f"  [{status}] {plugin_dir.name}  ({n_err} error(s), {n_warn} warning(s))")
        for issue in issues:
            print(f"    {issue}")

    n_err = sum(1 for i in all_issues if i.level == "error")
    n_warn = sum(1 for i in all_issues if i.level == "warn")
    print(f"==> Total: {n_err} error(s), {n_warn} warning(s)")

    if n_err > 0:
        return 1
    if args.strict and n_warn > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
