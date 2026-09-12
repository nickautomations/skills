#!/usr/bin/env python3
"""
LinkedIn Sales Navigator URL Builder

Usage:
    python3 build_url.py spec.json        # build URL from spec
    python3 build_url.py --test           # run regression tests
    python3 build_url.py --help           # show help
"""

import json
import os
import sys
from pathlib import Path
from urllib.parse import quote, unquote

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
REFS_DIR = SKILL_ROOT / "references"

# Text-only filters wrapped as (type:X,values:List((text:..., selectionType:...))).
# NOTE: KEYWORDS is also a text field but uses a different URL structure (top-level
# `keywords:VALUE` property, not wrapped in filters:List). It's extracted before
# build_filter runs — see build_url().
TEXT_FILTERS = {"FIRST_NAME", "LAST_NAME", "CURRENT_TITLE", "PAST_TITLE"}

# Filters that support boolean syntax inside filters:List. KEYWORDS also accepts
# boolean but is validated separately via _validate_keywords_text().
BOOLEAN_CAPABLE_FILTERS = {"CURRENT_TITLE", "PAST_TITLE"}

# Import the validator. Same dir, so direct import works.
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from validate_boolean import validate as validate_boolean
except ImportError:
    validate_boolean = None

# Filter types that take an ID + reference file to validate against.
ID_BASED_FILTERS = {
    "INDUSTRY": "industries.json",
    "FUNCTION": "functions.json",
    "SENIORITY_LEVEL": "seniority.json",
    "COMPANY_HEADCOUNT": "company-headcount.json",
    "COMPANY_TYPE": "company-type.json",
    "YEARS_AT_CURRENT_COMPANY": "years-ranges.json",
    "YEARS_IN_CURRENT_POSITION": "years-ranges.json",
    "YEARS_OF_EXPERIENCE": "years-ranges.json",
    "PROFILE_LANGUAGE": "languages.json",
    "REGION": "regions.json",
}

# Toggle filters: hardcoded ID, no user value needed.
TOGGLE_FILTERS = {
    "RECENTLY_CHANGED_JOBS": {"id": "RPC", "text": "Changed jobs"},
    "POSTED_ON_LINKEDIN": {"id": "RPOL", "text": "Posted on LinkedIn"},
    "PAST_COLLEAGUE": {"id": "PCOLL", "text": "Past colleague"},
    "FOLLOWS_YOUR_COMPANY": {"id": "CF", "text": None},  # no text in real URL
}


def load_reference(filename):
    path = REFS_DIR / filename
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _geo_cache_paths():
    """Candidate geo-cache.json locations, in priority order."""
    paths = [REFS_DIR / "geo-cache.json"]
    env_override = os.getenv("SALES_NAV_GEO_CACHE")
    if env_override:
        paths.append(Path(env_override))
    data_home = os.getenv("SALES_NAV_DATA_HOME")
    if data_home:
        user_dir = Path(data_home)
    elif sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        user_dir = Path(base) / "sales-nav-builder"
    else:
        user_dir = Path(os.path.expanduser("~/.sales-nav-builder"))
    paths.append(user_dir / "geo-cache.json")
    return paths


def load_geo_cache():
    """Load and merge every discoverable geo-cache.json. Tolerant of corruption."""
    merged = []
    for path in _geo_cache_paths():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                merged.extend(data)
        except (OSError, ValueError):
            continue
    return merged


def load_reference_for(filter_type):
    """Load a reference file. For REGION, also merge dynamic geo-cache entries."""
    base = load_reference(ID_BASED_FILTERS[filter_type])
    if filter_type == "REGION":
        base = base + load_geo_cache()
    return base


def inner_encode(text):
    """Pass 1: LinkedIn inner encoding. Replaces special chars with %XX."""
    # Use quote with safe='' so everything non-alphanumeric except - _ . ~ gets encoded.
    return quote(str(text), safe="-_.~")


def outer_encode(query_string):
    """Pass 2: URL encoding of the whole query string, keeping parens unencoded."""
    return quote(query_string, safe="()")


def build_filter_value(filter_type, value, references_cache):
    """Build the inner string for one filter value, e.g. (id:4,text:Software%20Development,selectionType:INCLUDED)."""
    selection = value.get("selectionType", "INCLUDED")
    if selection not in ("INCLUDED", "EXCLUDED"):
        raise ValueError(f"Invalid selectionType '{selection}' in {filter_type}")

    parts = []

    if filter_type in ID_BASED_FILTERS:
        vid = value.get("id")
        if vid is None:
            raise ValueError(f"Missing 'id' in {filter_type} value")
        # Validate against reference
        ref = references_cache.setdefault(
            filter_type, load_reference_for(filter_type)
        )
        match = next((r for r in ref if r["id"] == vid), None)
        if match is None:
            valid_ids = ", ".join(str(r["id"]) for r in ref[:10])
            raise ValueError(
                f"Unknown id '{vid}' for filter {filter_type}. "
                f"Check {ID_BASED_FILTERS[filter_type]} (first valid ids: {valid_ids}…)"
            )
        text = value.get("text") or match["displayValue"]
        parts.append(f"id:{vid}")
        parts.append(f"text:{inner_encode(text)}")

    elif filter_type in TEXT_FILTERS:
        text = value.get("text")
        if text is None:
            raise ValueError(f"Missing 'text' in {filter_type} value")

        # If this is a boolean-capable field, run the boolean validator.
        if filter_type in BOOLEAN_CAPABLE_FILTERS and validate_boolean is not None:
            result = validate_boolean(text)
            if result.errors:
                error_msg = "; ".join(result.errors)
                raise ValueError(
                    f"Boolean validation failed for {filter_type}: {error_msg}"
                )
            if result.warnings:
                for w in result.warnings:
                    print(f"  [warn] {filter_type}: {w}", file=sys.stderr)

        parts.append(f"text:{inner_encode(text)}")

    elif filter_type in TOGGLE_FILTERS:
        meta = TOGGLE_FILTERS[filter_type]
        parts.append(f"id:{meta['id']}")
        if meta["text"]:
            parts.append(f"text:{inner_encode(meta['text'])}")

    else:
        raise ValueError(f"Unsupported filter type: {filter_type}")

    parts.append(f"selectionType:{selection}")
    return "(" + ",".join(parts) + ")"


def build_filter(filter_obj, references_cache):
    """Build the inner string for one filter, e.g. (type:INDUSTRY,values:List((...),(...)))."""
    ftype = filter_obj["type"]

    # Toggle shorthand: {"type": "RECENTLY_CHANGED_JOBS", "toggle": true}
    if filter_obj.get("toggle"):
        if ftype not in TOGGLE_FILTERS:
            raise ValueError(f"'toggle: true' only valid for {list(TOGGLE_FILTERS.keys())}, got {ftype}")
        values = [{"selectionType": "INCLUDED"}]
    else:
        values = filter_obj.get("values", [])
        if not values:
            raise ValueError(f"Filter {ftype} has no values")

    value_strings = [build_filter_value(ftype, v, references_cache) for v in values]
    return f"(type:{ftype},values:List({','.join(value_strings)}))"


def _validate_keywords_text(text):
    """Run boolean validation on a KEYWORDS string. Returns the text, raises on errors."""
    if validate_boolean is None:
        return text
    result = validate_boolean(text)
    if result.errors:
        error_msg = "; ".join(result.errors)
        raise ValueError(f"Boolean validation failed for KEYWORDS: {error_msg}")
    if result.warnings:
        for w in result.warnings:
            print(f"  [warn] KEYWORDS: {w}", file=sys.stderr)
    return text


def build_url(spec):
    """Build the full Sales Nav URL from a spec dict."""
    filters = spec.get("filters", [])
    if not filters:
        raise ValueError("Spec has no filters")

    references_cache = {}

    # KEYWORDS is a top-level property on the query, not a filter inside filters:List.
    # Pull it out before building the rest.
    keywords_value = None
    regular_filters = []
    for f in filters:
        if f.get("type") == "KEYWORDS":
            if keywords_value is not None:
                raise ValueError(
                    "Multiple KEYWORDS filters in spec. Only one KEYWORDS string is supported "
                    "(combine your terms with AND/OR in a single string)."
                )
            values = f.get("values", [])
            if not values or not values[0].get("text"):
                raise ValueError("KEYWORDS filter must have a value with 'text' set.")
            keywords_value = _validate_keywords_text(values[0]["text"])
        else:
            regular_filters.append(f)

    filter_strings = [build_filter(f, references_cache) for f in regular_filters]

    # Assemble the top-level query object.
    # Order matches what LinkedIn produces: spellCorrectionEnabled, keywords, then filters.
    query_parts = []
    if keywords_value is not None:
        query_parts.append("spellCorrectionEnabled:true")
        query_parts.append(f"keywords:{inner_encode(keywords_value)}")
    if filter_strings:
        query_parts.append(f"filters:List({','.join(filter_strings)})")

    inner_query = f"({','.join(query_parts)})"
    encoded_query = outer_encode(inner_query)
    return f"https://www.linkedin.com/sales/search/people?query={encoded_query}&viewAllFilters=true"


# ----------------------------------------------------------------------------
# Regression tests against real Sales Nav URLs captured November 2026
# ----------------------------------------------------------------------------

def normalize_url(url):
    """Extract the canonical inner query content (one decode pass, recentSearchParam stripped).

    Returns the full query body (parens included) so we can compare both the
    filters:List(...) shape AND the top-level KEYWORDS shape.
    """
    import re
    m = re.search(r"query=([^&]+)", url)
    if not m:
        return None
    decoded = unquote(m.group(1))  # one decode pass
    # Strip recentSearchParam:(...) — session-scoped, not part of the canonical query
    decoded = re.sub(r"recentSearchParam:\([^)]*\),?", "", decoded)
    # Clean up "(,..." → "(..."
    decoded = re.sub(r"\(,", "(", decoded)
    return decoded


TEST_CASES = [
    {
        "name": "URL 1 — Multi-enum filters with include/exclude",
        "spec": {
            "filters": [
                {
                    "type": "INDUSTRY",
                    "values": [
                        {"id": 4, "selectionType": "INCLUDED"},
                        {"id": 96, "selectionType": "INCLUDED"},
                        {"id": 104, "selectionType": "EXCLUDED"},
                    ],
                },
                {
                    "type": "FUNCTION",
                    "values": [
                        {"id": 25, "selectionType": "INCLUDED"},
                        {"id": 15, "selectionType": "INCLUDED"},
                    ],
                },
                {
                    "type": "SENIORITY_LEVEL",
                    "values": [
                        {"id": 310, "selectionType": "INCLUDED"},
                        {"id": 220, "selectionType": "INCLUDED"},
                        {"id": 300, "selectionType": "INCLUDED"},
                    ],
                },
                {
                    "type": "COMPANY_HEADCOUNT",
                    "values": [
                        {"id": "D", "selectionType": "INCLUDED"},
                        {"id": "E", "selectionType": "INCLUDED"},
                    ],
                },
                {
                    "type": "REGION",
                    "values": [{"id": 105015875, "selectionType": "INCLUDED"}],
                },
                {
                    "type": "PROFILE_LANGUAGE",
                    "values": [{"id": "fr", "selectionType": "INCLUDED"}],
                },
            ]
        },
        "expected_filters": (
            "(filters:List("
            "(type:INDUSTRY,values:List("
            "(id:4,text:Software%20Development,selectionType:INCLUDED),"
            "(id:96,text:IT%20Services%20and%20IT%20Consulting,selectionType:INCLUDED),"
            "(id:104,text:Staffing%20and%20Recruiting,selectionType:EXCLUDED))),"
            "(type:FUNCTION,values:List("
            "(id:25,text:Sales,selectionType:INCLUDED),"
            "(id:15,text:Marketing,selectionType:INCLUDED))),"
            "(type:SENIORITY_LEVEL,values:List("
            "(id:310,text:CXO,selectionType:INCLUDED),"
            "(id:220,text:Director,selectionType:INCLUDED),"
            "(id:300,text:Vice%20President,selectionType:INCLUDED))),"
            "(type:COMPANY_HEADCOUNT,values:List("
            "(id:D,text:51-200,selectionType:INCLUDED),"
            "(id:E,text:201-500,selectionType:INCLUDED))),"
            "(type:REGION,values:List("
            "(id:105015875,text:France,selectionType:INCLUDED))),"
            "(type:PROFILE_LANGUAGE,values:List("
            "(id:fr,text:French,selectionType:INCLUDED)))"
            "))"
        ),
    },
    {
        "name": "URL 2 — Text filter (FIRST_NAME) + toggles",
        "spec": {
            "filters": [
                {
                    "type": "FIRST_NAME",
                    "values": [{"text": "brice", "selectionType": "INCLUDED"}],
                },
                {"type": "RECENTLY_CHANGED_JOBS", "toggle": True},
                {"type": "POSTED_ON_LINKEDIN", "toggle": True},
                {"type": "PAST_COLLEAGUE", "toggle": True},
                {"type": "FOLLOWS_YOUR_COMPANY", "toggle": True},
            ]
        },
        "expected_filters": (
            "(filters:List("
            "(type:FIRST_NAME,values:List("
            "(text:brice,selectionType:INCLUDED))),"
            "(type:RECENTLY_CHANGED_JOBS,values:List("
            "(id:RPC,text:Changed%20jobs,selectionType:INCLUDED))),"
            "(type:POSTED_ON_LINKEDIN,values:List("
            "(id:RPOL,text:Posted%20on%20LinkedIn,selectionType:INCLUDED))),"
            "(type:PAST_COLLEAGUE,values:List("
            "(id:PCOLL,text:Past%20colleague,selectionType:INCLUDED))),"
            "(type:FOLLOWS_YOUR_COMPANY,values:List("
            "(id:CF,selectionType:INCLUDED)))"
            "))"
        ),
    },
    {
        "name": "URL 3 — CURRENT_TITLE with boolean (verified live)",
        "spec": {
            "filters": [
                {
                    "type": "CURRENT_TITLE",
                    "values": [
                        {
                            "text": "(CMO OR Founder) NOT Fractional",
                            "selectionType": "INCLUDED",
                        }
                    ],
                },
            ]
        },
        "expected_filters": (
            "(filters:List("
            "(type:CURRENT_TITLE,values:List("
            "(text:%28CMO%20OR%20Founder%29%20NOT%20Fractional,selectionType:INCLUDED)))"
            "))"
        ),
    },
    {
        "name": "URL 4 — PAST_TITLE with boolean (verified live)",
        "spec": {
            "filters": [
                {
                    "type": "PAST_TITLE",
                    "values": [
                        {
                            "text": "(CMO OR Founder) NOT Fractional",
                            "selectionType": "INCLUDED",
                        }
                    ],
                },
            ]
        },
        "expected_filters": (
            "(filters:List("
            "(type:PAST_TITLE,values:List("
            "(text:%28CMO%20OR%20Founder%29%20NOT%20Fractional,selectionType:INCLUDED)))"
            "))"
        ),
    },
    {
        "name": "URL 5 — KEYWORDS top-level (verified live, with spellCorrectionEnabled)",
        "spec": {
            "filters": [
                {
                    "type": "KEYWORDS",
                    "values": [
                        {
                            "text": "(CMO OR Founder) NOT Fractional",
                            "selectionType": "INCLUDED",
                        }
                    ],
                },
            ]
        },
        "expected_filters": (
            "(spellCorrectionEnabled:true,"
            "keywords:%28CMO%20OR%20Founder%29%20NOT%20Fractional)"
        ),
    },
    {
        "name": "URL 6 — REGION with multiple countries (France + Germany)",
        "spec": {
            "filters": [
                {
                    "type": "REGION",
                    "values": [
                        {"id": 105015875, "selectionType": "INCLUDED"},
                        {"id": 101282230, "selectionType": "INCLUDED"},
                    ],
                },
            ]
        },
        "expected_filters": (
            "(filters:List("
            "(type:REGION,values:List("
            "(id:105015875,text:France,selectionType:INCLUDED),"
            "(id:101282230,text:Germany,selectionType:INCLUDED)))"
            "))"
        ),
    },
    {
        "name": "URL 7 — REGION from geo-cache (dynamically resolved location)",
        "needs_geo_cache": True,
        "spec": {
            "filters": [
                {
                    "type": "REGION",
                    "values": [
                        {"id": 105080838, "selectionType": "INCLUDED"}
                    ],
                },
            ]
        },
        "expected_filters": (
            "(filters:List("
            "(type:REGION,values:List("
            "(id:105080838,text:New%20York%2C%20United%20States,selectionType:INCLUDED)))"
            "))"
        ),
    },
]


def run_tests():
    print("Running regression tests against captured Sales Nav URLs...\n")

    # Seed a temporary geo-cache for tests that need dynamically resolved locations.
    geo_cache_entry = [{"id": 105080838, "displayValue": "New York, United States"}]
    import tempfile
    tmp_dir = Path(tempfile.mkdtemp())
    tmp_cache = tmp_dir / "geo-cache.json"
    tmp_cache.write_text(json.dumps(geo_cache_entry), encoding="utf-8")
    old_env = os.environ.get("SALES_NAV_GEO_CACHE")
    os.environ["SALES_NAV_GEO_CACHE"] = str(tmp_cache)

    all_passed = True
    for tc in TEST_CASES:
        try:
            url = build_url(tc["spec"])
            actual_filters = normalize_url(url)
            if actual_filters == tc["expected_filters"]:
                print(f"  PASS  {tc['name']}")
            else:
                all_passed = False
                print(f"  FAIL  {tc['name']}")
                print(f"    Expected: {tc['expected_filters']}")
                print(f"    Got:      {actual_filters}")
        except Exception as e:
            all_passed = False
            print(f"  ERROR {tc['name']}: {e}")

    # Clean up temp geo-cache.
    if old_env is not None:
        os.environ["SALES_NAV_GEO_CACHE"] = old_env
    else:
        os.environ.pop("SALES_NAV_GEO_CACHE", None)
    tmp_cache.unlink(missing_ok=True)
    tmp_dir.rmdir()

    print()
    if all_passed:
        print("All tests passed. The URL encoding matches what Sales Nav expects.")
        return 0
    else:
        print("Some tests failed. The URL encoding may need to be updated.")
        return 1


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--test":
        return run_tests()

    # Read spec from stdin if first arg is "-", otherwise from file
    if args[0] == "-":
        try:
            spec = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON on stdin: {e}", file=sys.stderr)
            return 1
    else:
        spec_path = Path(args[0])
        if not spec_path.exists():
            print(f"Error: spec file not found: {spec_path}", file=sys.stderr)
            return 1
        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)

    try:
        url = build_url(spec)
        print(url)
        return 0
    except Exception as e:
        print(f"Error building URL: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
