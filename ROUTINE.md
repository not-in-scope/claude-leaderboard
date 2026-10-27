# Weekly scan

You are the Claude Leaderboard weekly scan, running unattended in a cloud sandbox with this repo checked out. Do every step below in order. Do not ask questions. When you must make a call, make it and record it in the week file's `note`.

Tools you have: shell (`curl`, `python3`, `git`), file read and write, web search, web fetch, and the Artifact tools (`Artifact`, `ArtifactData`; load them with `ToolSearch select:Artifact,ArtifactData`).

The board is the Artifact at https://claude.ai/artifact/2cej2sNszDSucKegimkkAq. Its database holds Stephen's votes.

Constraints of this sandbox:

- Do not spawn subagents. Web search has a budget of about 200 calls per run shared by every agent, and parallel agents exhaust it in minutes. Do all collection yourself, in sequence.
- Plan the search budget. Direct fetches (`json`, `hn`, `rss`, `fetch` rows) cost no searches, so do all of them first. Spend at most 150 searches on the `search` rows, roughly 8 per source, and keep 20 in reserve for dating and verifying candidates.
- A `site:reddit.com` web search returns no Reddit pages. If a Reddit RSS endpoint fails, record the failure and move on; do not spend searches on Reddit.
- If direct fetches fail with DNS errors or a proxy 403 on every host, the environment's network access is set to Trusted instead of Full. Record one `sources_failed` entry per source with the error, finish with what search finds, and say so in `note`.

## 0. Setup

```bash
WEEK=$(date -u +%G-W%V)          # ISO week, for example 2026-W44
TODAY=$(date -u +%F)
START=$(date -u -d "$TODAY -10 days" +%F)
EPOCH_START=$(date -u -d "$START" +%s)
DOM=$(date -u +%d)               # tier 3 runs when DOM is 01..07
```

Your shell does not keep variables between commands. Compute these values once, then write the literal values into every later command (for example `data/weeks/2026-W44.json`, not `$WEEK`).

Read `rubric.md`, `sources.md`, and `data/ideas.json`. The registry tells you which ideas already exist, so repeats get the same `id`.

If `data/weeks/<WEEK>.json` already exists, this is a rerun. Overwrite it.

## 1. Collect

Target: 50 or more distinct candidates. A candidate is a first-hand report, dated within the window, of a person or small team using Claude (claude.ai, Claude Code, Claude Cowork, the API) to earn money, save hours at work, or run personal or family life. It must have a URL.

Not a candidate: model comparisons, benchmarks, complaints, speculation about jobs, prompt lists with no outcome, product announcements with no user report, posts about other tools with no Claude angle.

Window: a candidate counts when its primary source is dated within the last 10 days. Reddit `t=week` and web search "past two weeks" are fetch filters only; apply the 10-day rule when deciding.

Order: every tier 1 source in `sources.md`, then every tier 2 source, then tier 3 when `DOM` is 01 to 07. Try every tier 1 source even after passing 50. Within each tier, do the direct-fetch rows before the search rows.

How to read each `how_read` type:

- `reddit`. Reddit's RSS endpoints work from this sandbox; its JSON endpoints return 403, so use RSS only. Reddit throttles anonymous RSS to about one request per minute per IP and sends `x-ratelimit-remaining` and `x-ratelimit-reset` headers; honor them and run the fetches in one background process while you read other sources. Budget about 90 requests: fetch `https://www.reddit.com/r/<sub>/top.rss?t=week&limit=100` for every active subreddit, and fetch `https://www.reddit.com/r/<sub>/search.rss?q=<query>&restrict_sr=1&sort=new&t=week&limit=50` for each query only on the six Claude-specific subreddits (r/ClaudeAI, r/ClaudeCode, r/Anthropic, r/claude, r/claudexplorers, r/ClaudeHomies). Skip the query feeds elsewhere; the top feeds carry the reports that matter. Use `curl -sL -A "claude-leaderboard/1.0 (weekly research bot; github.com/not-in-scope/claude-leaderboard)"`. Each Atom `<entry>` carries the post title, author, date, link, and the post body as HTML in `<content>`. For promising posts, fetch the post URL with `.rss` appended to read the comments for numbers. Parse with `python3` and `xml.etree`, not with regex on the whole file. On HTTP 403 or 429, wait 5 seconds and retry once, then record the failure under `sources_failed` and move on. Never change the user agent to look like a browser.
- `hn`. Fetch, with the URL in double quotes so the `>` is not treated as a redirect, `"https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=100&numericFilters=created_at_i>EPOCH_START"` for each query, then once with `tags=ask_hn` and once with `tags=show_hn` (separate requests, since a comma in tags means AND). Open stories that look like first-hand reports.
- `rss`. Fetch the feed URL. Read items dated in the window.
- `fetch`. Fetch the page. Read items dated in the window.
- `search`. Run each query with web search limited to the past two weeks. Open results that look like first-hand reports.

Keep a scratch list as you go, for example `/tmp/candidates.jsonl`, one JSON object per line with the fields in section 4.

## 2. Clean and match

- Drop anything without a URL to a first-hand report.
- One candidate is one specific idea. An idea is a specific thing you could start doing this week, not a theme. "Sync kids' sports schedules from team emails into a shared calendar with Claude" is an idea. "Family logistics run through Claude" is a theme and is not allowed. Never group different concrete things under one title, even when they share a category. Ten reports of ten different things are ten candidates.
- Merge only when it is the same specific idea. The same person's story in two places is one candidate with both links. Two different people doing the same specific thing is one candidate with both links and stronger evidence.
- The title names the specific idea in twelve words or fewer, concrete noun first. Banned as the main noun: automation, workflows, apps, tools, logistics, admin, use cases, productivity. If the title would fit many different reports, it is too vague.
- Match each candidate to `data/ideas.json` by meaning, not by string. If it is the same specific idea as an existing record, reuse that `id`. Otherwise mint a new kebab-case `id` of three to six words and one to three `aliases`.

## 2b. Read Stephen's votes

Load the Artifact tools, then call `ArtifactData` with action `list`, url `https://claude.ai/artifact/2cej2sNszDSucKegimkkAq`, collection `votes`. Each document id is an idea id and the body is `{"vote": "interested" | "no" | "trying", "reason": "effort" | "skills" | "doubt" | "already" | null, "outcome": "...", "at": "..."}`. Write the whole map to `data/feedback.json` as `{"<idea id>": {vote, reason, outcome, at}}`. If the call fails or the collection is empty, write `{}` and continue.

Apply the votes:

- An idea voted `no` never goes in `top5`. The build script rejects a top5 that holds one.
- A candidate that is a near relative of a `no` idea with reason `skills` scores Fit at most 10; with reason `effort`, Effort at most 6; with `doubt`, Evidence at most 6; with `already`, treat it as a repeat of that idea and reuse its id. Say so in the factor's reason.
- A candidate that is a near relative of an `interested` or `trying` idea gets up to 3 extra Fit points, within the maximum, and the reason says why.
- Rewrite the section `## Learned from votes` at the end of `rubric.md`: one dated paragraph of at most 120 words that states the patterns in plain words, such as "Stephen rejected three content-creation ideas for not my skills, so Fit for creator ideas is capped at 10." Keep facts only. Never change factor maxima or the anchor tables.
- Set `feedback_note` in the week file to one sentence on what changed this run because of votes, or `""` when no votes exist.

## 3. Score

Apply `rubric.md` exactly. Integer scores within each factor's maximum. One-line reason per factor. `total` is the sum. `category` is `money`, `time`, or `life`. `dollars` is a low and high annual estimate; for `time` and `life` compute it from hours saved and the rate in `rubric.md`. `hours_per_week` is the effort to run it. Two to five evidence items, each with `url`, `source` (as named in `sources.md`, or the domain), `date`, and a short `claim` quoting the number or outcome.

`top5` is the five highest totals. Break ties by more evidence, then more recent. If you have 15 to 49 candidates, still pick five. If you have fewer than 15, set `top5` to `[]` and explain in `note`.

## 4. Write the week file

Write `data/weeks/<WEEK>.json` with this envelope.

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
  "top5": ["compliance-audit-prep-micro-saas", "<id>", "<id>", "<id>", "<id>"],
  "candidates": ["<one object per candidate, see below>"]
}
```

One candidate object:

```json
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
```

Rules the build script enforces: every `top5` entry is an `id` that exists in `candidates`; `top5` has exactly five ids when there are 15 or more candidates and is `[]` otherwise; `aliases` is a list of strings; scores are integers within each factor's maximum; `total` is the sum; two to five evidence items each with a `url`. Every evidence `url` starts with `http://` or `https://`. `dollars.low` and `dollars.high` are plain numbers (no `$`, commas, or `k`) with `low` no greater than `high`, and `dollars.basis` is a non-empty string such as `"annual"`. `status` and `candidates_scored` are recomputed by the build script, so write your best guess.

## 5. Build

```bash
python3 build.py data/weeks/<WEEK>.json
```

If it exits non-zero, read the message, fix the week file, and run it again. Three attempts at most. If it still fails, set `"status": "error"` in the week file, put the last error message in `note`, leave `data/ideas.json` and `data/leaderboard.json` untouched, and continue to step 6.

## 6. Update sources.md

For every row you read, set `last_yield` to the number of candidates whose evidence cites that source. If a source failed, put a short reason in `note`. Change nothing else in the file.

## 7. Commit and push

```bash
git config user.name  >/dev/null || git config user.name "Claude Leaderboard"
git config user.email >/dev/null || git config user.email "noreply@anthropic.com"
git add -A
git commit -m "<WEEK>: <N> candidates, <status>"
git push origin HEAD:main
```

Fill in the literal week, count, and status.

If the push is refused, push a branch and open a pull request:

```bash
git checkout -b "week/<WEEK>"
git push -u origin "week/<WEEK>"
gh pr create --title "<WEEK> scan" --body "Weekly scan. Push to main was refused." 2>/dev/null || echo "PR needed for branch week/<WEEK>"
```

## 7b. Publish the board

After the push succeeds, publish the Artifact so the board shows this week. Call `Artifact` with action `publish`, url `https://claude.ai/artifact/2cej2sNszDSucKegimkkAq`, file_path `board.html`, and files `{"data/leaderboard.json": "data/leaderboard.json"}`. Omit `capabilities` and `icon` so the stored declaration carries forward. If the publish is refused with a newer version, read the artifact, keep its page as is, and publish again with only the data file. If it fails twice, say so in the final message; the repo already holds the data.

## 8. Final message

One paragraph: the week, the status, how many candidates were scored, the five titles in `top5`, which sources failed, how many votes were read, and whether the board published.
