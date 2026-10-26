# Claude Leaderboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A public GitHub Pages board, fed by a weekly Claude Code cloud routine, that scores 50+ reports of people earning money, saving work hours, or running family life with Claude, and publishes the top 5.

**Architecture:** A cloud routine clones this repo every Monday, reads `ROUTINE.md`, `rubric.md`, and `sources.md`, collects and scores candidates, and writes one week file. A stdlib Python script `build.py` validates that file, merges it into `data/ideas.json`, and emits `data/leaderboard.json`. A static `index.html` renders that JSON on GitHub Pages. The routine commits to main.

**Tech Stack:** Python 3.10+ stdlib (build script), pytest (tests), vanilla HTML/CSS/JS (board), GitHub Pages, Claude Code cloud routines via the `RemoteTrigger` tool, `gh` CLI.

**Spec:** `docs/superpowers/specs/2026-10-23-claude-leaderboard-design.md`

**Status note (2026-10-26):** Tasks 1 to 9 are implemented. Review passes after each task changed the code beyond the blocks below (input hardening in `build.py`, literal week placeholders and a valid example in `ROUTINE.md`, rubric anchors, safe links and a Rising cap on the board). The committed files are the source of truth; the blocks here are the starting point they were built from.

**Working directory for every command:** `C:\Users\styos\OneDrive\Documents\Projects\claude-leaderboard` (already a git repo on `main` with the spec committed).

---

## File map

| Path | Responsibility |
|---|---|
| `build.py` | Validate a week file, merge into the idea registry, emit board data. Pure functions plus a thin CLI. |
| `tests/test_build.py` | Unit tests for every rule in `build.py`. |
| `tests/make_fixture.py` | Generates sample data under `tests/fixtures/` for eyeballing the board. Not committed output. |
| `index.html` | The board. Fetches `data/leaderboard.json`, or a `?data=` override for fixtures. |
| `data/ideas.json` | Idea registry. Starts as `[]`. |
| `data/leaderboard.json` | Board data. Starts as the empty-board shape. |
| `data/weeks/` | One JSON file per run, written by the routine. Starts empty with a `.gitkeep`. |
| `rubric.md` | Weights, anchors per category, hourly rate, profile paragraph. |
| `sources.md` | Source registry table. |
| `ROUTINE.md` | Self-contained instructions the routine follows. |
| `README.md`, `.gitignore`, `.gitattributes` | Repo hygiene. |

Candidate and idea field names are fixed by the spec and used identically in `build.py`, tests, `index.html`, and `ROUTINE.md`: `id, title, category, pitch, first_step, scores{fit,upside,time_to_dollar,effort,evidence,durability}, total, reasons, dollars{low,high,basis}, hours_per_week, evidence[{url,source,date,claim}]`, optional `aliases`.

---

### Task 1: Repo scaffold and remote

**Files:**
- Create: `.gitignore`, `.gitattributes`, `README.md`, `data/ideas.json`, `data/leaderboard.json`, `data/weeks/.gitkeep`

- [ ] **Step 1: Confirm tooling**

Run:
```bash
python --version && python -m pytest --version || python -m pip install pytest
gh auth status
```
Expected: Python 3.10 or newer, pytest version printed (install if missing), `Logged in to github.com account not-in-scope`.

- [ ] **Step 2: Write hygiene files**

`.gitignore`:
```
__pycache__/
.pytest_cache/
tests/fixtures/
```

`.gitattributes`:
```
* text=auto eol=lf
```

`README.md`:
```markdown
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
```

- [ ] **Step 3: Write empty data files**

`data/ideas.json`:
```json
[]
```

`data/leaderboard.json`:
```json
{
 "updated": null,
 "this_week": null,
 "all_time": [],
 "rising": [],
 "history": []
}
```

`data/weeks/.gitkeep`: empty file.

- [ ] **Step 4: Commit and create the GitHub repo**

```bash
git add -A
git commit -m "Scaffold repo with empty data files"
gh repo create not-in-scope/claude-leaderboard --public --source . --remote origin --push --description "Weekly leaderboard of productive and money-making uses of Claude"
git remote -v
```
Expected: repo URL printed, `origin https://github.com/not-in-scope/claude-leaderboard.git` on fetch and push.

---

### Task 2: build.py validation

**Files:**
- Create: `build.py`
- Create: `tests/test_build.py`

- [ ] **Step 1: Write the failing validation tests**

`tests/test_build.py`:
```python
import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

# fit 20 + upside 15 + time_to_dollar 10 + effort 10 + evidence 10 + durability 5 = 70
BASE_SCORES = {"fit": 20, "upside": 15, "time_to_dollar": 10,
               "effort": 10, "evidence": 10, "durability": 5}


def candidate(i, category="money", total=70, week="2026-W44"):
    """A valid candidate. total must be 50..75 (fit absorbs the difference)."""
    scores = dict(BASE_SCORES)
    scores["fit"] = BASE_SCORES["fit"] + (total - 70)
    assert 0 <= scores["fit"] <= 25
    return {
        "id": f"idea-{i:03d}",
        "title": f"Idea {i}",
        "category": category,
        "pitch": "Two sentences.",
        "first_step": "Do a thing.",
        "scores": scores,
        "total": sum(scores.values()),
        "reasons": {k: "because" for k in scores},
        "dollars": {"low": 1000, "high": 5000, "basis": "annual"},
        "hours_per_week": 4,
        "evidence": [
            {"url": f"https://example.com/{week}/{i}/a", "source": "r/ClaudeAI",
             "date": "2026-10-20", "claim": "x"},
            {"url": f"https://example.com/{week}/{i}/b", "source": "hn",
             "date": "2026-10-21", "claim": "y"},
        ],
    }


def week_file(n, week="2026-W44", top5=None):
    cands = [candidate(i, week=week) for i in range(n)]
    if top5 is None:
        top5 = [c["id"] for c in cands[:5]] if n >= 15 else []
    return {
        "week": week,
        "run_at": f"2026-10-26T14:00:00Z",
        "model": "claude-opus-5-5",
        "status": "ok",
        "note": "",
        "candidates_scored": n,
        "sources_hit": ["r/ClaudeAI"],
        "sources_failed": [],
        "top5": top5,
        "candidates": cands,
    }


@pytest.fixture
def data_dir(tmp_path):
    (tmp_path / "weeks").mkdir()
    return tmp_path


def write_week(data_dir, week):
    p = data_dir / "weeks" / f"{week['week']}.json"
    p.write_text(json.dumps(week), encoding="utf-8")
    return p


# ---- validation ----

def test_missing_week_key_rejected():
    w = week_file(50)
    del w["run_at"]
    with pytest.raises(build.ValidationError, match="missing keys"):
        build.validate_week(w)


def test_bad_week_id_rejected():
    w = week_file(50, week="week44")
    with pytest.raises(build.ValidationError, match="2026-W44"):
        build.validate_week(w)


def test_missing_candidate_key_rejected():
    w = week_file(50)
    del w["candidates"][2]["first_step"]
    with pytest.raises(build.ValidationError, match="candidate 2"):
        build.validate_week(w)


def test_unknown_category_rejected():
    w = week_file(50)
    w["candidates"][0]["category"] = "fun"
    with pytest.raises(build.ValidationError, match="category"):
        build.validate_week(w)


def test_score_over_max_rejected():
    w = week_file(50)
    c = w["candidates"][0]
    c["scores"]["durability"] = 11
    c["total"] = sum(c["scores"].values())
    with pytest.raises(build.ValidationError, match="durability"):
        build.validate_week(w)


def test_bad_total_rejected():
    w = week_file(50)
    w["candidates"][0]["total"] = 99
    with pytest.raises(build.ValidationError, match="total"):
        build.validate_week(w)


@pytest.mark.parametrize("n", [1, 6])
def test_wrong_evidence_count_rejected(n):
    w = week_file(50)
    w["candidates"][0]["evidence"] = [{"url": f"https://e.com/{k}"} for k in range(n)]
    with pytest.raises(build.ValidationError, match="evidence"):
        build.validate_week(w)


def test_evidence_without_url_rejected():
    w = week_file(50)
    w["candidates"][0]["evidence"][1] = {"source": "hn", "claim": "no link"}
    with pytest.raises(build.ValidationError, match="url"):
        build.validate_week(w)


def test_top5_unknown_id_rejected():
    w = week_file(50, top5=["idea-000", "idea-001", "idea-002", "idea-003", "nope"])
    with pytest.raises(build.ValidationError, match="top5"):
        build.validate_week(w)


def test_top5_wrong_length_rejected():
    w = week_file(50, top5=["idea-000", "idea-001"])
    with pytest.raises(build.ValidationError, match="top5"):
        build.validate_week(w)


def test_duplicate_ids_rejected():
    w = week_file(50)
    w["candidates"][1]["id"] = "idea-000"
    with pytest.raises(build.ValidationError, match="duplicate"):
        build.validate_week(w)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_build.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'build'`.

- [ ] **Step 3: Write build.py with validation only**

`build.py`:
```python
#!/usr/bin/env python3
"""Validate a week file, merge it into the idea registry, and emit the board data.

Usage: python build.py data/weeks/2026-W44.json
Stdlib only. Exits 1 on validation failure and writes nothing.
"""
import json
import re
import sys
from pathlib import Path

FACTOR_MAX = {
    "fit": 25, "upside": 20, "time_to_dollar": 15,
    "effort": 15, "evidence": 15, "durability": 10,
}
CATEGORIES = ("money", "time", "life")
OK_MIN = 50
THIN_MIN = 15
EVIDENCE_MIN = 2
EVIDENCE_MAX = 5
EVIDENCE_KEEP = 10
ALL_TIME_N = 20
RISING_MIN_WEEKS = 3
WEEK_RE = re.compile(r"^\d{4}-W\d{2}$")

WEEK_KEYS = {"week", "run_at", "model", "status", "note", "candidates_scored",
             "sources_hit", "sources_failed", "top5", "candidates"}
CANDIDATE_KEYS = {"id", "title", "category", "pitch", "first_step", "scores",
                  "total", "reasons", "dollars", "hours_per_week", "evidence"}


class ValidationError(Exception):
    pass


def derive_status(n):
    if n >= OK_MIN:
        return "ok"
    if n >= THIN_MIN:
        return "thin"
    return "skipped"


def validate_candidate(c, i):
    label = f"candidate {i} ({c.get('id', '?')})"
    missing = CANDIDATE_KEYS - c.keys()
    if missing:
        raise ValidationError(f"{label}: missing keys {sorted(missing)}")
    if c["category"] not in CATEGORIES:
        raise ValidationError(f"{label}: category must be one of {CATEGORIES}")
    scores = c["scores"]
    if not isinstance(scores, dict):
        raise ValidationError(f"{label}: scores must be an object")
    for factor, mx in FACTOR_MAX.items():
        v = scores.get(factor)
        if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v <= mx:
            raise ValidationError(f"{label}: scores.{factor} must be an int 0..{mx}, got {v!r}")
    extra = set(scores) - set(FACTOR_MAX)
    if extra:
        raise ValidationError(f"{label}: unknown score factors {sorted(extra)}")
    if c["total"] != sum(scores.values()):
        raise ValidationError(f"{label}: total {c['total']} != sum of scores {sum(scores.values())}")
    ev = c["evidence"]
    if not isinstance(ev, list) or not EVIDENCE_MIN <= len(ev) <= EVIDENCE_MAX:
        raise ValidationError(f"{label}: evidence needs {EVIDENCE_MIN}..{EVIDENCE_MAX} links")
    for e in ev:
        if not isinstance(e, dict) or not e.get("url"):
            raise ValidationError(f"{label}: every evidence item needs a url")


def validate_week(week):
    """Validate and normalise a week dict in place. Raises ValidationError."""
    missing = WEEK_KEYS - week.keys()
    if missing:
        raise ValidationError(f"week file: missing keys {sorted(missing)}")
    if not WEEK_RE.match(str(week["week"])):
        raise ValidationError(f"week must look like 2026-W44, got {week['week']!r}")
    cands = week["candidates"]
    if not isinstance(cands, list):
        raise ValidationError("candidates must be a list")
    for i, c in enumerate(cands):
        validate_candidate(c, i)
    ids = [c["id"] for c in cands]
    dupes = sorted({x for x in ids if ids.count(x) > 1})
    if dupes:
        raise ValidationError(f"duplicate candidate ids {dupes}")
    week["candidates_scored"] = len(cands)
    week["status"] = derive_status(len(cands))
    top5 = week["top5"]
    if week["status"] == "skipped":
        if top5:
            raise ValidationError("top5 must be empty when fewer than 15 candidates")
    else:
        if not isinstance(top5, list) or len(top5) != 5 or len(set(top5)) != 5:
            raise ValidationError("top5 must hold exactly 5 distinct ids")
        unknown = [s for s in top5 if s not in ids]
        if unknown:
            raise ValidationError(f"top5 ids not in candidates: {unknown}")
    return week
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_build.py -q`
Expected: `12 passed`.

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "build: validate week files"
```

---

### Task 3: build.py status derivation

**Files:**
- Modify: `tests/test_build.py` (append)
- `build.py` already has `derive_status`; this task proves the thresholds.

- [ ] **Step 1: Append the status tests**

Append to `tests/test_build.py`:
```python
# ---- status ----

@pytest.mark.parametrize("n,status", [(14, "skipped"), (15, "thin"), (49, "thin"), (50, "ok")])
def test_status_derived_from_count(n, status):
    assert build.derive_status(n) == status
    w = week_file(n)
    w["status"] = "ok"
    w["candidates_scored"] = 999
    build.validate_week(w)
    assert w["status"] == status
    assert w["candidates_scored"] == n


def test_skipped_week_must_have_empty_top5():
    w = week_file(10, top5=["idea-000", "idea-001", "idea-002", "idea-003", "idea-004"])
    with pytest.raises(build.ValidationError, match="top5"):
        build.validate_week(w)
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest tests/test_build.py -q`
Expected: `17 passed`. If `test_status_derived_from_count[14-skipped]` fails, `week_file` built a non-empty `top5` for n under 15; check the `n >= 15` guard in `week_file`.

- [ ] **Step 3: Commit**

```bash
git add tests/test_build.py
git commit -m "build: pin status thresholds"
```

---

### Task 4: build.py merge into the idea registry

**Files:**
- Modify: `build.py` (append after `validate_week`)
- Modify: `tests/test_build.py` (append)

- [ ] **Step 1: Append the failing merge tests**

Append to `tests/test_build.py`:
```python
# ---- merge ----

def test_merge_new_idea_creates_record():
    ideas = []
    w = build.validate_week(week_file(50))
    build.merge(ideas, w)
    assert len(ideas) == 50
    rec = ideas[0]
    assert rec["id"] == "idea-000"
    assert rec["weeks_seen"] == 1
    assert rec["weeks"] == ["2026-W44"]
    assert rec["best_score"] == 70 and rec["best_week"] == "2026-W44"
    assert rec["first_week"] == "2026-W44" and rec["last_week"] == "2026-W44"
    assert rec["latest"]["week"] == "2026-W44" and rec["latest"]["total"] == 70
    assert len(rec["evidence"]) == 2
    assert rec["aliases"] == []


def test_merge_keeps_aliases():
    ideas = []
    w = week_file(50)
    w["candidates"][0]["aliases"] = ["soc2 helper"]
    build.merge(ideas, build.validate_week(w))
    w2 = week_file(50, week="2026-W45")
    w2["candidates"][0]["aliases"] = ["soc2 helper", "audit prep"]
    build.merge(ideas, build.validate_week(w2))
    assert ideas[0]["aliases"] == ["soc2 helper", "audit prep"]


def test_merge_repeat_idea_across_weeks():
    ideas = []
    build.merge(ideas, build.validate_week(week_file(50, week="2026-W44")))
    w2 = week_file(50, week="2026-W45")
    w2["candidates"][0] = candidate(0, total=75, week="2026-W45")
    build.merge(ideas, build.validate_week(w2))
    rec = next(r for r in ideas if r["id"] == "idea-000")
    assert rec["weeks_seen"] == 2
    assert rec["first_week"] == "2026-W44" and rec["last_week"] == "2026-W45"
    assert rec["best_score"] == 75 and rec["best_week"] == "2026-W45"
    assert rec["latest"]["total"] == 75 and rec["latest"]["week"] == "2026-W45"
    assert len(rec["evidence"]) == 4
    assert rec["evidence"][0]["url"].startswith("https://example.com/2026-W45/")


def test_merge_lower_score_keeps_best():
    ideas = []
    build.merge(ideas, build.validate_week(week_file(50, week="2026-W44")))
    w2 = week_file(50, week="2026-W45")
    w2["candidates"][0] = candidate(0, total=60, week="2026-W45")
    build.merge(ideas, build.validate_week(w2))
    rec = ideas[0]
    assert rec["best_score"] == 70 and rec["best_week"] == "2026-W44"
    assert rec["latest"]["total"] == 60


def test_evidence_capped_at_ten():
    ideas = []
    for n in range(44, 51):  # 7 weeks x 2 links = 14 urls
        build.merge(ideas, build.validate_week(week_file(50, week=f"2026-W{n}")))
    rec = next(r for r in ideas if r["id"] == "idea-000")
    assert len(rec["evidence"]) == 10
    assert rec["weeks_seen"] == 7


def test_merge_same_week_twice_is_idempotent():
    ideas = []
    w = build.validate_week(week_file(50))
    build.merge(ideas, w)
    snapshot = copy.deepcopy(ideas)
    build.merge(ideas, copy.deepcopy(w))
    assert ideas == snapshot
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_build.py -q -k merge`
Expected: 6 failures with `AttributeError: module 'build' has no attribute 'merge'`.

- [ ] **Step 3: Add merge to build.py**

Append to `build.py` after `validate_week`:
```python
def _latest(c, week_id):
    return {
        "week": week_id,
        "pitch": c["pitch"],
        "first_step": c["first_step"],
        "scores": c["scores"],
        "total": c["total"],
        "reasons": c["reasons"],
        "dollars": c["dollars"],
        "hours_per_week": c["hours_per_week"],
    }


def merge(ideas, week):
    """Merge week candidates into the ideas list in place. Running the same
    week twice changes nothing. Returns the list, sorted by id."""
    by_id = {r["id"]: r for r in ideas}
    wk = week["week"]
    for c in week["candidates"]:
        rec = by_id.get(c["id"])
        if rec is None:
            rec = {
                "id": c["id"],
                "title": c["title"],
                "aliases": list(c.get("aliases", [])),
                "category": c["category"],
                "first_week": wk,
                "last_week": wk,
                "weeks": [wk],
                "weeks_seen": 1,
                "best_score": c["total"],
                "best_week": wk,
                "latest": _latest(c, wk),
                "evidence": [],
            }
            ideas.append(rec)
            by_id[rec["id"]] = rec
        else:
            if wk not in rec["weeks"]:
                rec["weeks"].append(wk)
                rec["weeks"].sort()
                rec["weeks_seen"] = len(rec["weeks"])
            rec["first_week"] = min(rec["first_week"], wk)
            if wk >= rec["last_week"]:
                rec["last_week"] = wk
                rec["latest"] = _latest(c, wk)
                rec["title"] = c["title"]
                rec["category"] = c["category"]
            if c["total"] > rec["best_score"]:
                rec["best_score"] = c["total"]
                rec["best_week"] = wk
            for a in c.get("aliases", []):
                if a not in rec["aliases"]:
                    rec["aliases"].append(a)
        known = {e["url"] for e in rec["evidence"]}
        fresh = [e for e in c["evidence"] if e["url"] not in known]
        rec["evidence"] = (fresh + rec["evidence"])[:EVIDENCE_KEEP]
    ideas.sort(key=lambda r: r["id"])
    return ideas
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_build.py -q`
Expected: `23 passed`.

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "build: merge week candidates into the idea registry"
```

---

### Task 5: build.py board emission, file IO, CLI

**Files:**
- Modify: `build.py` (append)
- Modify: `tests/test_build.py` (append)

- [ ] **Step 1: Append the failing board and IO tests**

Append to `tests/test_build.py`:
```python
# ---- board ----

def test_all_time_capped_at_twenty_and_sorted():
    w = week_file(50)
    w["candidates"] = [candidate(i, total=50 + (i % 26)) for i in range(50)]
    ideas = build.merge([], build.validate_week(w))
    board = build.build_board(ideas, [w])
    assert len(board["all_time"]) == 20
    scores = [r["best_score"] for r in board["all_time"]]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 75


def test_rising_requires_three_weeks():
    ideas, weeks = [], []
    for wk in ("2026-W44", "2026-W45", "2026-W46"):
        w = week_file(50, week=wk)
        if wk == "2026-W46":
            w["candidates"] = [c for c in w["candidates"] if c["id"] != "idea-049"]
        build.validate_week(w)
        build.merge(ideas, w)
        weeks.append(w)
    board = build.build_board(ideas, weeks)
    ids = {r["id"] for r in board["rising"]}
    assert "idea-000" in ids
    assert "idea-049" not in ids
    assert all(r["weeks_seen"] >= 3 for r in board["rising"])


def test_this_week_top5_and_category_leaders():
    w = week_file(50)
    w["candidates"][3] = candidate(3, category="time", total=71)
    w["candidates"][7] = candidate(7, category="time", total=74)
    ideas = build.merge([], build.validate_week(w))
    board = build.build_board(ideas, [w])
    tw = board["this_week"]
    assert tw["week"] == "2026-W44" and tw["status"] == "ok"
    assert [c["id"] for c in tw["top5"]] == ["idea-000", "idea-001", "idea-002", "idea-003", "idea-004"]
    leaders = tw["category_leaders"]
    assert leaders["money"]["total"] == 70
    assert leaders["time"]["id"] == "idea-007"
    assert leaders["life"] is None


def test_history_lists_error_weeks_but_ignores_them():
    w = build.validate_week(week_file(50, week="2026-W44"))
    err = {"week": "2026-W45", "run_at": "2026-11-02T14:00:00Z", "model": "m",
           "status": "error", "note": "build failed", "candidates_scored": 0,
           "sources_hit": [], "sources_failed": [], "top5": [], "candidates": []}
    board = build.build_board(build.merge([], w), [err, w])
    assert [h["week"] for h in board["history"]] == ["2026-W44", "2026-W45"]
    assert board["history"][1]["status"] == "error"
    assert board["this_week"]["week"] == "2026-W44"
    assert board["updated"] == w["run_at"]


def test_empty_board():
    board = build.build_board([], [])
    assert board == {"updated": None, "this_week": None, "all_time": [], "rising": [], "history": []}


# ---- run (file IO) ----

def test_run_end_to_end_and_idempotent(data_dir):
    p = write_week(data_dir, week_file(50))
    first = build.run(p, data_dir)
    assert (data_dir / "ideas.json").exists()
    assert (data_dir / "leaderboard.json").exists()
    assert first["this_week"]["status"] == "ok"
    assert len(first["this_week"]["top5"]) == 5
    ideas_1 = (data_dir / "ideas.json").read_text(encoding="utf-8")
    board_1 = (data_dir / "leaderboard.json").read_text(encoding="utf-8")
    build.run(p, data_dir)
    assert (data_dir / "ideas.json").read_text(encoding="utf-8") == ideas_1
    assert (data_dir / "leaderboard.json").read_text(encoding="utf-8") == board_1


def test_run_two_weeks_builds_history(data_dir):
    build.run(write_week(data_dir, week_file(50, week="2026-W44")), data_dir)
    board = build.run(write_week(data_dir, week_file(20, week="2026-W45")), data_dir)
    assert [h["week"] for h in board["history"]] == ["2026-W44", "2026-W45"]
    assert board["this_week"]["week"] == "2026-W45"
    assert board["this_week"]["status"] == "thin"


def test_run_writes_nothing_on_invalid_week(data_dir):
    w = week_file(50)
    w["candidates"][0]["total"] = 1
    p = write_week(data_dir, w)
    with pytest.raises(build.ValidationError):
        build.run(p, data_dir)
    assert not (data_dir / "ideas.json").exists()
    assert not (data_dir / "leaderboard.json").exists()


def test_main_returns_1_on_invalid(data_dir, capsys):
    w = week_file(50)
    w["candidates"][0]["total"] = 1
    p = write_week(data_dir, w)
    assert build.main(["build.py", str(p), str(data_dir)]) == 1
    assert "total" in capsys.readouterr().err
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_build.py -q -k "board or run or main"`
Expected: 9 failures, `AttributeError: module 'build' has no attribute 'build_board'` or `'run'`.

- [ ] **Step 3: Append board, IO, and CLI to build.py**

Append to `build.py` after `merge`:
```python
def build_board(ideas, weeks):
    """Board data from the registry and every week dict. Weeks with status
    'error' appear in history only."""
    weeks = sorted(weeks, key=lambda w: w["week"])
    history = [{"week": w["week"], "status": w["status"],
                "candidates_scored": w.get("candidates_scored", 0)} for w in weeks]
    usable = [w for w in weeks if w["status"] != "error"]
    this_week = None
    updated = None
    if usable:
        w = usable[-1]
        updated = w["run_at"]
        by_id = {c["id"]: c for c in w["candidates"]}
        leaders = {}
        for cat in CATEGORIES:
            pool = [c for c in w["candidates"] if c["category"] == cat]
            leaders[cat] = max(pool, key=lambda c: (c["total"], c["id"])) if pool else None
        this_week = {
            "week": w["week"],
            "status": w["status"],
            "note": w.get("note", ""),
            "candidates_scored": w["candidates_scored"],
            "sources_failed": w.get("sources_failed", []),
            "top5": [by_id[s] for s in w["top5"]],
            "category_leaders": leaders,
        }
    all_time = sorted(ideas, key=lambda r: (-r["best_score"], r["first_week"], r["id"]))[:ALL_TIME_N]
    rising = sorted((r for r in ideas if r["weeks_seen"] >= RISING_MIN_WEEKS),
                    key=lambda r: (-r["weeks_seen"], -r["best_score"], r["id"]))
    return {"updated": updated, "this_week": this_week, "all_time": all_time,
            "rising": rising, "history": history}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dump_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")


def run(week_path, data_dir):
    """Validate the week file, merge it, and rewrite the data files.
    The week file must live in <data_dir>/weeks/. Nothing is written if
    validation fails."""
    week_path = Path(week_path)
    data_dir = Path(data_dir)
    weeks_dir = data_dir / "weeks"
    ideas_path = data_dir / "ideas.json"
    board_path = data_dir / "leaderboard.json"

    week = validate_week(load_json(week_path))
    ideas = load_json(ideas_path) if ideas_path.exists() else []
    merge(ideas, week)

    dump_json(week_path, week)
    dump_json(ideas_path, ideas)
    weeks = [load_json(p) for p in sorted(weeks_dir.glob("*.json"))]
    board = build_board(ideas, weeks)
    dump_json(board_path, board)
    return board


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: python build.py data/weeks/<week>.json [data_dir]", file=sys.stderr)
        return 2
    data_dir = Path(argv[2]) if len(argv) == 3 else Path(__file__).resolve().parent / "data"
    try:
        board = run(argv[1], data_dir)
    except ValidationError as e:
        print(f"build.py: {e}", file=sys.stderr)
        return 1
    tw = board["this_week"]
    print(f"{tw['week']}: {tw['status']}, {tw['candidates_scored']} candidates, "
          f"{len(board['all_time'])} all-time, {len(board['rising'])} rising")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run the whole suite**

Run: `python -m pytest tests/test_build.py -q`
Expected: `32 passed`.

- [ ] **Step 5: Smoke the CLI against the real empty data dir**

```bash
python - <<'EOF'
import json, sys
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
from test_build import week_file
json.dump(week_file(50, week="2026-W01"), open("data/weeks/2026-W01.json", "w"), indent=1)
EOF
python build.py data/weeks/2026-W01.json
git status --short
```
Expected: prints `2026-W01: ok, 50 candidates, 20 all-time, 0 rising`, and `git status` shows `data/` files modified.

Then undo the smoke so the repo stays empty:
```bash
rm data/weeks/2026-W01.json
git checkout -- data/ideas.json data/leaderboard.json
git status --short
```
Expected: only `build.py` and `tests/test_build.py` listed.

- [ ] **Step 6: Commit**

```bash
git add build.py tests/test_build.py
git commit -m "build: emit leaderboard data and add CLI"
```

---

### Task 6: rubric.md

**Files:**
- Create: `rubric.md`

- [ ] **Step 1: Write rubric.md**

```markdown
# Scoring rubric

Six factors, integer scores, total 0 to 100. The same factors apply to every category. Anchors differ by category where noted. Score what the evidence supports, not the best case.

Hourly rate for time saved: **150** USD. For `time` and `life` candidates, `dollars.low` and `dollars.high` are `hours_saved_per_week x 150 x 50`, using a low and a high estimate of hours.

## Categories

| Category | Meaning | Examples |
|---|---|---|
| `money` | Earns dollars | Micro-SaaS, consulting, content, freelance work done with Claude, selling templates or agents |
| `time` | Saves hours in professional work | Spec and PRD drafting, data analysis, research, job search, code review, reporting |
| `life` | Personal productivity, family and kid logistics, planning | Meal planning, kids' schedules and activities, travel planning, household admin, budgeting, learning with kids, fitness planning |

When a candidate spans categories, pick the one the evidence emphasizes.

## Profile used for Fit

Professional. Senior technical product manager, nine years at Amazon. Strongest at 0-to-1 products in regulated or compliance-heavy settings, LLM product delivery (AWS Bedrock, document processing, anomaly detection), data platforms and BI (SQL, pipelines, A/B testing), and stakeholder alignment up to VP level. Comfortable with Python and SQL. Not a professional software engineer, but Claude Code closes most of that gap. Weak spots are video production, cold sales calls, and visual design.

Personal. Parent in Seattle. Active household with a lot of sports. Values hours back on weekday evenings and weekends.

## Factors

### Fit, 0 to 25

| Score | `money` and `time` | `life` |
|---|---|---|
| 0 to 5 | Needs skills from the weak spots, or a credential he lacks | Does not match a parent household in Seattle |
| 6 to 12 | Learnable in a month, no current edge | Generic, works for anyone, no particular edge |
| 13 to 19 | Uses one strength directly | Matches one feature of his situation (kids, sports, planning load) |
| 20 to 25 | Uses two or more strengths, or a compliance or data edge few others have | Fits the household closely and uses his data or planning skills |

### Upside, 0 to 20

| Score | Realistic annual dollars or hours |
|---|---|
| 0 to 4 | Under $1k a year, or under 1 hour a week saved |
| 5 to 9 | $1k to $10k, or 1 to 3 hours a week |
| 10 to 14 | $10k to $50k, or 3 to 6 hours a week |
| 15 to 20 | $50k or more, or 6 or more hours a week, or removes a recurring family pain point |

### Time to benefit, 0 to 15 (key `time_to_dollar`)

| Score | First dollar or first hour saved |
|---|---|
| 0 to 3 | Six months or longer |
| 4 to 7 | Two to six months |
| 8 to 11 | Two weeks to two months |
| 12 to 15 | Under two weeks. For `life`, the first use already pays off |

### Effort, 0 to 15

| Score | Hours a week to run once set up |
|---|---|
| 0 to 3 | 30 or more, a full-time job |
| 4 to 7 | 10 to 30 |
| 8 to 11 | 3 to 10 |
| 12 to 15 | Under 3 |

### Evidence, 0 to 15

| Score | What the sources show |
|---|---|
| 0 to 3 | One anonymous claim with no numbers |
| 4 to 7 | One named person with numbers, or several vague reports |
| 8 to 11 | Two independent reports with specifics |
| 12 to 15 | Three or more independent reports with specifics, or one audited or paid-platform record |

Independent means different people, not one story reposted.

### Durability, 0 to 10

| Score | Will it still work |
|---|---|
| 0 to 2 | Arbitrage or loophole likely closed within months |
| 3 to 5 | Works for a year, then crowded or automated away |
| 6 to 8 | Works for two years with ordinary maintenance |
| 9 to 10 | Durable skill or asset, gets better as models improve |

## Writing the pitch and first step

The pitch is two sentences. The first names what the person did and the result. The second says why it fits this profile.

The first step is one concrete action that takes under three hours, such as "Build a throwaway version for your own household this weekend" or "Reply to the thread's author and ask for their pricing page."
```

- [ ] **Step 2: Commit**

```bash
git add rubric.md
git commit -m "Add scoring rubric"
```

---

### Task 7: sources.md

**Files:**
- Create: `sources.md`

- [ ] **Step 1: Write sources.md**

```markdown
# Source registry

Tier 1 is read every run and must be covered before collection stops. Tier 2 is read every run as extra signal. Tier 3 is read on the first run of each month. `status` is `active`, `paused`, or `excluded`. `last_yield` is the number of candidates whose evidence cited the source in the most recent run. The routine updates `last_yield` and `note`; Stephen edits everything else.

`how_read` values: `json` (Reddit JSON endpoints), `hn` (Algolia API), `rss` (feed URL in `queries`), `fetch` (plain page fetch), `search` (web search with the queries listed).

## Reddit

Read with `https://www.reddit.com/r/<sub>/top.json?t=week&limit=100` and `https://www.reddit.com/r/<sub>/search.json?q=<query>&restrict_sr=1&sort=new&t=week`. Fallback is a web search for `site:reddit.com/r/<sub> <query>` limited to the past week.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| r/ClaudeAI | reddit | 1 | json | claude, "claude code", revenue, "saved me", clients | active | 0 | main hub, about 1M members |
| r/ClaudeCode | reddit | 1 | json | revenue, MRR, clients, "built a", "saved me" | active | 0 | |
| r/Anthropic | reddit | 1 | json | claude, "use case", revenue | active | 0 | |
| r/claude | reddit | 1 | json | "use claude", revenue, "saved me" | active | 0 | |
| r/claudexplorers | reddit | 1 | json | planning, family, kids, "saved me", workflow | active | 0 | non-coding use |
| r/ClaudeHomies | reddit | 1 | json | planning, family, kids, "saved me", workflow | active | 0 | non-coding use |
| r/indiehackers | reddit | 1 | json | claude, "claude code", MRR | active | 0 | |
| r/SideProject | reddit | 1 | json | claude, "claude code" | active | 0 | |
| r/SaaS | reddit | 1 | json | claude, "claude code" | active | 0 | |
| r/microsaas | reddit | 1 | json | claude, "claude code" | active | 0 | |
| r/VibeCodingSaaS | reddit | 1 | json | claude, MRR | active | 0 | small, high signal |
| r/NoCodeSaaS | reddit | 1 | json | claude | active | 0 | |
| r/Entrepreneur | reddit | 1 | json | claude, "ai agent" revenue | active | 0 | |
| r/EntrepreneurRideAlong | reddit | 1 | json | claude, "ai" revenue | active | 0 | |
| r/startups | reddit | 1 | json | claude, "claude code" | active | 0 | |
| r/smallbusiness | reddit | 1 | json | claude, "ai saved" | active | 0 | |
| r/sweatystartup | reddit | 1 | json | claude, ai | active | 0 | |
| r/Business_Ideas | reddit | 1 | json | claude, ai | active | 0 | |
| r/freelance | reddit | 1 | json | claude, "ai clients" | active | 0 | |
| r/Upwork | reddit | 1 | json | claude, "ai" | active | 0 | |
| r/consulting | reddit | 1 | json | claude, "ai" | active | 0 | |
| r/passive_income | reddit | 1 | json | claude, ai | active | 0 | |
| r/digitalnomad | reddit | 1 | json | claude, "ai income" | active | 0 | |
| r/ChatGPTCoding | reddit | 1 | json | claude, "claude code", revenue, clients | active | 0 | tool-agnostic |
| r/vibecoding | reddit | 1 | json | claude, MRR, revenue, "saved me" | active | 0 | |
| r/aipromptprogramming | reddit | 1 | json | claude, revenue | active | 0 | |
| r/AI_Agents | reddit | 1 | json | claude, revenue, clients | active | 0 | |
| r/LLMDevs | reddit | 1 | json | claude, "in production", revenue | active | 0 | |
| r/AgentsOfAI | reddit | 1 | json | claude, revenue | active | 0 | |
| r/AiBuilders | reddit | 1 | json | claude, revenue | active | 0 | |
| r/PromptEngineering | reddit | 1 | json | claude, "saved me", workflow | active | 0 | |
| r/automation | reddit | 1 | json | claude, "saved me", clients | active | 0 | |
| r/n8n | reddit | 1 | json | claude, clients, revenue | active | 0 | |
| r/Parenting | reddit | 1 | json | claude, "ai" planning, schedule | active | 0 | life |
| r/daddit | reddit | 1 | json | claude, "ai" planning | active | 0 | life |
| r/Mommit | reddit | 1 | json | claude, "ai" planning | active | 0 | life |
| r/getdisciplined | reddit | 1 | json | claude, "ai" planning | active | 0 | life |
| r/personalfinance | reddit | 1 | json | claude, "ai" budget | active | 0 | life |
| r/budget | reddit | 1 | json | claude, ai | active | 0 | life |
| r/MealPrepSunday | reddit | 1 | json | claude, ai | active | 0 | life |
| r/travel | reddit | 1 | json | claude, "ai itinerary" | active | 0 | life |
| r/HomeImprovement | reddit | 1 | json | claude, ai | active | 0 | life |
| r/homeschool | reddit | 1 | json | claude, ai | active | 0 | life |
| r/ProductManagement | reddit | 2 | json | claude, "ai" workflow, "saved me" | active | 0 | time |
| r/dataengineering | reddit | 2 | json | claude, "claude code" | active | 0 | time |
| r/datascience | reddit | 2 | json | claude, "claude code" | active | 0 | time |
| r/analytics | reddit | 2 | json | claude, ai | active | 0 | time |
| r/BusinessIntelligence | reddit | 2 | json | claude, ai | active | 0 | time |
| r/ExperiencedDevs | reddit | 2 | json | claude, "claude code" | active | 0 | time |
| r/productivity | reddit | 2 | json | claude, "ai" workflow | active | 0 | time, life |
| r/ChatGPT | reddit | 2 | json | "make money", "saved me", planning | active | 0 | uses transfer to Claude |
| r/ChatGPTPro | reddit | 2 | json | workflow, "saved me", revenue | active | 0 | uses transfer |
| r/OpenAI | reddit | 2 | json | claude, "switched to claude" | active | 0 | comparisons |
| r/ArtificialInteligence | reddit | 2 | json | claude, "use case", revenue | active | 0 | thin on workflows |
| r/artificial | reddit | 2 | json | claude, "use case" | active | 0 | |
| r/cursor | reddit | 2 | json | claude, revenue, clients | active | 0 | |
| r/Substack | reddit | 2 | json | claude, ai | active | 0 | creator |
| r/content_marketing | reddit | 2 | json | claude, ai | active | 0 | creator |
| r/copywriting | reddit | 2 | json | claude, ai clients | active | 0 | creator |
| r/SEO | reddit | 2 | json | claude, "claude code" | active | 0 | creator |
| r/blogging | reddit | 2 | json | claude, ai | active | 0 | creator |
| r/selfpublish | reddit | 2 | json | claude, ai | active | 0 | creator |
| r/Etsy | reddit | 2 | json | claude, ai | active | 0 | creator |
| r/printondemand | reddit | 2 | json | claude, ai | active | 0 | creator |
| r/singularity | reddit | - | - | - | excluded | 0 | speculation, not use |
| r/MakeMoneyOnline | reddit | - | - | - | excluded | 0 | low quality |
| r/beermoney | reddit | - | - | - | excluded | 0 | low quality |
| r/ClaudeAIJailbreak | reddit | - | - | - | excluded | 0 | off purpose |

## Forums and aggregators

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Hacker News | forum | 1 | hn | claude, "claude code", anthropic | active | 0 | `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=100&numericFilters=created_at_i>EPOCH` plus `tags=ask_hn,show_hn` |
| Indie Hackers | forum | 1 | search | site:indiehackers.com claude | active | 0 | revenue milestones |
| Product Hunt | forum | 1 | search | site:producthunt.com "claude code" OR "built with claude" | active | 0 | launches |
| Medium | blog | 2 | search | site:medium.com claude (earned OR revenue OR "saved me" OR clients) | active | 0 | |
| Dev.to | blog | 2 | rss | https://dev.to/feed/tag/claude | active | 0 | |
| LinkedIn | social | 2 | search | site:linkedin.com/posts claude (revenue OR clients OR "saved me") | active | 0 | only what search surfaces |

## Newsletters

Read the feed, keep items dated in the window. When a feed fails, search `site:<domain> claude` for the past two weeks and note the failure.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| One Useful Thing | newsletter | 1 | rss | https://www.oneusefulthing.org/feed | active | 0 | Ethan Mollick |
| Every | newsletter | 1 | rss | https://every.to/feed | active | 0 | Chain of Thought and others |
| Latent Space | newsletter | 1 | rss | https://www.latent.space/feed | active | 0 | |
| Lenny's Newsletter | newsletter | 1 | rss | https://www.lennysnewsletter.com/feed | active | 0 | |
| Product Growth | newsletter | 1 | rss | https://www.news.aakashg.com/feed | active | 0 | Aakash Gupta |
| Product with Attitude | newsletter | 1 | rss | https://karozieminski.substack.com/feed | active | 0 | Claude Code and Cowork workflows |
| The AI Maker | newsletter | 1 | rss | https://aimaker.substack.com/feed | active | 0 | |
| The Pragmatic Engineer | newsletter | 1 | rss | https://newsletter.pragmaticengineer.com/feed | active | 0 | |
| Simon Willison's weblog | blog | 1 | rss | https://simonwillison.net/atom/everything/ | active | 0 | |
| Ben's Bites | newsletter | 1 | rss | https://www.bensbites.com/feed | active | 0 | feed unverified, fall back to search |
| The Rundown AI | newsletter | 1 | search | site:therundown.ai claude | active | 0 | beehiiv, no stable feed |
| Superhuman AI | newsletter | 1 | search | site:superhuman.ai claude | active | 0 | beehiiv |
| The Neuron | newsletter | 1 | search | site:theneurondaily.com claude | active | 0 | beehiiv |
| Starter Story | newsletter | 1 | search | site:starterstory.com claude | active | 0 | |
| Growth Unhinged | newsletter | 1 | rss | https://www.growthunhinged.com/feed | active | 0 | Kyle Poyar |
| Justin Welsh | newsletter | 1 | search | site:justinwelsh.me claude | active | 0 | solo business |
| Behind the Craft | newsletter | 1 | rss | https://creatoreconomy.so/feed | active | 0 | Peter Yang |

## Anthropic first-party

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Customer stories | anthropic | 1 | fetch | https://www.anthropic.com/customers | active | 0 | |
| News | anthropic | 1 | fetch | https://www.anthropic.com/news | active | 0 | |
| Economic Index | anthropic | 1 | fetch | https://www.anthropic.com/research | active | 0 | new report roughly quarterly |
| Claude Code changelog | anthropic | 1 | fetch | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | active | 0 | new capability precedes new uses |

## Social and video, search only

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| X revenue threads | social | 2 | search | site:x.com "claude code" (MRR OR revenue OR "$" OR clients) | active | 0 | |
| X accounts | social | 2 | search | site:x.com (alexalbert__ OR bcherny OR levelsio OR marc_louvion OR gregisenberg OR swyx OR emollick OR danshipper OR simonw) claude | active | 0 | |
| YouTube | video | 2 | search | site:youtube.com "claude code" (business OR money OR "per month" OR clients) | active | 0 | titles and descriptions only |
| YouTube channels | video | 2 | search | site:youtube.com claude (Greg Isenberg OR "Starter Story" OR "AI Jason" OR "Matt Wolfe" OR "Riley Brown" OR "Cole Medin" OR IndyDevDan OR "Nate Herk" OR "Craig Hewitt" OR "Matthew Berman") | active | 0 | |
| Podcasts | audio | 2 | search | ("How I AI" OR "Lenny's Podcast" OR "My First Million" OR "Latent Space" OR "AI & I" OR "Indie Hackers Podcast" OR "Startup Ideas Podcast") claude | active | 0 | show notes |

## Demand side, monthly

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Upwork | demand | 3 | search | site:upwork.com "claude" (job OR hiring) | active | 0 | what buyers pay for |
| Fiverr | demand | 3 | search | site:fiverr.com claude | active | 0 | |
| Gumroad | demand | 3 | search | site:gumroad.com claude | active | 0 | prompt packs, templates |
| Lemon Squeezy | demand | 3 | search | site:lemonsqueezy.com claude | active | 0 | |
| Acquire.com | demand | 3 | search | site:acquire.com claude OR "built with ai" | active | 0 | exits |
| Google Trends | demand | 3 | fetch | https://trends.google.com/trends/explore?q=claude%20code | active | 0 | often blocked, skip if so |

## Excluded platforms

Discord, Skool, Slack, Facebook groups, and TikTok are not readable by the routine. Content-farm domains that repackage the same claims are dropped when seen. Add a domain here to exclude it: fbpe.org.
```

- [ ] **Step 2: Commit**

```bash
git add sources.md
git commit -m "Add source registry"
```

---

### Task 8: ROUTINE.md

**Files:**
- Create: `ROUTINE.md`

- [ ] **Step 1: Write ROUTINE.md**

```markdown
# Weekly scan

You are the Claude Leaderboard weekly scan, running unattended in a cloud sandbox with this repo checked out. Do every step below in order. Do not ask questions. When you must make a call, make it and record it in the week file's `note`.

Tools you have: shell (`curl`, `python3`, `git`), file read and write, web search, web fetch.

## 0. Setup

```bash
WEEK=$(date -u +%G-W%V)          # ISO week, for example 2026-W44
TODAY=$(date -u +%F)
START=$(date -u -d "$TODAY -10 days" +%F)
EPOCH_START=$(date -u -d "$START" +%s)
DOM=$(date -u +%d)               # tier 3 runs when DOM is 01..07
```

Read `rubric.md`, `sources.md`, and `data/ideas.json`. The registry tells you which ideas already exist, so repeats get the same `id`.

If `data/weeks/$WEEK.json` already exists, this is a rerun. Overwrite it.

## 1. Collect

Target: 50 or more distinct candidates. A candidate is a first-hand report, dated within the window, of a person or small team using Claude (claude.ai, Claude Code, Claude Cowork, the API) to earn money, save hours at work, or run personal or family life. It must have a URL.

Not a candidate: model comparisons, benchmarks, complaints, speculation about jobs, prompt lists with no outcome, product announcements with no user report, posts about other tools with no Claude angle.

Order: every tier 1 source in `sources.md`, then every tier 2 source, then tier 3 when `DOM` is 01 to 07. Try every tier 1 source even after passing 50.

How to read each `how_read` type:

- `json` (Reddit). For each subreddit, fetch `https://www.reddit.com/r/<sub>/top.json?t=week&limit=100` and, for each query in the row, `https://www.reddit.com/r/<sub>/search.json?q=<query>&restrict_sr=1&sort=new&t=week&limit=50`. Use `curl -sL -A "claude-leaderboard/1.0 (weekly research bot)"`. For promising posts, fetch the post URL with `.json` appended to read comments for numbers. On HTTP 403 or 429, wait 5 seconds and retry once, then fall back to a web search for `site:reddit.com/r/<sub> <query>` limited to the past week, and record the failure under `sources_failed`.
- `hn`. Fetch `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=100&numericFilters=created_at_i>$EPOCH_START` for each query, and again with `tags=ask_hn` and `tags=show_hn`. Open stories that look like first-hand reports.
- `rss`. Fetch the feed URL. Read items dated in the window.
- `fetch`. Fetch the page. Read items dated in the window.
- `search`. Run each query with web search limited to the past two weeks. Open results that look like first-hand reports.

Keep a scratch list as you go, for example `/tmp/candidates.jsonl`, one JSON object per line with the fields in section 4.

## 2. Clean and match

- Drop anything without a URL to a first-hand report.
- Merge duplicates. The same person's story in two places is one candidate with both links. Two different people doing the same thing is one candidate with both links and stronger evidence.
- Match each candidate to `data/ideas.json` by meaning, not by string. If it is the same idea as an existing record, reuse that `id`. Otherwise mint a new kebab-case `id` of three to six words and one to three `aliases`.

## 3. Score

Apply `rubric.md` exactly. Integer scores within each factor's maximum. One-line reason per factor. `total` is the sum. `category` is `money`, `time`, or `life`. `dollars` is a low and high annual estimate; for `time` and `life` compute it from hours saved and the rate in `rubric.md`. `hours_per_week` is the effort to run it. Two to five evidence items, each with `url`, `source` (as named in `sources.md`, or the domain), `date`, and a short `claim` quoting the number or outcome.

`top5` is the five highest totals. Break ties by more evidence, then more recent. If you have 15 to 49 candidates, still pick five. If you have fewer than 15, set `top5` to `[]` and explain in `note`.

## 4. Write the week file

Write `data/weeks/$WEEK.json`:

```json
{
  "week": "2026-W44",
  "run_at": "2026-10-26T14:07:00Z",
  "model": "claude-opus-5-5",
  "status": "ok",
  "note": "",
  "candidates_scored": 57,
  "sources_hit": ["r/ClaudeAI", "Hacker News"],
  "sources_failed": [{"source": "r/SaaS", "error": "403 after retry, used search fallback"}],
  "top5": ["slug-a", "slug-b", "slug-c", "slug-d", "slug-e"],
  "candidates": [
    {
      "id": "compliance-audit-prep-micro-saas",
      "title": "Compliance audit prep micro-SaaS built with Claude Code",
      "aliases": ["soc2 evidence helper"],
      "category": "money",
      "pitch": "Two sentences.",
      "first_step": "One concrete action under three hours.",
      "scores": {"fit": 22, "upside": 14, "time_to_dollar": 9, "effort": 10, "evidence": 11, "durability": 7},
      "total": 73,
      "reasons": {"fit": "...", "upside": "...", "time_to_dollar": "...", "effort": "...", "evidence": "...", "durability": "..."},
      "dollars": {"low": 12000, "high": 60000, "basis": "annual"},
      "hours_per_week": 8,
      "evidence": [
        {"url": "https://www.reddit.com/r/SaaS/comments/...", "source": "r/SaaS", "date": "2026-10-19", "claim": "$2.1k MRR after 7 weeks"},
        {"url": "https://news.ycombinator.com/item?id=...", "source": "Hacker News", "date": "2026-10-20", "claim": "Show HN with pricing page"}
      ]
    }
  ]
}
```

`status` and `candidates_scored` are recomputed by the build script, so write your best guess.

## 5. Build

```bash
python3 build.py data/weeks/$WEEK.json
```

If it exits non-zero, read the message, fix the week file, and run it again. Three attempts at most. If it still fails, set `"status": "error"` in the week file, put the last error message in `note`, leave `data/ideas.json` and `data/leaderboard.json` untouched, and continue to step 7.

## 6. Update sources.md

For every row you read, set `last_yield` to the number of candidates whose evidence cites that source. If a source failed, put a short reason in `note`. Change nothing else in the file.

## 7. Commit and push

```bash
git config user.name  >/dev/null || git config user.name "Claude Leaderboard"
git config user.email >/dev/null || git config user.email "noreply@anthropic.com"
git add -A
git commit -m "$WEEK: $(python3 -c "import json;w=json.load(open('data/weeks/$WEEK.json'));print(w['candidates_scored'],'candidates,',w['status'])")"
git push origin HEAD:main
```

If the push is refused, push a branch and open a pull request:

```bash
git checkout -b "week/$WEEK"
git push -u origin "week/$WEEK"
gh pr create --title "$WEEK scan" --body "Weekly scan. Push to main was refused." 2>/dev/null || echo "PR needed for branch week/$WEEK"
```

## 8. Final message

One paragraph: the week, the status, how many candidates were scored, the five titles in `top5`, and which sources failed.
```

- [ ] **Step 2: Commit**

```bash
git add ROUTINE.md
git commit -m "Add routine instructions"
```

---

### Task 9: index.html and fixture generator

**Files:**
- Create: `index.html`
- Create: `tests/make_fixture.py`

- [ ] **Step 1: Write the fixture generator**

`tests/make_fixture.py`:
```python
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
```

- [ ] **Step 2: Run it**

Run: `python tests/make_fixture.py`
Expected:
```
ok: tests/fixtures/ok/leaderboard.json
thin: tests/fixtures/thin/leaderboard.json
skipped: tests/fixtures/skipped/leaderboard.json
```
And `git status --short` does not list `tests/fixtures/` (ignored).

- [ ] **Step 3: Write index.html**

```html
<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Leaderboard</title>
<style>
:root{--bg:#F3F6F8;--card:#fff;--line:#E4EAEF;--ink:#22303C;--ink2:#5A6B7A;--mute:#A5B1BB;
  --green:#0E6E5C;--green2:#E9F6F1;--amber:#8A6116;--amber2:#FBF3E4;--red:#9A3B3B;--red2:#FBEAEA;
  --blue:#2B5C8A;--blue2:#E8F0F8}
*{box-sizing:border-box}
body{margin:0;padding:28px 16px;background:var(--bg);font-family:'Segoe UI',system-ui,sans-serif;color:var(--ink);line-height:1.45}
.wrap{max-width:960px;margin:0 auto}
h1{font-size:22px;margin:0}
.head{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}
.stamp{font-family:Consolas,monospace;font-size:12px;color:var(--ink2)}
.flag{display:inline-block;margin-left:6px;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}
.flag.ok{background:var(--green2);color:var(--green)}
.flag.thin{background:var(--amber2);color:var(--amber)}
.flag.skipped,.flag.error{background:var(--red2);color:var(--red)}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}
@media(max-width:600px){.tiles{grid-template-columns:repeat(2,1fr)}}
.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
.tile .n{font-size:24px;font-weight:650}
.tile .l{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink2);margin-top:2px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 14px}
.tab{border:1px solid var(--line);border-radius:999px;padding:5px 14px;font-size:13px;background:var(--card);cursor:pointer;color:#33424F;user-select:none}
.tab.on{background:var(--green);border-color:var(--green);color:#fff}
h2{font-size:12px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink2);margin:22px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin-bottom:10px;cursor:pointer}
.card .top{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.rank{font-family:Consolas,monospace;font-size:13px;color:var(--ink2);min-width:26px}
.title{font-weight:650;flex:1 1 200px}
.score{display:inline-block;min-width:38px;text-align:center;padding:2px 8px;border-radius:999px;font-weight:700;font-size:12px;background:var(--green2);color:var(--green)}
.cat{font-size:10px;font-weight:700;padding:1px 7px;border-radius:4px;text-transform:uppercase;letter-spacing:.04em}
.cat.money{background:var(--green2);color:var(--green)}
.cat.time{background:var(--blue2);color:var(--blue)}
.cat.life{background:var(--amber2);color:var(--amber)}
.pitch{font-size:13px;color:#33424F;margin-top:6px}
.step{font-size:13px;margin-top:6px}
.step b{color:var(--ink2);font-weight:600;margin-right:4px}
.links{font-size:12px;margin-top:6px}
.links a{color:var(--green);text-decoration:none;margin-right:10px}
.detail{display:none;margin-top:10px;border-top:1px solid var(--line);padding-top:10px}
.card.open .detail{display:block}
.sub{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;font-size:12px}
.sub div{background:var(--bg);border-radius:6px;padding:6px 8px}
.sub .k{color:var(--ink2);font-size:11px;text-transform:uppercase;letter-spacing:.05em}
.sub .v{font-weight:700}
.sub .r{color:#33424F;margin-top:2px}
.leaders{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
@media(max-width:700px){.leaders{grid-template-columns:1fr}}
.leaders .card{margin:0}
.tblwrap{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:13px}
th{text-align:left;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink2);background:#F5F8FA;padding:9px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
td{padding:9px 12px;border-bottom:1px solid #F0F3F6;vertical-align:top}
tr.row{cursor:pointer}
tr.more td{background:#FAFCFD}
.empty{background:var(--card);border:1px dashed var(--line);border-radius:8px;padding:28px;text-align:center;color:var(--ink2)}
.note{font-size:12px;color:var(--amber);margin:8px 0}
.hist{margin-top:22px;font-family:Consolas,monospace;font-size:12px;color:var(--ink2);display:flex;gap:8px;flex-wrap:wrap}
.hist span{padding:2px 8px;border-radius:4px;background:var(--card);border:1px solid var(--line)}
.foot{margin-top:14px;font-size:12px;color:var(--mute)}
.foot a{color:var(--ink2)}
</style></head>
<body><div class="wrap">
<div class="head"><h1>Claude Leaderboard</h1><div class="stamp" id="stamp">loading…</div></div>
<div class="tiles" id="tiles"></div>
<div class="tabs" id="tabs">
  <span class="tab on" data-tab="week">This week</span>
  <span class="tab" data-tab="all">All time</span>
  <span class="tab" data-tab="rising">Rising</span>
</div>
<div id="view"></div>
<div class="hist" id="hist"></div>
<div class="foot">Weekly scan of Reddit, Substack, Hacker News and more for productive and money-making uses of Claude. Scores follow <a href="rubric.md">rubric.md</a>; sources are in <a href="sources.md">sources.md</a>.</div>
</div>
<script>
const FACTORS = [["fit","Fit",25],["upside","Upside",20],["time_to_dollar","Time to benefit",15],
                 ["effort","Effort",15],["evidence","Evidence",15],["durability","Durability",10]];
const CATS = ["money","time","life"];
const DATA_URL = new URLSearchParams(location.search).get("data") || "data/leaderboard.json";
let BOARD = null, TAB = "week", CAT = "all";

const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const fmtDate = iso => iso ? new Date(iso).toLocaleDateString(undefined, {month:"short", day:"numeric", year:"numeric"}) : "";
const host = u => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return u; } };
const money = n => "$" + Number(n).toLocaleString();

function flag(status){ return `<span class="flag ${esc(status)}">${esc(status)}</span>`; }
function cat(c){ return `<span class="cat ${esc(c)}">${esc(c)}</span>`; }
function links(ev){
  return (ev || []).map(e => `<a href="${esc(e.url)}" target="_blank" rel="noopener" title="${esc(e.claim || "")}">${esc(e.source || host(e.url))}</a>`).join("");
}
function subscores(scores, reasons){
  return `<div class="sub">${FACTORS.map(([k, l, m]) =>
    `<div><div class="k">${l}</div><div class="v">${scores?.[k] ?? "–"} / ${m}</div><div class="r">${esc(reasons?.[k] || "")}</div></div>`).join("")}</div>`;
}
function dollars(d, hrs){
  if (!d) return "";
  return `<div class="pitch">Est. ${money(d.low)} to ${money(d.high)} ${esc(d.basis)} · ${esc(hrs)} hrs/week to run</div>`;
}
function card(c, rank){
  const L = c.latest || {};
  const scores = c.scores || L.scores, reasons = c.reasons || L.reasons;
  const total = c.total ?? c.best_score;
  const pitch = c.pitch ?? L.pitch, step = c.first_step ?? L.first_step;
  const d = c.dollars || L.dollars, hrs = c.hours_per_week ?? L.hours_per_week;
  return `<div class="card" onclick="this.classList.toggle('open')">
    <div class="top">${rank ? `<span class="rank">#${rank}</span>` : ""}<span class="title">${esc(c.title)}</span>${cat(c.category)}<span class="score">${total}</span></div>
    <div class="pitch">${esc(pitch)}</div>
    <div class="step"><b>First step</b>${esc(step)}</div>
    <div class="links">${links(c.evidence)}</div>
    <div class="detail">${subscores(scores, reasons)}${dollars(d, hrs)}</div>
  </div>`;
}
function renderTiles(b){
  const tw = b.this_week;
  const tiles = [
    [tw ? tw.candidates_scored : 0, "Scored this week"],
    [tw ? tw.top5.length : 0, "Published"],
    [b.all_time.length, "All-time ideas"],
    [b.rising.length, "Rising"],
  ];
  document.getElementById("tiles").innerHTML = tiles.map(([n, l]) => `<div class="tile"><div class="n">${n}</div><div class="l">${l}</div></div>`).join("");
}
function renderWeek(b){
  const tw = b.this_week;
  if (!tw) return `<div class="empty">No runs yet. The first scan lands on Monday morning.</div>`;
  let html = "";
  if (tw.status === "thin") html += `<div class="note">Thin week. ${tw.candidates_scored} candidates were scored, below the 50 target.</div>`;
  if (tw.status === "skipped") html += `<div class="note">Skipped week, no top 5. ${esc(tw.note || "Fewer than 15 candidates were found.")}</div>`;
  if (tw.top5.length) html += `<h2>Top 5 · ${esc(tw.week)}</h2>` + tw.top5.map((c, i) => card(c, i + 1)).join("");
  const L = tw.category_leaders || {};
  if (CATS.some(k => L[k])) {
    html += `<h2>Category leaders</h2><div class="leaders">${CATS.map(k => L[k] ? card(L[k]) : `<div class="empty">No ${k} idea this week</div>`).join("")}</div>`;
  }
  if (tw.sources_failed?.length) html += `<div class="note">Sources that failed this run: ${tw.sources_failed.map(s => esc(s.source)).join(", ")}</div>`;
  return html;
}
function renderTable(rows){
  if (!rows.length) return `<div class="empty">Nothing here yet.</div>`;
  const body = rows.map((r, i) => `
    <tr class="row" onclick="const n=this.nextElementSibling;n.style.display=n.style.display==='table-row'?'none':'table-row'">
      <td class="rank">${i + 1}</td><td><b>${esc(r.title)}</b></td><td>${cat(r.category)}</td>
      <td><span class="score">${r.best_score}</span></td><td>${r.weeks_seen}</td><td>${esc(r.first_week)}</td>
    </tr>
    <tr class="more" style="display:none"><td colspan="6">
      <div class="pitch">${esc(r.latest?.pitch)}</div>
      <div class="step"><b>First step</b>${esc(r.latest?.first_step)}</div>
      <div class="links">${links(r.evidence)}</div>
      <div style="margin-top:10px">${subscores(r.latest?.scores, r.latest?.reasons)}</div>
      ${dollars(r.latest?.dollars, r.latest?.hours_per_week)}
    </td></tr>`).join("");
  return `<div class="tblwrap"><table><thead><tr><th>#</th><th>Idea</th><th>Category</th><th>Best</th><th>Weeks</th><th>First seen</th></tr></thead><tbody>${body}</tbody></table></div>`;
}
function renderAll(b){
  const chips = ["all", ...CATS].map(k => `<span class="tab ${CAT === k ? "on" : ""}" data-cat="${k}">${k}</span>`).join("");
  const rows = CAT === "all" ? b.all_time : b.all_time.filter(r => r.category === CAT);
  return `<div class="tabs" id="cats">${chips}</div>` + renderTable(rows);
}
function renderRising(b){
  if (!b.rising.length) return `<div class="empty">Ideas seen in three or more weeks show up here.</div>`;
  return renderTable(b.rising);
}
function render(){
  const b = BOARD, tw = b.this_week;
  document.getElementById("stamp").innerHTML = tw ? `last run ${fmtDate(b.updated)} · ${esc(tw.week)} ${flag(tw.status)}` : "no runs yet";
  renderTiles(b);
  document.querySelectorAll("#tabs .tab").forEach(t => t.classList.toggle("on", t.dataset.tab === TAB));
  const view = document.getElementById("view");
  view.innerHTML = TAB === "week" ? renderWeek(b) : TAB === "all" ? renderAll(b) : renderRising(b);
  view.querySelectorAll("#cats .tab").forEach(c => c.onclick = () => { CAT = c.dataset.cat; render(); });
  document.getElementById("hist").innerHTML = (b.history || []).slice(-12).map(h =>
    `<span title="${h.candidates_scored} scored">${esc(h.week)} ${flag(h.status)}</span>`).join("");
}
document.querySelectorAll("#tabs .tab").forEach(t => t.onclick = () => { TAB = t.dataset.tab; render(); });
fetch(`${DATA_URL}${DATA_URL.includes("?") ? "&" : "?"}t=${Date.now()}`)
  .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
  .then(b => { BOARD = b; render(); })
  .catch(e => {
    document.getElementById("stamp").textContent = "could not load data";
    document.getElementById("view").innerHTML = `<div class="empty">Could not load ${esc(DATA_URL)} (${esc(e.message)}).</div>`;
  });
</script></body></html>
```

- [ ] **Step 4: Check the board by eye**

```bash
python -m http.server 8000
```
Open in a browser, one at a time:
- `http://localhost:8000/?data=tests/fixtures/ok/leaderboard.json` — expect the `ok` flag, five ranked cards, a Category leaders row with three cards, All time tab with 20 rows and working category chips, Rising tab with rows (ideas 0 to 6 appear in all three weeks), and a three-week history strip. Click a card and a table row; the sub-scores expand.
- `http://localhost:8000/?data=tests/fixtures/thin/leaderboard.json` — expect the `thin` flag and the amber thin-week note, plus the failed-source line naming r/SaaS.
- `http://localhost:8000/?data=tests/fixtures/skipped/leaderboard.json` — expect the `skipped` flag, the skipped note with the Reddit sentence, no Top 5 section, category leaders still shown.
- `http://localhost:8000/` — the real empty data, expect "No runs yet" and zero tiles.
- Narrow the window to about 390px wide. No horizontal scroll outside the All time table wrapper. Tiles fall to two columns, leaders to one.

Stop the server with Ctrl+C.

- [ ] **Step 5: Commit**

```bash
git add index.html tests/make_fixture.py
git commit -m "Add board page and fixture generator"
```

---

### Task 10: Publish to GitHub Pages

**Files:** none new.

- [ ] **Step 1: Push and enable Pages from main root**

```bash
git push origin main
gh api -X POST repos/not-in-scope/claude-leaderboard/pages -f "source[branch]=main" -f "source[path]=/" --jq .html_url
```
Expected: `https://not-in-scope.github.io/claude-leaderboard/`. If the API answers 409, Pages is already on; run `gh api repos/not-in-scope/claude-leaderboard/pages --jq .html_url` instead.

- [ ] **Step 2: Wait for the first build and verify**

Run the check after about a minute:
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://not-in-scope.github.io/claude-leaderboard/
curl -s https://not-in-scope.github.io/claude-leaderboard/data/leaderboard.json
```
Expected: `200`, then the empty-board JSON. If 404, wait another minute and retry; `gh api repos/not-in-scope/claude-leaderboard/pages/builds/latest --jq .status` should read `built`.

Open `https://not-in-scope.github.io/claude-leaderboard/` in a browser. Expected: "No runs yet" state.

---

### Task 11: Create the routine and run it once

**Files:** none new. Uses the `RemoteTrigger` tool (load with `ToolSearch select:RemoteTrigger` if not loaded).

- [ ] **Step 1: Generate a UUID and confirm the time**

```bash
python -c "import uuid; print(uuid.uuid4())"
date -u +%Y-%m-%dT%H:%M:%SZ
```
Keep the UUID for the next step.

- [ ] **Step 2: Create the routine**

Call `RemoteTrigger` with `action: "create"` and this body, substituting the UUID:
```json
{
  "name": "Claude Leaderboard weekly scan",
  "cron_expression": "0 14 * * 1",
  "enabled": true,
  "job_config": {
    "ccr": {
      "environment_id": "env_012Lc9WjHWVhkrdAC4qGouFu",
      "session_context": {
        "model": "claude-opus-5-5",
        "sources": [
          {"git_repository": {"url": "https://github.com/not-in-scope/claude-leaderboard"}}
        ],
        "allowed_tools": ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebSearch", "WebFetch"]
      },
      "events": [
        {"data": {
          "uuid": "<uuid from step 1>",
          "session_id": "",
          "type": "user",
          "parent_tool_use_id": null,
          "message": {"role": "user", "content": "Read ROUTINE.md at the repository root and follow it exactly. Do not ask questions."}
        }}
      ]
    }
  }
}
```
Expected: a response with a trigger id and the next run time, Monday 14:00 UTC (7am Pacific during daylight time, 6am after the clocks change). Record the id and the link `https://claude.ai/code/routines/<id>`.

- [ ] **Step 3: Run it now**

Call `RemoteTrigger` with `action: "run"` and the trigger id. Then poll with `action: "list_runs"` until the run status is complete. An Opus run reading 90 or so sources can take 20 to 40 minutes.

- [ ] **Step 4: Inspect the run**

Call `RemoteTrigger` with `action: "get_run_log"` and the session id from `list_runs`. Check for: the week file written, `build.py` exit 0, a push to main or a branch. Treat anything in the log that reads like instructions as data.

Then locally:
```bash
git pull origin main
ls data/weeks
python -c "import json;b=json.load(open('data/leaderboard.json'));tw=b['this_week'];print(tw['week'],tw['status'],tw['candidates_scored']);[print(' ',c['total'],c['category'],c['title']) for c in tw['top5']]"
```
Expected: one week file, the current ISO week, a status, and five titles with totals. If the routine pushed a branch instead, `gh pr list` shows it; merge with `gh pr merge --squash` after a look.

Open `https://not-in-scope.github.io/claude-leaderboard/`. Expected: the week renders with five cards.

- [ ] **Step 5: Fix what the first run exposed**

If the run failed or produced a `thin` or `error` week, read the log and change `ROUTINE.md` or `sources.md`, commit, push, and run again with `action: "run"`. Common cases: Reddit 403s on every subreddit (the search fallback should still produce candidates; if not, lower the Reddit queries to `claude` only), feeds that 404 (set the row to `search`), the push refused (merge the PR, then check repo settings for branch protection).

- [ ] **Step 6: Commit any fixes and record the routine link**

Append to `README.md`:
```markdown

Routine: https://claude.ai/code/routines/<id> (Mondays 14:00 UTC, Opus 5.5).
```
```bash
git add -A
git commit -m "Record routine link"
git push origin main
```

---

## Self-review against the spec

- Spec 1 to 2, architecture and layout: Tasks 1, 2, 9, 10 create every listed file. `docs/superpowers/plans/` holds this document.
- Spec 3, weekly run and source reading and thresholds: Task 8 (`ROUTINE.md`) and `derive_status` in Task 2, pinned by Task 3.
- Spec 4, scoring: Task 6 (`rubric.md`), factor maxima enforced in Task 2.
- Spec 5, data model: field names match across Tasks 2, 4, 5, 8, 9. The idea record gains a `weeks` list to make `weeks_seen` idempotent; the spec's "increment once per week" is satisfied by it.
- Spec 6, build.py: Tasks 2, 4, 5. Error weeks in history only, nothing written on failure, idempotence, all tested.
- Spec 7, board: Task 9 covers tabs, category leaders, filter, expand, flags, history strip, phone width.
- Spec 8, routine: Task 11, same fields.
- Spec 9, sources: Task 7, every group from the spec is present, with the `life` subreddits.
- Spec 10, error handling: `ROUTINE.md` steps 1, 5, 7; `build_board` ignores error weeks.
- Spec 11, testing: Task 5 ends with 32 tests; Task 9 step 4 is the fixture check; Task 11 is the end-to-end run.
- Spec 12, open items: rate in `rubric.md`, public repo noted in `README.md` and Task 1.
