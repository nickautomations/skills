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

## Evals

`evals/` holds one case per mode (humanize, detect, write without inventing, voice sample, plan). Each case pairs a realistic prompt with graders: a check that the skill fired, plus judged criteria such as "every fact preserved" and "no testimonial invented".

```bash
claude plugin eval skills/human-content --model claude-sonnet-5 --judge-model claude-haiku-4-5
```

This runs each case 3 times with the skill and 3 times without, and reports the difference. Always pin `--model`: the default follows your Claude Code settings, and scores differ a lot by model (Opus reads the reference files; Sonnet often answers from `SKILL.md` alone). CI uses the command above.

Baseline, 2026-09-13:

| Case | Sonnet 5 with | Sonnet 5 without | Opus 5 with | Opus 5 without |
|---|---|---|---|---|
| detect-ai-patterns | 0.78 | 0.67 | 1.00 | 0.56 |
| humanize-linkedin-post | 0.71 | 0.48 | 1.00 | 0.67 |
| landing-hero-no-invention | 0.92 | 0.25 | 1.00 | 0.75 |
| plan-content-quarter | 1.00 | 1.00 | 0.89 | 1.00 |
| voice-sample-wins | 0.89 | 0.78 | 1.00 | 1.00 |

The Opus column predates the plan-mode fix (assume and deliver instead of stopping to ask), which took Sonnet's plan score from 0.50 to 1.00. A case moving by about 0.1 is one run out of three flipping on a judge vote; treat a drop of 0.2 or more as real. `detect-ai-patterns` is the noisiest case.

## Staying current

A weekly GitHub Action (`.github/workflows/upstream-human-content.yml`) checks every source below for changes. When one moves, Claude folds the useful parts into this skill, the eval suite scores the current skill against the draft, and a PR opens with that table. Tracked sources and baselines live in `upstream/human-content.json`.

## Credits

Synthesized in our own words from [blader/humanizer](https://github.com/blader/humanizer), Corey Haines' [marketingskills](https://github.com/coreyhaines31/marketingskills) (copywriting, marketing-psychology, content-strategy), Peter Yang's [no-ai-slop](https://github.com/petergyang/no-ai-slop), [The Human Claude Content Guide](https://theaibuilders.co/blog/the-human-claude-content-guide), and structured with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills).
