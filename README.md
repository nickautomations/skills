# Nick Automations Skills

Open-source Agent Skills from [Nick Automations](https://nickautomations.com) — AI/automation consulting & implementation for businesses.

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. They follow the [Agent Skills specification](https://agentskills.io) and work across Claude Code, Claude.ai, Cursor, Gemini CLI, and other compatible agents.

## Available Skills

| Skill | Description | Install |
|-------|-------------|---------|
| [youtube-to-infographic](./skills/youtube-to-infographic) | Turn a YouTube video, article, or text into a branded editorial infographic in the Nick Automations design system | `npx skills add nickautomations/skills --skill youtube-to-infographic` |

More coming soon. See [CONTRIBUTING.md](./CONTRIBUTING.md) if you want to add one.

## Install

You have three ways to install skills from this repo.

### Option 1: `npx skills` CLI (recommended)

```bash
npx skills add nickautomations/skills --skill youtube-to-infographic
```

This is the simplest path. Works for any agent that supports the Agent Skills standard (Claude Code, Cursor, Gemini CLI, Codex CLI, etc.).

### Option 2: Claude Code Plugin Marketplace

Inside Claude Code:

```
/plugin marketplace add nickautomations/skills
/plugin install content-skills@nick-automations-skills
```

This installs the full **content-skills** bundle, which currently includes `youtube-to-infographic`. As we add more content-related skills, they'll be included automatically.

### Option 3: Git clone (for forking or contributing)

```bash
git clone https://github.com/nickautomations/skills
cp -r skills/youtube-to-infographic ~/.claude/skills/
```

Then restart your agent.

## What's in this repo

```
nickautomations/skills/
├── .claude-plugin/           # Claude Code plugin marketplace manifest
│   └── marketplace.json
├── skills/                   # All published skills
│   └── youtube-to-infographic/
├── template/                 # Starter scaffold for new skills
├── scripts/                  # Repo-level helper scripts (validation, etc.)
├── .github/workflows/        # CI: validates SKILL.md on every PR
├── LICENSE                   # Apache 2.0
├── CONTRIBUTING.md           # How to propose a new skill
└── README.md                 # This file
```

Every skill in `skills/` is a self-contained folder with its own `SKILL.md` (instructions, YAML frontmatter) plus optional `scripts/`, `references/`, and `assets/` subfolders. See the [Agent Skills spec](https://agentskills.io) for the full format.

## About Nick Automations

[Nick Automations](https://nickautomations.com) builds AI and automation systems for businesses. These skills encode the workflows and design system we use ourselves. You're welcome to fork them, adapt them, or use them as-is.

If you want this kind of thing built for your business → [nickautomations.com](https://nickautomations.com)

## License

Apache 2.0 — see [LICENSE](./LICENSE). Fork it, modify it, ship it. Commercial use is fine.
