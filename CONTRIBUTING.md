# Contributing

Thanks for your interest in adding a skill to this repo.

## Adding a new skill

1. **Copy the template:**
   ```bash
   cp -r template skills/my-skill-name
   ```

2. **Edit `skills/my-skill-name/SKILL.md`:**
   - Set a clear `name` (lowercase, hyphens, must match the folder name)
   - Write a `description` that covers *what the skill does* and *when to use it*. The description is what Claude uses to decide whether to trigger the skill — be specific.
   - Replace the placeholder instructions with real ones

3. **Add any supporting files:**
   - `scripts/` — executable helpers (Python, Node, shell)
   - `references/` — markdown reference docs that Claude can load on demand
   - `assets/` — templates, logos, static files

4. **Test locally before submitting:**
   ```bash
   # Copy to your local Claude skills directory
   cp -r skills/my-skill-name ~/.claude/skills/
   # Restart Claude Code, then trigger the skill in a session
   ```

5. **Open a pull request.** CI will validate the `SKILL.md` frontmatter automatically.

## Skill structure conventions

Follow the structure used by [Anthropic's reference skills](https://github.com/anthropics/skills):

```
skills/my-skill-name/
├── SKILL.md              # required — YAML frontmatter + instructions
├── README.md             # recommended — install + setup guide for end users
├── scripts/              # optional — executable helpers
├── references/           # optional — additional markdown context loaded on demand
└── assets/               # optional — templates, images, fonts, etc.
```

## SKILL.md format

```markdown
---
name: my-skill-name
description: Short, specific description of what this skill does and when to use it. Include trigger phrases so Claude knows when to fire it.
---

# Skill Name

## When to use this skill
...

## Workflow
...

## Reference files
...
```

The `description` field is the most important part — it's what Claude reads to decide if the skill applies to the current request. Write it like a search query: include the keywords and phrases that should trigger it.

## What we'll merge

- Skills that follow the [Agent Skills standard](https://agentskills.io)
- Skills relevant to the Nick Automations brand (AI, automation, business workflows, content)
- Skills that pass CI (valid frontmatter, no broken references)
- Skills with clear documentation and an honest description of what they do and don't do

## What we won't merge

- Skills that fabricate or invent facts the source material doesn't support
- Skills that require proprietary services the user can't easily replicate
- Skills that don't include a `README.md` or have an unclear purpose
- Skills that duplicate existing skills without meaningful improvement

## Questions?

Open a discussion or reach out at [nickautomations.com](https://nickautomations.com).
