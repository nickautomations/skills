#!/usr/bin/env python3
"""
Render a before/after table from two `claude plugin eval --json` results.

Each case is scored 0..1 per run by LLM and deterministic graders, so a
single failed run in three moves a case by ~0.1 with no real change. A case
is flagged only when its score drops by FLAG_DROP or more.

Usage:
  python scripts/eval_compare.py before.json after.json > eval.md
"""

import json
import sys

FLAG_DROP = 0.2


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def failures(case: dict) -> str:
    counts: dict[str, int] = {}
    runs = case["arms"].get("with", [])
    for run in runs:
        for grader in run["graders"]:
            if grader.get("scored") and not grader["passed"]:
                counts[grader["name"]] = counts.get(grader["name"], 0) + 1
    return ", ".join(f"{name} ({n}/{len(runs)})" for name, n in sorted(counts.items())) or "—"


def main() -> int:
    before, after = load(sys.argv[1]), load(sys.argv[2])
    before_scores = {c["name"]: c["aggregates"]["score"] for c in before["cases"]}

    rows, flagged = [], []
    for case in after["cases"]:
        name, new = case["name"], case["aggregates"]["score"]
        old = before_scores.get(name)
        delta = "new case" if old is None else f"{new - old:+.2f}"
        mark = ""
        if old is not None and old - new >= FLAG_DROP:
            mark = " ⚠️"
            flagged.append(name)
        old_txt = "—" if old is None else f"{old:.2f}"
        rows.append(f"| {name}{mark} | {old_txt} | {new:.2f} | {delta} | {failures(case)} |")

    b, a = before["aggregates"]["overallScore"], after["aggregates"]["overallScore"]
    print("| Case | Before | After | Δ | Failing graders after |")
    print("|---|---|---|---|---|")
    print("\n".join(rows))
    print(f"| **Overall** | **{b:.2f}** | **{a:.2f}** | **{a - b:+.2f}** | |")
    print()
    if flagged:
        print(f"⚠️ Score dropped {FLAG_DROP} or more on: {', '.join(flagged)}. Check those graders before merging.")
    else:
        print(f"No case dropped {FLAG_DROP} or more. Smaller moves are judge noise at 3 runs per case.")
    print(f"\nEval cost: before ${before['costUsd']:.2f}, after ${after['costUsd']:.2f}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
