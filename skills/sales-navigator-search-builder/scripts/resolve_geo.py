#!/usr/bin/env python3
"""
LinkedIn Geo Typeahead Resolver

Resolves free-text location names (cities, states, metros) to LinkedIn geo URN IDs
via the LinkedIn Typeahead API. Results are cached locally so repeat lookups work
offline. Falls back gracefully when no LinkedIn credentials are configured.

Usage (invoke with your Python 3 launcher: `py -3` on Windows, `python3` on macOS/Linux):
    python scripts/resolve_geo.py "Austin, Texas"          # resolve (human-readable)
    python scripts/resolve_geo.py "Austin, Texas" --json   # resolve (JSON)
    python scripts/resolve_geo.py "Austin, Texas" --refresh # bypass cache
    python scripts/resolve_geo.py --auth                   # run OAuth flow
    python scripts/resolve_geo.py --auth-status            # show token status
    python scripts/resolve_geo.py --test                   # run offline tests
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent

GEO_TYPEAHEAD_URL = "https://api.linkedin.com/rest/geoTypeahead"

sys.path.insert(0, str(SCRIPT_DIR))
from linkedin_auth import (  # noqa: E402
    auth_command,
    LinkedInOAuth,
    OAuthConfig,
    OAuthError,
    ReauthorizationRequired,
    TokenStore,
)


class GeoResolverError(RuntimeError):
    """Base error for geo resolution."""


class GeoNotConfigured(GeoResolverError):
    """No LinkedIn credentials found — skill falls back to static regions.json."""


class GeoAuthRequired(GeoResolverError):
    """Token expired or missing — user needs to run --auth."""


class GeoNoMatch(GeoResolverError):
    """Typeahead returned no results for the query."""


class GeoAPIError(GeoResolverError):
    """Network or API error during typeahead lookup."""


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _user_data_dir() -> Path:
    """Per-user writable directory, platform-aware."""
    override = os.getenv("SALES_NAV_DATA_HOME")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / "sales-nav-builder"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "sales-nav-builder"
    return Path(os.getenv("XDG_DATA_HOME", "~/.local/share")).expanduser() / "sales-nav-builder"


def _config_paths() -> tuple[Path, Path, Path]:
    """Return (.env_path, token_path, geo_cache_path)."""
    user_dir = _user_data_dir()
    user_dir.mkdir(parents=True, exist_ok=True)

    # SALES_NAV_ENV_FILE pins the .env location. Without it the skill root wins
    # unconditionally, which also makes it impossible to run against a clean
    # configuration once a real .env exists — the offline tests need exactly that.
    env_override = os.getenv("SALES_NAV_ENV_FILE")
    if env_override:
        env_path = Path(env_override)
    else:
        env_candidates = [SKILL_ROOT / ".env", user_dir / ".env"]
        env_path = next((p for p in env_candidates if p.exists()), env_candidates[0])

    token_path = Path(os.getenv("LINKEDIN_TOKEN_FILE", str(user_dir / ".linkedin_token.json")))
    cache_path = Path(os.getenv("SALES_NAV_GEO_CACHE", str(user_dir / "geo-cache.json")))

    return env_path, token_path, cache_path


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

def _normalize_query(q: str) -> str:
    """Normalize a location query for cache matching."""
    return re.sub(r"\s+", " ", q.strip().lower())


def _load_cache(path: Path) -> list[dict[str, Any]]:
    """Load geo-cache.json. Returns [] on missing or corrupt file."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (OSError, ValueError):
        pass
    return []


def _save_cache(path: Path, entries: list[dict[str, Any]]) -> None:
    """Atomically write the cache file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _cache_lookup(entries: list[dict[str, Any]], query: str) -> dict[str, Any] | None:
    """Find a cache entry matching the query by displayValue or alias."""
    normalized = _normalize_query(query)
    for entry in entries:
        if _normalize_query(entry.get("displayValue", "")) == normalized:
            return entry
        for alias in entry.get("aliases", []):
            if _normalize_query(alias) == normalized:
                return entry
    return None


# ---------------------------------------------------------------------------
# Credentials check
# ---------------------------------------------------------------------------

def _credentials_available(env_path: Path, token_path: Path) -> bool:
    """Check whether LinkedIn credentials exist anywhere."""
    if os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip():
        return True
    if env_path.exists():
        return True
    if token_path.exists():
        return True
    return False


# ---------------------------------------------------------------------------
# Typeahead client
# ---------------------------------------------------------------------------

class GeoTypeaheadClient:
    """Thin wrapper around the LinkedIn Geo Typeahead API."""

    def __init__(self, access_token: str, api_version: str = "202607",
                 session: requests.Session | None = None) -> None:
        self.session = session or requests.Session()
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "X-RestLi-Protocol-Version": "2.0.0",
            "Linkedin-Version": api_version,
        }

    def search(self, query: str) -> list[dict[str, Any]]:
        params = {"q": "search", "query": query}
        try:
            resp = self.session.get(
                GEO_TYPEAHEAD_URL, params=params, headers=self.headers, timeout=30
            )
        except requests.RequestException as exc:
            raise GeoAPIError(f"Could not reach LinkedIn Typeahead API: {exc}") from exc

        if resp.status_code == 401:
            raise GeoAuthRequired(
                "LinkedIn returned 401. The access token may be expired or revoked."
            )
        if resp.status_code == 403:
            raise GeoAPIError(
                "LinkedIn returned 403. Confirm the app has the r_ads scope and "
                "the Typeahead product enabled."
            )
        if resp.status_code == 429:
            raise GeoAPIError("LinkedIn rate limit reached. Wait before retrying.")
        if not resp.ok:
            try:
                msg = resp.json().get("message", resp.text[:200])
            except ValueError:
                msg = resp.text[:200]
            raise GeoAPIError(f"Typeahead request failed ({resp.status_code}): {msg}")

        try:
            data = resp.json()
        except ValueError as exc:
            raise GeoAPIError("Typeahead returned non-JSON content") from exc

        results = []
        for el in data.get("elements", []):
            urn = el.get("entity", "")
            urn_id_str = urn.rsplit(":", 1)[-1] if urn else ""
            if not urn_id_str.isdigit():
                continue
            results.append({
                "id": int(urn_id_str),
                "displayValue": el.get("displayText", ""),
                "urn": urn,
            })
        return results


# ---------------------------------------------------------------------------
# Core resolve function
# ---------------------------------------------------------------------------

def resolve(query: str, *, force_refresh: bool = False) -> dict[str, Any]:
    """Resolve a location name to a geo URN. Returns a result dict.

    Raises GeoNotConfigured, GeoAuthRequired, GeoNoMatch, or GeoAPIError.
    """
    env_path, token_path, cache_path = _config_paths()

    if not force_refresh:
        cache_entries = _load_cache(cache_path)
        hit = _cache_lookup(cache_entries, query)
        if hit is not None:
            return {
                "id": hit["id"],
                "displayValue": hit["displayValue"],
                "urn": f"urn:li:geo:{hit['id']}",
                "source": "cache",
                "cached": True,
                "alternatives": [],
            }

    if not _credentials_available(env_path, token_path):
        raise GeoNotConfigured(
            "No LinkedIn credentials configured. Copy .env.example to .env and run "
            f"'{auth_command()}', or set LINKEDIN_ACCESS_TOKEN."
        )

    load_dotenv(dotenv_path=env_path)
    direct_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
    if direct_token:
        access_token = direct_token
    else:
        config = OAuthConfig.from_env(env_path)
        oauth = LinkedInOAuth(config, TokenStore(token_path))
        try:
            access_token = oauth.valid_access_token()
        except ReauthorizationRequired as exc:
            raise GeoAuthRequired(str(exc)) from exc
        except OAuthError as exc:
            raise GeoNotConfigured(str(exc)) from exc

    api_version = os.getenv("LINKEDIN_API_VERSION", "202607")
    client = GeoTypeaheadClient(access_token, api_version)
    results = client.search(query)

    if not results:
        raise GeoNoMatch(f"No location matched '{query}'.")

    best = results[0]
    alternatives = results[1:]

    cache_entries = _load_cache(cache_path)
    new_entry = {
        "id": best["id"],
        "displayValue": best["displayValue"],
        "aliases": [_normalize_query(query)],
        "resolved_at": int(time.time()),
        "source": "typeahead",
    }

    existing_ids = {e["id"] for e in cache_entries if "id" in e}
    if new_entry["id"] not in existing_ids:
        cache_entries.append(new_entry)
        _save_cache(cache_path, cache_entries)

    return {
        "id": best["id"],
        "displayValue": best["displayValue"],
        "urn": best["urn"],
        "source": "typeahead",
        "cached": False,
        "alternatives": [
            {"id": a["id"], "displayValue": a["displayValue"], "urn": a["urn"]}
            for a in alternatives
        ],
    }


# ---------------------------------------------------------------------------
# Auth subcommands
# ---------------------------------------------------------------------------

def run_auth(mode: str = "paste") -> None:
    """Run the OAuth flow to obtain an access token."""
    env_path, token_path, _ = _config_paths()
    load_dotenv(dotenv_path=env_path)
    config = OAuthConfig.from_env(env_path)
    oauth = LinkedInOAuth(config, TokenStore(token_path))

    if mode == "callback":
        oauth.authenticate_with_callback_server(open_browser=True)
    else:
        oauth.authenticate_with_pasted_redirect(open_browser=True)
    print(f"\nToken saved to {token_path}")


def show_auth_status() -> None:
    """Show token expiry without revealing the token."""
    _, token_path, _ = _config_paths()
    if not token_path.exists():
        print(f"No token file found. Run '{auth_command()}' first.")
        return
    token = json.loads(token_path.read_text(encoding="utf-8"))
    now = int(time.time())
    scope = token.get("scope", "?")
    expires_at = token.get("expires_at", 0)
    refresh_expires_at = token.get("refresh_token_expires_at", 0)

    access_status = "valid" if expires_at > now else "EXPIRED"
    refresh_status = "valid" if refresh_expires_at > now else "EXPIRED"
    access_days = max(0, (expires_at - now)) // 86400
    refresh_days = max(0, (refresh_expires_at - now)) // 86400

    print(f"Token file:  {token_path}")
    print(f"Scope:       {scope}")
    print(f"Access:      {access_status} ({access_days} days remaining)")
    print(f"Refresh:     {refresh_status} ({refresh_days} days remaining)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    if args[0] == "--test":
        return run_tests()

    if args[0] == "--auth-status":
        show_auth_status()
        return 0

    if args[0] == "--auth":
        mode = "paste"
        if "--mode" in args:
            idx = args.index("--mode")
            if idx + 1 < len(args):
                mode = args[idx + 1]
        try:
            run_auth(mode)
        except OAuthError as exc:
            print(f"Auth failed: {exc}", file=sys.stderr)
            return 1
        return 0

    # Location resolution mode
    force_refresh = "--refresh" in args
    as_json = "--json" in args
    query_args = [a for a in args if a not in ("--refresh", "--json")]
    if not query_args:
        print("Error: provide a location name to resolve.", file=sys.stderr)
        return 1
    query = " ".join(query_args)

    try:
        result = resolve(query, force_refresh=force_refresh)
    except GeoNotConfigured as exc:
        print(f"Not configured: {exc}", file=sys.stderr)
        return 2
    except GeoAuthRequired as exc:
        print(f"Auth required: {exc}", file=sys.stderr)
        print(f"Run: {auth_command()}", file=sys.stderr)
        return 3
    except GeoNoMatch as exc:
        print(f"No match: {exc}", file=sys.stderr)
        return 4
    except GeoAPIError as exc:
        print(f"API error: {exc}", file=sys.stderr)
        return 5

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Resolved: {result['displayValue']}")
        print(f"ID:       {result['id']}")
        print(f"URN:      {result['urn']}")
        print(f"Source:   {result['source']}{' (cached)' if result['cached'] else ''}")
        if result["alternatives"]:
            print(f"\nAlternatives (stderr):", file=sys.stderr)
            for alt in result["alternatives"]:
                print(f"  {alt['displayValue']}  ->  {alt['urn']}", file=sys.stderr)

    return 0


# ---------------------------------------------------------------------------
# Offline tests
# ---------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, payload: Any, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self) -> Any:
        return self.payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[tuple] = []

    def get(self, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append(("GET", url, kwargs))
        if not self.responses:
            return FakeResponse({}, 500)
        return self.responses.pop(0)


TEST_CASES = [
    {
        "name": "Cache hit skips API",
        "query": "Austin, Texas",
        "cache": [{"id": 103743287, "displayValue": "Austin, Texas Metropolitan Area",
                    "aliases": ["austin, texas"]}],
        "credentials": False,
        "force_refresh": False,
        "expect_source": "cache",
        "expect_id": 103743287,
    },
    {
        "name": "Alias match finds cached entry",
        "query": "nyc",
        "cache": [{"id": 90000070, "displayValue": "New York City Metropolitan Area",
                    "aliases": ["nyc", "new york city"]}],
        "credentials": False,
        "force_refresh": False,
        "expect_source": "cache",
        "expect_id": 90000070,
    },
    {
        "name": "No credentials returns not configured",
        "query": "Berlin",
        "cache": [],
        "credentials": False,
        "force_refresh": False,
        "expect_error": GeoNotConfigured,
    },
    {
        "name": "Corrupt cache returns empty",
        "query": "Paris",
        "cache_raw": "not json at all",
        "credentials": False,
        "force_refresh": False,
        "expect_error": GeoNotConfigured,
    },
    {
        "name": "Typeahead extracts numeric ID from URN",
        "query": "New York",
        "cache": [],
        "credentials": True,
        "force_refresh": True,
        "api_response": FakeResponse({
            "elements": [
                {"displayText": "New York, United States", "entity": "urn:li:geo:105080838"},
                {"displayText": "New York City Metropolitan Area", "entity": "urn:li:geo:90000070"},
            ]
        }),
        "expect_source": "typeahead",
        "expect_id": 105080838,
        "expect_alternatives_count": 1,
    },
    {
        "name": "Empty typeahead response raises no match",
        "query": "Nonexistent Place",
        "cache": [],
        "credentials": True,
        "force_refresh": True,
        "api_response": FakeResponse({"elements": []}),
        "expect_error": GeoNoMatch,
    },
    {
        "name": "403 response includes scope hint",
        "query": "London",
        "cache": [],
        "credentials": True,
        "force_refresh": True,
        "api_response": FakeResponse({"message": "access denied"}, 403),
        "expect_error": GeoAPIError,
        "expect_error_contains": "r_ads",
    },
]


def run_tests() -> int:
    print("Running geo resolver offline tests...\n")
    passed = 0
    failed = 0

    for tc in TEST_CASES:
        import tempfile
        tmp_dir = Path(tempfile.mkdtemp())
        cache_path = tmp_dir / "geo-cache.json"
        token_path = tmp_dir / ".linkedin_token.json"
        env_path = tmp_dir / ".env"

        if "cache" in tc:
            cache_path.write_text(json.dumps(tc["cache"]), encoding="utf-8")
        elif "cache_raw" in tc:
            cache_path.write_text(tc["cache_raw"], encoding="utf-8")

        old_env = {
            k: os.environ.get(k)
            for k in ("SALES_NAV_GEO_CACHE", "SALES_NAV_DATA_HOME", "SALES_NAV_ENV_FILE",
                      "LINKEDIN_TOKEN_FILE", "LINKEDIN_ACCESS_TOKEN")
        }
        os.environ["SALES_NAV_DATA_HOME"] = str(tmp_dir)
        # Pin .env to the temp dir. Without this the developer's own configured
        # .env in the skill root leaks in, and the "no credentials" cases fail on
        # any machine where the skill actually works.
        os.environ["SALES_NAV_ENV_FILE"] = str(env_path)
        os.environ.pop("SALES_NAV_GEO_CACHE", None)
        os.environ.pop("LINKEDIN_TOKEN_FILE", None)
        os.environ.pop("LINKEDIN_ACCESS_TOKEN", None)

        if not tc.get("credentials"):
            pass
        else:
            env_path.write_text(
                "LINKEDIN_CLIENT_ID=test\nLINKEDIN_CLIENT_SECRET=test\n"
                "LINKEDIN_REDIRECT_URI=https://example.com/cb\nLINKEDIN_SCOPES=r_ads\n",
                encoding="utf-8",
            )

        fake_session = None
        if "api_response" in tc:
            fake_session = FakeSession([tc["api_response"]])

        error_expected = tc.get("expect_error")
        result = None
        error_caught = None

        try:
            if fake_session:
                original_client_init = GeoTypeaheadClient.__init__
                def patched_init(self, access_token, api_version="202607", session=None):
                    original_client_init(self, access_token, api_version, fake_session)
                GeoTypeaheadClient.__init__ = patched_init

                original_valid = LinkedInOAuth.valid_access_token
                LinkedInOAuth.valid_access_token = lambda self: "fake_token"

            result = resolve(tc["query"], force_refresh=tc.get("force_refresh", False))

            if fake_session:
                GeoTypeaheadClient.__init__ = original_client_init
                LinkedInOAuth.valid_access_token = original_valid

        except Exception as exc:
            error_caught = exc
            if fake_session:
                try:
                    GeoTypeaheadClient.__init__ = original_client_init
                    LinkedInOAuth.valid_access_token = original_valid
                except NameError:
                    pass

        for k, v in old_env.items():
            if v is not None:
                os.environ[k] = v
            else:
                os.environ.pop(k, None)

        ok = True
        if error_expected:
            if not isinstance(error_caught, error_expected):
                ok = False
            elif "expect_error_contains" in tc:
                if tc["expect_error_contains"].lower() not in str(error_caught).lower():
                    ok = False
        elif result is not None:
            if result.get("source") != tc.get("expect_source"):
                ok = False
            if result.get("id") != tc.get("expect_id"):
                ok = False
            if "expect_alternatives_count" in tc:
                if len(result.get("alternatives", [])) != tc["expect_alternatives_count"]:
                    ok = False
        else:
            ok = False

        if ok:
            print(f"  PASS  {tc['name']}")
            passed += 1
        else:
            print(f"  FAIL  {tc['name']}")
            if error_caught:
                print(f"    Got error: {type(error_caught).__name__}: {error_caught}")
            elif result:
                print(f"    Got: {json.dumps(result)}")
            else:
                print(f"    Got: no result, no error")
            failed += 1

    print(f"\n{passed} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
