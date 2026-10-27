# Source registry

Tier 1 is read every run and must be covered before collection stops. Tier 2 is read every run as extra signal. Tier 3 is read on the first run of each month. `status` is `active`, `paused`, or `excluded`. `last_yield` is the number of candidates whose evidence cited the source in the most recent run. The routine updates `last_yield` and `note`; Stephen edits everything else.

`how_read` values: `reddit` (Reddit RSS endpoints), `hn` (Algolia API), `rss` (feed URL in `queries`), `fetch` (plain page fetch), `search` (web search with the queries listed).

## Reddit

Reddit stopped self-serve app registration in late 2025, so API credentials exist only if Reddit approves an application. With `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` set on the cloud environment, the routine uses the official API at `oauth.reddit.com` (100 requests a minute, every subreddit's top listing and every query). Otherwise it reads RSS: `https://www.reddit.com/r/<sub>/top.rss?t=week&limit=100` and `https://www.reddit.com/r/<sub>/search.rss?q=<query>&restrict_sr=1&sort=new&t=week&limit=50`. The `.json` endpoints return 403 from the cloud sandbox and web search returns no Reddit pages, so RSS is the only path; a failed subreddit is recorded and skipped. Reddit allows about one anonymous RSS request per minute, so the routine fetches the top feed for every subreddit and the query feeds only for the six Claude-specific ones.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| r/ClaudeAI | reddit | 1 | reddit | claude, "claude code", revenue, "saved me", clients | active | 12 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute; main hub, about 1M members |
| r/ClaudeCode | reddit | 1 | reddit | revenue, MRR, clients, "built a", "saved me" | active | 3 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/Anthropic | reddit | 1 | reddit | claude, "use case", revenue | active | 2 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/claude | reddit | 1 | reddit | "use claude", revenue, "saved me" | active | 1 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/claudexplorers | reddit | 1 | reddit | planning, family, kids, "saved me", workflow | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute; non-coding use |
| r/ClaudeHomies | reddit | 1 | reddit | planning, family, kids, "saved me", workflow | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute; non-coding use |
| r/indiehackers | reddit | 1 | reddit | claude, "claude code", MRR | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute; MRR query 429 |
| r/SideProject | reddit | 1 | reddit | claude, "claude code" | active | 3 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/SaaS | reddit | 1 | reddit | claude, "claude code" | active | 2 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/microsaas | reddit | 1 | reddit | claude, "claude code" | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/VibeCodingSaaS | reddit | 1 | reddit | claude, MRR | active | 0 | W44 rerun: RSS 404 on top and search (subreddit unavailable); small, high signal |
| r/NoCodeSaaS | reddit | 1 | reddit | claude | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/Entrepreneur | reddit | 1 | reddit | claude, "ai agent" revenue | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/EntrepreneurRideAlong | reddit | 1 | reddit | claude, "ai" revenue | active | 1 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/startups | reddit | 1 | reddit | claude, "claude code" | active | 0 | W44 rerun: top.rss and search.rss read; RSS limited to about 1 request a minute |
| r/smallbusiness | reddit | 1 | reddit | claude, "ai saved" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/sweatystartup | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/Business_Ideas | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/freelance | reddit | 1 | reddit | claude, "ai clients" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/Upwork | reddit | 1 | reddit | claude, "ai" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/consulting | reddit | 1 | reddit | claude, "ai" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/passive_income | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/digitalnomad | reddit | 1 | reddit | claude, "ai income" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/ChatGPTCoding | reddit | 1 | reddit | claude, "claude code", revenue, clients | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); tool-agnostic |
| r/vibecoding | reddit | 1 | reddit | claude, MRR, revenue, "saved me" | active | 3 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/aipromptprogramming | reddit | 1 | reddit | claude, revenue | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/AI_Agents | reddit | 1 | reddit | claude, revenue, clients | active | 1 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/LLMDevs | reddit | 1 | reddit | claude, "in production", revenue | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/AgentsOfAI | reddit | 1 | reddit | claude, revenue | active | 1 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/AiBuilders | reddit | 1 | reddit | claude, revenue | active | 1 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/PromptEngineering | reddit | 1 | reddit | claude, "saved me", workflow | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/automation | reddit | 1 | reddit | claude, "saved me", clients | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/n8n | reddit | 1 | reddit | claude, clients, revenue | active | 1 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/Parenting | reddit | 1 | reddit | claude, "ai" planning, schedule | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/daddit | reddit | 1 | reddit | claude, "ai" planning | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/Mommit | reddit | 1 | reddit | claude, "ai" planning | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/getdisciplined | reddit | 1 | reddit | claude, "ai" planning | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/personalfinance | reddit | 1 | reddit | claude, "ai" budget | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/budget | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/MealPrepSunday | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/travel | reddit | 1 | reddit | claude, "ai itinerary" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/HomeImprovement | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/homeschool | reddit | 1 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); life |
| r/ProductManagement | reddit | 2 | reddit | claude, "ai" workflow, "saved me" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time |
| r/dataengineering | reddit | 2 | reddit | claude, "claude code" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time |
| r/datascience | reddit | 2 | reddit | claude, "claude code" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time |
| r/analytics | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time |
| r/BusinessIntelligence | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time |
| r/ExperiencedDevs | reddit | 2 | reddit | claude, "claude code" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time |
| r/productivity | reddit | 2 | reddit | claude, "ai" workflow | active | 1 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); time, life |
| r/ChatGPT | reddit | 2 | reddit | "make money", "saved me", planning | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); uses transfer to Claude |
| r/ChatGPTPro | reddit | 2 | reddit | workflow, "saved me", revenue | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); uses transfer |
| r/OpenAI | reddit | 2 | reddit | claude, "switched to claude" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); comparisons |
| r/ArtificialInteligence | reddit | 2 | reddit | claude, "use case", revenue | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); thin on workflows |
| r/artificial | reddit | 2 | reddit | claude, "use case" | active | 2 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/cursor | reddit | 2 | reddit | claude, revenue, clients | active | 1 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute) |
| r/Substack | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/content_marketing | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/copywriting | reddit | 2 | reddit | claude, ai clients | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/SEO | reddit | 2 | reddit | claude, "claude code" | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/blogging | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/selfpublish | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/Etsy | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/printondemand | reddit | 2 | reddit | claude, ai | active | 0 | W44 rerun: top.rss read; search.rss queries not reached (RSS limited to about 1 request a minute); creator |
| r/singularity | reddit | - | - | - | excluded | 0 | speculation, not use |
| r/MakeMoneyOnline | reddit | - | - | - | excluded | 0 | low quality |
| r/beermoney | reddit | - | - | - | excluded | 0 | low quality |
| r/ClaudeAIJailbreak | reddit | - | - | - | excluded | 0 | off purpose |

## Forums and aggregators

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Hacker News | forum | 1 | hn | claude, "claude code", anthropic | active | 21 | W44 rerun: Algolia API worked, URL-encode the numeric filter; comment search (tags=comment) found first-hand reports; `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=100&numericFilters=created_at_i>EPOCH` then separate requests with `tags=ask_hn` and `tags=show_hn` |
| Indie Hackers | forum | 1 | search | site:indiehackers.com claude | active | 0 | revenue milestones |
| Product Hunt | forum | 1 | search | site:producthunt.com "claude code" OR "built with claude" | active | 0 | launches |
| Medium | blog | 2 | search | site:medium.com claude (earned OR revenue OR "saved me" OR clients) | active | 4 | W44 rerun: read via tag RSS feeds (claude, claude-code, claude-ai); article pages 403, used feed subtitles |
| Dev.to | blog | 2 | rss | https://dev.to/feed/tag/claude | active | 11 | W44 rerun: feed plus dev.to API by tag worked |
| LinkedIn | social | 2 | search | site:linkedin.com/posts claude (revenue OR clients OR "saved me") | active | 0 | only what search surfaces |

## Newsletters

Read the feed, keep items dated in the window. When a feed fails, search `site:<domain> claude` for the past two weeks and note the failure.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| One Useful Thing | newsletter | 1 | rss | https://www.oneusefulthing.org/feed | active | 0 | W44 rerun: feed read directly; Ethan Mollick |
| Every | newsletter | 1 | search | site:every.to claude | active | 1 | no public RSS; Chain of Thought, Vibe Check and others |
| Latent Space | newsletter | 1 | rss | https://www.latent.space/feed | active | 0 | W44 rerun: feed read directly |
| Lenny's Newsletter | newsletter | 1 | rss | https://www.lennysnewsletter.com/feed | active | 2 | W44 rerun: feed read directly |
| Product Growth | newsletter | 1 | rss | https://news.aakashg.com/feed | active | 1 | W44 rerun: feed read directly; Aakash Gupta |
| Product with Attitude | newsletter | 1 | rss | https://karozieminski.substack.com/feed | active | 0 | W44 rerun: feed read directly; Claude Code and Cowork workflows |
| The AI Maker | newsletter | 1 | rss | https://aimaker.substack.com/feed | active | 1 | W44 rerun: feed read directly |
| The Pragmatic Engineer | newsletter | 1 | rss | https://newsletter.pragmaticengineer.com/feed | active | 0 | W44 rerun: feed read directly |
| Simon Willison's weblog | blog | 1 | rss | https://simonwillison.net/atom/everything/ | active | 0 | W44 rerun: feed read directly |
| Ben's Bites | newsletter | 1 | rss | https://www.bensbites.com/feed | active | 0 | W44 rerun: feed read directly; feed unverified, fall back to search |
| The Rundown AI | newsletter | 1 | search | site:therundown.ai claude | active | 0 | beehiiv, no stable feed |
| Superhuman AI | newsletter | 1 | search | site:superhuman.ai claude | active | 0 | beehiiv |
| The Neuron | newsletter | 1 | search | site:theneurondaily.com claude | active | 0 | beehiiv |
| Starter Story | newsletter | 1 | search | site:starterstory.com claude | active | 0 | |
| Growth Unhinged | newsletter | 1 | search | site:growthunhinged.com claude | active | 0 | feed 404; Kyle Poyar |
| Justin Welsh | newsletter | 1 | search | site:justinwelsh.me claude | active | 0 | solo business |
| Behind the Craft | newsletter | 1 | rss | https://creatoreconomy.so/feed | active | 2 | W44 rerun: feed read directly; Peter Yang |

## Anthropic first-party

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Customer stories | anthropic | 1 | fetch | https://www.anthropic.com/customers | active | 0 | W44 rerun: newest stories undated, none kept |
| News | anthropic | 1 | fetch | https://www.anthropic.com/news | active | 0 | |
| Economic Index | anthropic | 1 | fetch | https://www.anthropic.com/research | active | 0 | new report roughly quarterly |
| Claude Code changelog | anthropic | 1 | fetch | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | active | 0 | new capability precedes new uses |

## Social and video, search only

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| X revenue threads | social | 2 | search | site:x.com "claude code" (MRR OR revenue OR "$" OR clients) | active | 4 | W44 rerun: X links reached via shippedandpaid.com case pages and search |
| X accounts | social | 2 | search | site:x.com (alexalbert__ OR bcherny OR levelsio OR marc_louvion OR gregisenberg OR swyx OR emollick OR danshipper OR simonw) claude | active | 2 | |
| YouTube | video | 2 | search | site:youtube.com "claude code" (business OR money OR "per month" OR clients) | active | 1 | titles and descriptions only |
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

Discord, Skool, Slack, and Facebook groups are not readable by the routine. TikTok has no readable transcripts. Content-farm domains that repackage the same claims are dropped when seen. Excluded domains: fbpe.org.
