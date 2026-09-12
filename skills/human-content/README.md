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

## Staying current

A weekly GitHub Action (`.github/workflows/upstream-human-content.yml`) checks every source below for changes. When one moves, Claude folds the useful parts into this skill and opens a PR for review. Tracked sources and baselines live in `upstream/human-content.json`.

## Credits

Synthesized in our own words from [blader/humanizer](https://github.com/blader/humanizer), Corey Haines' [marketingskills](https://github.com/coreyhaines31/marketingskills) (copywriting, marketing-psychology, content-strategy), Peter Yang's [no-ai-slop](https://github.com/petergyang/no-ai-slop), [The Human Claude Content Guide](https://theaibuilders.co/blog/the-human-claude-content-guide), and structured with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills).
