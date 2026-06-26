# Voice Forge

A skill that clones any LinkedIn creator's writing voice into a reusable skill.

Invoke `voice-forge` once, point it at a profile, and it scrapes their last 100 posts, distills the writing mechanics, and installs a new `<name>-voice` skill that drafts future posts in that voice.

## 🎯 What it does

`voice-forge` is a **meta-skill** — its output is *another* skill. You run it once per creator; from then on you invoke the produced skill (e.g. `/marios-voice`) whenever you want a draft in that voice.

The user never pastes a prompt, opens a spreadsheet, or runs a script by hand. Conversation in, skill out.

## 🧩 How it works

```
voice-forge  →  scrape  →  select+dedup  →  features.json  →  analyze  →  skill-creator
   │                                                                            │
   └─ scripts own every measurable step ────────────────────┐  LLM owns ──────┘
                                                              the one semantic step
```

The pipeline deliberately splits work between **deterministic scripts** (fetch, dedup, all counting/ranking/percentiles) and **one LLM step** (reading the pre-computed digest and naming the rhetorical patterns). The LLM never counts, sums, or ranks — it only reasons about *why*.

## 📦 Source actor

Posts come from [`capable_cauldron/linkedin-profile-posts-scraper`](https://apify.com/capable_cauldron/linkedin-profile-posts-scraper) on Apify.

- No cookies, no login — public profiles only.
- 55 pre-enriched fields per post; `voice-forge` uses just 13.
- 100 posts ≈ $0.31 per run.

## 🔑 Setup

Node.js 18+ is required (the scripts use the built-in `fetch`; no `npm install`).

The Apify token lives in your environment — it is **never** collected through a form or pasted in chat.

1. Create a token at https://console.apify.com/account/integrations
2. Set it as an environment variable:
   ```bash
   export APIFY_API_TOKEN=your_token_here
   ```
3. Restart your Claude client so it picks up the variable.

## ▶️ Usage

Invoke the skill and answer its questions:

```
/voice-forge
```

It will ask for:
- The target creator's LinkedIn URL or username
- A name for the new skill (defaults to `<username>-voice`)

Then it runs scrape → extract → analyze → build, and tells you the new skill is ready. Invoke it any time with `/<name>-voice`.

## 🗂️ Project structure

```
voice-forge/
├── SKILL.md                        # Orchestration: the brain
├── scripts/
│   ├── fetch_posts.js              # Apify HTTP API call (token from env var)
│   └── extract_features.js         # Select 13 fields + dedup + compute → features.json
├── references/
│   └── voice_analysis_prompt.md    # Refined voice-mechanics extraction prompt
└── README.md
```

When the skill runs, it also creates a `data/` folder for cached artifacts:

```
data/
├── raw_posts.json      # Raw scrape output (skipped on re-run)
├── features.json       # Deterministic feature digest (skipped on re-run)
└── voice_profile.md    # The synthesized voice (skipped on re-run)
```

## ♻️ Resume logic

Every step is idempotent. If an artifact already exists, the step is skipped. This means:

- Re-running after a failure picks up where it left off.
- Disliking the voice profile? Re-run the analysis step for free — no re-scrape, no re-paying Apify.

## 🛡️ Guardrails

- **Volume floor.** Below 80 posts, the skill warns that patterns won't surface reliably.
- **Dedup.** LinkedIn emits multiple activity URNs per share; the extractor always dedups on `share_urn` so engagement never double-counts.
- **Credential isolation.** The Apify token stays in the environment. It never appears in chat, logs, comments, or generated files.
- **Scope.** Built for the Claude skill ecosystem (Claude Code / Cowork). The generated `<name>-voice` skill installs into the same place.

## ⚠️ Honest limits

- You can't clone a voice from 12 posts. Need 80+ for patterns to surface.
- A weak voice stays weak — pick a creator whose writing is distinctive, not just popular.
- The agent copies style, not insight. It can match *how they sound*. It cannot match *how they think*. You bring the ideas.
- This is a practice tool. Borrow mechanics while you build your own voice, then take the training wheels off.
