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
