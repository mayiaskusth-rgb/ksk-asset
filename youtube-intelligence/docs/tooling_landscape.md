# Hosted tools, extensions and provider landscape

**Reviewed:** 2026-11-13  
**Scope:** Public product/help pages and API documentation inspected on the review date. Pricing and entitlements change; treat them as point-in-time observations and verify at checkout.

## Outlier and creator-research products

| Product | Publicly documented approach | Access / limitations | Product implication |
|---|---|---|---|
| [vidIQ Outliers](https://vidiq.com/features/outliers/) | The 2026 help page describes an Outlier Score (0–100+) and says the score considers views, velocity and performance against a channel's usual baseline. It also describes separate views-per-hour and channel-size filters. | Free access is limited: current plan docs list 8 Outliers results/search in the web app; the extension exposes an Outlier Score on Free, while advanced filters are paid. The exact scoring formula and weighting are proprietary. | Benchmark discovery UX and candidate ranking, not the black-box formula. Do not claim to reproduce vidIQ's score. Treat VPH as a separately sourced/estimated signal, never infer historical velocity from a single snapshot. |
| [Viewstats Outliers](https://viewstats.zendesk.com/hc/en-us/articles/22966946776091-Outliers-Tool) | Official help describes the example score as views divided by the last 10 videos' average views **at the time**. The extension describes its score as views compared with the channel average at that point in time. | Public docs describe search, channel/topic filters, long-vs-Shorts filters and historical comparisons. Current Pro pricing/feature access varies; confirm in product UI. | Useful benchmark for time-aligned creator-relative scoring. Our median baseline is more robust to skew than a mean, but only when we have comparable historical snapshots. |
| [1of10](https://1of10.com/about) | Outlier Finder plus channel tracking, title/thumbnail/idea tools; the company says its AI is trained on a proprietary YouTube outlier dataset. | The current About page lists Free (60 credits), Basic ($19/month or $15/month billed yearly), Pro ($89/month or $69/month billed yearly), and Ultra ($4,999/year). API and MCP access are described as Pro or higher. Prices are USD and may change. | Useful workflow/packaging benchmark and possible later paid benchmark source. Do not depend on it as a data provider in v1; its ranking corpus and score are proprietary. |

## Data acquisition and developer tooling

| Option | Strengths | Constraints | Decision |
|---|---|---|---|
| Official YouTube Data API v3 | Documented search, videos, channels, playlists, comments and statistics endpoints; structured IDs and metadata; explicit quota model. | Current default allocation is 100 `search.list` calls/day in its own bucket and 10,000 units/day for most other endpoints. Each extra page is another request. Captions listing costs 50 units and does not itself provide transcript text. Public API does not expose arbitrary historical daily view counts. | **Preferred first discovery/metadata adapter.** Implement quota ledger, field selection, paging, cache and explicit missing values. |
| Python `yt-dlp` | Broad extractor ecosystem, JSON metadata, playlist/channel collection, subtitle/comment options; easy local CLI integration. | Unofficial extraction surface can break; reliability and YouTube terms/policy need review for each use. Some repositories derive misleading velocity proxies. | **Isolated prototype/fallback only**, not assumed primary provider. |
| Python transcript libraries / local corpus | Direct Python integration, timestamp-aware processing, local files and deterministic search possible. | Caption availability varies; method/access terms and language coverage differ. Need source provenance, retry behavior and data-retention controls. | **Prototype** after adapter contract and legal/policy review. |
| YouTube MCP servers | Convenient search/transcript/comment tools for compatible agents; useful for human-in-loop exploration. | Often Node-based, may rely on unofficial extraction or hosted services; tool schemas and server uptime become dependencies. | **Optional edge integration** only; do not make MCP the engine architecture. |
| Hosted transcript APIs | Convenient API/MCP integration and broad transcript coverage claims. | Pricing, credits, rate limits, retention, data processing and vendor lock-in require diligence. | Defer until a coverage gap is demonstrated. |

## Official API facts relevant to architecture

As checked on 2026-11-13:
- `search.list` has a separate default daily quota of 100 calls; every additional page request consumes another call in that bucket.
- The general default quota allocation is 10,000 units/day for most other methods. Most list/read methods cost 1 unit, while `captions.list` costs 50 units.
- Search results identify videos/channels/playlists; hydrate video details separately with `videos.list`.
- For a channel's recent uploads, use its uploads playlist and `playlistItems.list` rather than assuming `search.list` gives a complete upload history.
- Public API snapshots do not provide arbitrary historical daily view counts; velocity requires multiple observations or clearly attributed third-party estimates.

## Build vs buy

- Use official API for baseline metadata and discovery first, with quota-aware query planning.
- Keep our own run manifests, normalized data contract, baseline builder and scoring methodology.
- Use vidIQ, Viewstats and 1of10 as external benchmark products for comparing discovery relevance and relative-performance rankings; do not scrape their proprietary interfaces.
- Do not purchase a plan or add a hosted API dependency during Iteration 0.
- A commercial product's score is a comparison target, not ground truth. Record disagreement rather than tuning our score to imitate a black box.

## Sources

- YouTube API: [Search: list](https://developers.google.com/youtube/data/reference/rest/v3/search/list), [Videos: list](https://developers.google.com/youtube/data/reference/rest/v3/videos/list), [Quota calculator](https://developers.google.com/youtube/data/determine_quota_cost), [API overview](https://developers.google.com/youtube/data/getting-started).
- vidIQ: [Outliers](https://support.vidiq.com/en/articles/9660010-outliers), [features by plan](https://support.vidiq.com/en/articles/13928456-features-credits-by-plan), [product page](https://vidiq.com/features/outliers/).
- Viewstats: [Outliers tool](https://viewstats.zendesk.com/hc/en-us/articles/22966946776091-Outliers-Tool), [extension](https://viewstats.zendesk.com/hc/en-us/articles/23013034988955-Chrome-Extension).
- 1of10: [About, pricing and API/MCP](https://1of10.com/about).
