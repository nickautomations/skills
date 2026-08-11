---
name: youtube-to-infographic
description: Turn a YouTube video, article URL, or pasted text into a Nick Automations branded editorial infographic. Use when the user wants long-form content turned into a shareable visual, or pastes a link or transcript and asks for a graphic.
---

# Nick Automations Infographic Generator

Turn any YouTube video, article URL, or pasted text into a polished editorial-style infographic in the Nick Automations design system.

It produces one specific editorial aesthetic — heavy display headlines with the orange slash as a typographic device, monospace command/tag labels, hand-coded SVG illustrations per item, and a clean soft CTA footer driving to nickautomations.com. `design_principles.md` puts it best: what you'd get if *The Economist* designed a developer documentation page. When two options are open, take the more restrained one.

**Nick Automations** is the brand. Domain: `nickautomations.com`. The logo is an "N / A" mark where the diagonal orange slash between the letters IS the signature element. The slash isn't decoration — it's the brand's visual DNA, and it reappears as a separator inside headlines (`features/that`, `read-only/pass`, `Summarize/without forgetting`).

## Where the design system lives

This file is the **workflow**. The design system it produces is specified in the references, and each is the single source of truth for its area — read the relevant one before writing HTML rather than working from memory:

| Reference | Owns |
|-----------|------|
| `references/design_principles.md` | Color tokens, type scale, layout grid, alignment discipline, header/card/footer markup, common mistakes |
| `references/voice_guide.md` | Headline patterns, the slash treatment, card copy, command badges, the category label, words to embrace and avoid |
| `references/illustrations.md` | Ready-to-use SVG illustrations plus the rules every illustration follows |
| `assets/templates/infographic.html` | Base HTML template — every page starts as a copy of this file |
| `assets/logos/` | Logo SVGs (light bg, dark bg, favicon) — pasted inline, so the page stays portable |

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

The script reads `RAPIDAPI_KEY` from `scripts/.env` (gitignored, so the key stays local). When it is missing the script exits 1 with a JSON error carrying the whole setup walkthrough — which API to subscribe to, and where the key goes. Relay that message to the user; it is the single source of truth for the setup, and `scripts/.env.example` is the template to copy.

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
| `RAPIDAPI_KEY is not set` | Relay the script's own setup message |
| `Could not extract a YouTube video ID` | Ask the user to verify the URL |
| `RapidAPI returned HTTP 429` | Rate limited — suggest waiting or upgrading their RapidAPI plan |
| `RapidAPI returned HTTP 403` | Invalid key, or the subscription is missing |
| `No transcript content` | Captions are likely disabled — ask the user to paste the content |

Report the failure and stop there. Every fact on the finished page traces back to source text you actually hold.

**Article URLs**: Use `web_fetch`. Extract the main body, skip nav/footer/ads.

**Pasted text**: Use directly.

**Done when** you hold the full source text and can state its length. A source you could not retrieve is a stop, not a smaller infographic.

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
- **Sections/cards** — only as many content units as the source honestly supports. Each carries an item number (`01`, `02`…), a monospace badge (`/clear`, `SKILL.md`, `value-first DM`), a title with optional slash, a short body, and one inline SVG illustration. A card ends at its body — the body is the last element inside it.

`design_principles.md` Rule 3 owns the title and body limits, Rule 4 owns the card counts. Take both from there rather than from memory or from this file, which states neither on purpose. The limits exist to hold **the grid**: every column carries the same number of cards, and every card in a row ends at the same height. When a point needs more room, change the layout shape rather than padding the grid.

**Done when** you can name the variant, the category label, the headline, and a card count that divides evenly across the columns.

### Step 3: Illustrations

Every illustration is a small, hand-built SVG that depicts the concept: flat, two-colour, technical-schematic rather than cartoon.

`references/illustrations.md` owns the palette, stroke widths and viewBox, and ships a ready-made library — reach for the library first, and hand-build in the same style when no entry matches. Take the numbers from there. This file states none of them, because a second copy drifts from the first and then quietly wins.

Each visual on the page is one of exactly two things: an SVG built to that spec, or a company's name set as text. That is the entire set — and it is what keeps raster generation, stock icons, emoji-as-visual and third-party marks off the page, each of which has produced a broken piece before.

**Done when** every card carries its own illustration, no two cards share one, and each renders inside the template's illustration box.

### Step 4: Assemble the HTML

Start from `assets/templates/infographic.html` and fill it in. It already carries the striped diagonal header, the category label and logo slots, the card structure, and the CTA footer, with the alignment CSS from `design_principles.md` baked in.

Two things the template can't do for you:

- Embed the Nick Automations logo inline from `assets/logos/logo-white-bg.svg` at top-right of page 1, paired with the wordmark `Nick / AUTOMATIONS` in mono caps with an orange slash. Inline SVG keeps the file portable; an external link breaks it.
- End with exactly the one-line CTA footer: `See how we automate / nickautomations.com`. That line is the entire footer.

**Done when** the logo is inline, the footer is that single line, and the page carries every asset inside the file — the font `<link>` tags are the only external references it makes.

### Step 5: Save and present

Pick the output location from the environment:

- **`/mnt/user-data/outputs/` exists** (claude.ai / Cowork): save there and call `present_files` with the path.
- **Otherwise** (Claude Code and everywhere else): save to `outputs/` in the working directory and give the user the absolute path. `present_files` does not exist here — calling it fails the run.

Name the file `[topic-slug]-infographic.html` either way. Then brief the user:

- Open it in a browser to view
- Screenshot for posting via DevTools → "Capture full size screenshot" (Chrome: Cmd/Ctrl+Shift+P)
- 1080px wide is optimal for social; the design is responsive
- For a LinkedIn carousel, screenshot each page separately

**Done when** the file exists at the reported path, every alignment check in `design_principles.md` Rule 5 passes, and the user has been told how to view it.

Rule 5 is the step that gets skipped, and it is the one that decides whether the piece reads as designed or as assembled. **The grid** breaking — cards in a row ending at different heights — is invisible in the markup and obvious the moment anyone looks at the page. Render the file and check it rather than reasoning about the CSS: a single card body wrapping to one more line than its neighbours is enough to throw a whole row out, and nothing in the HTML will tell you.

## Content integrity rules

These three are the skill's own; everything else about quality lives in the references.

1. **Every point traces to the source.** A thin source earns a shorter infographic — six honest cards beat nine padded ones.
2. **A company appears as its name in text.** That is how brands are rendered here, in place of any drawn mark, so the page stays free of approximated logos.
3. **Every character on the page is real text.** Copy is finished copy, and any code inside an illustration is code that would run.
