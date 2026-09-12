---
name: sales-navigator-search-builder
description: "Build a LinkedIn Sales Navigator search URL from a natural-language ICP. Use when the user describes who they want to find (industry, seniority, function, headcount, geography, language), asks for a Sales Nav or LinkedIn search URL, or wants job-title variants normalized into a boolean string."
---

# Sales Navigator Search Builder

Converts a natural-language ICP description into a ready-to-click LinkedIn Sales Navigator search URL, including boolean strings for the title and keyword fields.

## What this file owns

Everything needed to build a Sales Nav URL is here: the spec format, the boolean rules, the presets, and the ID tables for every small enum. Work from this file rather than from `references/`.

Open a reference only in these cases:

| Case | Where to look |
|---|---|
| An industry outside the top-10 table and the presets — "maritime shipping", "veterinary services" | `references/industries.json` |
| A country outside the top-30 table and the region presets — "Kazakhstan", "Senegal" | `references/regions.json` |
| Anything below country level — a city, US state or metro area | Run the resolver, see [Dynamic geo resolution](#dynamic-geo-resolution) |

Check the presets before opening anything. They are built around how B2B sellers actually describe geography ("EMEA", "DACH", "Nordics") and verticals ("SaaS", "FinTech", "HRTech"), so the answer is usually already on this page — which is what keeps a lookup from costing a tool call.

**About the inline ID tables.** The Function, Seniority, Headcount, Company type, Years and Language tables reproduce their `references/*.json` files in full. `build_url.py` validates against the JSON, never against this file, so the JSON is authoritative. Those six enums are stable, and an ID that no longer exists fails loudly at build time rather than silently — which is what makes the copies safe to work from. When one changes, edit the JSON and this table together.

## Step 0 — Resolve the Python launcher

Every command in this file is written as `<PY>`. Resolve it once, before the first command, and reuse that exact string throughout.

| Operating system | Use | What goes wrong otherwise |
|---|---|---|
| Windows | `py -3` | `python3` is usually a Microsoft Store stub that opens the Store and runs nothing |
| macOS / Linux | `python3` | `python` is often absent, or is Python 2 |

Confirm the choice with a single call before relying on it:

```bash
py -3 --version        # Windows
python3 --version      # macOS / Linux
```

That prints a version like `Python 3.13.1`. If the command is missing or prints nothing, try the other row, then bare `python`; use the first that reports 3.9 or higher.

**Done when** one launcher has printed a 3.9+ version and you are using that exact string for every `<PY>` below.

## Workflow

1. **Resolve any sub-country location first.** For a city, US state or metro area, run the resolver before building the spec:
   ```bash
   <PY> scripts/resolve_geo.py "Austin, Texas" --json
   ```
   Take the `id` from its JSON output and use it in the spec's `REGION` values. Every non-zero exit is defined once in [Exit codes](#exit-codes) — act on that table.

   Countries and native super-regions skip this step; their IDs are already inline below.

2. **Build the JSON spec** from the inline content below.

3. **Pipe the spec to the builder** and capture the URL:
   ```bash
   echo '<JSON_SPEC>' | <PY> scripts/build_url.py -
   ```

4. **Hand over the URL** — see [Output format](#output-format) at the end of this file.

The builder validates every ID against the reference files, runs boolean validation on text fields, and refuses to emit an invalid URL.

**Done when** `build_url.py` has exited 0 and the user has the URL plus a one-line recap of the filters it encodes.

## Spec format

```json
{
  "filters": [
    {"type": "INDUSTRY", "values": [{"id": 4, "selectionType": "INCLUDED"}]},
    {"type": "FUNCTION", "values": [{"id": 15, "selectionType": "INCLUDED"}]},
    {"type": "REGION", "values": [{"id": 105015875, "selectionType": "INCLUDED"}]},
    {"type": "CURRENT_TITLE", "values": [{"text": "(CMO OR \"Chief Marketing Officer\") NOT Fractional", "selectionType": "INCLUDED"}]},
    {"type": "RECENTLY_CHANGED_JOBS", "toggle": true}
  ]
}
```

**Field rules** (complete):
- `type` — one of the filter types listed below.
- `values` — array of value objects.
- `id` — for ID-based filters. Integer for most enums; single-letter string for `COMPANY_HEADCOUNT` and `COMPANY_TYPE`; 2-letter code for `PROFILE_LANGUAGE`.
- `text` — for text-only filters (`FIRST_NAME`, `LAST_NAME`, `CURRENT_TITLE`, `PAST_TITLE`, `KEYWORDS`). Auto-resolved for ID-based filters — omit it there.
- `selectionType` — `"INCLUDED"` (default) or `"EXCLUDED"`. Use `EXCLUDED` when the user says "exclude", "except", "not", "without".
- `toggle: true` — shortcut for toggle filters; the builder auto-fills the hardcoded ID.

When a user targets multiple values of the same filter type (e.g., "France, Germany, Italy"), put them all in one filter object's `values` array — LinkedIn applies OR within a filter and AND across filters.

## Region presets

> **City, state, and metro targeting:** the presets and `regions.json` cover countries and LinkedIn-native super-regions only. For sub-country targeting, resolve the location dynamically with `<PY> scripts/resolve_geo.py "<location>"` — see [Dynamic geo resolution](#dynamic-geo-resolution). Resolved IDs are cached and validated by `build_url.py` exactly like country IDs.

B2B sellers think in regional groupings, not individual countries. **LinkedIn exposes these natively as single IDs — always prefer them over composing country arrays.** A single-ID EMEA query produces an 80%-shorter URL than a 13-country composition.

### LinkedIn native regions (preferred — single ID)

When the user names one of these, use the single ID directly in `values:`. No country composition needed.

| User says | ID | LinkedIn entity |
|---|---|---|
| EMEA | `91000007` | EMEA |
| DACH | `91000006` | DACH |
| Benelux | `91000005` | Benelux |
| Nordics | `91000009` | Nordics |
| APAC | `91000003` | APAC |
| APJ (Asia Pacific Japan) | `91000004` | APJ |
| MENA (Middle East / North Africa) | `91000008` | MENA |
| Oceania | `91000010` | Oceania |
| North America / NorAm | `102221843` | North America |
| South America | `104514572` | South America |
| Europe (whole continent) | `100506914` | Europe |
| Asia | `102393603` | Asia |
| Africa | `103537801` | Africa |
| Worldwide / "anywhere" | `92000000` | Worldwide |

Example spec:
```json
{"type": "REGION", "values": [{"id": 91000007, "selectionType": "INCLUDED"}]}
```

### Custom country composition (only when user wants a non-standard subset)

Use these only when the user explicitly wants a custom grouping that doesn't match a native region — e.g. "Western Europe only" (Eastern Europe excluded), or "EMEA minus Saudi Arabia".

#### EMEA core — 20 countries (narrower than native EMEA, B2B SaaS focus)

`101165590, 105015875, 101282230, 105646813, 103350119, 102890719, 100565514, 106693272, 104738515, 105117694, 103819153, 104514075, 100456013, 103883259, 100364837, 105072130, 104042105, 101620260, 104305776, 100459316`

UK, France, Germany, Spain, Italy, Netherlands, Belgium, Switzerland, Ireland, Sweden, Norway, Denmark, Finland, Austria, Portugal, Poland, Luxembourg, Israel, UAE, Saudi Arabia.

#### Western Europe — 12 countries (no native equivalent)

`101165590, 105015875, 101282230, 105646813, 103350119, 102890719, 100565514, 106693272, 104738515, 103883259, 100364837, 104042105`

UK, France, Germany, Spain, Italy, Netherlands, Belgium, Switzerland, Ireland, Austria, Portugal, Luxembourg.

#### LATAM core — 5 countries (different from native South America: includes Mexico)

`106057199, 103323778, 100446943, 104621616, 100876405`

Brazil, Mexico, Argentina, Chile, Colombia.

For DACH, Benelux, Nordics, NorAm, APAC, MENA, Oceania the native single ID above is the whole answer.

## Industry presets

When the user names a B2B vertical, **use the preset below** instead of grepping industries.json.

| User says | Industry IDs | What it maps to |
|---|---|---|
| **SaaS** / B2B SaaS / "software companies" | `4, 6` | Software Development + Tech Info Internet |
| **FinTech** | `4, 43` | Software Development + Financial Services |
| **InsurTech** | `4, 42` | Software Development + Insurance |
| **HRTech** | `4, 137, 104` | Software Dev + HR Services + Staffing & Recruiting |
| **EdTech** | `4, 132, 3208` | Software Dev + E-Learning Providers + E-learning |
| **HealthTech** | `4, 14, 3207` | Software Dev + Hospitals & Health Care + Health Wellness Fitness |
| **BioTech** | `3238, 15` | Biotechnology + Pharmaceutical Manufacturing |
| **Cybersecurity** | `118, 4` | Computer & Network Security + Software Development |
| **DataTech / AI** | `2458, 4` | Data Infrastructure & Analytics + Software Development |
| **AdTech / MarTech** | `4, 1862, 80` | Software Dev + Marketing Services + Advertising Services |
| **eCommerce** | `4, 6, 27` | Software Dev + Tech Info Internet + Retail |
| **Agency / Consulting** | `11, 1862, 80` | Business Consulting + Marketing Services + Advertising Services |
| **Logistics / SupplyChain** | `116, 4` | Transportation/Logistics/Supply Chain + Software Dev |
| **PE / VC** | `106, 46` | Venture Capital and Private Equity Principals + Investment Management |
| **Pure B2B (any tech)** | `4, 6, 96` | Software Dev + Tech Info Internet + IT Services |

For specific verticals not covered (e.g. "veterinary SaaS", "maritime tech"), consult `references/industries.json`.

## Top countries (when no preset fits)

| ID | Country | ID | Country |
|---|---|---|---|
| 103644278 | United States | 102713980 | India |
| 105015875 | France | 102454443 | Singapore |
| 101165590 | United Kingdom | 101355337 | Japan |
| 101282230 | Germany | 101452733 | Australia |
| 105646813 | Spain | 105149562 | South Korea |
| 103350119 | Italy | 103291313 | Hong Kong SAR |
| 102890719 | Netherlands | 106057199 | Brazil |
| 100565514 | Belgium | 103323778 | Mexico |
| 106693272 | Switzerland | 104305776 | United Arab Emirates |
| 104738515 | Ireland | 101620260 | Israel |
| 105117694 | Sweden | 102105699 | Türkiye |
| 104042105 | Luxembourg | 92000000 | Worldwide |
| 101174742 | Canada | 102890883 | China |

**Full 268 countries**: consult `references/regions.json` when the user names something not above and not in a region preset.

## Top industries (when no preset fits)

| ID | Industry |
|---|---|
| 4 | Software Development |
| 6 | Technology, Information and Internet |
| 96 | IT Services and IT Consulting |
| 43 | Financial Services |
| 11 | Business Consulting and Services |
| 80 | Advertising Services |
| 1862 | Marketing Services |
| 25 | Manufacturing |
| 27 | Retail |
| 105 | Professional Training and Coaching |

**Full 350+ industries**: consult `references/industries.json` for niche verticals.

## Functions (`FUNCTION`)

| ID | Function | ID | Function |
|---|---|---|---|
| 1 | Accounting | 14 | Legal |
| 2 | Administrative | 15 | Marketing |
| 3 | Arts and Design | 16 | Media and Communication |
| 4 | Business Development | 17 | Military and Protective Services |
| 5 | Community and Social Services | 18 | Operations |
| 6 | Consulting | 19 | Product Management |
| 7 | Education | 20 | Program and Project Management |
| 8 | Engineering | 21 | Purchasing |
| 9 | Entrepreneurship | 22 | Quality Assurance |
| 10 | Finance | 23 | Real Estate |
| 11 | Healthcare Services | 24 | Research |
| 12 | Human Resources | 25 | Sales |
| 13 | Information Technology | 26 | Customer Success and Support |

## Seniority (`SENIORITY_LEVEL`)

| ID | Level | ID | Level |
|---|---|---|---|
| 320 | Owner / Partner | 210 | Experienced Manager |
| 310 | CXO | 200 | Entry Level Manager |
| 300 | Vice President | 130 | Strategic |
| 220 | Director | 120 | Senior |
| 110 | Entry Level | 100 | In Training |

## Company headcount (`COMPANY_HEADCOUNT`)

| ID | Range | ID | Range |
|---|---|---|---|
| A | Self-employed | F | 501-1,000 |
| B | 1-10 | G | 1,001-5,000 |
| C | 11-50 | H | 5,001-10,000 |
| D | 51-200 | I | 10,001+ |
| E | 201-500 |  |  |

## Company type (`COMPANY_TYPE`)

| ID | Type | ID | Type |
|---|---|---|---|
| C | Public Company | E | Self Employed |
| P | Privately Held | O | Self Owned |
| N | Non Profit | G | Government Agency |
| D | Educational Institution | S | Partnership |

## Years ranges (`YEARS_AT_CURRENT_COMPANY`, `YEARS_IN_CURRENT_POSITION`, `YEARS_OF_EXPERIENCE`)

`1` Less than 1 year · `2` 1 to 2 years · `3` 3 to 5 years · `4` 6 to 10 years · `5` More than 10 years.

## Profile language (`PROFILE_LANGUAGE`)

2-letter codes: `fr` French · `en` English · `de` German · `es` Spanish · `it` Italian · `pt` Portuguese · `nl` Dutch · `pl` Polish · `ru` Russian · `zh` Chinese · `ja` Japanese · `ko` Korean · `ar` Arabic · `tr` Turkish · `sv` Swedish · `no` Norwegian · `da` Danish · `cs` Czech · `ro` Romanian · `tl` Tagalog · `ms` Malay · `in` Bahasa Indonesia.

## Toggle filters

| Type | Hardcoded ID | Behavior |
|---|---|---|
| `RECENTLY_CHANGED_JOBS` | `RPC` | Changed jobs in last 90 days |
| `POSTED_ON_LINKEDIN` | `RPOL` | Posted on LinkedIn in last 30 days |
| `PAST_COLLEAGUE` | `PCOLL` | People from your past companies |
| `FOLLOWS_YOUR_COMPANY` | `CF` | Follows your LinkedIn page |

Shorthand: `{"type": "RECENTLY_CHANGED_JOBS", "toggle": true}`.

## Boolean search (authoritative)

Works in **3 fields only**: `KEYWORDS`, `CURRENT_TITLE`, `PAST_TITLE`. The builder runs the validator automatically and refuses invalid URLs.

### Operators

`AND` (both match) · `OR` (either matches) · `NOT` (exclude) · `"..."` (exact phrase) · `(...)` (grouping)

Precedence: `()` > `""` > `NOT` > `AND` > `OR`. When in doubt, wrap groups in parens.

### Hard rules

1. **UPPERCASE operators** only. Lowercase = treated as search term.
2. **Straight quotes only** (`"`). Curly quotes silently break the query.
3. **No wildcards**: `Manag*` doesn't expand. Use `(Manager OR Management OR Managing)`.
4. **Stop words ignored**: `the a an to for of on in with by and` (lowercase).
5. **Hard limit: 15 operators per field, ~2,000 chars, 3-4 levels nesting max.**

### Standard B2B patterns

```
CMO       → ("CMO" OR "Chief Marketing Officer" OR "Head of Marketing" OR "VP Marketing")
CRO/Sales → ("CRO" OR "Chief Revenue Officer" OR "Head of Sales" OR "VP Sales" OR "SVP Sales")
CEO       → (CEO OR "Chief Executive Officer" OR Founder OR Co-Founder OR Owner)
CFO       → (CFO OR "Chief Financial Officer" OR "Head of Finance" OR "VP Finance")
CTO       → (CTO OR "Chief Technology Officer" OR "VP Engineering" OR "Head of Engineering")
RevOps    → ("Head of Sales Operations" OR "RevOps" OR "Revenue Operations" OR "Sales Operations Manager")
Growth    → ("Head of Growth" OR "Growth Manager" OR "Growth Marketing Manager" OR "Demand Generation Manager")
SDR Mgr   → ("SDR Manager" OR "BDR Manager" OR "Head of SDR" OR "Sales Development Manager")
```

### Standard exclusions (noise filter)

When targeting full-time decision-makers, always add:
```
NOT (Fractional OR Freelance OR Consultant OR Advisor OR Intern OR Assistant)
```
For tighter exclusions add: `Student OR Junior OR Retired OR Former OR Ex`. Watch the 15-operator limit.

"Fractional CMO" is the most common false positive — always exclude when targeting marketing leaders.

### Decision tree (compact)

1. Is the role written multiple ways? → wrap variants in `(... OR ... OR ...)`
2. Common false positive? → add `NOT (...)`
3. Multi-word role? → straight quotes
4. Ambiguous precedence? → parens
5. Operator count near 15? → trim or split into two searches

### Anti-patterns

| Wrong | Right |
|---|---|
| `CMO or Founder` (lowercase) | `CMO OR Founder` |
| `"Head of Sales"` (curly) | `"Head of Sales"` (straight) |
| `Head of Sales OR Director` | `"Head of Sales" OR Director` |
| `Manag*` | `(Manager OR Management)` |
| `CMO OR CRO AND SaaS` | `(CMO OR CRO) AND SaaS` |
| `NOT Assistant OR Intern` | `NOT (Assistant OR Intern)` |

For extremely complex patterns (5+ nested groups, tool-stack signals in KEYWORDS), see `references/boolean-search.md`.

## How to call the builder

```bash
# Stdin (preferred — no temp file needed)
echo '<JSON_SPEC>' | <PY> scripts/build_url.py -

# Or from a file
<PY> scripts/build_url.py spec.json
```

The script prints the URL to stdout. Warnings go to stderr; errors fail the build.

To lint a boolean string standalone (rarely needed — the builder validates automatically):
```bash
<PY> scripts/validate_boolean.py '(CMO OR "Chief Marketing Officer") NOT Fractional'
```

## Out of scope

These filters need entity URN lookup and aren't supported:
- Current/Past company (needs LinkedIn company URN)
- Company HQ location
- School, Groups, Persona, Account/Lead lists, Connections of

Cities and metropolitan areas are supported dynamically via `scripts/resolve_geo.py` when LinkedIn credentials are configured (see "Dynamic geo resolution" below). Without credentials, the user adds them manually in the Sales Nav UI.

When asked for the remaining out-of-scope items, explain they need to be added in the Sales Navigator UI directly.

## Dynamic geo resolution

`scripts/resolve_geo.py` resolves any free-text location to a LinkedIn geo URN via the LinkedIn Typeahead API, then caches it so repeat lookups work offline.

### When to call it

Call the resolver when the user names a location that is **not a country** and **not one of the native super-regions above** — i.e. a US state ("Texas"), a city ("Berlin"), a metro area ("Bay Area"), or a sub-national grouping ("Greater London").

Do **not** call it for countries or native super-regions — those are already in `regions.json` and the presets.

### How to call it

```bash
# Default: human-readable
<PY> scripts/resolve_geo.py "Austin, Texas"

# Machine-parseable (preferred when building a spec)
<PY> scripts/resolve_geo.py "Austin, Texas" --json
```

On success it prints (and caches) the geo ID. Drop the `id` into the spec's `REGION` values exactly like a country ID — `build_url.py` validates it against `regions.json` **and** the geo cache.

### Exit codes

| Code | Meaning | What you do |
|---|---|---|
| 0 | Resolved | Use the `id` |
| 2 | LinkedIn credentials not configured | Fall back to manual UI capture — this exit is final |
| 3 | Token expired | Tell the user to run `<PY> scripts/resolve_geo.py --auth` |
| 4 | No match | Ask the user for a more specific name |
| 5 | Network/API error | Retry once, then fall back |

### First-time setup (one-time per user)

If exit 2 keeps happening and the user wants city-level targeting, they need to configure LinkedIn OAuth once:

1. Copy `.env.example` to `.env` in the skill root.
2. Fill in `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_REDIRECT_URI` from the LinkedIn Developer Portal. The app needs the `r_ads` scope.
3. Run `<PY> scripts/resolve_geo.py --auth` and follow the pasted-redirect flow.

After that, resolutions work and cache locally.

## Output format

Give the user three things, in this order:

1. **The URL**, on its own line, exactly as `build_url.py` printed it.
2. **A one-line recap** of the ICP in plain language — e.g. "Senior marketing leaders at FinTech companies in DACH, 51-500 employees."
3. **A filter table** listing only the filters actually applied.

| Filter | Value format |
|---|---|
| Industries | Full names, comma-separated |
| Region | `EMEA` for a native region, or `France, Germany, UK + 10` for a composition |
| Headcount | `11-50 + 51-200`, or the single range |
| Seniority | `Director, VP, CXO` |
| Function | `Sales, Marketing` |
| Title | 2-3 representative terms, then `… (N operators)` |
| Keywords | 2-3 representative terms |
| Recent job change | `Yes`, when the toggle is on |
| Posted on LinkedIn | `Yes`, when the toggle is on |

Order: Industries, Region, Headcount, Seniority/Function, Title, Keywords, toggles.

For the boolean fields, show the representative terms and the operator count rather than the full string — a 15-operator boolean is unreadable inline and the user has it in the URL already.

Match the user's language if they wrote in something other than English.

## Examples

- `examples/marketing-leaders.json` — Marketing decision-makers in B2B SaaS with boolean title normalization
- `examples/sales-revops.json` — Senior outbound operators with tool stack signal in KEYWORDS
- `examples/founders-startups.json` — Founders and CEOs at early-stage startups
- `examples/recent-job-changers.json` — Senior leaders who recently changed jobs (warm signal)

## Testing

```bash
<PY> scripts/build_url.py --test
<PY> scripts/validate_boolean.py --test
<PY> scripts/resolve_geo.py --test
<PY> scripts/resolve_geo.py --auth-status
```

Origin and attribution: see `README.md`.
