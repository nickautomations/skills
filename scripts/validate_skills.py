#!/usr/bin/env python3
"""
Validate SKILL.md files in skills/* for correct Agent Skills format.

Checks each skill folder has:
- A SKILL.md file at the root
- Valid YAML frontmatter
- Required fields: `name`, `description`
- name matches the folder name
- description is non-empty and a reasonable length

Also checks that skills/ and .claude-plugin/marketplace.json agree: every skill
folder is listed in some plugin, and every listed skill has a folder. Without
this, a new skill ships invisible to anyone installing via the marketplace.

Exit codes:
  0 = all skills valid
  1 = one or more validation errors

Usage:
  python scripts/validate_skills.py
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)
DESC_RE = re.compile(r"^description:\s*(.+?)$", re.MULTILINE | re.DOTALL)


def parse_simple_yaml(text: str) -> dict:
    """
    Parse a tiny subset of YAML — enough for SKILL.md frontmatter.
    We only support top-level `key: value` pairs (no nested structures).
    Description may span multiple lines until the next `key:` line or end of frontmatter.
    """
    result = {}
    lines = text.splitlines()
    current_key = None
    current_value_parts: list[str] = []

    for line in lines:
        # New top-level key (starts at column 0, has `: `)
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", line)
        if m and not line.startswith(" "):
            # Flush previous key
            if current_key is not None:
                result[current_key] = " ".join(current_value_parts).strip()
            current_key = m.group(1).strip()
            initial = m.group(2).strip()
            current_value_parts = [initial] if initial else []
        else:
            # Continuation line for the current value
            if current_key is not None:
                current_value_parts.append(line.strip())

    if current_key is not None:
        result[current_key] = " ".join(current_value_parts).strip()

    return result


def validate_skill(skill_dir: Path) -> list[str]:
    """Return list of error messages (empty list = valid)."""
    errors: list[str] = []
    folder_name = skill_dir.name

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{folder_name}: missing SKILL.md")
        return errors

    content = skill_md.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(content)
    if not m:
        errors.append(f"{folder_name}: SKILL.md is missing YAML frontmatter (must start with --- on the first line)")
        return errors

    frontmatter = parse_simple_yaml(m.group(1))

    # Required: name
    name = frontmatter.get("name", "").strip().strip('"').strip("'")
    if not name:
        errors.append(f"{folder_name}: frontmatter missing required `name` field")
    elif name != folder_name:
        errors.append(f"{folder_name}: frontmatter name `{name}` does not match folder name `{folder_name}`")

    if name and not re.fullmatch(r"[a-z0-9][a-z0-9-]*[a-z0-9]", name):
        errors.append(f"{folder_name}: name `{name}` should be lowercase with hyphens (no spaces, no underscores, no caps)")

    # Required: description
    description = frontmatter.get("description", "").strip().strip('"').strip("'")
    if not description:
        errors.append(f"{folder_name}: frontmatter missing required `description` field")
    elif len(description) < 30:
        errors.append(f"{folder_name}: description is too short ({len(description)} chars) — should clearly explain what the skill does and when to trigger it")
    elif len(description) > 2000:
        errors.append(f"{folder_name}: description is too long ({len(description)} chars) — keep under 2000 chars")

    return errors


def validate_marketplace(skill_names: list[str]) -> list[str]:
    """Return list of error messages for skills/ vs marketplace.json drift."""
    errors: list[str] = []

    if not MARKETPLACE_JSON.is_file():
        return [f"marketplace: {MARKETPLACE_JSON.relative_to(REPO_ROOT)} not found"]

    try:
        manifest = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"marketplace: marketplace.json is not valid JSON ({exc})"]

    listed: dict[str, str] = {}  # skill name -> plugin that lists it
    for plugin in manifest.get("plugins", []):
        plugin_name = plugin.get("name", "<unnamed plugin>")
        for skill in plugin.get("skills", []):
            listed[skill] = plugin_name

    for name in skill_names:
        if name not in listed:
            errors.append(
                f"marketplace: skill `{name}` exists in skills/ but is listed in no plugin "
                f"— add it to a plugin's `skills` array in marketplace.json"
            )

    for name, plugin_name in listed.items():
        if name not in skill_names:
            errors.append(
                f"marketplace: plugin `{plugin_name}` lists skill `{name}`, "
                f"but skills/{name}/ does not exist"
            )

    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"ERROR: skills/ directory not found at {SKILLS_DIR}", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    if not skill_dirs:
        print("WARNING: no skill folders found under skills/")
        return 0

    print(f"Validating {len(skill_dirs)} skill(s)...\n")

    all_errors: list[str] = []
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            for err in errors:
                print(f"  ✗ {err}")
                all_errors.append(err)
        else:
            print(f"  ✓ {skill_dir.name}")

    print("\nChecking marketplace.json coverage...\n")
    marketplace_errors = validate_marketplace([d.name for d in skill_dirs])
    if marketplace_errors:
        for err in marketplace_errors:
            print(f"  ✗ {err}")
            all_errors.append(err)
    else:
        print("  ✓ every skill is listed in marketplace.json")

    print()
    if all_errors:
        print(f"FAIL: {len(all_errors)} validation error(s)")
        return 1

    print(f"PASS: all {len(skill_dirs)} skill(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
