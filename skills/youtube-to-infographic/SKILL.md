---
name: youtube-to-infographic
description: Turn a YouTube video, article URL, or pasted text into a Nick Automations branded editorial infographic. Use when the user wants long-form content turned into a shareable visual, or pastes a link or transcript and asks for a graphic.
---

# Nick Automations Infographic Generator

Turn any YouTube video, article URL, or pasted text into a polished editorial-style infographic in the Nick Automations design system.

This skill does NOT produce generic infographics. It produces a specific editorial aesthetic — heavy display headlines with the orange slash as a typographic device, monospace command/tag labels, hand-coded SVG illustrations per item, and a clean soft CTA footer driving to nickautomations.com.

**Nick Automations** is the brand. Domain: `nickautomations.com`. The logo is an "N / A" mark where the diagonal orange slash between the letters IS the signature element. The slash isn't decoration — it's the brand's visual DNA, and it reappears as a separator inside headlines (`features/that`, `read-only/pass`, `Summarize/without forgetting`).

## Where the design system lives

This file is the **workflow**. The design system it produces is specified in the references, and each is the single source of truth for its area — read the relevant one before writing HTML rather than working from memory:

| Reference | Owns |
|-----------|------|
| `references/design_principles.md` | Color tokens, type scale, layout grid, alignment discipline, header/card/footer markup, common mistakes |
| `references/voice_guide.md` | Headline patterns, the slash treatment, card copy, command badges, the category label, words to embrace and avoid |
| `references/illustrations.md` | Ready-to-use SVG illustrations plus the rules every illustration follows |
| `assets/templates/infographic.html` | Base HTML template — start here, don't rebuild from scratch |
| `assets/logos/` | Logo SVGs (light bg, dark bg, favicon) — embed inline, never link |

## Runtime requirements

Python 3 and network access to `rapidapi.com`, needed only for the YouTube path. Article URLs and pasted text need neither.

- **Claude Code** on a laptop/server — works (recommended)
- **claude.ai web/mobile** — works if the sandbox reaches `*.rapidapi.com` (may require an allowlist update)
- **Air-gapped environments** — the YouTube path won't work; ask the user to paste the content instead

`fetch_transcript.py` uses only the Python standard library, so there is no `pip install`.

The launcher differs by platform. Use whichever resolves: `python3` on macOS/Linux, `py -3` on Windows, `python` as the fallback. On Windows, bare `python3` opens the Microsoft Store instead of running the script — if you see that, switch to `py -3`.

## Workflow

### Step 1: Identify input and extract content

**YouTube URLs** (`youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...`):

Call the bundled script. It hits the RapidAPI yt-api service and prints a normalized JSON response on stdout.

```bash
python3 scripts/fetch_transcript.py "VIDEO_URL" > outputs/transcript.json   # py -3 on Windows
```

Write the transcript to `outputs/` (gitignored) rather than `/tmp`, which doesn't exist on Windows.

The script reads `RAPIDAPI_KEY` from `scripts/.env`. If it isn't set, the script exits 1 with a JSON error explaining how to get a key.

**Setting up RAPIDAPI_KEY (one-time, per environment):**

1. Sign up at https://rapidapi.com (free)
2. Subscribe to **yt-api by ytjar** at https://rapidapi.com/ytjar/api/yt-api — there's a free tier
3. Copy your API key from the RapidAPI dashboard
4. Copy `scripts/.env.example` to `scripts/.env`, then replace the placeholder:
   ```dotenv
   RAPIDAPI_KEY=your_key_here
   ```
   `.env` is gitignored, so the key stays local.

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
    {"start": 0.08, "duration": 5.36, "text": "..."}
  ]
}
```

Read `fullText` for the content, and `title` / `channel` for headline context only — neither becomes a source tag on the page. Parse with `jq -r '.fullText' outputs/transcript.json`, or with Python when `jq` is absent:

```bash
python3 -c "import json; print(json.load(open('outputs/transcript.json'))['fullText'])"
```

**When `success` is `false`**, read the `error` field and act on it:

| Error | Action |
|-------|--------|
| `RAPIDAPI_KEY is not set` | Walk the user through the setup above |
| `Could not extract a YouTube video ID` | Ask the user to verify the URL |
| `RapidAPI returned HTTP 429` | Rate limited — suggest waiting or upgrading their RapidAPI plan |
| `RapidAPI returned HTTP 403` | Invalid key, or the subscription is missing |
| `No transcript content` | Captions are likely disabled — ask the user to paste the content |

Report the failure and stop. A missing transcript is never filled in from memory.

**Article URLs**: Use `web_fetch`. Extract the main body, skip nav/footer/ads.

**Pasted text**: Use directly.

### Step 2: Distill into infographic structure

Read the full content, then pick the layout variant from what the source actually is:

| Source pattern | Variant |
|----------------|---------|
| "X tips/features/skills/steps" | **modular list** |
| "X vs Y" or before/after | **comparison split** |
| Single concept deep-dive | **hero + evidence** |
| Process/tutorial | **timeline/process map** |
| Dense tactical advice | **checklist/playbook** |
| Short or thin source | **compact brief** |

Reuse of one composition across every piece is the failure mode here — pick the shape the source earns. `design_principles.md` Rule 4 has the card-count configurations for each.

For all variants, extract:

- **Top-left category label** — `BREAKDOWN`, `PLAYBOOK`, `TOOLKIT`, `BRIEFING`, `GUIDE`, `COMPARED`, or `TAKE`, formatted `LABEL / [topic]` in mono caps. Pick the one matching the content, and vary it between consecutive pieces. `voice_guide.md` defines when each applies.
- **Main headline** — 4-10 words with at least one orange slash. Punchy, editorial, not clickbait.
- **Subtitle paragraph** — 2-3 sentences stating what the reader gets.
- **Sections/cards** — only as many content units as the source honestly supports, usually 4-9. Each carries an item number (`01`, `02`…), a monospace badge (`/clear`, `SKILL.md`, `value-first DM`), a 2-5 word title with optional slash, a 2-3 sentence body, and one inline SVG illustration. Cards end clean at the body: no source tags, no attribution badges.

Card titles fit two lines and bodies run 25-50 words — those limits are what keep a grid aligned, and `design_principles.md` Rule 3 is the source of truth. When a point needs more room, change the layout shape rather than padding the grid.

### Step 3: Illustrations

Use **small, hand-built SVG illustrations** that depict the concept: flat, two-color (`#1A1A1A` outlines and fills, `#FF6B35` for the one accent element), 2-3px strokes, rounded caps. Each sits in the 160px-tall illustration box from the template, with the SVG itself capped at 128px tall and roughly 280px wide.

`references/illustrations.md` has a ready-made library — reach for it first, and hand-build in the same style when no entry matches.

Guardrails, because each of these has produced a broken piece before: no AI-generated raster images (wrong logos, garbled text, off-palette color), no stock-photo icons, no emoji as the primary visual, and no third-party company logos. Where a real company must be named, set its name as text.

### Step 4: Assemble the HTML

Start from `assets/templates/infographic.html` and fill it in. It already carries the striped diagonal header, the category label and logo slots, the card structure, and the CTA footer, with the alignment CSS from `design_principles.md` baked in.

Two things the template can't do for you:

- Embed the Nick Automations logo inline from `assets/logos/logo-white-bg.svg` at top-right of page 1, paired with the wordmark `Nick / AUTOMATIONS` in mono caps with an orange slash. Inline SVG only — an external link breaks portability.
- End with exactly the one-line CTA footer: `See how we automate / nickautomations.com`. Nothing else goes at the bottom — no source list, no volume label.

### Step 5: Save and present

Pick the output location from the environment:

- **`/mnt/user-data/outputs/` exists** (claude.ai / Cowork): save there and call `present_files` with the path.
- **Otherwise** (Claude Code and everywhere else): save to `outputs/` in the working directory and give the user the absolute path. `present_files` does not exist here — calling it fails the run.

Name the file `[topic-slug]-infographic.html` either way. Then brief the user:

- Open it in a browser to view
- Screenshot for posting via DevTools → "Capture full size screenshot" (Chrome: Cmd/Ctrl+Shift+P)
- 1080px wide is optimal for social; the design is responsive
- For a LinkedIn carousel, screenshot each page separately

**Done when** the file exists at the reported path and the user has been told how to view it.

## Content integrity rules

These three are the skill's own; everything else about quality lives in the references.

1. **No invented facts.** Every point comes from the source content. A thin source gets a shorter infographic — six honest cards beat nine padded ones.
2. **No fake company logos.** Never draw the OpenAI, Anthropic, Google, or any other company mark. Use a text label or an abstract SVG.
3. **Real, legible text only.** No placeholder copy, no gibberish inside illustrations. If you draw a diff, the code in it is real code.
