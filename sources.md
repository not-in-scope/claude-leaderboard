# Source registry

Tier 1 is read every run and must be covered before collection stops. Tier 2 is read every run as extra signal. Tier 3 is read on the first run of each month. `status` is `active`, `paused`, or `excluded`. `last_yield` is the number of candidates whose evidence cited the source in the most recent run. The routine updates `last_yield` and `note`; Stephen edits everything else.

`how_read` values: `reddit` (Reddit RSS endpoints, until 2026-11-13), `tavily` (Reddit posts through the Tavily search API restricted to reddit.com; needs `TAVILY_API_KEY`), `hn` (Algolia API), `rss` (feed URL in `queries`), `fetch` (plain page fetch), `search` (web search with the queries listed).

## Reddit

Reddit stopped self-serve app registration in late 2025, so API credentials exist only if Reddit approves an application (developer request form, submitted 2026-10-27). Reddit announced on 2026-09-30 that RSS feeds end on 2026-11-13 and the public API closes by March 2027 for everyone except approved developers, so from mid-November the RSS path below stops working and every Reddit row will show as failed until credentials exist. With `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` set on the cloud environment, the routine uses the official API at `oauth.reddit.com` (100 requests a minute, every subreddit's top listing and every query). Otherwise it reads RSS: `https://www.reddit.com/r/<sub>/top.rss?t=week&limit=100` and `https://www.reddit.com/r/<sub>/search.rss?q=<query>&restrict_sr=1&sort=new&t=week&limit=50`. The `.json` endpoints return 403 from the cloud sandbox and web search returns no Reddit pages, so RSS is the only path; a failed subreddit is recorded and skipped. Reddit allows about one anonymous RSS request per minute, so the routine fetches the top feed for every subreddit and the query feeds only for the six Claude-specific ones.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| r/ClaudeAI | reddit | 1 | reddit | claude, "claude code", revenue, "saved me", clients | active | 13 | W46: top.rss and search.rss read; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ClaudeCode | reddit | 1 | reddit | revenue, MRR, clients, "built a", "saved me" | active | 5 | W46: top.rss and search.rss read; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Anthropic | reddit | 1 | reddit | claude, "use case", revenue | active | 2 | W46: top.rss and search.rss read; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/claude | reddit | 1 | reddit | "use claude", revenue, "saved me" | active | 6 | W46: top.rss and search.rss read; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/claudexplorers | reddit | 1 | reddit | planning, family, kids, "saved me", workflow | active | 0 | W46: top.rss and search.rss read; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ClaudeHomies | reddit | 1 | reddit | planning, family, kids, "saved me", workflow | active | 0 | W46: top.rss and search.rss read; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/indiehackers | reddit | 1 | reddit | claude, "claude code", MRR | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/SideProject | reddit | 1 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/SaaS | reddit | 1 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/microsaas | reddit | 1 | reddit | claude, "claude code" | active | 1 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/VibeCodingSaaS | reddit | 1 | reddit | claude, MRR | active | 0 | W46: top.rss 404 (subreddit unavailable) |
| r/NoCodeSaaS | reddit | 1 | reddit | claude | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Entrepreneur | reddit | 1 | reddit | claude, "ai agent" revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/EntrepreneurRideAlong | reddit | 1 | reddit | claude, "ai" revenue | active | 3 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/startups | reddit | 1 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/smallbusiness | reddit | 1 | reddit | claude, "ai saved" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/sweatystartup | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Business_Ideas | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/freelance | reddit | 1 | reddit | claude, "ai clients" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Upwork | reddit | 1 | reddit | claude, "ai" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/consulting | reddit | 1 | reddit | claude, "ai" | active | 1 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/passive_income | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/digitalnomad | reddit | 1 | reddit | claude, "ai income" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ChatGPTCoding | reddit | 1 | reddit | claude, "claude code", revenue, clients | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/vibecoding | reddit | 1 | reddit | claude, MRR, revenue, "saved me" | active | 3 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/aipromptprogramming | reddit | 1 | reddit | claude, revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/AI_Agents | reddit | 1 | reddit | claude, revenue, clients | active | 2 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/LLMDevs | reddit | 1 | reddit | claude, "in production", revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/AgentsOfAI | reddit | 1 | reddit | claude, revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/AiBuilders | reddit | 1 | reddit | claude, revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/PromptEngineering | reddit | 1 | reddit | claude, "saved me", workflow | active | 1 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/automation | reddit | 1 | reddit | claude, "saved me", clients | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/n8n | reddit | 1 | reddit | claude, clients, revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Parenting | reddit | 1 | reddit | claude, "ai" planning, schedule | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/daddit | reddit | 1 | reddit | claude, "ai" planning | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Mommit | reddit | 1 | reddit | claude, "ai" planning | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/getdisciplined | reddit | 1 | reddit | claude, "ai" planning | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/personalfinance | reddit | 1 | reddit | claude, "ai" budget | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/budget | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/MealPrepSunday | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/travel | reddit | 1 | reddit | claude, "ai itinerary" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/HomeImprovement | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/homeschool | reddit | 1 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ProductManagement | reddit | 2 | reddit | claude, "ai" workflow, "saved me" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/dataengineering | reddit | 2 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/datascience | reddit | 2 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/analytics | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/BusinessIntelligence | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ExperiencedDevs | reddit | 2 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/productivity | reddit | 2 | reddit | claude, "ai" workflow | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ChatGPT | reddit | 2 | reddit | "make money", "saved me", planning | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ChatGPTPro | reddit | 2 | reddit | workflow, "saved me", revenue | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/OpenAI | reddit | 2 | reddit | claude, "switched to claude" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/ArtificialInteligence | reddit | 2 | reddit | claude, "use case", revenue | active | 2 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/artificial | reddit | 2 | reddit | claude, "use case" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/cursor | reddit | 2 | reddit | claude, revenue, clients | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Substack | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/content_marketing | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/copywriting | reddit | 2 | reddit | claude, ai clients | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/SEO | reddit | 2 | reddit | claude, "claude code" | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/blogging | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/selfpublish | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/Etsy | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/printondemand | reddit | 2 | reddit | claude, ai | active | 0 | W46: top.rss read; query feeds skipped by design; RSS about 1 request a minute; feeds end 2026-11-13 |
| r/singularity | reddit | - | - | - | excluded | 0 | speculation, not use |
| r/MakeMoneyOnline | reddit | - | - | - | excluded | 0 | low quality |
| r/beermoney | reddit | - | - | - | excluded | 0 | low quality |
| r/ClaudeAIJailbreak | reddit | - | - | - | excluded | 0 | off purpose |

## Reddit through the Tavily search API

Used when `TAVILY_API_KEY` is set on the cloud environment. Each query is restricted to reddit.com and the past week, returns up to 20 posts with an excerpt, and the routine spends at most 40 searches a run (free plan: 1,000 a month). Google's Custom Search JSON API was tried first and is closed to new customers.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Google: Claude money | search | 1 | tavily | "claude code" (MRR OR revenue OR clients OR "paying customers") | active | 2 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude built | search | 1 | tavily | "built with claude" OR "claude code" ("I built" OR shipped OR launched) | active | 0 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude saved time | search | 1 | tavily | claude ("saved me" OR "hours a week" OR "my workflow") | active | 0 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude freelance | search | 1 | tavily | claude (upwork OR freelance OR consulting OR clients) | active | 3 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude family | search | 1 | tavily | claude (kids OR family OR parenting OR household OR "meal plan") | active | 2 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude planning | search | 1 | tavily | claude (budget OR trip OR itinerary OR schedule OR "weekly review") | active | 0 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude agents | search | 1 | tavily | claude (agent OR automation OR n8n OR MCP) (clients OR revenue OR "saved me") | active | 2 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude data work | search | 1 | tavily | claude (dashboard OR SQL OR "data pipeline" OR analytics OR PRD) ("I built" OR "saved me") | active | 4 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude side project | search | 1 | tavily | claude ("side project" OR "micro saas" OR "indie") (users OR revenue) | active | 1 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |
| Google: Claude content | search | 2 | tavily | claude (newsletter OR substack OR youtube OR etsy) (revenue OR subscribers OR sales) | active | 3 | W46: read via Tavily (1 credit, 20 results, past week); excerpts dated by Reddit id |

## Forums and aggregators

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Hacker News | forum | 1 | hn | claude, "claude code", anthropic | active | 14 | W46: Algolia API read (story, ask_hn, show_hn) plus comment searches and the Ask HN working-on and agentic-setup threads; URL-encode the numeric filter |
| Indie Hackers | forum | 1 | search | site:indiehackers.com claude | active | 0 | W46: search found no in-window pages |
| Product Hunt | forum | 1 | search | site:producthunt.com "claude code" OR "built with claude" | active | 0 | W46: search found no in-window pages |
| Medium | blog | 2 | search | site:medium.com claude (earned OR revenue OR "saved me" OR clients) | active | 0 | W46: one search, no in-window first-hand pages |
| Dev.to | blog | 2 | rss | https://dev.to/feed/tag/claude | active | 4 | W46: feed plus dev.to API by tag (claude, claudecode, anthropic, claudeai) read |
| LinkedIn | social | 2 | search | site:linkedin.com/posts claude (revenue OR clients OR "saved me") | active | 0 | W46: search found no in-window pages |

## Newsletters

Read the feed, keep items dated in the window. When a feed fails, search `site:<domain> claude` for the past two weeks and note the failure.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| One Useful Thing | newsletter | 1 | rss | https://www.oneusefulthing.org/feed | active | 0 | W46: feed timed out once, read on retry; no in-window items |
| Every | newsletter | 1 | search | site:every.to claude | active | 0 | W46: search found no in-window pages |
| Latent Space | newsletter | 1 | rss | https://www.latent.space/feed | active | 0 | W46: feed read directly |
| Lenny's Newsletter | newsletter | 1 | rss | https://www.lennysnewsletter.com/feed | active | 2 | W46: feed read directly |
| Product Growth | newsletter | 1 | rss | https://news.aakashg.com/feed | active | 0 | W46: feed read directly |
| Product with Attitude | newsletter | 1 | rss | https://karozieminski.substack.com/feed | active | 0 | W46: feed read directly |
| The AI Maker | newsletter | 1 | rss | https://aimaker.substack.com/feed | active | 1 | W46: feed read directly |
| The Pragmatic Engineer | newsletter | 1 | rss | https://newsletter.pragmaticengineer.com/feed | active | 0 | W46: feed read directly |
| Simon Willison's weblog | blog | 1 | rss | https://simonwillison.net/atom/everything/ | active | 0 | W46: feed read directly |
| Ben's Bites | newsletter | 1 | rss | https://www.bensbites.com/feed | active | 0 | W46: feed read directly |
| The Rundown AI | newsletter | 1 | search | site:therundown.ai claude | active | 0 | W46: search found no in-window pages |
| Superhuman AI | newsletter | 1 | search | site:superhuman.ai claude | active | 0 | W46: search found no in-window pages |
| The Neuron | newsletter | 1 | search | site:theneurondaily.com claude | active | 0 | W46: search found no in-window pages |
| Starter Story | newsletter | 1 | search | site:starterstory.com claude | active | 0 | W46: search found no in-window pages |
| Growth Unhinged | newsletter | 1 | search | site:growthunhinged.com claude | active | 0 | W46: search found no in-window pages |
| Justin Welsh | newsletter | 1 | search | site:justinwelsh.me claude | active | 0 | W46: search found no in-window pages |
| Behind the Craft | newsletter | 1 | rss | https://creatoreconomy.so/feed | active | 0 | W46: feed read directly |

## Anthropic first-party

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Customer stories | anthropic | 1 | fetch | https://www.anthropic.com/customers | active | 0 | W46: page read; stories undated, none kept |
| News | anthropic | 1 | fetch | https://www.anthropic.com/news | active | 0 | W46: page read; model, IPO and science news only |
| Economic Index | anthropic | 1 | fetch | https://www.anthropic.com/research | active | 0 | W46: research page read; Nov 2 to 6 items are studies, not user reports |
| Claude Code changelog | anthropic | 1 | fetch | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | active | 0 | W46: read 2.1.319 |

## Social and video, search only

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| X revenue threads | social | 2 | search | site:x.com "claude code" (MRR OR revenue OR "$" OR clients) | active | 0 | W46: search found no in-window pages |
| X accounts | social | 2 | search | site:x.com (alexalbert__ OR bcherny OR levelsio OR marc_louvion OR gregisenberg OR swyx OR emollick OR danshipper OR simonw) claude | active | 0 | W46: search found no in-window pages |
| YouTube | video | 2 | search | site:youtube.com "claude code" (business OR money OR "per month" OR clients) | active | 0 | W46: search found no in-window pages |
| YouTube channels | video | 2 | search | site:youtube.com claude (Greg Isenberg OR "Starter Story" OR "AI Jason" OR "Matt Wolfe" OR "Riley Brown" OR "Cole Medin" OR IndyDevDan OR "Nate Herk" OR "Craig Hewitt" OR "Matthew Berman") | active | 0 | W46: search found no in-window pages |
| Podcasts | audio | 2 | search | ("How I AI" OR "Lenny's Podcast" OR "My First Million" OR "Latent Space" OR "AI & I" OR "Indie Hackers Podcast" OR "Startup Ideas Podcast") claude | active | 0 | W46: search found no in-window pages |

## Demand side, monthly

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Upwork | demand | 3 | search | site:upwork.com "claude" (job OR hiring) | active | 0 | what buyers pay for; W45: search returned listings and undated pages only |
| Fiverr | demand | 3 | search | site:fiverr.com claude | active | 0 | W45: search returned listings and undated pages only |
| Gumroad | demand | 3 | search | site:gumroad.com claude | active | 0 | prompt packs, templates; W45: search returned listings and undated pages only |
| Lemon Squeezy | demand | 3 | search | site:lemonsqueezy.com claude | active | 0 | W45: search returned listings and undated pages only |
| Acquire.com | demand | 3 | search | site:acquire.com claude OR "built with ai" | active | 0 | exits; W45: search returned listings and undated pages only |
| Google Trends | demand | 3 | fetch | https://trends.google.com/trends/explore?q=claude%20code | active | 0 | W45: HTTP 429, skipped |

## Excluded platforms

Discord, Skool, Slack, and Facebook groups are not readable by the routine. TikTok has no readable transcripts. Content-farm domains that repackage the same claims are dropped when seen. Excluded domains: fbpe.org.
