# Voice Analysis Prompt

> **This is an internal asset of the `voice-forge` skill. The user never sees it.**
> The orchestrator reads `data/<username>/features.json`, then applies this prompt to
> produce a single VOICE PROFILE block saved to `data/<username>/voice_profile.md`.

---

You are analyzing the writing voice of one LinkedIn creator. You have been given a **feature digest** (`features.json`) that was computed deterministically over all of their scraped posts. It contains:

- **Exact aggregate stats** (engagement percentiles, median word count, format mix, reaction mix, cadence) computed over the FULL dataset.
- **`top_30_posts`** — the 30 highest-engagement posts, each with full text, the first two lines (hook) and last two lines (close) split out, plus engagement numbers and format.
- **`stratified_sample_20`** — 20 posts spanning the full engagement range (bottom, middle, and top), so you see the creator's *everyday* writing, not just their winners.

## Your job

Produce a single, reusable block titled **VOICE PROFILE** (under 600 words) that describes **how this person writes** — precisely enough that another agent, given only this profile, could draft a new post in the same voice on an unrelated topic.

This is a voice-mechanics extraction. It is **not** a content report, not a coaching deliverable, not a strategy memo. Ignore topic-level analysis. You care only about *mechanics*: rhythm, structure, register, tone, the shape of the writing.

## Rules (read carefully)

1. **Do NOT recompute any number.** Every stat in the digest is already exact. Quote the digest's pre-computed figures (median words, engagement percentiles, format counts) and reason about them — never recalculate. If a stat isn't in the digest, you don't need it.
2. **Quote real lines.** Every claim about opening patterns, line breaks, tone, or structure must be backed by a quoted line from `top_30_posts` or `stratified_sample_20`. No quoted example = no claim.
3. **Describe mechanics, not content.** "They open with a one-line provocation, then a line break, then the payoff" — yes. "They write about GTM workflows" — no. The voice must transfer to any topic.
4. **Name the opening patterns.** Most creators reuse 3–5 opening templates. Identify them, label them, and quote two examples of each.
5. **Be mechanical about rhythm.** How long are sentences? Where do they force line breaks (after a single word? after a question? after the hook)? Are paragraphs one sentence? Two? Quote evidence.
6. **Capture what they DON'T do.** Absences are as diagnostic as presences. No emojis? No hashtags? Never questions? Never first person? State it, citing the structural signals.

## Structure your VOICE PROFILE like this

Write exactly these sections, in order. Keep each tight.

**## VOICE PROFILE**

**Opening patterns** — The 3–5 opening templates they reuse, each labeled and with two quoted examples. This is the most important section; future drafts live or die on the hook.

**Sentence rhythm & line breaks** — Sentence length, where they break lines, their relationship to white space. Quote evidence. Mention the median word count from the digest.

**Vocabulary register** — Formal/casual, contractions, jargon vs plain English, their distinctive repeated words/phrases (give the ~10 most notable).

**Tone & emotional posture** — The dominant register (confident, vulnerable, contrarian, encouraging, provocative). How they *shift* tone mid-post for effect. Tie to the reaction mix from the digest if relevant (e.g. high `love` suggests warmth lands).

**Recurring skeleton** — The structural template they use most (hook → story → lesson → takeaway? list → confession → close?). Map it as a formula.

**Closings** — How they end: CTA, question, one-liner, callback. Quote examples.

**What they avoid** — The patterns absent from this voice. Use the structural signals (emoji/question/hashtag rates) as evidence.

**One-line summary** — A single sentence capturing this voice so distinctively that if two agents read only that line they'd produce similar drafts.

## Final constraints

- Under 600 words total.
- Every claim grounded in a quoted line or a digest stat.
- No invented numbers. No re-summing.
- No coaching advice. No "what they should do." Pure description of *what is*.

Begin. Output only the VOICE PROFILE block.
