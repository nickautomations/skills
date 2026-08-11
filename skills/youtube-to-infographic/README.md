# youtube-to-infographic

A Claude skill that turns YouTube videos, articles, or pasted text into editorial-style infographics in the **Nick Automations design system** — heavy display typography, orange-slash separators, a layout chosen to fit the source, hand-coded SVG illustrations, soft CTA footer driving to nickautomations.com.

Built and maintained by [Nick Automations](https://nickautomations.com).

## Install

### Claude Code (recommended)

```bash
# From the directory where you downloaded the .skill file:
unzip youtube-to-infographic.skill -d ~/.claude/skills/

# Restart Claude Code
```

### Claude.ai (web/mobile)

Settings → Capabilities → Skills → Upload skill → choose `youtube-to-infographic.skill`.

## Setup

The skill needs a RapidAPI key to fetch YouTube transcripts. One-time setup:

1. Sign up at [https://rapidapi.com](https://rapidapi.com) (free)
2. Subscribe to **[yt-api by ytjar](https://rapidapi.com/ytjar/api/yt-api)** — there's a free tier
3. Copy your API key from the RapidAPI dashboard
4. Copy `scripts/.env.example` to `scripts/.env`, then replace the placeholder:

   ```dotenv
   RAPIDAPI_KEY=your_key_here
   ```

The `.env` file is ignored by Git, so your key stays local.

## Usage

Once installed and the key is set, just give Claude a YouTube URL:

```
Make an infographic from https://www.youtube.com/watch?v=VIDEO_ID
```

The skill will:
1. Fetch the transcript via the RapidAPI yt-api service
2. Distill the content into the strongest 4-9 ideas
3. Generate an HTML infographic in the Nick Automations design system
4. Save the file to your outputs and tell you how to screenshot it for posting

You can also paste an article URL or raw text — the skill handles all three input types.

## What the skill produces

A single self-contained HTML file with:
- Heavy display typography (Satoshi → Geist → Cabinet Grotesk cascade)
- A source-driven editorial layout: compact brief, timeline, checklist, comparison split, hero + evidence, or a balanced card grid
- Hand-coded SVG illustrations matching each concept
- Orange-slash separator treatment in headlines
- Contextual category label (`BREAKDOWN`, `PLAYBOOK`, `TOOLKIT`, etc.) top-left
- Nick Automations logo and wordmark embedded inline
- Soft CTA footer driving to nickautomations.com

Open the HTML in a browser, then use your browser's "capture full page screenshot" (DevTools) to export as PNG for posting.

## Customizing the design system

The brand identity is encoded in:
- `references/design_principles.md` — typography, color palette, spacing, alignment rules
- `references/illustrations.md` — SVG snippets for common concepts
- `references/voice_guide.md` — editorial tone, headline patterns, words to avoid
- `assets/templates/infographic.html` — base HTML template
- `assets/logos/` — Nick Automations logo SVGs

Edit any of these to fork the design for your own brand.

## Troubleshooting

**Windows opens the Microsoft Store instead of running the script** → Bare `python3` is a Store alias on Windows. Use `py -3 scripts/fetch_transcript.py "URL"` instead.

**"RAPIDAPI_KEY is not set"** → Copy `skills/youtube-to-infographic/scripts/.env.example` to `skills/youtube-to-infographic/scripts/.env`, replace the placeholder key, then run the script again.

**"RapidAPI returned HTTP 403"** → Your subscription expired or the key is wrong. Check the RapidAPI dashboard.

**"RapidAPI returned HTTP 429"** → You've hit the rate limit on your tier. Wait, or upgrade your RapidAPI plan.

**"No transcript content was returned"** → The video has captions disabled. Paste a manual summary instead.

**Cards aren't lining up in columns** → If you use a column grid, keep columns balanced (2/2/2 or 3/3/3). If the content does not fit evenly, use a timeline, checklist, comparison split, or compact brief instead.

## Cost

- The skill itself: free
- RapidAPI yt-api: free tier covers casual use; paid tiers if you generate dozens of infographics per day

## License

Apache 2.0 — see [LICENSE](../../LICENSE) at the repo root. Fork it, modify it, use it. If you build something cool, [tell us](https://nickautomations.com).
