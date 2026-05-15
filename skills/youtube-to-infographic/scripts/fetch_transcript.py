#!/usr/bin/env python3
"""
Fetch a YouTube transcript via the RapidAPI yt-api service.

Usage:
    RAPIDAPI_KEY=xxx python fetch_transcript.py <youtube_url>

Outputs (stdout): JSON with the shape:
    {
        "success": true,
        "videoId": "...",
        "title": "...",            # if available
        "channel": "...",          # if available
        "fullText": "...",         # the spoken transcript joined
        "segments": [              # individual subtitle entries
            {"start": 0.0, "duration": 5.36, "text": "..."},
            ...
        ]
    }

On failure, prints a JSON error to stdout and exits with code 1:
    {"success": false, "error": "..."}

Requires: RAPIDAPI_KEY environment variable.
Subscription: https://rapidapi.com/ytjar/api/yt-api
"""

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

RAPIDAPI_HOST = "yt-api.p.rapidapi.com"


def extract_video_id(url_or_id: str) -> str | None:
    """Pull the 11-char video ID out of any common YouTube URL form, or pass through if already an ID."""
    s = url_or_id.strip()

    # If it looks like a bare video ID already (11 chars, alphanumeric + - _), use it
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s

    # Standard watch URL
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)

    # youtu.be short URL
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)

    # Shorts URL
    m = re.search(r"/shorts/([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)

    # Embed URL
    m = re.search(r"/embed/([A-Za-z0-9_-]{11})", s)
    if m:
        return m.group(1)

    return None


def call_rapidapi(path: str, params: dict, api_key: str) -> dict:
    """Make a GET request to the RapidAPI host. Returns parsed JSON or raises."""
    qs = urllib.parse.urlencode(params)
    url = f"https://{RAPIDAPI_HOST}{path}?{qs}"
    req = urllib.request.Request(
        url,
        headers={
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": api_key,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)


def normalize_subtitles(raw: dict) -> tuple[str, list[dict]]:
    """
    The yt-api subtitles endpoint returns a structure that varies a bit by request.
    Common shapes:
      {"subtitles": [{"start": "0.08", "dur": "5.36", "text": "..."}, ...]}
      {"events": [...]}
      {"transcript": [...]}
    Normalize to (fullText, segments) regardless of which one came back.
    """
    candidates = []
    for key in ("subtitles", "transcript", "events", "captions"):
        if isinstance(raw.get(key), list):
            candidates = raw[key]
            break

    if not candidates:
        # Sometimes the response is just a list at the top level
        if isinstance(raw, list):
            candidates = raw

    segments = []
    text_parts = []
    for entry in candidates:
        if not isinstance(entry, dict):
            continue
        text = entry.get("text") or entry.get("snippet") or ""
        if not text:
            continue
        try:
            start = float(entry.get("start", entry.get("startTime", 0)))
        except (TypeError, ValueError):
            start = 0.0
        try:
            duration = float(entry.get("dur", entry.get("duration", 0)))
        except (TypeError, ValueError):
            duration = 0.0

        segments.append({"start": start, "duration": duration, "text": text})
        text_parts.append(text)

    full_text = " ".join(t.strip() for t in text_parts if t.strip())
    return full_text, segments


def fetch_video_info(video_id: str, api_key: str) -> dict:
    """Try to get title and channel name. Best-effort — returns {} if it fails."""
    try:
        data = call_rapidapi("/video/info", {"id": video_id}, api_key)
    except Exception:
        return {}

    info = {}
    if isinstance(data, dict):
        title = data.get("title")
        if isinstance(title, str):
            info["title"] = title
        channel = data.get("channelTitle") or data.get("channel") or data.get("author")
        if isinstance(channel, str):
            info["channel"] = channel
    return info


def main() -> int:
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: fetch_transcript.py <youtube_url>"}))
        return 1

    api_key = os.environ.get("RAPIDAPI_KEY", "").strip()
    if not api_key:
        print(json.dumps({
            "success": False,
            "error": "RAPIDAPI_KEY environment variable is not set. Subscribe to yt-api at https://rapidapi.com/ytjar/api/yt-api and export RAPIDAPI_KEY=your_key."
        }))
        return 1

    url_or_id = sys.argv[1]
    video_id = extract_video_id(url_or_id)
    if not video_id:
        print(json.dumps({"success": False, "error": f"Could not extract a YouTube video ID from: {url_or_id}"}))
        return 1

    # Fetch subtitles
    try:
        subs = call_rapidapi("/subtitles", {"id": video_id}, api_key)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        print(json.dumps({
            "success": False,
            "error": f"RapidAPI returned HTTP {e.code}: {body[:300]}",
            "videoId": video_id,
        }))
        return 1
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Network error: {e}", "videoId": video_id}))
        return 1

    full_text, segments = normalize_subtitles(subs)

    if not full_text:
        print(json.dumps({
            "success": False,
            "error": "No transcript content was returned. The video may have captions disabled, or the API response shape is unexpected.",
            "videoId": video_id,
            "raw_keys": list(subs.keys()) if isinstance(subs, dict) else None,
        }))
        return 1

    # Best-effort metadata
    meta = fetch_video_info(video_id, api_key)

    result = {
        "success": True,
        "videoId": video_id,
        "title": meta.get("title"),
        "channel": meta.get("channel"),
        "segmentCount": len(segments),
        "fullText": full_text,
        "segments": segments,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
