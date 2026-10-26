# Claude Leaderboard

Weekly scan of Reddit, Substack, Hacker News, and other sources for concrete reports of people earning money, saving work hours, or running family life with Claude. Each week 50 or more candidates are scored on a fixed rubric and the top 5 are published.

Board: https://not-in-scope.github.io/claude-leaderboard/

- `ROUTINE.md` is what the weekly cloud routine follows.
- `rubric.md` holds the scoring weights, anchors, and profile.
- `sources.md` is the source registry. Edit it to add or drop sources.
- `data/weeks/` holds every scored candidate for every run.
- `build.py` validates a week file, merges it into `data/ideas.json`, and rewrites `data/leaderboard.json`.

Run tests with `python -m pytest -q`. Preview the board against sample data with `python tests/make_fixture.py` then `python -m http.server 8000` and open `http://localhost:8000/?data=tests/fixtures/ok/leaderboard.json`.

Design: `docs/superpowers/specs/2026-10-23-claude-leaderboard-design.md`.
