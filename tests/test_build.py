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
        "run_at": "2026-10-26T14:00:00Z",
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
    with pytest.raises(build.ValidationError, match="week must look like"):
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


# ---- board ----

def test_all_time_capped_and_sorted(monkeypatch):
    monkeypatch.setattr(build, "ALL_TIME_N", 20)
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
    assert len(tw["candidates"]) == 50
    assert [c["total"] for c in tw["candidates"]] == sorted((c["total"] for c in tw["candidates"]), reverse=True)
    assert tw["candidates"][0]["id"] == "idea-007"
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
    assert board == {"updated": None, "this_week": None, "all_time": [], "rising": [],
                     "picks": {"interested": [], "trying": [], "hidden": []}, "history": []}


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


# ---- hardening ----

def test_aliases_must_be_list_of_strings():
    w = week_file(50)
    w["candidates"][0]["aliases"] = "soc2 helper"
    with pytest.raises(build.ValidationError, match="aliases"):
        build.validate_week(w)
    w["candidates"][0]["aliases"] = ["ok", ""]
    with pytest.raises(build.ValidationError, match="aliases"):
        build.validate_week(w)


def test_week_must_be_dict():
    with pytest.raises(build.ValidationError, match="object"):
        build.validate_week([])


def test_non_dict_candidate_rejected():
    w = week_file(50)
    w["candidates"][1] = "oops"
    with pytest.raises(build.ValidationError, match="candidate 1"):
        build.validate_week(w)


@pytest.mark.parametrize("bad", [["idea-000"], ""])
def test_bad_id_rejected(bad):
    w = week_file(50)
    w["candidates"][0]["id"] = bad
    with pytest.raises(build.ValidationError, match="id"):
        build.validate_week(w)


def test_float_total_rejected():
    w = week_file(50)
    w["candidates"][0]["total"] = 70.0
    with pytest.raises(build.ValidationError, match="total"):
        build.validate_week(w)


def test_week_id_out_of_range_rejected():
    w = week_file(50, week="2026-W54")
    with pytest.raises(build.ValidationError, match="week must look like"):
        build.validate_week(w)


def test_category_leader_tie_picks_lowest_id():
    w = week_file(50)
    w["candidates"][3] = candidate(3, category="time", total=72)
    w["candidates"][7] = candidate(7, category="time", total=72)
    ideas = build.merge([], build.validate_week(w))
    board = build.build_board(ideas, [w])
    assert board["this_week"]["category_leaders"]["time"]["id"] == "idea-003"


def test_run_survives_malformed_older_week(data_dir):
    (data_dir / "weeks" / "2026-W45.json").write_text('{"status":"ok"}', encoding="utf-8")
    (data_dir / "weeks" / "2026-W46.json").write_text("not json", encoding="utf-8")
    board = build.run(write_week(data_dir, week_file(50, week="2026-W44")), data_dir)
    hist = {h["week"]: h["status"] for h in board["history"]}
    assert hist == {"2026-W44": "ok", "2026-W45": "error", "2026-W46": "error"}
    assert board["this_week"]["week"] == "2026-W44"


def test_run_rejects_week_outside_weeks_dir(data_dir):
    p = data_dir / "2026-W44.json"
    p.write_text(json.dumps(week_file(50)), encoding="utf-8")
    with pytest.raises(build.ValidationError, match="must live in"):
        build.run(p, data_dir)


def test_main_returns_1_on_missing_file(data_dir, capsys):
    assert build.main(["build.py", str(data_dir / "weeks" / "nope.json"), str(data_dir)]) == 1
    assert capsys.readouterr().err


def test_load_json_accepts_bom(tmp_path):
    p = tmp_path / "x.json"
    p.write_bytes("﻿{\"a\": 1}".encode("utf-8"))
    assert build.load_json(p) == {"a": 1}


def test_year_boundary_merge():
    ideas = []
    build.merge(ideas, build.validate_week(week_file(50, week="2026-W52")))
    build.merge(ideas, build.validate_week(week_file(50, week="2027-W01")))
    rec = ideas[0]
    assert rec["last_week"] == "2027-W01" and rec["weeks_seen"] == 2


def test_skipped_week_becomes_this_week_via_run(data_dir):
    build.run(write_week(data_dir, week_file(50, week="2026-W44")), data_dir)
    board = build.run(write_week(data_dir, week_file(10, week="2026-W45")), data_dir)
    assert board["this_week"]["week"] == "2026-W45"
    assert board["this_week"]["status"] == "skipped"
    assert board["this_week"]["top5"] == []


def test_top5_non_string_entry_rejected():
    w = week_file(50, top5=["idea-000", "idea-001", "idea-002", "idea-003", {"id": "x"}])
    with pytest.raises(build.ValidationError, match="top5"):
        build.validate_week(w)


def test_error_week_minimal_keys_kept_in_history(data_dir):
    err = {"week": "2026-W43", "status": "error", "candidates_scored": 7, "note": "boom"}
    (data_dir / "weeks" / "2026-W43.json").write_text(json.dumps(err), encoding="utf-8")
    board = build.run(write_week(data_dir, week_file(50, week="2026-W44")), data_dir)
    row = next(h for h in board["history"] if h["week"] == "2026-W43")
    assert row == {"week": "2026-W43", "status": "error", "candidates_scored": 7}


def test_error_week_with_non_string_week_becomes_stub(data_dir):
    err = {"week": 44, "status": "error", "candidates_scored": 7}
    (data_dir / "weeks" / "2026-W43.json").write_text(json.dumps(err), encoding="utf-8")
    board = build.run(write_week(data_dir, week_file(50, week="2026-W44")), data_dir)
    row = next(h for h in board["history"] if h["week"] == "2026-W43")
    assert row == {"week": "2026-W43", "status": "error", "candidates_scored": 0}


@pytest.mark.parametrize("url", ["javascript:alert(1)", "//evil", 5])
def test_evidence_url_must_be_http(url):
    w = week_file(50)
    w["candidates"][0]["evidence"][0]["url"] = url
    with pytest.raises(build.ValidationError, match="url"):
        build.validate_week(w)


def test_dollars_missing_high_rejected():
    w = week_file(50)
    del w["candidates"][0]["dollars"]["high"]
    with pytest.raises(build.ValidationError, match="dollars"):
        build.validate_week(w)


def test_dollars_low_above_high_rejected():
    w = week_file(50)
    w["candidates"][0]["dollars"].update(low=9000, high=100)
    with pytest.raises(build.ValidationError, match="dollars"):
        build.validate_week(w)


def test_rising_capped():
    ideas, weeks = [], []
    for wk in ("2026-W44", "2026-W45", "2026-W46"):
        w = week_file(50, week=wk)
        build.validate_week(w)
        build.merge(ideas, w)
        weeks.append(w)
    board = build.build_board(ideas, weeks)
    assert len(board["rising"]) == build.RISING_N == 20


# ---- feedback ----

FB = {"idea-001": {"vote": "no", "reason": "skills", "outcome": "", "at": "2026-10-27T18:00:00Z"},
      "idea-002": {"vote": "interested", "reason": None, "outcome": "", "at": "2026-10-27T18:01:00Z"},
      "idea-003": {"vote": "trying", "reason": None, "outcome": "built it", "at": "2026-10-27T18:02:00Z"}}
TOP5_OK = ["idea-000", "idea-002", "idea-003", "idea-004", "idea-005"]


def test_top5_may_not_hold_rejected_idea():
    w = week_file(50)
    with pytest.raises(build.ValidationError, match="rejected"):
        build.validate_week(w, FB)


def test_top5_without_rejected_idea_passes_with_feedback():
    w = week_file(50, top5=TOP5_OK)
    build.validate_week(w, FB)
    assert w["status"] == "ok"


def test_board_picks_and_hidden():
    w = week_file(50, top5=TOP5_OK)
    w["feedback_note"] = "Hid one content idea."
    ideas = build.merge([], build.validate_week(w, FB))
    board = build.build_board(ideas, [w], FB)
    ids = [r["id"] for r in board["all_time"]]
    assert "idea-001" not in ids and "idea-002" in ids
    assert [r["id"] for r in board["picks"]["hidden"]] == ["idea-001"]
    assert [r["id"] for r in board["picks"]["interested"]] == ["idea-002"]
    assert [r["id"] for r in board["picks"]["trying"]] == ["idea-003"]
    assert board["picks"]["trying"][0]["feedback"]["outcome"] == "built it"
    assert next(r for r in board["all_time"] if r["id"] == "idea-000")["feedback"] is None
    assert board["this_week"]["feedback_note"] == "Hid one content idea."


def test_rising_excludes_hidden():
    ideas, weeks = [], []
    for wk in ("2026-W44", "2026-W45", "2026-W46"):
        w = build.validate_week(week_file(50, week=wk, top5=TOP5_OK), FB)
        build.merge(ideas, w)
        weeks.append(w)
    board = build.build_board(ideas, weeks, FB)
    assert "idea-001" not in {r["id"] for r in board["rising"]}


def test_board_without_feedback_has_empty_picks():
    w = build.validate_week(week_file(50))
    board = build.build_board(build.merge([], w), [w])
    assert board["picks"] == {"interested": [], "trying": [], "hidden": []}
    assert board["this_week"]["feedback_note"] == ""
    assert all(r["feedback"] is None for r in board["all_time"])


def test_run_reads_feedback_file_and_renders_pages(data_dir):
    (data_dir / "feedback.json").write_text(json.dumps(FB), encoding="utf-8")
    (data_dir.parent / "board.html").write_text("<title>T</title>\n<div>hi</div>\n", encoding="utf-8")
    p = write_week(data_dir, week_file(50, top5=TOP5_OK))
    board = build.run(p, data_dir)
    assert [r["id"] for r in board["picks"]["interested"]] == ["idea-002"]
    page = (data_dir.parent / "index.html").read_text(encoding="utf-8")
    assert page.startswith("<!doctype html>") and "<div>hi</div>" in page and page.rstrip().endswith("</html>")


def test_run_rejects_top5_with_rejected_idea(data_dir):
    (data_dir / "feedback.json").write_text(json.dumps(FB), encoding="utf-8")
    p = write_week(data_dir, week_file(50))
    with pytest.raises(build.ValidationError, match="rejected"):
        build.run(p, data_dir)
    assert not (data_dir / "leaderboard.json").exists()


def test_malformed_feedback_file_is_ignored(data_dir):
    (data_dir / "feedback.json").write_text("not json", encoding="utf-8")
    board = build.run(write_week(data_dir, week_file(50)), data_dir)
    assert board["picks"]["hidden"] == []
