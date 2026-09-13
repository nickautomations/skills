---
type: llm
weight: 2
---

PASS if the response identifies at least 4 distinct, specific patterns (for example: sales language like "nestled in the heart of", inflated importance like "stands as a beacon" or "pivotal role", weasel attribution "experts agree", a "doesn't just X, we Y" contrast, a trailing "-ing" phrase like "highlighting our commitment", filler buzzwords like "seamless" or "state-of-the-art"), and for each one quotes the offending wording from the text and says briefly how to fix it.

FAIL if it gives a general impression ("it sounds robotic", "too formal") without quoting specific wording, or names fewer than 4 patterns.
