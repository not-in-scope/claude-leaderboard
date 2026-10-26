# Source registry

Tier 1 is read every run and must be covered before collection stops. Tier 2 is read every run as extra signal. Tier 3 is read on the first run of each month. `status` is `active`, `paused`, or `excluded`. `last_yield` is the number of candidates whose evidence cited the source in the most recent run. The routine updates `last_yield` and `note`; Stephen edits everything else.

`how_read` values: `json` (Reddit JSON endpoints), `hn` (Algolia API), `rss` (feed URL in `queries`), `fetch` (plain page fetch), `search` (web search with the queries listed).

## Reddit

Read with `https://www.reddit.com/r/<sub>/top.json?t=week&limit=100` and `https://www.reddit.com/r/<sub>/search.json?q=<query>&restrict_sr=1&sort=new&t=week&limit=50`. Fallback is a web search for `site:reddit.com/r/<sub> <query>` limited to the past week.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| r/ClaudeAI | reddit | 1 | json | claude, "claude code", revenue, "saved me", clients | active | 0 | W44: proxy blocked JSON, search fallback found nothing; main hub, about 1M members |
| r/ClaudeCode | reddit | 1 | json | revenue, MRR, clients, "built a", "saved me" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/Anthropic | reddit | 1 | json | claude, "use case", revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/claude | reddit | 1 | json | "use claude", revenue, "saved me" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/claudexplorers | reddit | 1 | json | planning, family, kids, "saved me", workflow | active | 0 | W44: proxy blocked JSON, search fallback found nothing; non-coding use |
| r/ClaudeHomies | reddit | 1 | json | planning, family, kids, "saved me", workflow | active | 0 | W44: proxy blocked JSON, search fallback found nothing; non-coding use |
| r/indiehackers | reddit | 1 | json | claude, "claude code", MRR | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/SideProject | reddit | 1 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/SaaS | reddit | 1 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/microsaas | reddit | 1 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/VibeCodingSaaS | reddit | 1 | json | claude, MRR | active | 0 | W44: proxy blocked JSON, search fallback found nothing; small, high signal |
| r/NoCodeSaaS | reddit | 1 | json | claude | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/Entrepreneur | reddit | 1 | json | claude, "ai agent" revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/EntrepreneurRideAlong | reddit | 1 | json | claude, "ai" revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/startups | reddit | 1 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/smallbusiness | reddit | 1 | json | claude, "ai saved" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/sweatystartup | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/Business_Ideas | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/freelance | reddit | 1 | json | claude, "ai clients" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/Upwork | reddit | 1 | json | claude, "ai" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/consulting | reddit | 1 | json | claude, "ai" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/passive_income | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/digitalnomad | reddit | 1 | json | claude, "ai income" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/ChatGPTCoding | reddit | 1 | json | claude, "claude code", revenue, clients | active | 0 | W44: proxy blocked JSON, search fallback found nothing; tool-agnostic |
| r/vibecoding | reddit | 1 | json | claude, MRR, revenue, "saved me" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/aipromptprogramming | reddit | 1 | json | claude, revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/AI_Agents | reddit | 1 | json | claude, revenue, clients | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/LLMDevs | reddit | 1 | json | claude, "in production", revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/AgentsOfAI | reddit | 1 | json | claude, revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/AiBuilders | reddit | 1 | json | claude, revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/PromptEngineering | reddit | 1 | json | claude, "saved me", workflow | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/automation | reddit | 1 | json | claude, "saved me", clients | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/n8n | reddit | 1 | json | claude, clients, revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/Parenting | reddit | 1 | json | claude, "ai" planning, schedule | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/daddit | reddit | 1 | json | claude, "ai" planning | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/Mommit | reddit | 1 | json | claude, "ai" planning | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/getdisciplined | reddit | 1 | json | claude, "ai" planning | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/personalfinance | reddit | 1 | json | claude, "ai" budget | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/budget | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/MealPrepSunday | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/travel | reddit | 1 | json | claude, "ai itinerary" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/HomeImprovement | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/homeschool | reddit | 1 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; life |
| r/ProductManagement | reddit | 2 | json | claude, "ai" workflow, "saved me" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time |
| r/dataengineering | reddit | 2 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time |
| r/datascience | reddit | 2 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time |
| r/analytics | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time |
| r/BusinessIntelligence | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time |
| r/ExperiencedDevs | reddit | 2 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time |
| r/productivity | reddit | 2 | json | claude, "ai" workflow | active | 0 | W44: proxy blocked JSON, search fallback found nothing; time, life |
| r/ChatGPT | reddit | 2 | json | "make money", "saved me", planning | active | 0 | W44: proxy blocked JSON, search fallback found nothing; uses transfer to Claude |
| r/ChatGPTPro | reddit | 2 | json | workflow, "saved me", revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing; uses transfer |
| r/OpenAI | reddit | 2 | json | claude, "switched to claude" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; comparisons |
| r/ArtificialInteligence | reddit | 2 | json | claude, "use case", revenue | active | 0 | W44: proxy blocked JSON, search fallback found nothing; thin on workflows |
| r/artificial | reddit | 2 | json | claude, "use case" | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/cursor | reddit | 2 | json | claude, revenue, clients | active | 0 | W44: proxy blocked JSON, search fallback found nothing |
| r/Substack | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/content_marketing | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/copywriting | reddit | 2 | json | claude, ai clients | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/SEO | reddit | 2 | json | claude, "claude code" | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/blogging | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/selfpublish | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/Etsy | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/printondemand | reddit | 2 | json | claude, ai | active | 0 | W44: proxy blocked JSON, search fallback found nothing; creator |
| r/singularity | reddit | - | - | - | excluded | 0 | speculation, not use |
| r/MakeMoneyOnline | reddit | - | - | - | excluded | 0 | low quality |
| r/beermoney | reddit | - | - | - | excluded | 0 | low quality |
| r/ClaudeAIJailbreak | reddit | - | - | - | excluded | 0 | off purpose |

## Forums and aggregators

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Hacker News | forum | 1 | hn | claude, "claude code", anthropic | active | 1 | W44: Algolia API and news.ycombinator.com unreachable; search fallback via i.buzzing.cc mirror only; `https://hn.algolia.com/api/v1/search_by_date?query=<q>&tags=story&hitsPerPage=100&numericFilters=created_at_i>EPOCH` then separate requests with `tags=ask_hn` and `tags=show_hn` |
| Indie Hackers | forum | 1 | search | site:indiehackers.com claude | active | 0 | revenue milestones |
| Product Hunt | forum | 1 | search | site:producthunt.com "claude code" OR "built with claude" | active | 0 | launches |
| Medium | blog | 2 | search | site:medium.com claude (earned OR revenue OR "saved me" OR clients) | active | 0 | |
| Dev.to | blog | 2 | rss | https://dev.to/feed/tag/claude | active | 2 | W44: RSS feed blocked by proxy; search fallback used |
| LinkedIn | social | 2 | search | site:linkedin.com/posts claude (revenue OR clients OR "saved me") | active | 0 | only what search surfaces |

## Newsletters

Read the feed, keep items dated in the window. When a feed fails, search `site:<domain> claude` for the past two weeks and note the failure.

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| One Useful Thing | newsletter | 1 | rss | https://www.oneusefulthing.org/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; Ethan Mollick |
| Every | newsletter | 1 | rss | https://every.to/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; Chain of Thought and others |
| Latent Space | newsletter | 1 | rss | https://www.latent.space/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used |
| Lenny's Newsletter | newsletter | 1 | rss | https://www.lennysnewsletter.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used |
| Product Growth | newsletter | 1 | rss | https://news.aakashg.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; Aakash Gupta |
| Product with Attitude | newsletter | 1 | rss | https://karozieminski.substack.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; Claude Code and Cowork workflows |
| The AI Maker | newsletter | 1 | rss | https://aimaker.substack.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used |
| The Pragmatic Engineer | newsletter | 1 | rss | https://newsletter.pragmaticengineer.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used |
| Simon Willison's weblog | blog | 1 | rss | https://simonwillison.net/atom/everything/ | active | 0 | W44: feed blocked by proxy; search fallback used |
| Ben's Bites | newsletter | 1 | rss | https://www.bensbites.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; feed unverified, fall back to search |
| The Rundown AI | newsletter | 1 | search | site:therundown.ai claude | active | 0 | beehiiv, no stable feed |
| Superhuman AI | newsletter | 1 | search | site:superhuman.ai claude | active | 0 | beehiiv |
| The Neuron | newsletter | 1 | search | site:theneurondaily.com claude | active | 0 | beehiiv |
| Starter Story | newsletter | 1 | search | site:starterstory.com claude | active | 0 | |
| Growth Unhinged | newsletter | 1 | rss | https://www.growthunhinged.com/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; Kyle Poyar |
| Justin Welsh | newsletter | 1 | search | site:justinwelsh.me claude | active | 0 | solo business |
| Behind the Craft | newsletter | 1 | rss | https://creatoreconomy.so/feed | active | 0 | W44: feed blocked by proxy (403) and WebFetch DNS failure; search fallback used; Peter Yang |

## Anthropic first-party

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| Customer stories | anthropic | 1 | fetch | https://www.anthropic.com/customers | active | 1 | |
| News | anthropic | 1 | fetch | https://www.anthropic.com/news | active | 0 | |
| Economic Index | anthropic | 1 | fetch | https://www.anthropic.com/research | active | 0 | new report roughly quarterly |
| Claude Code changelog | anthropic | 1 | fetch | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | active | 0 | new capability precedes new uses |

## Social and video, search only

| source | type | tier | how_read | queries | status | last_yield | note |
|---|---|---|---|---|---|---|---|
| X revenue threads | social | 2 | search | site:x.com "claude code" (MRR OR revenue OR "$" OR clients) | active | 0 | |
| X accounts | social | 2 | search | site:x.com (alexalbert__ OR bcherny OR levelsio OR marc_louvion OR gregisenberg OR swyx OR emollick OR danshipper OR simonw) claude | active | 0 | W44: not searched: web search budget exhausted |
| YouTube | video | 2 | search | site:youtube.com "claude code" (business OR money OR "per month" OR clients) | active | 0 | W44: not searched: web search budget exhausted; titles and descriptions only |
| YouTube channels | video | 2 | search | site:youtube.com claude (Greg Isenberg OR "Starter Story" OR "AI Jason" OR "Matt Wolfe" OR "Riley Brown" OR "Cole Medin" OR IndyDevDan OR "Nate Herk" OR "Craig Hewitt" OR "Matthew Berman") | active | 0 | W44: not searched: web search budget exhausted |
| Podcasts | audio | 2 | search | ("How I AI" OR "Lenny's Podcast" OR "My First Million" OR "Latent Space" OR "AI & I" OR "Indie Hackers Podcast" OR "Startup Ideas Podcast") claude | active | 0 | W44: not searched: web search budget exhausted; show notes |

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
