"""Generate sample board data for eyeballing index.html.

Usage, from the repo root:
    python tests/make_fixture.py
    python -m http.server 8000
Open http://localhost:8000/?data=tests/fixtures/ok/leaderboard.json
and the same with thin and skipped in place of ok.
"""
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

CATS = ["money", "money", "time", "life"]
WORDS = ["compliance audit prep", "meal planning", "SOC 2 evidence", "youth sports schedule",
         "Upwork data cleanup", "newsletter repurposing", "Etsy listing copy", "travel itinerary",
         "PRD drafting", "SQL review bot"]


def candidate(i, week, rng):
    scores = {k: rng.randint(m // 3, m) for k, m in build.FACTOR_MAX.items()}
    return {
        "id": f"idea-{i:03d}",
        "title": f"{WORDS[i % len(WORDS)].title()} with Claude #{i}",
        "category": CATS[i % len(CATS)],
        "pitch": "Someone ran this for a few weeks and posted numbers. It maps to skills Stephen already has.",
        "first_step": "Spend one evening building a throwaway version and show it to two people.",
        "scores": scores,
        "total": sum(scores.values()),
        "reasons": {k: f"{k} reason for idea {i}" for k in scores},
        "dollars": {"low": 1000 * (i + 1), "high": 5000 * (i + 1), "basis": "annual"},
        "hours_per_week": rng.randint(1, 20),
        "evidence": [
            {"url": f"https://www.reddit.com/r/ClaudeAI/comments/{week}{i}a", "source": "r/ClaudeAI",
             "date": "2026-10-20", "claim": f"${rng.randint(1, 9)}k MRR"},
            {"url": f"https://news.ycombinator.com/item?id={week[-2:]}{i}", "source": "Hacker News",
             "date": "2026-10-21", "claim": "Show HN thread"},
        ],
    }


def week(wk, n, seed):
    rng = random.Random(seed)
    cands = [candidate(i, wk, rng) for i in range(n)]
    ranked = sorted(cands, key=lambda c: -c["total"])
    return {
        "week": wk,
        "run_at": f"2026-10-{20 + seed:02d}T14:00:00Z",
        "model": "claude-opus-5-5",
        "status": "ok",
        "note": "" if n >= 15 else "Reddit blocked every request this week.",
        "candidates_scored": n,
        "sources_hit": ["r/ClaudeAI", "Hacker News"],
        "sources_failed": [{"source": "r/SaaS", "error": "403"}] if n < 50 else [],
        "top5": [c["id"] for c in ranked[:5]] if n >= 15 else [],
        "candidates": cands,
    }


def main():
    out = ROOT / "tests" / "fixtures"
    shutil.rmtree(out, ignore_errors=True)
    for name, last_n in (("ok", 56), ("thin", 22), ("skipped", 7)):
        d = out / name
        (d / "weeks").mkdir(parents=True)
        for wk, n, seed in (("2026-W42", 53, 1), ("2026-W43", 51, 2), ("2026-W44", last_n, 3)):
            p = d / "weeks" / f"{wk}.json"
            p.write_text(json.dumps(week(wk, n, seed)), encoding="utf-8")
            build.run(p, d)
        print(f"{name}: tests/fixtures/{name}/leaderboard.json")


if __name__ == "__main__":
    main()
