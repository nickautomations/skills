---
name: voice-forge
description: 'Build a reusable voice-cloning skill from any LinkedIn creator''s posts. Scrape their last 100 posts via the Apify LinkedIn Profile Posts scraper (capable_cauldron/linkedin-profile-posts-scraper), distill the posts into a deterministic feature digest, analyze the writing voice with the LLM, then hand the result to the built-in skill-creator to install a new voice skill that drafts future posts in that voice. Use when the user wants to clone a person''s voice, build a voice skill from their LinkedIn, sound like a specific creator, or otherwise capture someone''s writing style and turn it into a reusable skill.'
---

# Voice Forge: Clone a LinkedIn Voice Into a Reusable Skill

This skill is a **meta-skill**: its output is *another* skill. The user invokes `voice-forge` once per target creator; `voice-forge` then scrapes, distills, analyzes, and — at the final step — calls the built-in **skill-creator** to install a new `<name>-voice` skill. The user never pastes a prompt, never opens a spreadsheet, never runs a script by hand.

## Requirements

- **Node.js 18+** — the scripts use the built-in `fetch`, so there's no `npm install`. If `node --version` is below 18, tell the user before running anything; the scripts will otherwise fail mid-run with an unhelpful error.
- **`APIFY_API_TOKEN`** in the environment — see Step 2. Never collected through chat or a form field.
- **The built-in `skill-creator` skill** — Step 6 delegates to it.

## Architecture (two layers)

```
voice-forge                       (this skill — runs once per creator)
   │
   │  scrape → select+dedup → features.json → analyze → skill-creator
   ▼
<name>-voice                      (the skill this produces — runs every post)
   │
   │  asks 2-3 questions → drafts in the cloned voice
   ▼
finished post draft
```

- **Layer 1 (this skill)** owns everything deterministic plus the one semantic step (voice analysis).
- **Layer 2 (the generated skill)** is produced by the built-in `skill-creator` at step 6. Don't hand-write the second skill — delegate it.

## The script / LLM split

The whole design rests on a clean division of labor, and it's worth keeping intact because it's what makes the output trustworthy: scripts own everything *measurable*, so the LLM is never asked to do arithmetic it tends to get subtly wrong. The LLM owns only the semantic voice analysis and the final skill assembly.

- **Scripts (deterministic):** fetching posts, selecting the 13 needed fields, deduplicating on `share_urn`, computing engagement percentiles, format distribution, top-30 selection, stratified sampling, opening/closing-line extraction.
- **LLM (semantic only):** reading the feature digest plus the top-30 quoted posts to name rhetorical patterns and synthesize the VOICE PROFILE, then invoking `skill-creator`.

If you ever find yourself about to ask the LLM to count, sum, average, or rank, stop — that belongs in a script. The LLM reads pre-computed numbers and reasons about *why* they look the way they do.

## Outcome Contract

- **Outcome:** a new installed `<name>-voice` skill that drafts LinkedIn posts in the target creator's register, plus a cached `features.json` the user can re-analyze for free.
- **Done when:** the generated skill exists, the user can invoke it with a `/` command, and it returns a draft in the cloned voice.
- **Evidence:** the new skill file path, the `features.json` path, and a one-line sample draft.

## Inputs (collected conversationally — never via an input form)

1. **Target creator's LinkedIn URL or username** — ask: "Which LinkedIn creator do you want to sound like? Paste their profile URL."
2. **Skill name** — ask: "What should I call the new skill? (e.g. `marios-voice`, `hormozi-voice`)". Default to `<username>-voice` if they don't care.
3. **Post count** — default `maxPostsPerProfile: 100`. Only ask if the user wants more; 100 is the sweet spot and costs ~$0.31.

API credentials are **never** collected through a field. The Apify token must already live in the environment. See step 2.

## Step-by-Step Orchestration

Run these in order. Each step that produces a file should **skip if the file already exists** (resume logic — re-runs must be cheap and idempotent).

### Step 1 — Resolve the target
Parse the profile URL/username the user gave you. The actor's `usernames` field accepts a username (`satyanadella`), member ID, or full URL. Extract the username segment (`linkedin.com/in/<this>`). Confirm the skill name.

### Step 2 — Check the Apify token
Check for the `APIFY_API_TOKEN` environment variable.
- If **present**: proceed silently.
- If **absent**: tell the user exactly how to set it, then stop. Never ask them to paste the token into chat, never put it in a form field, never log it. Example message: *"I need an Apify API token to scrape posts. Create one at https://console.apify.com/account/integrations, then set it as an environment variable: `APIFY_API_TOKEN=your_token_here`. Restart your Claude client so it picks up the variable, then tell me to continue."* Then wait.

### Step 3 — Fetch the posts
Run the fetch script. It calls the Apify HTTP API directly (no MCP dependency) and writes the raw dataset to `data/raw_posts.json`.

```bash
node scripts/fetch_posts.js --username "<username>" --max 100 --out data/raw_posts.json
```

- **Skip if `data/raw_posts.json` exists** unless the user explicitly says "re-scrape".
- The script polls the run to completion. Expect 1–3 minutes for 100 posts.

### Step 4 — Extract features
Run the feature extractor. It selects the 13 needed fields, deduplicates on `share_urn`, computes all the deterministic stats, and writes `data/features.json`.

```bash
node scripts/extract_features.js --in data/raw_posts.json --out data/features.json
```

- **Skip if `data/features.json` exists.**
- This step replaces what would otherwise be a "cleaning" stage — the source actor already pre-enriches 55 fields, so we only *select + dedup*, never transform.

### Step 5 — Analyze the voice (the one LLM step)
Read `references/voice_analysis_prompt.md`, substitute nothing (it references `data/features.json`), and run it against the full contents of `data/features.json`. This is the **only** place the LLM does heavy semantic work.

- Read `data/features.json` yourself (it is ~8–12k tokens — cheap, grounded, pre-computed).
- Apply the prompt in `references/voice_analysis_prompt.md`.
- The output is a single block titled **VOICE PROFILE** (under 600 words). Save it to `data/voice_profile.md`.
- **Skip if `data/voice_profile.md` exists** unless the user wants to re-analyze (they can tweak the prompt and rerun this step for free — no re-scrape, no re-extract).

### Step 6 — Build the skill via `skill-creator`
Don't hand-write the new skill. Invoke the built-in **skill-creator** skill and hand it the materials below. Since you already have a finished VOICE PROFILE, ask skill-creator to generate and install the skill directly — you don't need its full draft→eval→iterate loop for this one-shot assembly.

Hand `skill-creator`:
- The VOICE PROFILE from `data/voice_profile.md`.
- The target skill name (`<name>-voice`).
- The behavioral contract the new skill must follow (below).

> Create a skill called `<name>-voice`. Its single purpose: draft LinkedIn posts in the writing voice described in the VOICE PROFILE below.
>
> The skill must, every time it is invoked:
> 1. Use the AskUserQuestion tool to ask 2–3 questions tailored to this voice — enough to get the topic, angle, and any required specifics before drafting. Never draft with zero input.
> 2. Produce 3 angle/hook options for the user to pick from, each matching the opening patterns in the VOICE PROFILE.
> 3. After the user picks one, write the full caption in the cloned voice (matching sentence rhythm, line breaks, tone, structure) and describe what the media/image should contain.
> 4. Never copy the source posts' wording — only their mechanics.
>
> The entire VOICE PROFILE block below is the style spec. Embed it verbatim in the generated skill.
>
> [PASTE THE FULL VOICE PROFILE HERE]

Let `skill-creator` produce and install the skill. Then confirm to the user: the new skill name, where it's installed, and how to invoke it (`/<name>-voice`).

## Resume Logic (idempotent runs)

At the start of every step, check for the output artifact:

| Step | Artifact | Skip if exists? |
|------|----------|-----------------|
| 3. Fetch | `data/raw_posts.json` | Yes |
| 4. Extract | `data/features.json` | Yes |
| 5. Analyze | `data/voice_profile.md` | Yes |
| 6. skill-creator | the installed `<name>-voice` skill | No — always runs, but it regenerates from cached `voice_profile.md` |

This means: if the user dislikes the first voice profile, they edit `data/voice_profile.md` (or you re-run step 5) and step 6 regenerates the skill without re-scraping or re-paying Apify.

## Source Actor Contract (do not drift)

The scraper is **`capable_cauldron/linkedin-profile-posts-scraper`**. Hard facts, from its public Apify page:

- **Input:** `{ "usernames": ["<username>"], "maxPostsPerProfile": 100, "maxDatasetItems": 10000 }`
- **Pricing:** $0.003/post + $0.01/profile → 100 posts ≈ $0.31.
- **No cookies required** — public-profile scraping only.
- **55 pre-enriched fields** per post. We use only 13 (see `scripts/extract_features.js`). Don't recompute fields the actor already provides (engagement totals, word counts, ISO dates, format flags).

The 13 fields used: `text`, `posted_date_iso`, `content_category`, `media_type`, `total_engagement`, `reaction_like`, `reaction_love`, `reaction_celebrate`, `reaction_insight`, `num_comments`, `word_count`, `is_repost`, `share_urn`, `post_url`.

## Guardrails

- **Volume floor.** If the scrape returns fewer than 80 posts, warn the user that voice patterns won't surface reliably and ask whether to proceed. Don't silently build a weak skill — the output is only as distinctive as the sample behind it.
- **Dedup is mandatory.** LinkedIn emits multiple activity URNs per share (edits, re-feeds). Always dedup on `share_urn` inside `extract_features.js` — otherwise engagement double-counts and the top-30 list repeats posts.
- **No credential leakage.** The token stays in the environment. It never appears in chat, in logs, in a comment, or in a generated file.
- **Tool scope.** This skill is built for the Claude skill ecosystem (Claude Code / Cowork). The generated `<name>-voice` skill installs into the same place. Don't claim it works somewhere it doesn't.
- **Honesty.** If a step fails (actor down, profile too small, token invalid), say so plainly. Don't fabricate a voice profile from thin air.
