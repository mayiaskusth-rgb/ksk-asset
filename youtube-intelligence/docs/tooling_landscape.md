# Hosted tools, extensions and provider landscape

**Reviewed:** 2026-11-13  
**Scope:** Publicly documented capabilities and plan limits at review time. Prices/limits change; verify at checkout or provider documentation before purchasing or building integrations.

## Outlier and creator-research products

| Product | Publicly documented approach | Access / limitations | Product implication |
|---|---|---|---|
| [vidIQ Outliers](https://vidiq.com/features/outliers/) | Finds videos overperforming a channel baseline; product describes a score using views, velocity and performance vs usual baseline. Help docs describe channel-relative performance and filters for score, views, subscribers, VPH, length and publish date. | Free plan has limited result count; advanced filters and unlimited searches are paid. Extension surfaces an outlier score. Exact scoring formula is proprietary/not disclosed in inspected docs. | Benchmark UX and candidate-discovery filters, not formula. Do not claim to reproduce its score. Treat its VPH as vendor-supplied, not a value inferred from one snapshot. |
| [Viewstats Outliers](https://viewstats.zendesk.com/hc/en-us/articles/22966946776091-Outliers-Tool) | Help article describes outlier score as video views divided by the last 10 videos' average at the time. Extension shows a score based on views relative to channel average at that point in time. | Some outlier discovery and competitor features require Pro. Public pricing page showed Business starting at $249/month; Pro price is dynamically displayed and not reliably extractable. Historical tracking depends on provider data availability. | Useful second benchmark for creator-relative scoring and historic snapshots. Our median is intentionally more robust than a 10-upload mean; compare both in a future benchmark. |
| [1of10](https://1of10.com/about) | Outlier Finder plus channel tracking, title/thumbnail/idea tools; product states models are informed by a large proprietary dataset. | About page lists a limited free tier and paid Basic/Pro tiers; API/MCP access described as Pro or higher. Pricing and credit terms are subject to change. | Strong inspiration for workflow and packaging, but not a transparent source of reproducible score methodology. Do not depend on it as a data provider in v1. |

## Data acquisition and developer tooling

| Option | Strengths | Constraints | Decision |
|---|---|---|---|
| Official YouTube Data API v3 | Documented search, videos, channels, playlists, comments and statistics endpoints; structured IDs and metadata; explicit quota model. | Search is separately quota-limited (current docs: 100 calls/day default); other methods share default 10,000 units/day. Search is relatively expensive in quota terms compared with hydration/list calls. Not all analytics/history are public. | **Preferred first discovery/metadata adapter.** Implement quota ledger, field selection, paging, cache and explicit missing values. |
| Python `yt-dlp` | Broad extractor ecosystem, JSON metadata, playlist/channel collection, subtitle/comment options; easy local CLI integration. | Unofficial extraction surface can break; reliability and YouTube terms/policy need review for each use. Some repositories derive misleading velocity proxies. | **Isolated prototype/fallback only**, not assumed primary provider. |
| Python transcript libraries / local corpus | Direct Python integration, timestamp-aware processing, local files and deterministic search possible. | Caption availability varies; method/access terms and language coverage differ. Need source provenance, retry behavior and data-retention controls. | **Prototype** after adapter contract and legal/policy review. |
| YouTube MCP servers | Convenient search/transcript/comment tools for compatible agents; useful for human-in-loop exploration. | Often Node-based, may rely on unofficial extraction or hosted services; tool schemas and server uptime become dependencies. | **Optional edge integration** only; do not make MCP the engine architecture. |
| Hosted transcript APIs | Convenient API/MCP integration and broad transcript coverage claims. | Pricing, credits, rate limits, retention, data processing and vendor lock-in require diligence. | Defer until a coverage gap is demonstrated. |

## Official API facts relevant to architecture

As checked on 2026-11-13:
- YouTube Data API `search.list` has a default 100 calls/day quota bucket; each call costs one unit in that bucket. A page fetch is another request.
- Most read/list methods such as videos and channels list cost one unit in the general daily quota bucket; default general allocation is 10,000 units/day.
- Search results can return video/channel/playlist IDs and snippets; hydrate video details separately with `videos.list`.
- To retrieve a channel's recent uploads reliably, use its uploads playlist and `playlistItems.list` rather than assuming `search.list` provides a complete channel history.
- Public API snapshots do not provide arbitrary historical daily view counts; velocity requires multiple observations or clearly attributed third-party estimates.

## Build vs buy

- Use official API for baseline metadata and discovery first, with quota-aware query planning.
- Keep our own run manifests, normalized data contract, baseline builder and scoring methodology.
- Use vidIQ/Viewstats/1of10 as manual benchmark products for comparing discovery relevance and relative-performance rankings; do not scrape their proprietary interfaces.
- Do not purchase a plan or add a hosted API dependency during Iteration 0.
- A commercial product's score is a comparison target, not ground truth. Record disagreement rather than tuning our score to imitate a black box.

## Sources

- YouTube API: [Search: list](https://developers.google.com/youtube/data/reference/rest/v3/search/list), [Videos: list](https://developers.google.com/youtube/data/reference/rest/v3/videos/list), [Quota calculator](https://developers.google.com/youtube/data/determine_quota_cost), [API overview](https://developers.google.com/youtube/data/getting-started).
- vidIQ: [Outliers](https://support.vidiq.com/en/articles/9660010-outliers), [features by plan](https://support.vidiq.com/en/articles/13928456-features-credits-by-plan), [plans](https://vidiq.com/plans/).
- Viewstats: [Outliers tool](https://viewstats.zendesk.com/hc/en-us/articles/22966946776091-Outliers-Tool), [extension](https://viewstats.zendesk.com/hc/en-us/articles/23013034988955-Chrome-Extension), [pricing](https://www.viewstats.com/pricing).
- 1of10: [About and pricing](https://1of10.com/about).
