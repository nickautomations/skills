---
name: youtube-to-infographic
description: Generate a Nick Automations branded editorial infographic from a YouTube video URL, article URL, or pasted text. Use this skill whenever the user wants to turn long-form content into a visual infographic, including phrases like "make an infographic from this video", "turn this article into an infographic", "summarize this in a visual", "build a Nick Automations infographic", or any time the user pastes a URL or text and asks for a shareable graphic. Always produces output in the Nick Automations design system — heavy display typography (Satoshi/Geist), orange-slash separators, three-column editorial layout, monospace command labels, the Nick Automations logo in the header, and a soft CTA in the footer. Brand voice is factual and direct, with no invented facts, no fake company logos, and no source tags cluttering cards.
---

# Nick Automations Infographic Generator

Turn any YouTube video, article URL, or pasted text into a polished editorial-style infographic in the Nick Automations design system.

This skill does NOT produce generic infographics. It produces a specific editorial aesthetic — three-column grid, heavy display headlines with the orange slash as a typographic device, monospace command/tag labels, hand-coded SVG illustrations per item, and a clean soft CTA footer driving to nickautomations.com.

## When to trigger

Trigger on any of:
- "Make an infographic from this video: [URL]"
- "Turn this article into an infographic"
- "Create an infographic from this"
- "Build a Nick Automations infographic about..."
- A URL (YouTube or article) plus any visualization request
- A pasted transcript or article with a request to summarize visually

## Brand identity (memorize this)

**Nick Automations** is the brand. Domain: `nickautomations.com`. The logo is an "N / A" mark where the diagonal orange slash between the letters IS the signature element. The slash isn't decoration — it's the brand's visual DNA, and it shows up throughout the design as a separator in headlines (`features/that`, `read-only/pass`, `Summarize/without forgetting`).

**Voice**: editorial, confident, direct. No hype, no hustle-culture claims, no "vibe coding." Concrete language over filler words. The brand sells AI/automation consulting to businesses — so the tone is "we do this work, here's the breakdown" rather than "you NEED to know!!!"

## Brand colors (use these exact hex codes — no others)

```
Primary accent (orange):     #FF6B35
Heading / dark text:         #1A1A1A
Body text:                   #3F3F50
Background (cream):          #FAF7F2
Card background:             #FFFFFF
Subtle fill:                 #F5EFE8
Divider lines:               #E8E4DD
Muted label text:            #8A8578
```

Rule: 70% cream/white surfaces, 25% dark text, 5% orange. Orange is precious — use it on slashes, command names, key callouts, and the signature mark. Never on body text. Never gradients. Never additional accent colors.

## Typography (locked, no substitutions)

**Headline & body font cascade**: `'Satoshi', 'Geist', 'Cabinet Grotesk', system-ui, sans-serif`. Satoshi is primary (loaded from Fontshare), Geist is the Google Fonts fallback, Cabinet Grotesk is the secondary fallback, then system. Inter is **not** in the cascade — banned by the design-taste check.

Use weights `800-900` for the main headline, `700` for card titles. Tight letter-spacing (`-0.03em`) on the big headline. The fonts pair well with this tracking because they're geometric sans serifs with similar x-heights — fallbacks won't visibly jolt the layout.

**Monospace font** (for command names, file paths, badges, category labels): `'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace`. Every command like `/clear`, every file like `SKILL.md`, every category label like `BREAKDOWN / [topic]` gets the mono treatment. This signals "this is a real, technical thing."

Load Satoshi from Fontshare and Geist + Cabinet Grotesk + JetBrains Mono from Google Fonts:

```html
<link rel="preconnect" href="https://api.fontshare.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;700;800;900&family=Cabinet+Grotesk:wght@500;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

**Why this cascade**: Satoshi has the strongest editorial character (slightly humanist proportions, premium feel). Geist is Vercel's geometric sans and falls back cleanly if Fontshare is slow. Cabinet Grotesk is another high-end editorial sans as a third tier. System UI catches everything else without visible degradation.

## The slash treatment (the most important brand element)

In headlines, use the orange slash as a separator inside phrases. Examples from the reference design:

- "9 features `/` that actually exist"
- "A read-only `/` pass on your diff"
- "Summarize `/` without forgetting"
- "Vulnerabilities `/` before the PR"

Implementation: wrap the slash in a span and color it orange:

```html
<h1>9 features<span class="brand-slash">/</span>that actually exist</h1>
```

```css
.brand-slash {
  color: #FF6B35;
  font-weight: 900;
  margin: 0 0.05em;
}
```

Pick natural breakpoints in the headline where a slash adds rhythm. Not every headline needs one, but the main title and 2-4 card titles should use it. Don't overdo it.

## Workflow

### Step 1: Identify input and extract content

**YouTube URLs** (`youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...`):

Call the bundled Python script. It hits the RapidAPI yt-api service and returns a normalized JSON response on stdout.

```bash
python3 scripts/fetch_transcript.py "VIDEO_URL" > /tmp/transcript.json
```

The script reads `RAPIDAPI_KEY` from `scripts/.env`. If it isn't set, the script exits with code 1 and prints a clear error explaining how to get a key.

**Setting up RAPIDAPI_KEY (one-time, per environment):**

1. Sign up at https://rapidapi.com (free)
2. Subscribe to **yt-api by ytjar** at https://rapidapi.com/ytjar/api/yt-api — there's a free tier
3. Copy your API key from the RapidAPI dashboard
4. Copy `scripts/.env.example` to `scripts/.env`, then replace the placeholder:
   ```dotenv
   RAPIDAPI_KEY=your_key_here
   ```
   The `.env` file is ignored by Git, so the key stays local.

**Response shape** (on success):
```json
{
  "success": true,
  "videoId": "abc123",
  "title": "Video title (if available)",
  "channel": "Channel name (if available)",
  "segmentCount": 239,
  "fullText": "Full spoken transcript as one string...",
  "segments": [
    {"start": 0.08, "duration": 5.36, "text": "..."},
    ...
  ]
}
```

**Parsing the response:**

```bash
# Get the full transcript text
jq -r '.fullText' /tmp/transcript.json

# Get title (for the headline context, not for sources)
jq -r '.title' /tmp/transcript.json

# Get channel name (for headline context, not for sources)
jq -r '.channel' /tmp/transcript.json
```

If `jq` isn't available, parse with Python: `python3 -c "import json; print(json.load(open('/tmp/transcript.json'))['fullText'])"`

**Failure handling:**

- If the script returns `"success": false`, read the `error` field and act accordingly:
  - "RAPIDAPI_KEY is not set" → tell the user to copy `scripts/.env.example` to `scripts/.env` and replace the placeholder key (see above)
  - "Could not extract a YouTube video ID" → ask the user to verify the URL
  - "RapidAPI returned HTTP 429" → rate limited, suggest waiting or upgrading their RapidAPI plan
  - "RapidAPI returned HTTP 403" → invalid key or subscription required
  - "No transcript content" → the video likely has captions disabled; ask the user to paste content
- Never invent transcript content if the fetch fails.

**Article URLs**: Use `web_fetch`. Extract the main body, skip nav/footer/ads.

**Pasted text**: Use directly.

### Runtime requirements

This skill requires Python 3 and an internet connection that reaches `rapidapi.com`. It works anywhere those two are satisfied:

- **Claude Code** on a laptop/server — works (recommended)
- **claude.ai web/mobile** — works if the sandbox allows network access to `*.rapidapi.com` (may require allowlist update)
- **Self-hosted Claude** — works
- **Air-gapped environments** — won't work; ask the user to paste content directly

The skill has no other external dependencies — `fetch_transcript.py` uses only the Python standard library, so no `pip install` is needed.

### Step 2: Distill into infographic structure

Read the full content, then decide the layout variant based on what's actually in the source:

| Source pattern | Variant |
|----------------|---------|
| "X tips/features/skills/steps" | **modular list** |
| "X vs Y" or before/after | **comparison split** |
| Single concept deep-dive | **hero + evidence** |
| Process/tutorial | **timeline/process map** |
| Dense tactical advice | **checklist/playbook** |
| Short or thin source | **compact brief** |

For all variants, extract:

- **Top-left label**: a contextual category tag in mono caps. Pick the one that matches the content:
  - `BREAKDOWN / [topic]` — explainers, "how X works", deep-dives
  - `PLAYBOOK / [topic]` — numbered playbooks, "how to do X"
  - `TOOLKIT / [topic]` — tool/feature roundups, "X tools for Y"
  - `BRIEFING / [topic]` — trends, news, market analysis
  - `GUIDE / [topic]` — step-by-step processes, tutorials
  - `COMPARED / [topic]` — comparisons, "X vs Y"
  - `TAKE / [topic]` — opinion pieces, hot takes
  Don't use the same label twice in a row across pieces — pick what fits the actual content.
- **Main headline**: 4-10 words with at least one orange slash. Punchy. Editorial. Not clickbait.
- **Subtitle paragraph**: 2-3 sentences explaining the piece. State what the reader gets out of it.
- **Layout shape**: Pick a structure that fits the source. Do not default to the same three-column card grid every time. Valid shapes include:
  - 4-6 item compact brief with one large hero insight and supporting cards
  - 5-7 step vertical timeline or process map
  - 6 item two-column checklist/playbook
  - 6 or 9 item three-column editorial grid for list-heavy content
  - Comparison split with two sides plus a bottom takeaway band
- **Sections/cards**: Use only as many content units as the source can honestly support, usually 4-9. Each unit:
  - Item number (`01`, `02`...)
  - Item name in a monospace tag/badge (e.g., `/clear`, `SKILL.md`, `value-first DM`, `10h minimum`)
  - 2-5 word title with optional orange slash
  - 2-3 sentence body
  - A simple inline illustration (see illustration rules below)
  - **No source tags. No attribution badges. Clean card bottom.**

### Step 3: Illustrations

Do NOT use:
- AI-generated raster images (they produce wrong logos, garbled text, off-palette colors)
- Big stock-photo icons
- Emojis as the primary visual (small inline emojis are okay sparingly, not as main icon)
- Any third-party company logos as illustrations

DO use: **small, hand-built SVG illustrations** that visually represent the concept. Keep them flat, 2-color (orange + dark slate), and concept-driven. Examples to model:

- For "start fresh" or reset: a document with a slash through it and an arrow forward
- For "code review": a code snippet with `+`/`-`/`!` lines and a magnifying glass
- For "files / formats": three small folder/file rectangles
- For "security check": a shield outline with risk tags scattered around it
- For "subagents / network": a central node connected to surrounding nodes
- For "summary / compression": two stacked documents with an X between them
- For comparison content: split-screen rectangles
- For data/stats: simple bar shapes
- For workflows: numbered arrows or path lines

Each illustration sits in a ~280px × 140px box centered above the card title. Use only `#1A1A1A` for outlines/dark fills and `#FF6B35` for the one accent element. Stroke width 2-3px, rounded line caps. See `references/illustrations.md` for ready-to-use SVG snippets.

### Step 4: Assemble the HTML

Use `assets/templates/infographic.html` as the base. It includes:

- Striped diagonal header pattern (orange diagonal lines, ~6px wide)
- Contextual category label (`BREAKDOWN / [topic]`, `PLAYBOOK / [topic]`, etc.) top-left
- Nick Automations logo (top-right, embedded from `assets/logos/logo-white-bg.svg`)
- Flexible editorial layout chosen from the source structure
- Cards/sections with consistent spacing
- **Clean cards: number, badge, illustration, title, body. No source tags.**
- Soft CTA footer: `See how we automate / nickautomations.com`

The Nick Automations logo must appear at top-right of every infographic. Embed it directly as inline SVG (the file is in `assets/logos/logo-white-bg.svg`) — do not link externally. Pair it with the wordmark in mono caps: `Nick / AUTOMATIONS` where the slash is orange.

### Step 5: Save and present

1. Save to `/mnt/user-data/outputs/[topic-slug]-infographic.html`
2. Call `present_files` with the path
3. Brief the user:
   - Open in browser to view
   - Use browser DevTools → "Capture full size screenshot" for posting (Chrome: Cmd+Shift+P → "capture full size screenshot")
   - Optimal width is 1080px for social posting; the design is responsive
   - For LinkedIn carousel, screenshot each page separately

## Critical content rules

1. **No invented facts.** If a point isn't in the source content, don't include it. If the source is thin, make a shorter infographic — six honest cards beat nine padded ones.

2. **No source tags on cards.** Cards have: number, badge, illustration, title, body. Clean bottom. Do not add gray attribution tags, orange callout tags as "sources," or any "based on" lines per card. The Nick Automations brand owns the piece — viewers don't need a receipt on every card.

3. **No fake company logos.** Never use OpenAI, Anthropic, Google, or other company logos as illustrations. Use text labels or abstract SVG illustrations instead.

4. **Real, legible text only.** No placeholder text. No gibberish in illustrations. If you draw a diff illustration, the code in it should be real.

5. **Soft CTA footer is mandatory.** Every infographic ends with the standard footer:
   ```
   See how we automate / nickautomations.com
   ```
   Set in mono caps, small, with the orange slash. No `Sources:` line, no `VOLUME XX` line, no other footer text. The CTA is the only thing at the bottom.

6. **Nick Automations logo + wordmark** in top-right of page 1, always. Embed the SVG inline. Don't substitute with emojis.

7. **Contextual category label** in top-left of every piece. Pick from `BREAKDOWN`, `PLAYBOOK`, `TOOLKIT`, `BRIEFING`, `GUIDE`, `COMPARED`, `TAKE` based on what the content actually is. Format: `BREAKDOWN / [topic]` in mono caps. Don't use the same label twice in a row — vary based on content.

8. **Layout variety is required.** Do not reuse the same 9-card, three-column composition by default. Choose the structure from the source pattern: compact brief, timeline, checklist, comparison split, hero + evidence, or editorial grid. Only use a three-column grid when the content is clearly list-heavy and has enough substance for equal columns.

9. **Alignment discipline still applies inside the chosen layout.** For column grids, keep columns balanced (2/2/2 or 3/3/3) unless using a deliberate non-grid layout. Card bodies should usually be 25-50 words across 2-3 sentences, card titles should fit in 1-2 lines, and command badges should be 1-3 short tokens. If a point needs more space, switch layout shape instead of padding the grid.

## Reference files

- `references/design_principles.md` — Full design system (typography scale, spacing, layout rules, dos/don'ts)
- `references/illustrations.md` — Library of ready-to-use SVG illustrations for common concepts
- `references/voice_guide.md` — Editorial voice, tone examples, headline patterns
- `assets/templates/infographic.html` — Base HTML template
- `assets/logos/` — Logo SVGs (light bg, dark bg, favicon) — embed inline, don't link

## Example trigger and response

**User**: "Make an infographic from this video: https://youtube.com/watch?v=abc123"

**You**:
1. Briefly acknowledge: "Pulling the transcript and building the infographic now."
2. Run `fetch_transcript.py`, extract transcript, title, channel
3. Read transcript, identify the strongest 4-9 concepts grounded in what the source actually says
4. Choose a layout variant from the source pattern instead of defaulting to a three-column grid
5. Pick a contextual category label (`BREAKDOWN`, `PLAYBOOK`, etc.) based on content type
6. Draft headline using the slash treatment
7. Build the HTML, embedding the logo SVG and custom illustrations
8. Save to outputs, call `present_files`
9. Tell user: ready to view, here's how to screenshot it for posting
