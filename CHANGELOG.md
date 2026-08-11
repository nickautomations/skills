# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `voice-forge` skill: clone any LinkedIn creator's writing voice into a reusable Agent Skill. Scrapes posts via Apify, distills deterministic features, analyzes voice, then delegates to the built-in skill-creator to install the output skill. Claude Code only.
- `voice-forge` is now listed in the `content-skills` marketplace bundle, so it installs via `/plugin install content-skills@nick-automations-skills`.
- `scripts/validate_skills.py` now fails CI when `skills/` and `.claude-plugin/marketplace.json` disagree — a new skill can no longer ship invisible to marketplace installs.

### Fixed
- `skills-lock.json` had no `voice-forge` entry, and its `youtube-to-infographic` hash had been stale since the commit that introduced it — the recorded value matched the skill folder two commits earlier. Both entries now carry hashes reproduced with the CLI's own `computeSkillFolderHash` algorithm and verified against a clean clone.
- `youtube-to-infographic` step 5 saved only to `/mnt/user-data/outputs/` and called `present_files` — neither exists in Claude Code, the runtime the skill recommends, so the final step failed there. It now picks the output location from the environment.
- `youtube-to-infographic` hardcoded `python3` and `/tmp`, neither of which works on Windows (bare `python3` opens the Microsoft Store). The launcher fallbacks are documented and the transcript now lands in `outputs/`.
- `youtube-to-infographic/README.md` declared MIT while the repository, root README, and marketplace manifest all declare Apache-2.0. Corrected to Apache 2.0.
- `youtube-to-infographic` SKILL.md and `design_principles.md` disagreed on the color usage split (70/25/5 vs 65/25/5/5) and the illustration box (280×140 vs the hard-locked 160px the template actually uses). The reference is now the single source of truth for both.
- `voice-forge` cached its artifacts at a fixed `data/raw_posts.json`, so cloning a second creator hit the resume check and silently reused the first creator's posts. Artifacts are now namespaced per creator under `data/<username>/`.
- `voice-forge` docs claimed 13 selected source fields; `extract_features.js` selects 14.
- `voice-forge` documented an actor input of `maxDatasetItems: 10000`; the script pins the dataset cap to the post limit so a run can't overrun its cost.
- `voice-forge` steps now name the `--force` flag the scripts already support, instead of telling the agent to re-scrape with no stated mechanism.

### Changed
- `youtube-to-infographic` SKILL.md cut from 300 to 165 lines. The color tokens, type scale, slash CSS, category-label list, and illustration library it inlined are all owned by files in `references/`; SKILL.md now points at them instead of holding a second, drifting copy. The font-cascade rationale and the full monospace stack, which existed only in SKILL.md, moved into `design_principles.md` rather than being dropped.
- `youtube-to-infographic` description trimmed from 830 to 233 characters, and the `When to trigger` section that restated it verbatim was removed.
- `voice-forge` description trimmed from 613 to 271 characters — it is always-loaded context, and four restatements of one trigger were collapsed into one.

## [0.1.0] — 2026-05-15

### Added
- Initial repository structure
- `youtube-to-infographic` skill: generate Nick Automations branded editorial infographics from YouTube videos, articles, or pasted text. Uses RapidAPI yt-api for transcript fetching.
- Claude Code plugin marketplace manifest (`.claude-plugin/marketplace.json`) with `content-skills` bundle
- Skill validation CI workflow
- `template/` scaffold for new skills
- Contributing guide
