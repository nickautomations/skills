---
name: voice-forge
description: Clone a LinkedIn creator's writing voice into a reusable <name>-voice skill — scrape their posts, extract the voice mechanics, install the generated skill. Use when the user wants to sound like a specific creator, or turn someone's LinkedIn writing into a drafting skill.
---

# Voice Forge: Clone a LinkedIn Voice Into a Reusable Skill

This skill is a **meta-skill**: its output is *another* skill. The user invokes `voice-forge` once per target creator; `voice-forge` then scrapes, distills, analyzes, and — at the final step — calls the built-in **skill-creator** to install a new `<name>-voice` skill. The user never pastes a prompt, never opens a spreadsheet, never runs a script by hand.

## Requirements

- **Node.js 18+** — the scripts use the built-in `fetch`, so there's no `npm install`. If `node --version` is below 18, tell the user before running anything; the scripts will otherwise fail mid-run with an unhelpful error.
- **`APIFY_API_TOKEN`** — in the environment, or in `scripts/.env` beside the fetch script. See Step 2. Never collected through chat or a form field.
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

- **Scripts (deterministic):** fetching posts, selecting the 14 needed fields, deduplicating on `share_urn`, computing engagement percentiles, format distribution, top-30 selection, stratified sampling, opening/closing-line extraction.
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

Run every command from the `voice-forge` skill directory. Artifacts land under `data/<username>/`, namespaced by creator so a second run never reads the first creator's cache.

Each script skips its own work when its output already exists, and redoes it when passed `--force`. That makes the pipeline idempotent: a re-run after a failure resumes where it stopped, and nothing re-charges Apify unless you explicitly force it.

### Step 1 — Resolve the target
Parse the profile URL/username the user gave you. The actor's `usernames` field accepts a username (`satyanadella`), member ID, or full URL. Extract the username segment (`linkedin.com/in/<this>`). Confirm the skill name.

### Step 2 — Check the Apify token
The token comes from one of two places, checked in this order: the `APIFY_API_TOKEN` environment variable, then `scripts/.env` beside the fetch script. A shell variable always overrides the file. The script resolves `.env` relative to its own location, so it is found regardless of which directory you invoke from.

- If **either is set**: proceed silently.
- If **neither**: tell the user how to set one, then stop and wait. The token belongs in the environment or in `.env` — never in chat, never in a form field, never in a log, and never as a CLI argument, which would leak it into shell history. Example message: *"I need an Apify API token to scrape posts. Create one at https://console.apify.com/account/integrations, then either copy `scripts/.env.example` to `scripts/.env` and put the token there, or set `APIFY_API_TOKEN` in your environment and restart your Claude client. Tell me when it's in place."*

### Step 3 — Fetch the posts
Run the fetch script. It calls the Apify HTTP API directly (no MCP dependency) and writes the raw dataset.

```bash
node scripts/fetch_posts.js --username "<username>" --max 100 --out "data/<username>/raw_posts.json"
```

- The script exits early with a `SKIP:` notice when the output already exists. Add `--force` only when the user explicitly asks to re-scrape — a forced run re-charges Apify.
- It polls the run to completion. Expect 1–3 minutes for 100 posts.
- Done when the script prints `Wrote <n> posts` or `SKIP:`. A non-zero exit means stop and report, not proceed.

### Step 4 — Extract features
Run the feature extractor. It writes the deterministic digest the analysis step reads.

```bash
node scripts/extract_features.js --in "data/<username>/raw_posts.json" --out "data/<username>/features.json"
```

What it does, in one pass: drops reposts and text-less posts, dedups on `share_urn` (falling back to exact post text when the URN is missing), keeps the 14 fields listed under *Source Actor Contract*, and computes every stat. Same `--force` semantics as step 3.

This step replaces what would otherwise be a "cleaning" stage — the source actor already pre-enriches 55 fields, so we only *select + dedup*, never transform.

### Step 5 — Analyze the voice (the one LLM step)
This is the **only** place the LLM does heavy semantic work.

- Check the digest's `volume_check.meets_floor` first. If it is `false`, apply the volume floor guardrail below before analyzing.
- Read `data/<username>/features.json` yourself (~8–12k tokens — cheap, grounded, pre-computed).
- Apply the prompt in `references/voice_analysis_prompt.md` to it.
- Save the output — a single block titled **VOICE PROFILE**, under 600 words — to `data/<username>/voice_profile.md`.
- Skip this step when that file already exists, unless the user wants to re-analyze. Re-analysis is free: it reads the cached digest, so there is no re-scrape and no re-extract.

### Step 6 — Build the skill via `skill-creator`
Don't hand-write the new skill. Invoke the built-in **skill-creator** skill and hand it the materials below. Since you already have a finished VOICE PROFILE, ask skill-creator to generate and install the skill directly — you don't need its full draft→eval→iterate loop for this one-shot assembly.

Hand `skill-creator`:
- The VOICE PROFILE from `data/<username>/voice_profile.md`.
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

Let `skill-creator` produce and install the skill. **Done when** the generated `SKILL.md` exists on disk — read it back and confirm the VOICE PROFILE is embedded verbatim. Then tell the user the skill name, its install path, and the invocation (`/<name>-voice`).

Step 6 has no skip check — it always runs, regenerating from the cached voice profile. So if the user dislikes the voice, they edit `data/<username>/voice_profile.md` (or re-run step 5) and step 6 rebuilds the skill with no re-scrape and no further Apify charge.

## Source Actor Contract (do not drift)

The scraper is **`capable_cauldron/linkedin-profile-posts-scraper`**. Hard facts, from its public Apify page:

- **Input sent by `fetch_posts.js`:** `{ "usernames": ["<username>"], "maxPostsPerProfile": <max>, "maxDatasetItems": <max> }` — the dataset cap is pinned to the post limit so a run can't overrun its cost.
- **Pricing:** $0.003/post + $0.01/profile → 100 posts ≈ $0.31.
- **No cookies required** — public-profile scraping only.
- **55 pre-enriched fields** per post. We use only 14 (`SELECT_FIELDS` in `scripts/extract_features.js` is the source of truth). Read the fields the actor already provides — engagement totals, word counts, ISO dates, format flags — rather than recomputing them.

The 14 fields used: `text`, `posted_date_iso`, `content_category`, `media_type`, `total_engagement`, `reaction_like`, `reaction_love`, `reaction_celebrate`, `reaction_insight`, `num_comments`, `word_count`, `is_repost`, `share_urn`, `post_url`.

## Guardrails

- **Volume floor.** `features.json` reports `volume_check.meets_floor`, true at 80+ usable posts. When it is `false`, tell the user the count, say plainly that voice patterns won't surface reliably at that size, and ask whether to proceed. The output is only as distinctive as the sample behind it — a weak sample gets an explicit warning, never a silent build.
- **Dedup is mandatory.** LinkedIn emits multiple activity URNs per share (edits, re-feeds). Dedup stays inside `extract_features.js`, keyed on `share_urn` — without it engagement double-counts and the top-30 list repeats posts.
- **No credential leakage.** The token stays in the environment. It never appears in chat, in logs, in a comment, or in a generated file.
- **Tool scope.** This skill is built for the Claude skill ecosystem (Claude Code / Cowork). The generated `<name>-voice` skill installs into the same place. Don't claim it works somewhere it doesn't.
- **Honesty.** If a step fails (actor down, profile too small, token invalid), say so plainly. Don't fabricate a voice profile from thin air.
