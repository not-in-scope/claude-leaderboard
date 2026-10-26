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
