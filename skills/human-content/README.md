# Human Content

Write, edit, and plan content that reads like a person wrote it.

## What it does

One skill, four modes:

| Mode | Ask | You get |
|------|-----|---------|
| **Write** | "Draft a landing page for…" | Copy by section, annotated choices, 2-3 headline/CTA alternatives |
| **Edit** | "Make this post sound less AI" | Edited draft + a short "What changed" note |
| **Detect** | "Does this read as AI-written?" | Named patterns, quoted lines, a fix for each. No rewrite |
| **Plan** | "What should we publish next quarter?" | Topics mapped to buyer stage, prioritized |

Every draft runs in a fixed order: strategy → psychology → copy → humanize pass. A writing sample you provide overrides every style rule.

## Rules it will not break

- Never invents a fact, number, quote, or testimonial.
- Uses persuasion levers honestly or not at all.
- Preserves your voice when editing: minimum effective edit.

## Files

```
human-content/
├── SKILL.md                  # workflow, modes, editing principles
└── references/
    ├── ai-patterns.md        # AI-writing tells, loaded for humanize/detect
    └── psychology.md         # persuasion models, loaded when picking an angle
```

## Install

```bash
npx skills add nickautomations/skills --skill human-content
```

Or in Claude Code: `/plugin install content-skills@nick-automations-skills`. No dependencies, no API keys.
