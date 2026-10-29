#!/usr/bin/env python3
"""Validate a week file, merge it into the idea registry, and emit the board data.

Usage: python build.py data/weeks/2026-W44.json
It uses only the standard library. Exits 1 on validation failure and writes nothing.
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
TOP_N = 5
EVIDENCE_MIN = 2
EVIDENCE_MAX = 5
EVIDENCE_KEEP = 10
ALL_TIME_N = 500
RISING_MIN_WEEKS = 3
RISING_N = 20
WEEK_RE = re.compile(r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")

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
    if not isinstance(c, dict):
        raise ValidationError(f"candidate {i}: must be an object")
    label = f"candidate {i} ({c.get('id', '?')})"
    missing = CANDIDATE_KEYS - c.keys()
    if missing:
        raise ValidationError(f"{label}: missing keys {sorted(missing)}")
    for key in ("id", "title"):
        if not isinstance(c[key], str) or not c[key].strip():
            raise ValidationError(f"{label}: {key} must be a non-empty string")
    aliases = c.get("aliases", [])
    if not isinstance(aliases, list) or not all(isinstance(a, str) and a.strip() for a in aliases):
        raise ValidationError(f"{label}: aliases must be a list of non-empty strings")
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
    if not isinstance(c["total"], int) or isinstance(c["total"], bool):
        raise ValidationError(f"{label}: total must be an int")
    if c["total"] != sum(scores.values()):
        raise ValidationError(f"{label}: total {c['total']} != sum of scores {sum(scores.values())}")
    ev = c["evidence"]
    if not isinstance(ev, list) or not EVIDENCE_MIN <= len(ev) <= EVIDENCE_MAX:
        raise ValidationError(f"{label}: evidence needs {EVIDENCE_MIN}..{EVIDENCE_MAX} links")
    for e in ev:
        if not isinstance(e, dict) or not e.get("url"):
            raise ValidationError(f"{label}: every evidence item needs a url")
        if not isinstance(e["url"], str) or not e["url"].startswith(("http://", "https://")):
            raise ValidationError(f"{label}: evidence url must start with http:// or https://")
    d = c["dollars"]
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    if (not isinstance(d, dict) or not num(d.get("low")) or not num(d.get("high"))
            or d["low"] > d["high"] or not isinstance(d.get("basis"), str) or not d["basis"].strip()):
        raise ValidationError(f"{label}: dollars needs numeric low <= high and a basis string")


VOTES = ("interested", "no", "trying")


def rejected_ids(feedback):
    """Idea ids Stephen marked 'no'. feedback is the votes map or None."""
    if not isinstance(feedback, dict):
        return set()
    return {k for k, v in feedback.items() if isinstance(v, dict) and v.get("vote") == "no"}


def validate_week(week, feedback=None):
    """Validate and normalise a week dict in place. Raises ValidationError.
    With feedback, top5 may not hold an idea voted 'no'."""
    if not isinstance(week, dict):
        raise ValidationError("week file must be a JSON object")
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
            raise ValidationError(f"top5 must be empty when fewer than {THIN_MIN} candidates")
    else:
        if not isinstance(top5, list) or not all(isinstance(t, str) for t in top5):
            raise ValidationError("top5 must be a list of id strings")
        if len(top5) != TOP_N or len(set(top5)) != TOP_N:
            raise ValidationError(f"top5 must hold exactly {TOP_N} distinct ids")
        unknown = [s for s in top5 if s not in ids]
        if unknown:
            raise ValidationError(f"top5 ids not in candidates: {unknown}")
        rejected = [s for s in top5 if s in rejected_ids(feedback)]
        if rejected:
            raise ValidationError(f"top5 holds ideas Stephen rejected, pick others: {rejected}")
    if "feedback_note" in week and not isinstance(week["feedback_note"], str):
        raise ValidationError("feedback_note must be a string")
    return week


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


def build_board(ideas, weeks, feedback=None):
    """Board data from the registry and every week dict. Weeks with status
    'error' appear in history only. Ideas voted 'no' leave all_time and
    rising and sit under picks.hidden."""
    feedback = feedback if isinstance(feedback, dict) else {}
    ideas = [dict(r, feedback=feedback.get(r["id"]) or None) for r in ideas]
    hidden_ids = rejected_ids(feedback)
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
            leaders[cat] = sorted(pool, key=lambda c: (-c["total"], c["id"]))[0] if pool else None
        this_week = {
            "week": w["week"],
            "status": w["status"],
            "note": w.get("note", ""),
            "candidates_scored": w["candidates_scored"],
            "sources_failed": w.get("sources_failed", []),
            "top5": [by_id[s] for s in w["top5"]],
            "category_leaders": leaders,
            "candidates": sorted(w["candidates"], key=lambda c: (-c["total"], c["id"])),
            "feedback_note": w.get("feedback_note", ""),
        }
    shown = [r for r in ideas if r["id"] not in hidden_ids]
    all_time = sorted(shown, key=lambda r: (-r["best_score"], r["first_week"], r["id"]))[:ALL_TIME_N]
    rising = sorted((r for r in shown if r["weeks_seen"] >= RISING_MIN_WEEKS),
                    key=lambda r: (-r["weeks_seen"], -r["best_score"], r["id"]))[:RISING_N]
    by_vote = lambda v: sorted((r for r in ideas if (r["feedback"] or {}).get("vote") == v),
                               key=lambda r: (-r["best_score"], r["id"]))
    picks = {"interested": by_vote("interested"), "trying": by_vote("trying"), "hidden": by_vote("no")}
    return {"updated": updated, "this_week": this_week, "all_time": all_time,
            "rising": rising, "picks": picks, "history": history}


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def dump_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")


def _load_week_or_error(path):
    """Load a stored week file. A file that is unreadable or invalid becomes
    an error stub so it shows in history and nothing else."""
    try:
        week = load_json(path)
        if not isinstance(week, dict):
            raise ValidationError("not an object")
        if week.get("status") == "error":
            if not isinstance(week.get("week"), str):
                raise ValidationError("week must be a string")
            return week
        return validate_week(week)
    except (ValidationError, OSError, ValueError):
        return {"week": Path(path).stem, "status": "error", "candidates_scored": 0,
                "note": "", "sources_failed": [], "top5": [], "candidates": []}


PAGE_HEAD = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
             '<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head>\n<body>\n')
PAGE_TAIL = "\n</body></html>\n"


def render_pages(board_html_path, out_path):
    """Wrap the Artifact page source in a document skeleton for GitHub Pages."""
    body = Path(board_html_path).read_text(encoding="utf-8-sig")
    out_path = Path(out_path)
    out_path.write_text(PAGE_HEAD + body.rstrip("\n") + PAGE_TAIL, encoding="utf-8", newline="\n")
    return out_path


def load_feedback(data_dir):
    """The votes snapshot the routine writes, or {} when absent or unreadable."""
    path = Path(data_dir) / "feedback.json"
    if not path.exists():
        return {}
    try:
        fb = load_json(path)
    except (OSError, ValueError):
        return {}
    return fb if isinstance(fb, dict) else {}


def run(week_path, data_dir):
    """Validate the week file, merge it, and rewrite the data files.
    The week file must live in <data_dir>/weeks/. Nothing is written if
    validation fails. When board.html sits beside the data folder,
    index.html is regenerated from it."""
    week_path = Path(week_path)
    data_dir = Path(data_dir)
    weeks_dir = data_dir / "weeks"
    if week_path.resolve().parent != weeks_dir.resolve():
        raise ValidationError(f"week file must live in {weeks_dir}")
    ideas_path = data_dir / "ideas.json"
    board_path = data_dir / "leaderboard.json"

    feedback = load_feedback(data_dir)
    week = validate_week(load_json(week_path), feedback)
    ideas = load_json(ideas_path) if ideas_path.exists() else []
    merge(ideas, week)

    dump_json(week_path, week)
    dump_json(ideas_path, ideas)
    weeks = [_load_week_or_error(p) for p in sorted(weeks_dir.glob("*.json"))]
    board = build_board(ideas, weeks, feedback)
    dump_json(board_path, board)
    board_src = data_dir.parent / "board.html"
    if board_src.exists():
        render_pages(board_src, data_dir.parent / "index.html")
    return board


def main(argv):
    if len(argv) not in (2, 3):
        print("usage: python build.py data/weeks/<week>.json [data_dir]", file=sys.stderr)
        return 2
    data_dir = Path(argv[2]) if len(argv) == 3 else Path(__file__).resolve().parent / "data"
    try:
        board = run(argv[1], data_dir)
    except (ValidationError, OSError, ValueError) as e:
        print(f"build.py: {e}", file=sys.stderr)
        return 1
    tw = board["this_week"]
    p = board["picks"]
    print(f"{tw['week']}: {tw['status']}, {tw['candidates_scored']} candidates, "
          f"{len(board['all_time'])} all-time, {len(board['rising'])} rising, "
          f"votes: {len(p['interested'])} interested, {len(p['trying'])} trying, {len(p['hidden'])} hidden")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
