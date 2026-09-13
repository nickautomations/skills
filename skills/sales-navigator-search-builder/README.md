# Sales Navigator Search Builder

> Turns a natural-language ICP description into a precise LinkedIn Sales Navigator search URL — complete with boolean strings, role normalization, and noise exclusion.

## What it does

You describe who you're trying to find:

> "CMOs at B2B SaaS companies in France, 50-500 employees, exclude fractional and freelance."

The skill builds the matching Sales Navigator URL — industries mapped to LinkedIn IDs, the title field normalized into a boolean string (`CMO OR "Chief Marketing Officer" OR "VP Marketing"`), noise excluded (`NOT (Fractional OR Freelance OR Intern)`), headcount and region applied. Click the URL and Sales Navigator opens with every filter in place.

## Why it exists

Sales Navigator URLs are powerful but painful to hand-craft. The format is undocumented, double-URL-encoded, requires LinkedIn-specific IDs for industries, geographies and seniority levels, and breaks silently on small mistakes — a lowercase `or`, a curly quote, an unbalanced parenthesis.

This skill encodes the format, ships LinkedIn's reference IDs, and validates boolean syntax before building the URL — refusing to emit an invalid one. It also bakes in the boolean patterns experienced prospectors learn the hard way: C-suite role normalization, fractional/freelance exclusion, tool-stack signals.

## Usage

Ask Claude directly — e.g. *"Build a Sales Nav URL for senior RevOps leaders in US SaaS, 200-5,000 employees, who mention Outreach or Salesloft in their profile."*

The skill returns the URL, a one-line recap of the ICP, and a table of the filters it encoded.

**Prerequisites:** Python 3.9+, and an active Sales Navigator subscription to open the resulting URL.

Building URLs needs nothing else — `build_url.py` and `validate_boolean.py` use only the standard library. The optional city/state/metro resolver is the one part with dependencies:

```bash
pip install -r requirements.txt   # requests, python-dotenv
```

On Windows invoke Python as `py -3`; on macOS and Linux as `python3`.

## What's supported

- **Filters with full ID mapping** — Industry, Function, Seniority level, Company headcount, Company type, Years in current company / position / experience, Profile language, Region (curated list of countries + dynamic city/state/metro resolution via `scripts/resolve_geo.py` when LinkedIn credentials are configured). The JSON files in `references/` are the authoritative ID lists; `scripts/build_url.py` validates every ID against them.
- **Text filters with boolean** — Keywords (global), Current job title, Past job title — accept `AND`, `OR`, `NOT`, `"…"`, `(…)` with automatic validation (refuses lowercase operators, curly quotes, unbalanced parentheses, wildcards, exceeded operator budget).
- **Text filters without boolean** — First name, Last name.
- **Toggle filters** — Changed jobs (90d), Posted on LinkedIn (30d), Past colleague, Follows your company.
- **Deterministic URL builder + validator** (`scripts/build_url.py`, `scripts/validate_boolean.py`) — refuses to emit an invalid URL and ships a regression suite that reproduces real captured Sales Nav URLs.

## What's not supported

Filters that require entity URN lookup are out of scope:

- Current/Past company (needs LinkedIn company URN)
- School, Groups, Persona, Account/Lead lists, Connections of

Cities, states and metro areas sit in between: the bundled `regions.json` covers countries and LinkedIn's native super-regions only, so sub-country targeting needs `scripts/resolve_geo.py` and LinkedIn API credentials. Without those credentials the skill says so and asks you to add the location in the Sales Navigator UI.

## Limitations

- **Sales Navigator subscription required.** The URLs only work if you have an active Sales Nav subscription on the LinkedIn account you're using. LinkedIn redirects to an upsell page otherwise.
- **English-oriented patterns.** The boolean patterns assume English-language titles ("CMO", "Head of Sales"). For French, German, Spanish or other non-English prospects, adapt the titles to local equivalents (e.g. "Directeur Marketing", "Geschäftsführer").
- **LinkedIn changes the URL format from time to time.** When it does, the skill needs an update.

## Standalone by design

This skill needs no account, subscription, or third-party product. It builds a URL and hands it to you; where you take it next is your business. The only external service it can touch is LinkedIn's own API, and only if you opt into city-level geo resolution by configuring your own LinkedIn app.

## Credits

Derived from an MIT-licensed original by a third party, with substantial modifications. See [`LICENSE`](LICENSE) for the copyright notice and the list of changes.
