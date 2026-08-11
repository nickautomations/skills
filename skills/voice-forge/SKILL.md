---
name: voice-forge
description: Clone a LinkedIn creator's writing voice into a reusable <name>-voice drafting skill. Use when the user names a creator they want to write like, or points at a LinkedIn profile and asks for a skill built from it.
---

# Voice Forge: Clone a LinkedIn Voice Into a Reusable Skill

This skill is a **meta-skill**: its output is *another* skill. The user invokes `voice-forge` once per target creator; `voice-forge` then scrapes, distills, analyzes, and — at the final step — writes and installs a new `<name>-voice` skill. `voice-forge` runs every command and writes every file itself; the user answers questions and nothing else.

## Requirements

- **Node.js 18+** — the scripts use the built-in `fetch`, so there's no `npm install`. If `node --version` is below 18, tell the user before running anything; the scripts will otherwise fail mid-run with an unhelpful error.
- **`APIFY_API_TOKEN`** — in the environment, or in `scripts/.env` beside the fetch script. See Step 2.

**No other skill is required.** Step 6 writes the generated skill itself and carries everything it needs inline. Two skills make it better if they happen to be installed, and neither is worth installing solely for this:

- **`writing-for-agents`** (`mattpocock-skills` plugin) — the reference Step 6's structure was derived from. Reading it adds the reasoning behind the structure; skipping it costs nothing, because the structure is spelled out.
- **`skill-creator`** (official plugin marketplace) — a full draft→eval→iterate loop. Useful when you want to *measure* the generated skill, not to assemble it. Despite reading like a built-in it is a plugin, and a `~/.claude/skills/skill-creator/` folder with no `SKILL.md` inside means it is not installed.

## Architecture (two layers)

```
voice-forge                       (this skill — runs once per creator)
   │
   │  scrape → select+dedup → features.json → analyze → write skill
   ▼
<name>-voice                      (the skill this produces — runs every post)
   │
   │  asks 2-3 questions → drafts in the cloned voice
   ▼
finished post draft
```

- **Layer 1 (this skill)** owns everything deterministic plus the one semantic step (voice analysis).
- **Layer 2 (the generated skill)** is written at step 6, to the structure specified there.

## The script / LLM split

The whole design rests on a clean division of labor, and it's worth keeping intact because it's what makes the output trustworthy: scripts own everything *measurable*, so the LLM is never asked to do arithmetic it tends to get subtly wrong. The LLM owns only the semantic voice analysis and the final skill assembly.

- **Scripts (deterministic):** fetching posts, selecting the 14 needed fields, deduplicating on `share_urn`, computing engagement percentiles, format distribution, top-30 selection, stratified sampling, opening/closing-line extraction.
- **LLM (semantic only):** reading the feature digest plus the top-30 quoted posts to name rhetorical patterns and synthesize the VOICE PROFILE, then writing the generated skill around it.

If you ever find yourself about to ask the LLM to count, sum, average, or rank, stop — that belongs in a script. The LLM reads pre-computed numbers and reasons about *why* they look the way they do.

## Outcome Contract

- **Outcome:** a new installed `<name>-voice` skill that drafts LinkedIn posts in the target creator's register, plus a cached `features.json` the user can re-analyze for free.
- **Done when:** the generated skill exists, the user can invoke it with a `/` command, and it returns a draft in the cloned voice.
- **Evidence:** the new skill file path, the `features.json` path, and a one-line sample draft.

## Inputs (collected conversationally — never via an input form)

1. **Target creator's LinkedIn URL or username** — ask: "Which LinkedIn creator do you want to sound like? Paste their profile URL."
2. **Skill name** — ask: "What should I call the new skill? (e.g. `marios-voice`, `hormozi-voice`)". Default to `<username>-voice` if they don't care.
3. **Post count** — default `maxPostsPerProfile: 120`, costing ~$0.37. Only ask if the user wants more. The default is set above the 80-post volume floor on purpose: roughly a quarter of any scrape is written by other people and gets dropped, so 120 raw lands near 92 usable. Scraping exactly 100 clears the floor only if nothing is dropped, which does not happen. See *Source Actor Contract*.

## Step-by-Step Orchestration

Run every command from the `voice-forge` skill directory. Artifacts land under `data/<username>/`, namespaced by creator so a second run never reads the first creator's cache.

Each script skips its own work when its output already exists, and redoes it when passed `--force`. That makes the pipeline idempotent: a re-run after a failure resumes where it stopped, and nothing re-charges Apify unless you explicitly force it.

### Step 1 — Resolve the target
Parse the profile URL/username the user gave you. The actor's `usernames` field accepts a username (`satyanadella`), member ID, or full URL. Extract the username segment (`linkedin.com/in/<this>`).

**Done when** you can state the bare username and the target skill name, both confirmed with the user.

### Step 2 — Check the Apify token
The token comes from one of two places, checked in this order: the `APIFY_API_TOKEN` environment variable, then `scripts/.env` beside the fetch script. A shell variable always overrides the file. The script resolves `.env` relative to its own location, so it is found regardless of which directory you invoke from.

- If **either is set**: proceed silently.
- If **neither**: tell the user how to set one, then stop and wait. The token belongs in the environment or in `.env` — never in chat, never in a form field, never in a log, and never as a CLI argument, which would leak it into shell history. Example message: *"I need an Apify API token to scrape posts. Create one at https://console.apify.com/account/integrations, then either copy `scripts/.env.example` to `scripts/.env` and put the token there, or set `APIFY_API_TOKEN` in your environment and restart your Claude client. Tell me when it's in place."*

### Step 3 — Fetch the posts
Run the fetch script. It calls the Apify HTTP API directly (no MCP dependency) and writes the raw dataset.

```bash
node scripts/fetch_posts.js --username "<username>" --max 120 --out "data/<username>/raw_posts.json"
```

- The script exits early with a `SKIP:` notice when the output already exists. Add `--force` only when the user explicitly asks to re-scrape — a forced run re-charges Apify.
- It polls the run to completion. Expect 1–3 minutes for 120 posts.
- Done when the script prints `Wrote <n> posts` or `SKIP:`. A non-zero exit means stop and report, not proceed.
- **Exit 5 means the run succeeded but returned zero posts.** The actor swallows LinkedIn rate limits (429s) and still exits 0, so a "successful" empty run is normal enough to plan for. Nothing is written in that case — deliberately, so the resume check can't lock in an empty cache. Tell the user it was likely rate-limited and retry; if a retry also returns zero, check that the profile has public posts before blaming the actor.

### Step 4 — Extract features
Run the feature extractor. It writes the deterministic digest the analysis step reads.

```bash
node scripts/extract_features.js --in "data/<username>/raw_posts.json" --out "data/<username>/features.json"
```

What it does, in one pass: drops reposts, text-less posts and **posts written by someone other than the target creator**, dedups on `share_urn` (falling back to exact post text when the URN is missing), keeps the fields in `SELECT_FIELDS`, and computes every stat. Same `--force` semantics as step 3.

This step replaces what would otherwise be a "cleaning" stage — the source actor already pre-enriches 55 fields, so we only *select + dedup*, never transform.

**Done when** `features.json` exists and you have read two numbers out of it and reported both to the user: `volume_check.posts` and `authorship.dropped_foreign_author`. The second is the one to watch — when a large share of the scrape was written by other people, the creator's own post count can land under the volume floor even though the raw scrape looked big enough. See *Guardrails*.

### Step 5 — Analyze the voice (the one LLM step)
This is the **only** place the LLM does heavy semantic work.

- Check the digest's `volume_check.meets_floor` first. If it is `false`, apply the volume floor guardrail below before analyzing.
- Read `data/<username>/features.json` yourself (~8–12k tokens — cheap, grounded, pre-computed).
- Apply the prompt in `references/voice_analysis_prompt.md` to it.
- Save the output — a single block titled **VOICE PROFILE**, under 600 words — to `data/<username>/voice_profile.md`.
- Skip this step when that file already exists, unless the user wants to re-analyze. Re-analysis is free: it reads the cached digest, so there is no re-scrape and no re-extract.

**Done when** every section the prompt asks for is present, and every claim about the voice carries a quoted line from `top_30_posts` or `stratified_sample_20` behind it. A claim with no quote is the failure mode here — it is where an invented voice gets in. Step 6 is mechanical assembly and will wait; this is the step that decides whether the generated skill is any good, so finish it properly before moving on.

### Step 6 — Write the skill

Write `~/.claude/skills/<name>-voice/SKILL.md` yourself. Everything you need is below — this step has no dependency on any other skill.

If `writing-for-agents` is installed, read it and its `SKILL-MECHANICS.md` first: the structure below was derived from it, and the reasoning catches what a template can't. If it isn't installed, carry on — the structure is stated in full.

`skill-creator` is for *measuring* a skill rather than assembling one: it drafts, evals and iterates from a blank page. You are starting from a finished VOICE PROFILE and the contract below, so its loop has nothing to add here.

#### The generated skill is user-invoked

Set `disable-model-invocation: true` and write a **human-facing** one-line `description`.

This is the decision that scales. A model-invoked skill's description is a context pointer pinned in context every turn, forever, whether or not it fires. A voice skill only ever fires when its owner types it — nobody asks an agent to autonomously decide to sound like a particular person. Clone five creators with descriptions and you have five permanent always-loaded pointers competing for attention, all to save typing a name. Pay the cognitive load instead: the user remembers the skill exists, which they do anyway, because they chose the creator.

#### Structure

Two leading words carry the generated skill; name them explicitly and reuse them as tokens throughout.

- **Mode** — the 3–6 recurring post types in the VOICE PROFILE (a launch, a metric, a tribute, a thesis…). One table maps each mode to its opening pattern and a word band. Modes are the branches, and the table is their single source of truth — state each band once, there, and let the steps refer to it.
- **Spine** — the creator's recurring skeleton, written as beats: `name the thing → what it does → widen → exit`. Every mode writes to the same spine.

Then the steps, each closing on a checkable completion criterion:

1. **Fix the mode** — AskUserQuestion, 2–3 questions: which mode, the concrete noun or number the post is built on, and how it exits. *Done when* you can name the mode and the concrete detail. Ask again rather than inventing the detail.
2. **Offer three hooks** — each from a *different* opening pattern. *Done when* three exist, each from a different pattern, none over two lines.
3. **Draft** — on the spine, inside the mode's band. *Done when* all beats appear in order and the draft sits in the band.
4. **Describe the media** — weight the suggestion by the digest's `format_distribution`. *Done when* the media line names what is on screen.

Then the drafting rules, then the full VOICE PROFILE embedded verbatim under its own heading.

#### Write the rules positively

State the target behaviour rather than the ban. A prohibition drags the banned thing into context and makes it *more* available — "no emojis" puts emojis in the model's head.

The move is to make the allowed set exhaustive, which closes the door without naming what's outside it: *"Warmth is punctuation and one word: a single exclamation mark, and `super` at most once, are the entire inventory."* That bans emojis without the word "emoji" appearing.

The VOICE PROFILE's own **What they avoid** section is the exception and stays as written — it is reference *describing* the voice for the agent to reason about, not an instruction steering it.

**Done when** the file exists at `~/.claude/skills/<name>-voice/SKILL.md`, its frontmatter `name` matches the folder exactly, `disable-model-invocation: true` is set, and the VOICE PROFILE is embedded verbatim — read it back and confirm. Then tell the user the skill name, its path, and that they invoke it with `/<name>-voice`.

Step 6 has no skip check — it always runs, regenerating from the cached voice profile. So if the user dislikes the voice, they edit `data/<username>/voice_profile.md` (or re-run step 5) and step 6 rebuilds the skill with no re-scrape and no further Apify charge.

## Source Actor Contract (do not drift)

The scraper is **`capable_cauldron/linkedin-profile-posts-scraper`**. Hard facts, from its public Apify page:

- **Input sent by `fetch_posts.js`:** `{ "usernames": ["<username>"], "maxPostsPerProfile": <max>, "maxDatasetItems": <max> }` — the dataset cap is pinned to the post limit so a run can't overrun its cost.
- **Pricing:** $0.003/post + $0.01/profile → the default 120-post scrape ≈ $0.37.
- **No cookies required** — public-profile scraping only.
- **55 pre-enriched fields** per post, of which the digest keeps a small subset. `SELECT_FIELDS` in `scripts/extract_features.js` is the source of truth — read it there rather than from a list here, which would go stale the first time the subset changes. Use the fields the actor already provides (engagement totals, word counts, ISO dates, format flags) instead of recomputing them.
- **The scrape is not single-author.** The actor returns everything on the profile's activity feed, which includes posts *written by other people*. They arrive with `is_repost: false`, so the repost filter never catches them. A 150-post `satyanadella` scrape contained 34 posts (23%) by fourteen other people — colleagues and fellow executives. `extract_features.js` drops them by comparing `author_username` against `profile_username`, both of which the actor supplies per post. Budget for the loss: scrape roughly 1.4× the number of posts you actually need.

## Guardrails

- **Volume floor.** `features.json` reports `volume_check.meets_floor`, true at 80+ usable posts. When it is `false`, tell the user the count, say plainly that voice patterns won't surface reliably at that size, and ask whether to proceed. The output is only as distinctive as the sample behind it — a weak sample gets an explicit warning, never a silent build.
- **Dedup is mandatory.** LinkedIn emits multiple activity URNs per share (edits, re-feeds). Dedup stays inside `extract_features.js`, keyed on `share_urn` — without it engagement double-counts and the top-30 list repeats posts.
- **One author, or it isn't a voice.** Every post in the digest must be written by the target creator — the mechanism is in *Source Actor Contract*. What it costs when it slips, measured on the `satyanadella` run: median words moved 38.5 → 50.5, and the emoji rate 0.01 → 0.14 per post with hashtags 0 → 0.1, because the colleagues use emojis and hashtags and he does not. The generated skill would have been taught habits the creator demonstrably does not have. When the filter leaves you under the volume floor, the fix is a larger scrape.
- **No credential leakage.** The token stays in the environment. It never appears in chat, in logs, in a comment, or in a generated file.
- **Tool scope.** This skill is built for the Claude skill ecosystem (Claude Code / Cowork), and the generated `<name>-voice` skill installs into the same place. Describe its reach as exactly that.
- **Honesty.** When a step fails — actor down, profile too small, token invalid — report the failure and stop there. Every VOICE PROFILE traces back to scraped posts; where there are no posts, there is no profile to write.
