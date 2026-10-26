# Claude Leaderboard

Date: 2026-10-23. Status: approved by Stephen in conversation (engine, board home, model, rubric, source registry, `life` category). Plan to follow.

## Problem

Reports of people earning money, saving real hours at work, or running their household and family life with Claude are scattered across Reddit, Substack, Hacker News, X, and YouTube. Reading them by hand is slow, the good ones are buried in hype, and nothing tracks which ideas keep coming back.

Three categories of use count.

| Category | Meaning | Examples |
|---|---|---|
| `money` | Earns dollars | Micro-SaaS, consulting, content, freelance work done with Claude, selling templates or agents |
| `time` | Saves hours in professional work | Spec and PRD drafting, data analysis, research, job search, code review, reporting |
| `life` | Personal productivity, family and kid logistics, planning | Meal planning, kids' schedules and activities, travel planning, household admin, budgeting, learning with kids, fitness planning |

## Goals

- A weekly scan collects 50 or more concrete candidates and publishes the top 5.
- Every candidate is scored on one fixed rubric that weights fit to Stephen's skills.
- A board shows this week, all time, and ideas that recur across weeks, plus the best idea in each category so `life` ideas stay visible next to dollar ideas.
- Every scored candidate is kept, so any ranking can be audited later.
- Sources, rubric, and routine instructions live in the repo and can be edited without touching the routine.

## Non-goals

- No email digest. The board is the only output.
- No auto-posting, no outreach, no purchases.
- No Reddit API keys, no paid data sources, no scraping behind logins.
- No separate database. JSON files in git are the store.

## 1. Architecture

| Part | What it is | Where it runs |
|---|---|---|
| Repo | `not-in-scope/claude-leaderboard`, public | GitHub |
| Routine | Claude Code cloud routine, Mondays 7am Pacific, Opus 5.5 | Anthropic cloud, clones the repo |
| Build script | `build.py`, stdlib Python, merges a week file into the registry and emits the board data | Inside the routine, and locally for tests |
| Board | `index.html`, static page that fetches `data/leaderboard.json` | GitHub Pages, main branch root |

The routine's cloud prompt is one line that says to read `ROUTINE.md` and follow it. All method lives in the repo.

## 2. Repo layout

```
index.html                       the board
build.py                         merge + validate + emit leaderboard.json
tests/test_build.py              pytest for build.py
data/leaderboard.json            what the board renders
data/ideas.json                  registry, one record per distinct idea
data/weeks/2026-W44.json         one file per run, every scored candidate
ROUTINE.md                       routine instructions, versioned
rubric.md                        weights, anchors, Stephen's profile, hourly rate
sources.md                       source registry with tiers and status
docs/superpowers/specs/          this document
docs/superpowers/plans/          implementation plan
```

## 3. Weekly run (ROUTINE.md)

The routine performs these steps in order.

1. Read `rubric.md`, `sources.md`, and `data/ideas.json`. Compute the ISO week for today.
2. Collect candidates from every tier 1 source, then tier 2, covering the past 10 days. Keep going until 50 or more distinct candidates exist. On the first run of each month, also check tier 3.
3. Drop any candidate with no linkable primary source. Merge duplicates. A newsletter that summarizes a Reddit post is one candidate with two links.
4. For each candidate, decide whether it matches an existing idea in `ideas.json` by meaning, not by string. Reuse that slug if it does, or mint a new slug and aliases if it does not.
5. Score each candidate on the six factors with a one-line reason per factor. Convert time saved to dollars with the rate in `rubric.md`.
6. Write `data/weeks/<week>.json`.
7. Run `python build.py data/weeks/<week>.json`. The script validates the week file, merges it into `ideas.json`, and rewrites `leaderboard.json`. If validation fails, fix the week file and rerun, at most three times.
8. Update the `last_yield` column in `sources.md` for every source touched.
9. Commit to main and push. If the push is refused, open a pull request titled with the week and stop.

### Reading each source type

| Type | Method | Fallback |
|---|---|---|
| Reddit | `https://www.reddit.com/r/<sub>/top.json?t=week&limit=100` plus `search.json` for Claude terms | Web search with `site:reddit.com/r/<sub>` and a date filter |
| Hacker News | Algolia API, query terms `claude`, `claude code`, `anthropic`, `numericFilters=created_at_i>` ten days back | None needed |
| Newsletters | RSS at `<publication>/feed`, read posts from the window | Web search of the publication |
| Anthropic | Fetch customer stories, news index, Claude Code changelog | None |
| X, YouTube, podcasts, Medium, Dev.to, LinkedIn | Dated web search with the queries in `sources.md` | None |
| Tier 3 demand side | Dated web search of Upwork, Fiverr, Gumroad, Acquire.com, Google Trends | None |

Every source failure is recorded in the week file under `sources_failed` and never stops the run.

### Candidate thresholds

| Candidates scored | Status | Effect |
|---|---|---|
| 50 or more | `ok` | Top 5 published |
| 15 to 49 | `thin` | Top 5 published, board shows a shortfall flag |
| Under 15 | `skipped` | No top 5, week file holds a note explaining why |

## 4. Scoring (rubric.md)

Each factor has a 0 to N scale with written anchors. Total is the sum, 0 to 100. The same six factors apply to every category, and the anchors for Fit, Upside, and Time to benefit change by category so a `life` idea can score as high as a `money` idea.

| Factor | Max | 0 means | Max means |
|---|---|---|---|
| Fit | 25 | `money` and `time`: needs skills Stephen lacks, such as video editing or sales calls. `life`: does not match his situation | `money` and `time`: uses PM, data, AI, or compliance skills he has. `life`: fits a parent in Seattle with an active, sports-heavy household |
| Upside | 20 | Under $1k a year realistic, or under 1 hour a week saved | $100k a year or more realistic, or 10 or more hours a week saved, or removes a recurring family pain point |
| Time to benefit | 15 | Six months or longer | Under two weeks. For `life`, the first use already pays off |
| Effort | 15 | 30 or more hours a week to run | Under 3 hours a week once set up |
| Evidence | 15 | One anonymous claim, no numbers | Three or more independent reports with specifics |
| Durability | 10 | Arbitrage or loophole likely closed within months | Still works in two years |

`time` and `life` ideas convert hours saved to dollars at $150 an hour, times hours saved a week, times 50 weeks, so the `dollars` field is filled for every candidate. The rate sits in `rubric.md` and Stephen can change it. `rubric.md` also holds a short profile paragraph, professional and personal, that the routine uses to judge fit, and a short note on how to write the pitch and the first step.

## 5. Data model

### Candidate (inside a week file)

```json
{
  "id": "claude-code-audit-micro-saas",
  "title": "Compliance audit prep micro-SaaS built with Claude Code",
  "category": "money",
  "pitch": "Two sentences.",
  "first_step": "One concrete action Stephen could take this week.",
  "scores": {"fit": 22, "upside": 14, "time_to_dollar": 9, "effort": 10, "evidence": 11, "durability": 7},
  "total": 73,
  "reasons": {"fit": "...", "upside": "...", "time_to_dollar": "...", "effort": "...", "evidence": "...", "durability": "..."},
  "dollars": {"low": 12000, "high": 60000, "basis": "annual"},
  "hours_per_week": 8,
  "evidence": [
    {"url": "https://reddit.com/r/SaaS/...", "source": "r/SaaS", "date": "2026-10-19", "claim": "$2.1k MRR after 7 weeks"}
  ]
}
```

`category` is `money`, `time`, or `life`. The scores key `time_to_dollar` is kept for all categories and means time to first benefit. Two to five evidence links per candidate.

### Week file `data/weeks/2026-W44.json`

```json
{
  "week": "2026-W44",
  "run_at": "2026-10-26T14:07:00Z",
  "model": "claude-opus-5-5",
  "status": "ok",
  "note": "",
  "candidates_scored": 57,
  "sources_hit": ["r/ClaudeAI", "hn"],
  "sources_failed": [{"source": "r/SaaS", "error": "403"}],
  "top5": ["slug-a", "slug-b", "slug-c", "slug-d", "slug-e"],
  "candidates": []
}
```

### Idea record (in `data/ideas.json`)

```json
{
  "id": "claude-code-audit-micro-saas",
  "title": "...",
  "aliases": ["audit prep saas", "soc2 helper"],
  "category": "money",
  "first_week": "2026-W44",
  "last_week": "2026-W47",
  "weeks_seen": 3,
  "best_score": 78,
  "best_week": "2026-W45",
  "latest": {"pitch": "...", "first_step": "...", "scores": {}, "total": 73},
  "evidence": []
}
```

`evidence` keeps the ten most recent distinct URLs across weeks. The record also carries `weeks`, the sorted list of week ids it appeared in, and `weeks_seen` is its length, so rerunning a week never double counts.

### Board data `data/leaderboard.json`

```json
{
  "updated": "2026-10-26T14:09:00Z",
  "this_week": {"week": "2026-W44", "status": "ok", "candidates_scored": 57, "top5": [], "category_leaders": {"money": {}, "time": {}, "life": {}}},
  "all_time": [],
  "rising": [],
  "history": [{"week": "2026-W44", "status": "ok", "candidates_scored": 57}]
}
```

`this_week.top5` holds full candidate records. `this_week.category_leaders` holds the highest-scoring candidate of the week in each category, or null when a category had none, so a `life` idea is always shown even when the top 5 is all `money`. `all_time` holds the 20 idea records with the highest `best_score`. `rising` holds the 20 idea records with `weeks_seen` of 3 or more that rank highest by `weeks_seen` then `best_score`. Evidence URLs must start with http or https, and `dollars` must hold numeric `low` and `high` with `low` at most `high`.

## 6. build.py

Stdlib only, so it runs in the cloud sandbox without installs.

```
python build.py data/weeks/2026-W44.json
```

- Validates the week file. Required keys present, scores within factor maxima, `total` equals the sum, two to five evidence links each with a URL, `top5` has five slugs that exist in `candidates` when status is `ok` or `thin`, and zero when `skipped`.
- Derives `status` from `candidates_scored` using the thresholds in section 3 and overwrites whatever the routine wrote.
- Merges each candidate into `ideas.json` by `id`. New ids create records. Existing ids update `last_week`, increment `weeks_seen` once per week, raise `best_score` when beaten, replace `latest`, and prepend new evidence URLs.
- Rewrites `leaderboard.json` from `ideas.json` and all week files. A week file whose `status` is `error` is listed in `history` and otherwise ignored.
- Exits non-zero with a plain message on any validation failure and writes nothing.
- Is idempotent. Running the same week file twice produces the same output.

## 7. Board (index.html)

- Vanilla HTML, CSS, and JS. No build step. Fetches `data/leaderboard.json` with a cache-busting query.
- Header with title, last run date, candidates scored, and status. A `thin` or `skipped` week shows a visible flag.
- Three tabs. This Week lists the top 5 as cards with rank, title, total, category, pitch, first step, and evidence links, followed by a Category Leaders row with the best `money`, `time`, and `life` idea of the week. All Time is a table of 20 rows with rank, title, category, best score, weeks seen, first seen, with a category filter. Rising lists ideas seen in three or more weeks.
- Any row or card expands to show the six sub-scores with their reasons and all evidence links.
- Works at phone width with no horizontal scroll. Same palette family as the job-digest board for familiarity.
- A footer line shows the run history as a compact list of weeks with status.

## 8. Routine configuration

| Field | Value |
|---|---|
| Name | Claude Leaderboard weekly scan |
| Cron | `0 14 * * 1`, Monday 7am PDT and 6am PST |
| Model | `claude-opus-5-5` |
| Source | `https://github.com/not-in-scope/claude-leaderboard` |
| Tools | Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch |
| Connectors | None |
| Prompt | "Read ROUTINE.md at the repo root and follow it exactly." |

After creation the routine is run once by hand so week 1 exists the same day and the whole path is proven.

## 9. Source registry (sources.md)

A table with columns `source`, `type`, `tier`, `how_read`, `queries`, `status`, `last_yield`, `note`. Tiers set how the routine treats each source. Tier 1 is read every week and must be covered before collection stops. Tier 2 is read every week as extra signal. Tier 3 is checked on the first run of each month. `status` is `active`, `paused`, or `excluded`. `last_yield` is the number of candidates the source produced in the most recent run.

Starting set, approved 2026-10-23.

**Tier 1, Reddit, Claude-specific.** r/ClaudeAI, r/ClaudeCode, r/Anthropic, r/claude, r/claudexplorers, r/ClaudeHomies.

**Tier 1, Reddit, builders and money.** r/indiehackers, r/SideProject, r/SaaS, r/microsaas, r/VibeCodingSaaS, r/NoCodeSaaS, r/Entrepreneur, r/EntrepreneurRideAlong, r/startups, r/smallbusiness, r/sweatystartup, r/Business_Ideas, r/freelance, r/Upwork, r/consulting, r/passive_income, r/digitalnomad.

**Tier 1, Reddit, AI coding and agents.** r/ChatGPTCoding, r/vibecoding, r/aipromptprogramming, r/AI_Agents, r/LLMDevs, r/AgentsOfAI, r/AiBuilders, r/PromptEngineering, r/automation, r/n8n.

**Tier 2, Reddit, professional fit.** r/ProductManagement, r/dataengineering, r/datascience, r/analytics, r/BusinessIntelligence, r/ExperiencedDevs, r/productivity, r/ChatGPT, r/ChatGPTPro, r/OpenAI, r/ArtificialInteligence, r/artificial, r/cursor.

**Tier 2, Reddit, creator monetization.** r/Substack, r/content_marketing, r/copywriting, r/SEO, r/blogging, r/selfpublish, r/Etsy, r/printondemand.

**Tier 1, Reddit, personal and family.** r/Parenting, r/daddit, r/Mommit, r/getdisciplined, r/personalfinance, r/budget, r/MealPrepSunday, r/travel, r/HomeImprovement, r/homeschool. r/claudexplorers and r/ClaudeHomies above also carry most non-coding personal use.

**Tier 1, forums and aggregators.** Hacker News (Algolia API), Indie Hackers, Product Hunt.

**Tier 1, newsletters via RSS.** One Useful Thing, Every (Chain of Thought), Latent Space, Lenny's Newsletter, Product Growth, Product with Attitude, The AI Maker, The Pragmatic Engineer, Simon Willison's weblog, Ben's Bites, The Rundown AI, Superhuman AI, The Neuron, Starter Story, Growth Unhinged, Justin Welsh, Behind the Craft. The Indie Hackers newsletter is covered by the Indie Hackers forum row.

**Tier 1, Anthropic first-party.** Customer stories, news blog, Economic Index reports, Claude Code changelog.

**Tier 2, social and video via web search.** X searches for Claude Code plus revenue terms and the accounts of Alex Albert, Boris Cherny, Pieter Levels, Marc Lou, Greg Isenberg, swyx, Ethan Mollick, Dan Shipper, Simon Willison. YouTube titles and descriptions for Greg Isenberg, Starter Story, AI Jason, Matt Wolfe, Riley Brown, Cole Medin, IndyDevDan, Nate Herk, Craig Hewitt, Matthew Berman. Podcast show notes for How I AI, Lenny's Podcast, My First Million, Latent Space, AI & I, Indie Hackers Podcast, The Startup Ideas Podcast. Medium and Dev.to under the Claude tag. LinkedIn only as surfaced by web search.

**Tier 3, demand side, monthly.** Upwork and Fiverr listings asking for Claude work, Gumroad and Lemon Squeezy products built on Claude, Acquire.com listings of AI-built micro-SaaS, Google Trends for Claude Code.

**Excluded.** r/singularity (speculation, not use), r/MakeMoneyOnline and r/beermoney (low quality), jailbreak subreddits (off purpose), Discord, Skool, Slack, and Facebook groups (not readable), TikTok (no transcripts), content-farm domains that repackage claims.

## 10. Error handling

| Failure | Handling |
|---|---|
| A source returns an error or blocks the request | Record under `sources_failed`, use the fallback, continue |
| Fewer than 50 candidates after all tiers | Publish as `thin` with the flag |
| Fewer than 15 candidates | Publish as `skipped` with a note, no top 5 |
| `build.py` rejects the week file | Routine fixes and reruns, three attempts, then commits the week file with `status: error` and a note so nothing is lost |
| Push to main refused | Open a pull request titled with the week |
| GitHub Pages build fails | Data is already in git. Stephen rebuilds by pushing any commit |

Run logs are available at claude.ai/code/routines.

## 11. Testing

- `tests/test_build.py` covers validation failures (missing keys, unknown category, score over max, bad total, wrong evidence count, top5 mismatch), category leaders with a missing category, status derivation at 14, 15, 49, and 50 candidates, merge of a new idea, merge of a repeat idea across two weeks, evidence cap at ten, all-time cap at 20, rising threshold at three weeks, and idempotence.
- The board is checked by opening `index.html` against a fixture `leaderboard.json` with `ok`, `thin`, and `skipped` weeks, at desktop and phone width.
- The routine is checked end to end by the manual first run, then by reading its run log and the resulting commit.

## 12. Open items for Stephen

- The hourly rate for time-saved ideas starts at $150. Change it in `rubric.md`.
- The repo is public because GitHub Pages on the free plan requires it. The data holds only public links and scores.
