# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `voice-forge` skill: clone any LinkedIn creator's writing voice into a reusable Agent Skill. Scrapes posts via Apify, distills deterministic features, analyzes voice, then delegates to the built-in skill-creator to install the output skill. Claude Code only.
- `voice-forge` is now listed in the `content-skills` marketplace bundle, so it installs via `/plugin install content-skills@nick-automations-skills`.
- `scripts/validate_skills.py` now fails CI when `skills/` and `.claude-plugin/marketplace.json` disagree — a new skill can no longer ship invisible to marketplace installs.

### Fixed
- `voice-forge` cached its artifacts at a fixed `data/raw_posts.json`, so cloning a second creator hit the resume check and silently reused the first creator's posts. Artifacts are now namespaced per creator under `data/<username>/`.
- `voice-forge` docs claimed 13 selected source fields; `extract_features.js` selects 14.
- `voice-forge` documented an actor input of `maxDatasetItems: 10000`; the script pins the dataset cap to the post limit so a run can't overrun its cost.
- `voice-forge` steps now name the `--force` flag the scripts already support, instead of telling the agent to re-scrape with no stated mechanism.

### Changed
- `voice-forge` description trimmed from 613 to 271 characters — it is always-loaded context, and four restatements of one trigger were collapsed into one.

## [0.1.0] — 2026-05-15

### Added
- Initial repository structure
- `youtube-to-infographic` skill: generate Nick Automations branded editorial infographics from YouTube videos, articles, or pasted text. Uses RapidAPI yt-api for transcript fetching.
- Claude Code plugin marketplace manifest (`.claude-plugin/marketplace.json`) with `content-skills` bundle
- Skill validation CI workflow
- `template/` scaffold for new skills
- Contributing guide
