# Feedback loop

Date: 2026-10-27. Status: approved by Stephen in conversation (direction: Artifact board with one-tap votes). Extends the 2026-10-23 design.

## Problem

The board shows ideas but cannot learn which ones Stephen cares about. A loop that needs a page hop to vote will not get used, and a vote without a reason cannot tell the scorer which factor to recalibrate.

## Goals

- One tap on a card records a vote. No page hop.
- Three votes: Interested, Not for me (with one reason), Trying it (with a later outcome note).
- The Monday run reads votes, hides rejected ideas, pins the rest, excludes rejected ideas from the top 5, and rewrites a short "learned from votes" section in the rubric.
- The board shows what changed because of votes each week.
- Data stays in the GitHub repo. Votes are also snapshotted into the repo for audit.

## Non-goals

- No multi-user voting. The artifact is private to Stephen.
- No automatic weight changes to the rubric's factor maxima. The routine edits anchors and a learned paragraph, in words, that Stephen can overrule.

## 1. Where things live

| Part | Home | Why |
|---|---|---|
| Board page | Claude Artifact, private, published by the routine each week | The only zero-infrastructure place a static page can save a tap |
| Board data | `data/leaderboard.json` in the repo, published into the Artifact as a supporting file | The Artifact page may fetch only from its own origin |
| Votes | The Artifact's `db`, collection `votes`, one document per idea id | Written by the page, read by the routine with `ArtifactData` |
| Vote snapshot | `data/feedback.json` in the repo, written by the routine each run | Audit trail, and `build.py` reads it |
| Public mirror | GitHub Pages `index.html`, generated from `board.html` by `build.py` | Keeps a shareable read-only URL; vote buttons hide themselves there |

`board.html` is the page source in the Artifact tool's content-only form (title and style first, no document skeleton). `build.py` wraps it in a skeleton to produce `index.html`.

## 2. Vote document

Path `votes/<idea id>`:

```json
{"vote": "interested" | "no" | "trying", "reason": "effort" | "skills" | "doubt" | "already" | null, "outcome": "free text or empty", "at": "2026-10-27T18:50:00Z"}
```

`reason` is set only for `no`. `outcome` is set only for `trying`, and may be edited later. A second tap on the same button clears the vote (document deleted).

## 3. Page behavior

- Capabilities `{db: {}, user: {}}`. Default rules: only the owner writes.
- On load the page renders from `data/leaderboard.json` first, then `await claude.use("db")`. If `null` (GitHub Pages mirror, or a viewer without access), vote controls stay hidden.
- One `onSnapshot` on the `votes` collection, registered once, drives the vote state.
- Every idea card and table row carries a vote bar with three buttons. The active vote is highlighted. Not for me reveals four reason chips inline; the vote is saved when a chip is tapped. Trying it reveals a one-line outcome field with Save.
- A Your picks section on This Week lists Interested and Trying ideas, Trying with their outcome field. Rejected ideas leave the lists and sit under a collapsed "Hidden (n)" row where a tap restores them.
- A line under the header reads the week's `feedback_note` when present.

## 4. Routine changes (ROUTINE.md)

New step between Clean and Score: read votes with `ArtifactData` (`list` on `votes`), write `data/feedback.json` as `{"<idea id>": {vote, reason, outcome, at}}`. Rules the routine applies:

- A candidate matching a `no` idea is kept in the week file but never placed in `top5`.
- Candidates similar to `no` ideas with reason `skills` or `effort` score Fit or Effort lower; the routine says how in the learned section.
- Candidates similar to `interested` or `trying` ideas get a Fit bonus of up to 3 points, stated in the reason.
- The routine rewrites the section `## Learned from votes` in `rubric.md`: a dated paragraph of at most 120 words summarizing patterns, kept factual ("rejected 3 content ideas for skills"). It never edits factor maxima.
- The week file gains `feedback_note`: one sentence on what changed this week because of votes, or an empty string.

New final step: publish the Artifact with `board.html` as the page and `data/leaderboard.json` under `files`, using the Artifact URL recorded in `ROUTINE.md`. The routine's allowed tools gain `Artifact` and `ArtifactData`.

## 5. build.py changes

- Reads `data/feedback.json` when present. Validation: `top5` must not contain an idea whose vote is `no`.
- Idea records gain `feedback` (the vote document or null).
- `leaderboard.json` gains `picks: {interested: [ideas], trying: [ideas], hidden: [ideas]}` and `this_week.feedback_note`. `all_time` and `rising` exclude hidden ideas.
- Writes `index.html` by wrapping `board.html` in a document skeleton with charset, viewport, and a zero-margin body.
- Tests: top5 rejection, picks lists, hidden exclusion, feedback null when the file is absent, index.html generation.

## 6. Error handling

- `ArtifactData` unavailable or the collection empty: `feedback.json` becomes `{}` and the run continues.
- Artifact publish fails: the run still commits to the repo; the note records the failure. Stephen can republish by asking Claude.
- A vote for an idea id not in the registry is kept in `feedback.json` and ignored by the board.
