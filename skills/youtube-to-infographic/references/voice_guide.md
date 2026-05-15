# Editorial Voice Guide

Nick Automations' voice is what makes these infographics *feel* different from the average AI content. The design system makes them look distinct; the voice makes them *read* distinct. Both matter equally.

## Core voice attributes

**Factual.** Every claim is verifiable. Use "ships in" not "revolutionizes." Use "documented at" not "trust me."

**Editorial.** This reads like a magazine field guide, not a startup deck. Periods over exclamation marks. Specifics over hype.

**Confident, not boastful.** "These are real" not "the BEST features you NEED to know!!!"

**Quietly opinionated.** Mild swipes at the genre are welcome ("not vibes", "no fictional commands", "real features, not magic"). Direct hostility is not.

## Headline patterns

### The slash separator (use in every piece)

The signature move: insert an orange slash inside a phrase to create rhythm and brand consistency. Pick natural pause points.

**Good examples:**
- "9 features / that actually exist"
- "Start fresh, / not fight drift"
- "A read-only / pass on your diff"
- "Summarize / without forgetting"
- "Vulnerabilities / before the PR"
- "Specialized Claudes / own context"
- "Master Claude. / 9 features that..."

**Avoid:**
- Slash at the very start or very end of a phrase
- Slash inside a compound noun
- More than one slash per headline (one is signature, two is gimmick)

### Hero headline structure

Always 2-3 lines. First line states subject, second line makes the editorial claim, optional third line clarifies.

**Pattern A** — Topic statement + claim:
> Master Claude.
> 9 features / that
> actually exist.

**Pattern B** — Action + outcome:
> Stop fighting drift.
> 8 patterns / that
> keep context clean.

**Pattern C** — Number + category + frame:
> The Claude Code
> security model / in
> 7 commands.

### Card titles

5-9 words. Should pair the *action* with the *outcome*. Slash optional but encouraged.

**Good:**
- "Start fresh, / not fight drift."
- "Vulnerabilities / before the PR."
- "Persistent project memory."
- "Specialized Claudes / own context."

**Avoid:**
- "How to use /clear" (too documentation-y)
- "/clear is amazing!" (too marketing)
- "Everything you need to know about /clear" (too SEO)

## Body copy patterns

### The 3-sentence card body

Structure:

1. **What it is** — one factual sentence
2. **Why it matters or how it works** — one practical sentence
3. **A specific detail that proves you know it** — one sentence with a real fact, command, version, or behavior

**Example (from the reference design, /clear):**
> Wipes the conversation and starts a new session.
> Anthropic's own guidance: use it between tasks — fresh context beats fighting drift.
> The up-arrow still navigates back through previous sessions if you need them.

That third sentence — "The up-arrow still navigates back" — is the credibility move. It shows you've actually used the thing.

### Command badge patterns (the mono-caps tag at the top of each card)

Cards don't have source tags. They have a single mono **command badge** at the top — a short identifier that names the thing the card is about. Think of it as a label, not a citation.

| Card subject | Badge example |
|---|---|
| A specific command | `/clear`, `/review`, `/agents` |
| A file or convention | `SKILL.md`, `CLAUDE.md`, `.env` |
| A step or count | `STEP 01`, `10h minimum`, `4 weeks` |
| A concept | `value-first DM`, `niche pick`, `cold open` |
| A tool | `webhook`, `RapidAPI`, `green screen` |

Pick the badge that makes the card scannable. The reader should see the badge and know what the card is about before reading the body.

Rule: 1-3 short tokens, no spaces inside if avoidable, mono caps (the badge is rendered in JetBrains Mono via CSS — write it in lowercase or natural case in the HTML).

## Tone calibration by content type

### Technical content (Claude, AI, dev tools)

Dry, precise, slightly understated. Trust that the reader is smart. Use specific commands, real version numbers, and exact file paths.

**Yes**: "Run `/init` in a fresh repo to generate a starter `CLAUDE.md`."
**No**: "Use the powerful `/init` command to instantly create amazing memory files!"

### Business / strategy content

Direct, opinionated, but not hyperbolic. Cite sources for numbers. Push back on conventional wisdom when the source does.

**Yes**: "Stripe's 2024 developer survey found 62% of engineers using AI assistants daily."
**No**: "AI is taking over and you NEED to adapt OR DIE."

### Creator / content / marketing content

Editorial, observation-based. Frame as "what's working" rather than "what you must do."

**Yes**: "The creators in our sample who posted 4× weekly saw 2.3× engagement vs. weekly posters — but only when the content stayed in one topic lane."
**No**: "POST DAILY OR LOSE TO THE ALGORITHM!"

## Headline templates by topic

For different source content, here are starting points:

**For "X tools / commands / features" content:**
- "[Topic]. / [N] features that [credibility hook]."
- "Master [topic]. / [N] [things] worth [verb]."

**For "How to / workflow" content:**
- "[Outcome] / in [N] moves."
- "The [topic] / playbook."

**For "Comparison" content:**
- "[X] / vs / [Y]."
- "Old [thing] / vs / what actually works."

**For "Common mistakes" content:**
- "[N] mistakes / [audience] still make."
- "What [topic] gets wrong / and how to fix it."

**For "Single deep dive" content:**
- "[Topic], / explained in [N] parts."
- "The complete [topic] / breakdown."

## Words and phrases to avoid

These are the linguistic tells of the AI-hype-infographic genre. Stay away from them:

- "leverage" (use "use")
- "unlock" (use "enable" or just describe it)
- "game-changing" (just don't)
- "revolutionary"
- "next-level" / "next-gen"
- "supercharge"
- "10X your workflow"
- "AI-powered" (almost always redundant)
- "in 2026" / "the future of" (dated immediately)
- "you NEED to know" / "what nobody tells you"
- "ChatGPT killer" / "Claude killer"
- "vibe code" (your brand explicitly rejects this)

## Words and phrases to embrace

- "ships in" / "ships with"
- "documented at"
- "built-in"
- "by default"
- "out of the box"
- "real" (when contrasting with hype)
- "actually" (sparingly, as in "features that actually exist")
- "field-tested"
- "verifiable"
- "specific" / "specifically"
- "see [source]"

## The category label (top-left of every piece)

Every infographic gets a contextual label in the top-left, in mono caps, orange. Format: `CATEGORY / [TOPIC]`. Pick the category that fits the actual content:

| Category | When to use | Example |
|---|---|---|
| `BREAKDOWN` | Explainers, "how X works", deep-dives | `BREAKDOWN / CLAUDE CODE SESSIONS` |
| `PLAYBOOK` | Numbered playbooks, "how to do X" | `PLAYBOOK / AI CONSULTING` |
| `TOOLKIT` | Tool/feature roundups | `TOOLKIT / VIDEO EDITING WITH AI` |
| `BRIEFING` | Trends, news, market analysis | `BRIEFING / SLOP ECONOMY` |
| `GUIDE` | Step-by-step processes, tutorials | `GUIDE / N8N AUTOMATIONS` |
| `COMPARED` | "X vs Y" or before/after pieces | `COMPARED / CURSOR VS CLAUDE CODE` |
| `TAKE` | Opinion pieces, hot takes, perspective | `TAKE / VIBE CODING` |

Vary the category across pieces — don't post three `BREAKDOWN` pieces in a row. The variety signals editorial range and keeps the feed visually rhythmic.

## Final test before publishing

Read the headline and the first card aloud. Ask:

1. Does it say something specific, or could it apply to any topic?
2. Is every claim something I can defend if someone pushes back?
3. Does the headline have one (and only one) orange slash that lands naturally?
4. Would someone who works in the field share this, or roll their eyes?

If you can't answer yes to all four, revise.
