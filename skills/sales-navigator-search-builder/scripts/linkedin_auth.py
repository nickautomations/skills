"""LinkedIn three-legged OAuth with optional programmatic token refresh."""

from __future__ import annotations

import json
import os
import secrets
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv


AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
TOKEN_EXPIRY_SKEW_SECONDS = 300


def auth_command() -> str:
    """The exact re-authorization command for this machine.

    Built from sys.executable and the real script path, so the message names an
    interpreter that is known to exist here rather than guessing between
    "python", "python3" and "py -3".
    """
    return f"{sys.executable} {Path(__file__).resolve().parent / 'resolve_geo.py'} --auth"


class OAuthError(RuntimeError):
    """LinkedIn OAuth failed."""


class ReauthorizationRequired(OAuthError):
    """No valid access token can be obtained without authorization."""


@dataclass(frozen=True)
class OAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: tuple[str, ...]
    callback_host: str = "127.0.0.1"
    callback_port: int = 8765

    @classmethod
    def from_env(cls, env_file: str | Path | None = None) -> "OAuthConfig":
        load_dotenv(dotenv_path=env_file)
        scopes = tuple(filter(None, os.getenv("LINKEDIN_SCOPES", "").split()))
        config = cls(
            client_id=os.getenv("LINKEDIN_CLIENT_ID", "").strip(),
            client_secret=os.getenv("LINKEDIN_CLIENT_SECRET", "").strip(),
            redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", "").strip(),
            scopes=scopes,
            callback_host=os.getenv("LINKEDIN_CALLBACK_HOST", "127.0.0.1"),
            callback_port=int(os.getenv("LINKEDIN_CALLBACK_PORT", "8765")),
        )
        missing = [
            name
            for name, value in (
                ("LINKEDIN_CLIENT_ID", config.client_id),
                ("LINKEDIN_CLIENT_SECRET", config.client_secret),
                ("LINKEDIN_REDIRECT_URI", config.redirect_uri),
                ("LINKEDIN_SCOPES", config.scopes),
            )
            if not value
        ]
        if missing:
            raise OAuthError(f"Missing required configuration: {', '.join(missing)}")
        redirect = urlparse(config.redirect_uri)
        if redirect.scheme != "https" or not redirect.netloc or redirect.fragment:
            raise OAuthError(
                "LINKEDIN_REDIRECT_URI must be an absolute HTTPS URL without a fragment"
            )
        return config


class TokenStore:
    def __init__(self, path: str | Path = ".linkedin_token.json") -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, token: dict[str, Any], previous: dict[str, Any] | None = None) -> None:
        now = int(time.time())
        merged = dict(previous or {})
        merged.update(token)
        merged["obtained_at"] = now
        merged["expires_at"] = now + int(token.get("expires_in", 0))
        if "refresh_token_expires_in" in token:
            merged["refresh_token_expires_at"] = now + int(
                token["refresh_token_expires_in"]
            )

        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(json.dumps(merged, indent=2), encoding="utf-8")
        os.replace(temporary, self.path)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass


class LinkedInOAuth:
    def __init__(
        self,
        config: OAuthConfig,
        token_store: TokenStore | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.config = config
        self.token_store = token_store or TokenStore()
        self.session = session or requests.Session()

    def authorization_url(self, state: str) -> str:
        return f"{AUTHORIZE_URL}?{urlencode({
            'response_type': 'code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'state': state,
            'scope': ' '.join(self.config.scopes),
        })}"

    def exchange_code(self, code: str) -> dict[str, Any]:
        return self._token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "redirect_uri": self.config.redirect_uri,
            }
        )

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        return self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            }
        )

    def _token_request(self, data: dict[str, str]) -> dict[str, Any]:
        try:
            response = self.session.post(TOKEN_URL, data=data, timeout=30)
        except requests.RequestException as exc:
            raise OAuthError(f"Could not reach LinkedIn token endpoint: {exc}") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise OAuthError(
                f"LinkedIn token endpoint returned HTTP {response.status_code} with non-JSON content"
            ) from exc
        if not response.ok:
            description = payload.get("error_description") or payload.get("message") or payload
            if data.get("grant_type") == "refresh_token" and response.status_code == 400:
                normalized = str(description).lower()
                if any(word in normalized for word in ("invalid", "expired", "revoked")):
                    raise ReauthorizationRequired(
                        "The LinkedIn refresh token is invalid, expired, or revoked. "
                        f"Run: {auth_command()}"
                    )
            raise OAuthError(f"LinkedIn token request failed ({response.status_code}): {description}")
        if "access_token" not in payload:
            raise OAuthError("LinkedIn token response did not contain access_token")
        return payload

    def save_token(self, token: dict[str, Any]) -> None:
        # A new authorization grant replaces the old token family. In particular,
        # do not retain an old refresh token if LinkedIn did not return one now.
        self.token_store.save(token)

    def valid_access_token(self) -> str:
        direct_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
        if direct_token:
            return direct_token

        token = self.token_store.load()
        if not token or "access_token" not in token:
            raise ReauthorizationRequired(f"No cached access token. Run: {auth_command()}")

        now = int(time.time())
        if int(token.get("expires_at", 0)) > now + TOKEN_EXPIRY_SKEW_SECONDS:
            return str(token["access_token"])

        refresh_token = token.get("refresh_token")
        refresh_expiry = int(token.get("refresh_token_expires_at", now + 1))
        if refresh_token and refresh_expiry > now + TOKEN_EXPIRY_SKEW_SECONDS:
            refreshed = self.refresh(str(refresh_token))
            self.token_store.save(refreshed, previous=token)
            return str(refreshed["access_token"])

        raise ReauthorizationRequired(
            "The access token is expired or near expiry and this app has no valid "
            f"programmatic refresh token. Run: {auth_command()}"
        )

    def authenticate_with_pasted_redirect(self, open_browser: bool = True) -> dict[str, Any]:
        state = secrets.token_urlsafe(32)
        url = self.authorization_url(state)
        print("Open this LinkedIn authorization URL:\n")
        print(url)
        if open_browser:
            webbrowser.open(url)
        redirected_url = input("\nPaste the complete final redirect URL: ").strip()
        code = self._parse_callback(redirected_url, state)
        token = self.exchange_code(code)
        self.save_token(token)
        return token

    def authenticate_with_callback_server(
        self, open_browser: bool = True, timeout_seconds: int = 300
    ) -> dict[str, Any]:
        state = secrets.token_urlsafe(32)
        callback: dict[str, str] = {}
        completed = threading.Event()
        oauth = self

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                expected_path = urlparse(oauth.config.redirect_uri).path or "/"
                if parsed.path != expected_path:
                    self.send_error(404)
                    return
                callback["url"] = f"{oauth.config.redirect_uri.split('?', 1)[0]}?{parsed.query}"
                try:
                    oauth._parse_callback(callback["url"], state)
                    status, message = 200, "LinkedIn authorization received. You can close this tab."
                except OAuthError as exc:
                    status, message = 401, str(exc)
                    returned_state = parse_qs(parsed.query).get("state", [""])[0]
                    if secrets.compare_digest(returned_state, state):
                        callback["error"] = str(exc)
                        completed.set()
                self.send_response(status)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(message.encode("utf-8"))
                if status == 200:
                    completed.set()

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(
            (self.config.callback_host, self.config.callback_port), CallbackHandler
        )
        server.timeout = 1
        url = self.authorization_url(state)
        print(
            f"Listening on http://{self.config.callback_host}:{self.config.callback_port}.\n"
            "Your registered HTTPS redirect URI must forward to this listener.\n\n"
            f"Open this URL if the browser does not open automatically:\n{url}\n"
        )
        if open_browser:
            webbrowser.open(url)

        deadline = time.monotonic() + timeout_seconds
        try:
            while not completed.is_set() and time.monotonic() < deadline:
                server.handle_request()
        finally:
            server.server_close()
        if not completed.is_set():
            raise OAuthError("Timed out waiting for LinkedIn callback")
        if "error" in callback:
            raise OAuthError(callback["error"])
        code = self._parse_callback(callback["url"], state)
        token = self.exchange_code(code)
        self.save_token(token)
        return token

    @staticmethod
    def _parse_callback(url: str, expected_state: str) -> str:
        query = parse_qs(urlparse(url).query)
        returned_state = query.get("state", [""])[0]
        if not secrets.compare_digest(returned_state, expected_state):
            raise OAuthError("OAuth state mismatch; authorization was rejected")
        if "error" in query:
            description = query.get("error_description", query["error"])[0]
            raise OAuthError(f"LinkedIn authorization failed: {description}")
        code = query.get("code", [""])[0]
        if not code:
            raise OAuthError("Callback URL did not contain an authorization code")
        return code
