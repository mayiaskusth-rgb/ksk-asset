# Public GitHub landscape — YouTube research and intelligence

**Reviewed:** 2026-11-13  
**Purpose:** Iteration 0 reuse-first reconnaissance. Findings are a snapshot of the named default-branch sources inspected on this date, not a guarantee of future maintenance or service availability.

## Shortlist and decisions

| Project | Category | License evidence | Implementation / inspected evidence | Reuse decision |
|---|---|---|---|---|
| [youtube-researcher-skill](https://github.com/cartcodes/youtube-researcher-skill) | Discovery, metadata, transcripts, comments | MIT | Python script uses `yt-dlp` JSON output, supports video/channel metadata and subtitle/comment collection; script also calculates a lifetime-view-count divided by elapsed upload age and labels it VPH. Small, focused collector. | **Borrow design / prototype**. Reuse its simple artifact organization and CLI ideas. Do not reuse its VPH calculation: one current count divided by age is not observed velocity. Validate yt-dlp reliability and platform-policy implications before adopting. |
| [youtube-video-insights](https://github.com/FlorianBruniaux/youtube-video-insights) | Transcript corpus, timestamped search, cumulative research, MCP | `pyproject.toml` declares MIT; root listing inspected did not show a LICENSE file, so legal reuse is **not cleared**. | Python 3.11+, yt-dlp, SQLite/FTS5 search, explicit approval gates before acquisition/discovery, deterministic dossier export, extensive tests and CLI/MCP options. Inspected acquisition service requires approved candidates and separates acquisition from index publication. | **Borrow design** pending license clarification. Strong reference for local transcript corpus, provenance, human approval gates and resumable research. Do not add as a dependency. |
| [youtube-research-mcp-server](https://github.com/meda-gpu/youtube-research-mcp-server) | MCP, transcripts, metadata, comments | MIT | TypeScript/Node 20; package includes MCP SDK, Google API client, youtubei.js and Zod. Inspected JSON3 transcript parser retains text offsets and durations. Tests cover parser, metadata, URL and server behavior. | **Prototype / wrap later** if agent-tool interoperability is required. Internal Python pipeline should call a provider adapter directly where possible; MCP server is not our core runtime. |
| [youtube-intelligence-stack](https://github.com/AlekseiUL/youtube-intelligence-stack) | Python CLI, discovery, channel watchlists, comments, transcripts, reports | MIT | Python CLI built around yt-dlp and YAML watchlists; inspected search module has provider fallbacks, retry/backoff, caching, throttling and JSONL artifacts. Project includes tests and CI-oriented verification docs. | **Borrow design / prototype**. Best near-term reference for operational collector patterns and run artifacts. Do not adopt wholesale: its scraping/provider assumptions need independent policy and reliability review. |
| [video2ctx / all-things-youtube](https://github.com/devhims/video2ctx) | TypeScript library, transcripts, metadata, storyboards, comments, channel/playlist data, research API | Apache-2.0 repo; package manifest for `all-things-youtube` declares MIT. | Active TypeScript monorepo with separate npm package and tests for captions, recovery, transport, storyboard and YouTube client. Includes hosted research platform and local/agent interfaces. | **Prototype / borrow design**. Candidate for isolated comparison of transcript and storyboard coverage. Do not couple Python core to a TypeScript package or hosted API without a measured need. |
| [transcriptapi-plugin](https://github.com/ZeroPointRepo/transcriptapi-plugin) | Hosted transcript MCP / agent plugin | MIT | Repository packages a remote Streamable HTTP endpoint at `transcriptapi.com/mcp`; capability depends on a third-party hosted service and its account/credit terms. | **Defer**. Convenient for agent clients, but creates hosted-provider dependency and does not meet our preference for reproducible Python-owned acquisition. Revisit only if coverage justifies it. |

## Category coverage

| Required category | Findings |
|---|---|
| Discovery and metadata | Official Data API remains preferred first adapter; yt-dlp collectors offer broader but more brittle fallback experiments. |
| Channel analytics / competitor research | The CLI stack and video-insights corpus show watchlists, upload retrieval, local indexes and comparison workflows. |
| Outlier detection | Public projects expose discovery/relative-performance patterns, but no candidate inspected provides a clearly reusable, validated scoring library. Keep our transparent baseline scorer. |
| Transcripts / captions | MCP parser and Python corpus projects show timestamp-preserving extraction, language-aware storage and local search. Prototype providers behind our contract. |
| Comments / audience signals | yt-dlp and MCP projects collect comments where available; collection coverage and policy constraints need careful validation. Minimize retained content. |
| Content/video intelligence | video2ctx has storyboard/frame and transcript tooling; evaluate rights, source availability and compute before a spike. |
| MCP / agent tools | Several servers expose transcript/search/metadata tools. Treat MCP as optional interface, not the data model or pipeline. |
| End-to-end products | Local CLI/corpus and hosted products exist. Prefer borrowing small operational patterns over adopting an entire application. |

## Important technical cautions

- A GitHub public page is not sufficient evidence of a reusable license. Confirm the exact license and package-level terms before copying or depending on code.
- `youtube-video-insights` declares MIT in project metadata but the inspected root did not list a LICENSE file; request clarification before reuse.
- `yt-dlp`-based collectors can fail as YouTube changes interfaces and may rely on access patterns that need terms/policy review. Isolate and test them.
- One current view count divided by elapsed age is not historical views-per-hour. Do not use that proxy as a measured velocity feature.
- Hosted APIs/MCP tools may change price, limits, retention or coverage; keep a provider-neutral adapter boundary.
- Stars are not a quality score. Selection is based on implementation fit, maintenance, tests, data source, license clarity and reliability.

## Build vs reuse decisions

| Capability | Decision |
|---|---|
| Internal normalized records and provenance | **Build** — our contract is product-defining and provider-neutral. |
| Creator-relative outlier scoring | **Build/retain** — existing deterministic scorer is small, transparent and already tested. |
| Official metadata discovery | **Wrap official YouTube Data API** first; use third-party collectors only as isolated prototypes. |
| Channel upload/baseline collection | **Build orchestration** over a selected source adapter; borrow retry/cache patterns, do not adopt another full CLI. |
| Transcript acquisition | **Prototype** official/allowed methods and yt-dlp/transcript libraries behind an adapter; preserve timestamps and language. |
| Local transcript search | **Defer** until transcript corpus volume/use case justifies SQLite FTS5 or embeddings. |
| Comment collection and theme analysis | **Build minimal sampling/analysis** only after access and policy review; do not bulk archive comments. |
| Thumbnail/storyboard analysis | **Prototype** only with permitted metadata/frame access; no bulk thumbnail/video redistribution. |
| MCP interface | **Defer** until a concrete external agent-client use case exists; core stays Python. |
| Audience opportunity report | **Build** — central product output and evidence model should remain ours. |

## Next technical spikes

1. Official Data API discovery + videos/channels hydration with quota accounting.
2. Channel uploads retrieval and comparable baseline selection (format, duration, age window, candidate exclusion).
3. Transcript extraction comparison: official caption access constraints vs maintained Python libraries and MCP providers.
4. A tiny local transcript index only after a real corpus and search-quality benchmark exist.
5. A safe comment-sampling spike with retention limits and explicit capability reporting.
