#!/usr/bin/env python3
"""
Check the upstream sources a skill was built from for changes.

Reads a manifest (e.g. upstream/human-content.json) listing GitHub paths and
web pages. For each GitHub source it compares the latest commit touching the
path against `last_sha` and collects the patch. For each web page it hashes
the visible text and keeps a snapshot under upstream/snapshots/, so a change
shows up as a normal git diff in the resulting PR.

Writes a markdown report of every change and, with --update, moves the
manifest's baselines forward. Stdlib only. Uses GITHUB_TOKEN when set.

Exit codes: 0 = ran (changed or not), 1 = a source could not be checked.

Usage:
  python scripts/check_upstream.py upstream/human-content.json \
      --report report.md [--update]
"""

import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = REPO_ROOT / "upstream" / "snapshots"
PATCH_LIMIT = 60_000  # chars per source; keeps the report readable for the model


def http_get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    headers = {"Accept": accept, "User-Agent": "nickautomations-upstream-check"}
    token = os.getenv("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        return resp.read()


def gh_json(endpoint: str):
    return json.loads(http_get(f"https://api.github.com/{endpoint}"))


def check_github(src: dict) -> dict | None:
    repo, path, last = src["repo"], src["path"], src["last_sha"]
    commits = gh_json(f"repos/{repo}/commits?path={path}&per_page=1")
    latest = commits[0]["sha"]
    if latest == last:
        return None

    compare = gh_json(f"repos/{repo}/compare/{last}...{latest}")
    messages = [
        f"- `{c['sha'][:7]}` {c['commit']['message'].splitlines()[0]}"
        for c in compare.get("commits", [])
    ]
    patches = []
    for f in compare.get("files", []):
        if f["filename"] == path or f["filename"].startswith(path.rstrip("/") + "/"):
            patch = f.get("patch", "(binary or too large — open the compare link)")
            patches.append(f"#### {f['filename']} ({f['status']})\n\n```diff\n{patch}\n```")
    body = "\n\n".join(patches) or "_Commits touched the path but no textual patch was returned._"
    if len(body) > PATCH_LIMIT:
        body = body[:PATCH_LIMIT] + "\n\n_…truncated; open the compare link for the rest._"

    return {
        "new_baseline": {"last_sha": latest},
        "report": (
            f"### {src['id']} — `{repo}/{path}`\n\n"
            f"Compare: https://github.com/{repo}/compare/{last[:12]}...{latest[:12]}\n\n"
            + "\n".join(messages) + "\n\n" + body
        ),
    }


def page_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|h[1-6]|li|tr|section|article)>", "\n", text)
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", text))
    lines = (re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines())
    return "\n".join(line for line in lines if line) + "\n"


def check_web(src: dict) -> dict | None:
    text = page_text(http_get(src["url"], accept="text/html"))
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    snapshot = SNAPSHOT_DIR / f"{src['id']}.txt"
    if digest == src.get("last_hash"):
        return None

    first_run = not src.get("last_hash")
    return {
        "new_baseline": {"last_hash": digest},
        "snapshot": (snapshot, text),
        "report": (
            f"### {src['id']} — {src['url']}\n\n"
            + ("_First snapshot recorded; nothing to compare yet._"
               if first_run else
               f"Page text changed. See the diff of `upstream/snapshots/{snapshot.name}` in this PR.")
        ),
        "baseline_only": first_run,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--report", required=True)
    ap.add_argument("--update", action="store_true", help="move baselines forward and write snapshots")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sections, failures, changed = [], [], False

    for src in manifest["sources"]:
        checker = check_github if src["type"] == "github" else check_web
        try:
            result = checker(src)
        except Exception as exc:  # one broken source must not hide the others
            failures.append(f"- {src['id']}: {exc}")
            continue
        if not result:
            print(f"unchanged  {src['id']}")
            continue
        print(f"CHANGED    {src['id']}")
        if not result.get("baseline_only"):
            changed = True
            sections.append(result["report"])
        if args.update:
            src.update(result["new_baseline"])
            if "snapshot" in result:
                path, text = result["snapshot"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

    if args.update:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    report = f"# Upstream changes for `{manifest['skill']}`\n\n"
    report += "\n\n".join(sections) if sections else "No content changes.\n"
    if failures:
        report += "\n\n## Sources that could not be checked\n\n" + "\n".join(failures)
    Path(args.report).write_text(report + "\n", encoding="utf-8")

    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write(f"changed={'true' if changed else 'false'}\n")
            fh.write(f"baseline_moved={'true' if args.update else 'false'}\n")

    print(f"\nchanged={changed}  report={args.report}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
