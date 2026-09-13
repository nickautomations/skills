# Nick Automations Skills

[![Validate](https://img.shields.io/github/actions/workflow/status/nickautomations/skills/validate.yml?branch=main&label=validate)](https://github.com/nickautomations/skills/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/nickautomations/skills)](./LICENSE)
[![Skills](https://img.shields.io/badge/skills-4-blue)](#the-skills)
[![Claude Code plugin](https://img.shields.io/badge/Claude_Code-plugin-D97757)](#install-in-30-seconds)
[![Agent Skills standard](https://img.shields.io/badge/Agent_Skills-standard-555)](https://agentskills.io)

Agent skills from an automation studio, for the work around the work: copy that sounds like a person wrote it, prospect searches from a plain-English description, and LinkedIn posts in a voice you choose.

Each skill is a folder of instructions and scripts your agent loads when the task fits. They follow the [Agent Skills standard](https://agentskills.io), so they run in Claude Code, Cursor, Codex, Gemini CLI and other compatible agents. Fork them, change them, ship them.

## Install in 30 seconds

Pick one path. **The Claude Code plugin** installs a managed, read-only bundle that you update with one command. **The `skills` CLI** copies editable files into your agent, so you can change them. Installing both loads every skill twice.

<details>
<summary><strong>Claude Code</strong></summary>

```
/plugin marketplace add nickautomations/skills
/plugin install content-skills@nick-automations-skills
/plugin install sales-skills@nick-automations-skills
```

Install only the bundle you want. Pull updates later with:

```
/plugin marketplace update nick-automations-skills
```

</details>

<details>
<summary><strong>Cursor, Codex, Gemini CLI and other agents</strong></summary>

```bash
npx skills add nickautomations/skills
```

The installer asks which skills to take and which agents to install them for. For a single skill:

```bash
npx skills add nickautomations/skills --skill human-content
```

</details>

<details>
<summary><strong>For tinkerers</strong></summary>

```bash
git clone https://github.com/nickautomations/skills
cp -r skills/skills/human-content ~/.claude/skills/
```

Restart your agent. Nothing updates behind your back; pull when you want changes.

</details>

## The skills

### Content

Bundled as the `content-skills` plugin.

| Skill | What it does | Needs |
|---|---|---|
| **[human-content](./skills/human-content)** | Write, edit, and plan copy that reads like a person wrote it. Audits a draft for AI patterns without rewriting it, and never invents a fact, number or testimonial. | Nothing |
| **[voice-forge](./skills/voice-forge)** | Clone a LinkedIn creator's writing voice into a reusable `<name>-voice` skill: scrape their posts, measure how they write, install a drafting skill. | Claude Code, Node.js 18+, an Apify token |
| **[youtube-to-infographic](./skills/youtube-to-infographic)** | Turn a YouTube video, article or pasted text into an editorial infographic in the Nick Automations design system. | Python, a RapidAPI key for transcripts |

### Sales

Bundled as the `sales-skills` plugin.

| Skill | What it does | Needs |
|---|---|---|
| **[sales-navigator-search-builder](./skills/sales-navigator-search-builder)** | Describe who you want to find and get a LinkedIn Sales Navigator search URL: industries mapped to LinkedIn IDs, job titles normalized into a validated boolean string, noise excluded. | Python 3.9+, Sales Navigator to open the URL. City-level targeting needs your own LinkedIn app. |

All four trigger on their own when a request matches. You can also call one by name, like `/human-content`.

## How we keep them honest

- **Evals.** `human-content` ships with an eval suite for `claude plugin eval`: five realistic requests, graded with and without the skill. On Sonnet 5 the skill adds +0.23 on average and +0.67 on landing page copy. Scores and method are in [its README](./skills/human-content#evals).
- **Weekly upstream sync.** `human-content` draws on several open-source writing skills. Every Monday a workflow checks them for changes, Claude drafts an update, the evals score the current skill against the draft, and a PR opens with the table. Nothing merges without review.
- **CI on every PR.** Each `SKILL.md` is validated, and every skill must be listed in the plugin marketplace, so nothing ships uninstallable.

## Repo layout

```
nickautomations/skills/
├── .claude-plugin/marketplace.json   # plugin bundles for Claude Code
├── skills/                           # one folder per skill
├── upstream/                         # sources human-content tracks, with baselines
├── scripts/                          # validation, upstream check, eval comparison
├── template/                         # starter scaffold for a new skill
└── .github/workflows/                # CI and the weekly upstream sync
```

Want to add a skill? See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

Apache 2.0, see [LICENSE](./LICENSE). `sales-navigator-search-builder` includes MIT-licensed code; its notice is in [its folder](./skills/sales-navigator-search-builder/LICENSE).

---

Built by [Nick Automations](https://www.nickautomations.com), an AI automation studio. If you want one of these wired into your own stack, [book a free call](https://cal.com/nickchoudhary).
