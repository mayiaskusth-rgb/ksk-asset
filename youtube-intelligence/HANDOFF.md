# YouTube Audience Intelligence Engine — Engineering Handoff

**Purpose:** This is the authoritative product and engineering handoff for the independent YouTube research module in this repository. A new ChatGPT engineering chat should read this file and the current code before making changes.

**Start command for the next chat:** “Read the handoff and current branch/PR state. Continue the transcript intelligence foundation from the latest dated handoff section; do not restart completed UI work or assume transcript collection is implemented.”

**Repository:** [mayiaskusth-rgb/ksk-asset](https://github.com/mayiaskusth-rgb/ksk-asset)  
**Module:** `youtube-intelligence/`  
**Status:** Existing Python MVP preserved. Iteration 0 foundation is implemented and CI-verified on `work/youtube-intelligence-iteration-0`; see the module README and `docs/` for deliverables.

---

## 1. Role and working agreement

Act as the user's senior Python engineer, product architect, and research-engineering partner. Own the iterative engineering process: inspect, plan, implement, test, run real experiments, analyze failures, document, and commit.

This is not a request for architecture discussion alone. Produce working software and evidence that it works.

The user is comfortable with Python, SQL, data science, and system design, and wants to understand important decisions. Keep explanations concise and substantive. Make routine engineering decisions independently; involve the user for meaningful product trade-offs.

Be explicit about status:
- **Implemented** — code exists.
- **Tested** — tests passed.
- **Experimentally validated** — run against real or clearly identified representative data.
- **Partially working** — known gaps remain.
- **Not implemented** — future work.

Never claim a commit, test, experiment, deployment, or background task happened unless it actually did. Work does not continue after a response ends; do not imply background progress.

## 2. Product vision

Build an independent YouTube research and audience-intelligence engine that helps answer:

1. What subjects and topics are attracting audience attention?
2. Which videos are performing unusually well relative to their creators' normal performance?
3. Which storytelling approaches, hooks, titles, structures, and visual techniques recur in strong performers?
4. What questions, interests, confusion, and unmet needs appear in audience responses?
5. Which content opportunities are differentiated and evidence-backed rather than simply popular?

The ultimate output is an **Audience Opportunity Report**, not a URL dump or a generic list of trending videos.

Distinguish three separate ideas:
- **Popular subject:** many views or broad demand.
- **Successful treatment:** a video performs unusually well for its creator or relevant comparison group.
- **KSK opportunity:** a differentiated, evidence-backed angle that is worth considering for a human-led editorial process.

Popularity is evidence, not editorial authority. Do not force trend-chasing or let metrics decide what should be made.

## 3. Outlier-score inspiration

The user shared this video as the inspiration for the outlier-score feature:

https://youtu.be/S9EIPMV6_t8

The creator discusses a browser extension/tool that surfaces an outlier score. The exact formula was not independently retrieved from the video. Do not claim to know the creator's exact formula without verifying it.

Investigate comparable tools and methods, including:
- vidIQ Outliers
- Viewstats
- 1of10
- Other YouTube outlier extensions and research tools
- Open-source GitHub projects and YouTube MCP servers

Evaluate what they calculate, data sources, limitations, free-tier constraints, terms, and whether their approach is reproducible.

### Metrics to distinguish

**Views-to-subscriber ratio**

`current video views / current channel subscribers`

A rough reach signal. It is not a creator-relative performance score and is affected by channel growth, video age, format, and subscriber activity.

**Creator-relative outlier ratio**

`candidate video views / median views of comparable uploads by the same creator`

This is the initial priority. Example:

| Creator | Typical comparable views | Candidate views | Ratio |
|---|---:|---:|---:|
| A | 5,000 | 100,000 | 20x |
| B | 500,000 | 1,000,000 | 2x |

A is the stronger relative outlier despite having fewer absolute views.

Do not treat a simple ratio as definitive proof of storytelling success. Build confidence and comparability into scoring. Baseline samples should exclude the candidate video and should preferably match format, duration class, and relevant time window. Use medians or robust statistics to reduce viral-video skew. Flag low sample sizes and missing data rather than manufacturing a score.

Potential later refinements:
- Views-to-subscriber ratio.
- Creator-relative median ratio.
- Format-specific baseline.
- Upload-age-aware comparisons.
- Robust percentile or median absolute deviation measures.
- Channel-size and topic cohort comparisons.
- Confidence / sample-size indicators.

Do not calculate VPH, historical velocity, or historical views from one current snapshot. Clearly distinguish observed data, historical snapshots, and third-party estimates.

## 4. Independence and relationship to KSK

This is an independent software product and development lifecycle. It is **not** a KSK agent and must not be merged into KSK's story-development, research, scriptwriting, review, or orchestration agents.

The two repositories have different responsibilities:

| Repository | Responsibility |
|---|---|
| [kabhi-socha-kya](https://github.com/mayiaskusth-rgb/kabhi-socha-kya) (private) | KSK editorial system: topic discovery, five cognitive lenses, research/challenge, story architecture, scripts, reviews, visual planning, workflow governance and private episode artefacts. |
| [ksk-asset](https://github.com/mayiaskusth-rgb/ksk-asset) (public) | Public-safe asset gallery and the independent `youtube-intelligence/` Python research-engineering product. |

The YouTube engine may eventually provide an evidence-backed audience opportunity report that KSK's human/editorial workflow can consider. That is a future, optional handoff—not a live integration and not an instruction to let metrics dictate KSK editorial decisions.

Keep private KSK scripts, internal agent instructions, private research notes, personal data, and unpublished assets out of the public repository. Public repository content must be safe for public inspection.

The root README files in both repositories describe this relationship. Keep those descriptions aligned when the boundary changes.

## 5. Existing implementation — preserve it

Inspect the current repository and code before editing. The existing MVP is a useful foundation, not disposable scaffolding.

Current known files:

- `youtube-intelligence/README.md`
- `youtube-intelligence/pyproject.toml`
- `youtube-intelligence/src/yti/__init__.py`
- `youtube-intelligence/src/yti/contracts.py` (added in Iteration 0; provider-neutral records, additive and not yet wired into the CLI)
- `youtube-intelligence/src/yti/scoring.py`
- `youtube-intelligence/src/yti/io.py`
- `youtube-intelligence/src/yti/report.py`
- `youtube-intelligence/src/yti/cli.py`
- `youtube-intelligence/data/sample_videos.json`
- `youtube-intelligence/tests/test_contracts.py` (added in Iteration 0)
- `youtube-intelligence/tests/test_scoring.py`
- `youtube-intelligence/tests/test_cli.py`
- `youtube-intelligence/.github/workflows/python-tests.yml`
- `youtube-intelligence/runs/.gitkeep`

Known current capabilities:
- Python package and `yti` CLI (Python 3.11+).
- Deterministic creator-relative outlier scoring.
- CSV output and basic Markdown report.
- Synthetic fixture data.
- Unit/CLI tests and GitHub Actions.
- CLI commands: `yti score --input ... --output ...` and `yti report --input ... --output ...`.

Known current scoring bands:
- Below 3x: ordinary
- 3x or above: candidate
- 5x or above: strong
- 10x or above: exceptional

Known limitation: the input supplies `creator_baseline_median_views` and `baseline_sample_size`; the code does not yet retrieve a creator's uploads or calculate the baseline itself. Re-inspect the actual code and tests to verify this snapshot before relying on it.

Previously verified CI run: [GitHub Actions run 43403961651](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43403961651), commit `f30bff6ef25c560906d09eaa442edc1c7b46844f`. Tests, sample scoring/report generation, and artifact upload passed at that time. This is historical evidence, not proof that the current branch is unchanged or that the workflow is currently green.

## 6. Proposed architecture

Use modular Python components with explicit data contracts and replaceable source adapters.

### 6.1 Research Strategist
Input: broad topic, target audience, language, geography where relevant, and general content context.

Responsibilities:
- Form initial research hypotheses and broad discovery questions.
- Generate diverse search directions from the brief.
- Inspect retrieved evidence and refine queries adaptively.
- Explore adjacent topics, creators, and unexpected directions.

**Critical constraint:** Give this component only a broad subject/audience brief—not a finished story arc or a list of story beats. The engine must discover audience-proven directions independently.

### 6.2 YouTube Discovery Engine
- Search YouTube and retrieve video metadata.
- Discover relevant channels and channel uploads.
- Expand discovery based on evidence.
- Deduplicate records and preserve query/source provenance.
- Store run configuration and retrieval timestamps.

Capture available fields such as video ID/URL, title, description, channel ID/name, publish date, observed view/like/comment counts, duration, thumbnail metadata, search query, source adapter, and retrieval time.

### 6.3 Channel Intelligence
- Retrieve comparable uploads.
- Calculate creator baselines.
- Separate Shorts and long-form.
- Consider upload age, duration class, sample size, and time window.
- Exclude the candidate from its own baseline.
- Identify channel publishing and performance patterns.

### 6.4 Outlier Intelligence
- Improve the existing scoring module rather than replacing it without evidence.
- Calculate creator-relative scores and views-to-subscriber ratios.
- Compare like with like.
- Report score, baseline, sample size, cohort/format, and confidence.
- Explicitly mark unscored cases and explain why.

### 6.5 Content Intelligence
Analyze available:
- Titles and descriptions.
- Thumbnails and visual presentation.
- Transcripts and timestamps.
- Opening hooks and story progression.
- Narrative structure, pacing, explanation techniques, and visual approaches.

Distinguish observed features from model-generated interpretations. Retain evidence references.

### 6.6 Audience Intelligence
Analyze permitted, privacy-conscious comment samples for:
- Repeated questions.
- Curiosity gaps and unanswered questions.
- Follow-up requests.
- Confusion and misunderstandings.
- Positive/negative reactions and reasons.
- Recurring interests and unmet needs.

Avoid unnecessary retention or exposure of personal information. Use representative, traceable examples rather than unsupported generalized sentiment claims.

### 6.7 Comparative Insight Engine
Compare strong outliers with ordinary performers and relevant peers. Identify recurring patterns and meaningful differences. Do not claim correlation proves causation.

### 6.8 Audience Opportunity Report
Produce a structured report with:
1. Topic demand overview.
2. Relevant channels and creators.
3. Strong outlier examples and transparent scores.
4. Successful storytelling patterns and evidence.
5. Audience questions and recurring interests.
6. Underexplored or underserved angles.
7. Potential differentiated opportunities.
8. Confidence levels and evidence links.
9. Data gaps, limitations, and alternative explanations.

The report should support a decision about what to investigate or create—not dictate the editorial answer.

## 7. Data acquisition, MCP, and tool evaluation

The user explicitly wants the actual product searches and analysis to run through Python modules. Do **not** substitute manual web searches by the assistant for a functioning pipeline.

External research is appropriate for evaluating libraries, APIs, extensions, MCP servers, licensing, and technical approaches. Product experiments must be run through the software being built.

Investigate:
- Official YouTube Data API.
- Open-source YouTube MCP servers.
- Python search/metadata libraries.
- Transcript retrieval libraries and permitted methods.
- Channel/video metadata and comment adapters.
- Outlier-analysis extensions and open-source implementations.

For each candidate, record:
- Repository/provider and URL.
- License and maintenance/activity.
- Data fields and capabilities.
- API keys, quotas, authentication, and costs.
- Reliability and failure modes.
- Terms/policy considerations.
- Suitability for direct Python use or MCP integration.

MCP is a connection/tool interface, not the product architecture. Prefer direct Python adapters when they provide stronger control, reproducibility, and tests.

Engineering constraints:
- Start with official YouTube Data API where practical.
- The public API does not expose arbitrary historical daily view counts.
- A single snapshot cannot establish historical velocity.
- Do not invent VPH, historical views, or unavailable engagement metrics.
- Transcript availability varies; preserve language, timestamps, retrieval method, and provenance.
- Respect YouTube terms, API policies, quotas, rate limits, privacy, and source rights.
- Do not download or redistribute video/audio or bulk thumbnails.
- Do not commit API keys, cookies, private transcripts, personal data, or bulk comments.
- Use synthetic/public non-sensitive fixtures in this public repository.
- Keep credentials in environment variables or an appropriate secret store.
- Build replaceable adapters and explicit source capability declarations.

## 8. Open-source GitHub reconnaissance and reuse-first strategy

**This is a required workstream in Iteration 0, not an optional later task.** Before building additional connectors or analysis modules, conduct a structured survey of public GitHub projects that solve parts of this problem. The goal is to reuse proven components where sensible and avoid rebuilding commodity plumbing.

Search GitHub broadly, not only for projects literally named "YouTube research". Include repositories in these categories:

1. **YouTube discovery and metadata:** search, video details, channel details, playlists, uploads, search expansion, and data collection.
2. **Channel analytics and competitor research:** channel upload history, video comparisons, creator baselines, niche discovery, and performance tracking.
3. **Outlier detection:** outlier scores, views/subscriber ratios, creator-relative scoring, viral-video discovery, and competitor analysis.
4. **Transcripts and captions:** transcript retrieval, language detection, timestamped segments, subtitle parsing, and transcript storage.
5. **Comments and audience signals:** comment retrieval, question/theme clustering, sentiment, audience pain points, and topic requests.
6. **Content/video intelligence:** title and thumbnail analysis, video summarization, chapter/structure extraction, visual/frame analysis, and multimodal understanding.
7. **MCP servers and agent tools:** YouTube MCP servers and MCP toolkits that expose search, metadata, transcripts, comments, or channel data.
8. **End-to-end research products:** open-source YouTube research dashboards, CLI tools, trend discovery, niche research, and creator intelligence platforms.

### Required discovery method

- Use GitHub repository search with multiple query variants and language/topic filters.
- Search for implementation terms and dependencies, not just project names.
- Follow references from useful repositories to libraries they depend on.
- Inspect repository source, not just README claims.
- Look at recent commits, releases, issues, pull requests, test coverage, examples, and maintainer activity.
- Confirm the actual license in the repository. A public repository is not automatically open-source or reusable.
- Check whether the project is archived, abandoned, API-dependent, brittle, or based on unofficial scraping.
- Record the date of the review and the commit/release inspected because project status changes.

### Candidate evaluation matrix

Create a maintained inventory, for example `docs/repo_landscape.md`, with one row per candidate:

| Field | What to record |
|---|---|
| Project | Name and repository URL |
| Category | Discovery, analytics, outliers, transcripts, comments, MCP, synthesis, etc. |
| License | Exact license and any reuse restrictions |
| Maintenance | Last meaningful commit/release, activity, open issues |
| Implementation | Language, framework, dependencies, architecture |
| Capabilities | Actual functions and data fields verified in code |
| Data source | Official API, public page, third-party API, scraping, browser automation |
| Setup | API key, OAuth, cookies, paid account, quota, hosted dependency |
| Reliability | Tests, retries, rate limiting, known breakages |
| Policy/privacy | Platform terms, data handling, user data, redistribution concerns |
| Reuse decision | Adopt, wrap with adapter, borrow design only, defer, or reject |
| Rationale | Concrete reason for the decision |

Do not rank projects by stars alone. Consider correctness, maintenance, license, data access, reliability, and fit with our modular architecture.

### Reuse decision rules

Classify each candidate:

- **Adopt:** mature, appropriately licensed, maintained, tested, and directly useful.
- **Wrap:** useful capability but isolate it behind our own adapter/data contract.
- **Borrow design:** useful algorithms or architecture, but do not depend on the project at runtime.
- **Prototype:** promising but uncertain; test in a disposable spike before adoption.
- **Reject/defer:** incompatible license, abandoned, unreliable, policy-risky, unnecessary, or poor fit.

Prefer small, composable dependencies over adopting a large application wholesale. Do not copy code without license review and attribution obligations. Do not add a dependency just because it exists.

### Minimum Iteration 0 outputs

- `docs/architecture.md` — module boundaries, provider strategy, persistence and quality constraints.
- `docs/data_contracts.md` plus `src/yti/contracts.py` — normalized records and provenance requirements.
- `docs/scoring_methodology.md` — preserved MVP bands and comparability requirements.
- `docs/repo_landscape.md` — reviewed GitHub projects, category coverage, findings, and reuse decisions.
- `docs/tooling_landscape.md` — hosted tools/extensions/MCP services, plan constraints, and comparison with open-source options.
- `tests/test_contracts.py` — deterministic contract validation tests.
- An explicit **build vs reuse** decision for each major capability and a shortlist of technical spikes.

**Iteration 0 status (2026-11-13):** Complete on `work/youtube-intelligence-iteration-0`. The above documents and additive contracts are present. Existing scoring, IO, report, CLI, fixtures and CI workflow are unchanged. GitHub Actions run [43420954353](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43420954353) completed successfully: package installation, **13 tests**, sample scoring of 5 videos, Markdown report generation and artifact upload all passed. PR [#1](https://github.com/mayiaskusth-rgb/ksk-asset/pull/1) is open and ready for review; it has not been merged.

The initial scan should be broad enough to avoid tunnel vision, then narrow to a small shortlist for deeper code/license review. Aim to inspect a meaningful spread of candidates across all eight categories; do not pad the inventory with irrelevant repositories just to hit a number.

**Important:** Do not assume that an MCP server is the best way to integrate a capability. Compare direct Python library/API use, an MCP adapter, and independent implementation. The engine's internal contracts must remain ours so a data provider can be replaced later.

## 8. Benchmark topics

Use these three initial benchmark subjects:

1. **How barcodes work**
2. **The evolution of smartphone photography and cameras**
3. **Satellites and their role in everyday life**

These represent different kinds of subjects. Give the system only the broad subject and target audience. Do not provide finished story arcs.

Compare discovery quality, outlier quality, audience insights, evidence coverage, and whether the resulting opportunities are genuinely useful.

## 10. Iteration roadmap

Every iteration requires: objective, acceptance criteria, implementation, tests, real experiment where applicable, failure analysis, documentation, and a verified commit.

### Iteration 0 — Architecture and data contracts [COMPLETE]
- Audit existing code, tests, README, workflow, and repository state.
- Conduct the required public GitHub repository reconnaissance across all eight categories; inspect source, licenses, maintenance, data sources, tests, and policy constraints.
- Create `docs/repo_landscape.md` and `docs/tooling_landscape.md` with explicit adopt/wrap/borrow/prototype/reject decisions.
- Compare direct Python/API integration with MCP and custom implementation; identify reusable components and avoid rebuilding commodity plumbing.
- Investigate relevant outlier tools/extensions and hosted research products.
- Define module boundaries and data models.
- Define source adapter interfaces and provenance requirements.
- Specify outlier scoring and comparability constraints.
- Define testing and reproducibility strategy.
- Deliver architecture/data-contract documents, update README/roadmap, and add tests for core contracts.

### Iteration 1 — YouTube search adapter
Implement actual search and metadata retrieval, save reproducible research runs, support broad topic searches, and validate with real topics.

### Iteration 2 — Channel intelligence
Retrieve channel uploads, calculate baselines, separate formats, and test sample-size and comparability limitations.

### Iteration 3 — Outlier intelligence
Extend existing scoring, add views-to-subscriber ratio, improve age/format-aware comparisons, and validate against known examples.

### Iteration 4 — Adaptive Research Strategist
Generate broad queries from a topic brief, inspect results, refine searches, and discover adjacent subjects/creators.

### Iteration 5 — Content intelligence
Add transcript retrieval, title/thumbnail observations, storytelling analysis, and evidence-backed structured outputs.

### Iteration 6 — Audience intelligence
Add permitted comment sampling, recurring questions, audience interests, and unmet-need analysis.

### Iteration 7 — Comparative synthesis
Compare outliers and ordinary performers, identify patterns, and distinguish evidence from hypotheses.

### Iteration 8 — End-to-end benchmark experiments
Run the complete workflow on barcode, camera evolution, and satellites.

### Iteration 9 — Reliability and usability
Add caching, retries, logging, quota/cost controls, reproducible run manifests, versioned reports, and a better CLI experience.

Do not build a dashboard first. Prove the engine through a reliable CLI before adding a UI.

Do not advance merely because code runs. Demonstrate that the intended capability works.

## 11. Engineering quality bar

Maintain:
- Clear module boundaries and type hints.
- Explicit schemas/data contracts.
- Structured logging and actionable errors.
- Unit and integration tests.
- Versioned prompts and structured model outputs.
- Evidence references and source provenance.
- Reproducible run configurations, queries, timestamps, scoring versions, and outputs.
- Caching, retries, rate-limit handling, and quota controls where appropriate.
- Honest confidence and limitations.

For each iteration:
1. State objective and acceptance criteria.
2. Inspect existing code and dependencies.
3. Implement the smallest coherent increment.
4. Add tests.
5. Run tests and CI.
6. Execute a real experiment when appropriate.
7. Inspect actual outputs and failure cases.
8. Update docs and roadmap.
9. Commit and report the exact commit/branch and verification evidence.

No dashboard-first approach. No manual-search substitution. No invented metrics. No unsupported claims.

## 12. First instruction to the next engineering chat

**Read this handoff and inspect the current repository. Iteration 0 is complete; plan Iteration 1.**

Next engineering chat should:
1. Verify PR #1 and whether it has been merged into `main`.
2. Re-read the current repository state and Iteration 0 architecture/contracts.
3. Plan Iteration 1 (YouTube search adapter) with explicit source capability, quota, provenance, and test acceptance criteria.
4. Keep the existing scoring CLI working and do not begin channel baseline work until discovery metadata is reliable.
5. Use the three broad benchmark subjects only when running real experiments; do not supply finished story arcs.

Do not implement every module immediately. Preserve the MVP and build one tested vertical slice at a time.

## 15. Research Run Explorer and transcript/analysis workflow (2026-11-13)

The public repository's existing root `index.html` is the KSK Visual Asset Library. Do not replace it. The additive `research.html` is a separate static YouTube Research Run Explorer, linked from the asset gallery. Both are deployed by the existing GitHub Pages workflow.

### Explorer implementation
- `research.html` loads `research-runs/index.json` and a selected run JSON file.
- `research-runs/satellite-43436550833.json` is the first public-safe run fixture, copied from GitHub Actions run 43436550833 / artifact 14043943457.
- It records 10 search phrases, 50 result slots and 47 unique videos, with per-query rank preserved and cross-query duplicates visible.
- UI supports run selection, query selection, filtering, sorting, metadata inspection, direct YouTube links and an opt-in embedded player.
- Transcript and analysis sections must remain explicitly marked as not collected/not analysed until real artefacts exist.
- Future run outputs should be added as separate JSON files and registered in `research-runs/index.json`. Do not store full transcripts or private data in this public repository.

### Video analysis instruction contract
- `docs/agents/VIDEO_ANALYSIS_AGENT.md` (under `youtube-intelligence/`) is a versioned, human/model-followed analysis rubric, not an autonomous paid-API agent.
- Follow it when analysing supplied transcripts. Require timestamps for claims about hooks, structure and moments; distinguish observation, interpretation and hypothesis; never infer retention or causality from public metadata.
- Refine only through versioned changes informed by the user's review.

### Transcript collection direction
- First candidate adapter: extend yt-dlp to inspect and retrieve available creator-provided or auto-generated captions without downloading video/audio (`--list-subs`, `--write-subs`, `--write-auto-subs`, `--skip-download`, language selection).
- Compare with the open-source `youtube-transcript-api` adapter on a small bounded sample; it may be blocked/rate-limited because it relies on YouTube web interfaces.
- Design and safety rules: `docs/experiments/transcript_collection.md`.
- Preserve language, caption type, timestamps, source/version, retrieval time and explicit unavailable/blocked states. No cookies, proxies, CAPTCHA bypasses, retries or media downloads in the first pass.
- Never fabricate missing transcripts. Keep full transcript artefacts out of this public repository.

### Known explorer data gaps
- Upload dates were unavailable in the first run.
- Channel IDs are intentionally omitted from the public display fixture; raw workflow artifact retains the full extractor output for seven days.
- The current fixture is a snapshot; it does not establish view velocity or historical performance.


## 16. Transcript intelligence foundation — latest handoff (2026-11-13)

**Active branch:** `research/transcript-intelligence-foundation` ([draft PR #11](https://github.com/mayiaskusth-rgb/ksk-asset/pull/11))  
**Base:** current `main` after PR #10 (expanded watch-page alignment).  
**Status:** Design/reconnaissance work in progress. This branch is not merged. No transcript collector, automated analysis runtime, new Python dependency, or dashboard work has been implemented.

### User-approved direction

Proceed in two distinct capabilities:

1. **Transcript acquisition:** retrieve captions for selected videos; preserve source, language, caption type, timestamped segments, retrieval status and provenance. No media download in the first pass.
2. **Transcript intelligence:** explain the subject/concepts, content format, narrative mode, hook/open loops/payoff, structure, explanation techniques, tone/rhetoric, pacing, strong moments and reusable techniques.

The user wants a practical research tool, not a generic summarizer or an opaque video-quality score. Keep the existing `VIDEO_ANALYSIS_AGENT.md` as the broader video communication analysis contract; the new transcript-specific contract gives more detail for transcript-derived signals.

### New design files on this branch

- `docs/agents/TRANSCRIPT_INTELLIGENCE_AGENT.md` — versioned analysis instructions and evidence rules.
- `docs/transcript_analysis_schema.md` — proposed provider-neutral structured output; conceptual v0.1, not yet JSON Schema or Python models.
- `docs/experiments/transcript_tools_reconnaissance.md` — inspected repositories, license notes, constraints and reuse decisions.
- `docs/experiments/transcript_collection.md` — acquisition design; now links the reconnaissance and selected first spike.
- Module README updated with current status, links, roadmap and immediate next work.
- Root README updated to identify this branch and avoid stale Iteration 0 status.

### Public repository reconnaissance (checked 2026-11-13)

1. [youtube-transcript-extractor](https://github.com/GregHabiskis/youtube-transcript-extractor): describes yt-dlp captions-only collection, creator-caption preference, JSON3/VTT/SRT parsing, rolling-caption cleanup and timestamps. GitHub metadata showed no declared license; pyproject requires Python 3.14, while our package targets Python 3.11+. **Borrow design only; do not copy or depend on it.**
2. [analyze-video](https://github.com/eruto-skills/analyze-video): MIT; skill describes full-transcript macro/micro structure, hook, information density, hedging, credibility, re-engagement, memorable phrasing, contrast and closing, with unscored evidence-led comparison. **Borrow analytical design; no runtime dependency.**
3. [youtube-transcriber](https://github.com/nickholdenproper/youtube-transcriber): Python CLI/GUI/API; captions, local Whisper fallback, Ollama analysis, optional visual/voice passes. Its custom Free-to-Use License is not a permissive OSI license; audio fallback downloads media and cloud Ollama conflicts with our initial constraints. **Borrow architecture ideas only; do not adopt or copy code.**

Full findings and links are in `docs/experiments/transcript_tools_reconnaissance.md`.

### Analysis principles agreed

- Use a **multi-label** content-format taxonomy: documentary, mystery/reveal, investigative, educational explainer, narrative essay, case study, tutorial/demo, listicle, commentary, interview, review/comparison, news, personal story, compilation/reaction, mixed/other.
- Also identify narrative mode separately: chronological, question-led, problem-solution, claim-evidence, thematic, episodic, list-based, etc.
- Keep three pacing concepts separate: speech rate (WPM), information density (new concepts/claims), and narrative pace (frequency of section/question/story-beat changes).
- Caption timestamps can be coarse or unreliable; report method and quality caveats. Transcript alone cannot establish visual editing pace, cuts, music, silence, vocal energy, retention, CTR or causal performance effects.
- Every claim about a hook, structure, moment or technique needs timestamp evidence.
- Separate observation, interpretation and hypothesis. No invented content and no opaque quality score.
- Compare individual reports only after a small batch exists; compare like with like (topic, format, duration, caption quality, publication age). Small samples yield hypotheses, not universal truths.

### Constraints unchanged

- No paid LLM API calls.
- No video/audio downloads in the first pass.
- No cookies, account sessions, proxies, proxy rotation, CAPTCHA bypasses or access-control workarounds.
- Bounded sequential requests, caching, zero retries initially; stop on 403/429/challenge.
- No full transcripts or private run artefacts in this public repository.
- Do not introduce Whisper, Ollama, embeddings, a database, MCP runtime or new UI in this design phase.
- Preserve the existing Python MVP and all earlier research explorer/layout work.

### Next engineering steps

1. Update `docs/experiments/transcript_collection.md` to link reconnaissance and record the selected first spike: yt-dlp subtitle-only adapter, subject to a bounded local test and current policy review.
2. Inspect existing `pyproject.toml`, contracts and CLI before implementation. Propose a minimal `TranscriptObservation` / `TranscriptSegment` contract that can represent retrieved, no-captions, unavailable, blocked and failed states.
3. Build a captions-only adapter with deterministic tests using synthetic VTT/JSON3 fixtures; never require live YouTube for unit tests.
4. Add a manual, bounded real-data experiment against a few selected satellite videos only after local tests pass. Record track availability, caption type, language, timestamps, coverage, errors and stop conditions; keep raw transcript output private.
5. Validate transcript quality checks and report output. Only then run a human/model-assisted analysis pilot on 3–5 videos and revise the rubric from user feedback.
6. Update module README, root README and this handoff in every material PR. Keep branch/PR/commit/test/experiment status explicit.

**Next chat must start from this section and inspect the branch.** Do not claim this branch is merged or that transcript acquisition/analysis is working until code, tests and a bounded experiment establish that.


## 17. First transcript code increment (2026-11-13)

The branch now contains the first executable transcript foundation:

- `src/yti/transcripts.py`
  - `TranscriptSegment`: start, duration, end property and non-empty text validation.
  - `TranscriptObservation`: video ID, explicit status (retrieved / no_captions / unavailable / blocked / failed), source provenance, language, caption type, source format, segments and normalized-content SHA-256.
  - `parse_vtt`: deterministic WebVTT cue parser; strips markup, decodes entities, preserves cue timing and sorts by start.
  - `parse_json3`: deterministic YouTube JSON3 event parser; preserves millisecond offsets/durations and joins text fragments.
  - `make_transcript_observation`: returns a truthful no_captions state for empty parsed content.
  - No network calls and no third-party dependencies.
- `tests/test_transcripts.py`: synthetic tests for VTT, JSON3, timing, markup/entities, empty captions, status invariants and checksum.

**Not implemented:** yt-dlp retrieval adapter, language-track discovery/selection, live collection, retries/cache, transcript quality scoring, analysis execution. Parser tests have been added but CI for the latest branch commit must be checked before claiming they pass.

### CI correction discovered

The first PR #11 CI run failed on an existing research explorer assertion, not on transcript code: `tests/test_research_explorer_data.py` expected the literal labels “Not collected yet” and “Not analysed yet”, while the expanded watch-page markup had changed the wording. This was corrected in `research.html` without changing functionality. Verify the next CI run against the latest head.

### Next implementation slice

1. Verify the current PR head and CI.
2. Review parser edge cases; add any missing deterministic tests.
3. Add a yt-dlp adapter using its Python API (not shell interpolation), isolated behind a small interface. Keep yt-dlp an optional/runtime dependency only if the package design supports it cleanly; otherwise add an explicit pinned-compatible dependency and document it.
4. Adapter should first list caption tracks, prefer creator-provided captions, then optionally auto captions; never silently choose translated captions. Return language/caption type/source format accurately.
5. Use skip-download semantics; never fetch media. Bound request count and timeout, cache only private/local artefacts, perform zero retries initially, and stop on 403/429/challenge signals. Do not use cookies, proxies or bypasses.
6. Unit tests mock the extractor boundary; no live YouTube calls in CI. Add an opt-in manual experiment command only after tests and error mapping are sound.
7. Update this handoff and both READMEs as the implementation evolves.


## 18. Optional yt-dlp adapter implementation (2026-11-13)

Added on the active PR #11 branch:

- `src/yti/transcript_adapter.py`: `YtDlpTranscriptAdapter` uses yt-dlp's Python API, performs metadata track inspection, prefers creator-provided captions over auto-generated captions, matches only the requested language/base-language regional variants, and retrieves only that track.
- Both metadata and subtitle retrieval set `skip_download=True`; no video/audio download is intended. Subtitle output is written only into a temporary directory and removed after normalization.
- No cookies, proxy settings, retries, fragment retries or extractor retries are configured.
- Maps no matching language track to `no_captions`, rate-limit/access challenge signals to `blocked`, and other extractor problems to `failed`; raw exception text is not exposed in the observation.
- `pyproject.toml` adds optional extra `youtube = ["yt-dlp>=2025.1.15"]`. Install with `pip install -e ".[youtube,dev]"`.
- `tests/test_transcript_adapter.py` mocks the yt-dlp Python API to verify manual-caption preference, skip-download options, no language substitution, 429 handling and URL validation.

**Caution:** This adapter has not yet been run against live YouTube. Confirm actual yt-dlp subtitle output behavior (including extension and requested_subtitles metadata) before a live experiment. No claims of live reliability yet. Current CI status must be checked against the latest PR head; test code was added after prior CI runs.


## 19. One-video transcript CLI (2026-11-13)

Added `yti transcript` to the existing CLI:
```bash
yti transcript --video-id VIDEO_ID --url YOUTUBE_URL --language en --output runs/private/VIDEO_ID.transcript.json
```
- Uses the optional yt-dlp adapter.
- Writes a structured JSON observation (including segments and provenance) to the caller-specified local path.
- Creates parent directories and prints only the status/path.
- CLI test mocks the adapter and verifies JSON output.
- The command does not add a public fixture or commit transcript data. The user/operator must keep output in a private local path.

Next: verify latest CI; confirm current yt-dlp API output details before live use; run only a tiny sequential satellite sample with no retries and stop on access challenges. The adapter/CLI are not yet experimentally validated against YouTube.


### Verification update — 2026-11-13

GitHub Actions run [43459990611](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43459990611) completed successfully on commit `4bb8905f4c8d7ba11eade85c7346548e930f992a`: **31 tests passed**, and the existing sample scoring/report pipeline completed. This run includes the parser, adapter and CLI tests. Subsequent commits in this branch are documentation-only; a workflow for the newest README commit `375e14b4cd10a06c4ea71eecc2d2c0b462e78839` is queued and must be checked before final PR review.

Earlier failures on this branch were due to the existing explorer placeholder-string assertion. The page wording was corrected, and later runs passed.


### Adapter hardening follow-up (2026-11-13)

The adapter now also:
- sets `noplaylist=True` so a supplied URL cannot expand into a playlist batch;
- allows regional variants only when the requested language is a base code (e.g. `en`); an explicit regional request (e.g. `en-US`) must match exactly;
- maps additional bot-verification wording to the blocked state.

Tests cover single-video scope and strict regional language matching. These changes are pending the newest CI run.


### Latest CI debugging note (2026-11-13)

A follow-up adapter-hardening commit initially introduced a literal escaped newline in the options dictionary, causing test collection to fail. The syntax issue was corrected in commit `cfec61f0f310954f9ce821263725f7fe2831aa4e`. The next CI run on that commit must pass before the PR is considered ready. The previous 33-test pass remains valid only for the earlier code state.


The next run exposed a second literal escaped-newline typo in the new adapter test assertion (not application code). It was corrected in commit `dbd366b20987ef17e485a67304c2cf7abd65e25a`. The latest run must be checked again; do not cite the earlier 33-test result as validation of these newest edits.


The regional-language test then exposed that the intended helper replacement had not actually applied; the old fallback remained. The helper was replaced explicitly in commit `ddcf55679ae14880ea085f56a07ffbca046b3b2c`. Verify the next CI run before proceeding. This was a test-detected behavior bug: explicit regional requests could have fallen back to a different region, which is now intended to be disallowed.


### Verification after adapter hardening — 2026-11-13

GitHub Actions run [43460851620](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43460851620) completed successfully on code commit `ddcf55679ae14880ea085f56a07ffbca046b3b2c`: **34 tests passed**, and the existing sample scoring/report pipeline completed. This includes strict regional-language selection and single-video mode. The later handoff-only commit `bd1b6516d0ec8cc7d9742d41835c7abf917f9942` records the verification; no code changed after the successful run.


## 20. Bounded satellite transcript experiment harness (2026-11-13)

Added on the active PR #11 branch:

- `scripts/run_transcript_probe.py` runs one preselected video by default or two selected videos sequentially.
- Default sample is the longest video in the original 47-video satellite discovery set: Norsat International's 59:14 satellite communications webinar (`efjBiVN_N3M`).
- Optional second sample is Astrum Extra's 48:17 satellite video (`jo8Z4UzIBQk`). The `both` mode runs these sequentially and stops immediately if the first result is blocked.
- `.github/workflows/satellite-transcript-probe.yml` provides a manual GitHub Actions workflow. It is opt-in and does not run as part of ordinary CI.
- The workflow uploads only a sanitized report: video metadata, status, language, caption type, subtitle format, segment count, transcript end timestamp, detail code, source method and retrieval timestamp.
- Transcript text, excerpts, checksums and raw subtitle payloads are deliberately excluded from the artifact. The full transcript remains in process memory and is not committed or uploaded.
- `tests/test_transcript_probe.py` verifies default one-video selection, two-video sequential stop-on-block behavior and that transcript text is absent from the report.

**Important validation boundary:** these tests are mocked. The actual GitHub-hosted live workflow has not been dispatched. Once this workflow is merged to `main`, run Actions → Satellite transcript probe → `norsat-webinar` for the first live test. Only if successful should the optional `both` selection be run. GitHub-hosted IP blocking is possible; 403/429/challenge means stop, not bypass.

### Next review gates

1. Merge after CI and code review; verify Pages deployment separately.
2. Trigger the default one-video workflow and inspect the sanitized artifact.
3. If successful, run the second video and compare completeness, caption source/language, segment count and timestamp coverage.
4. Fix adapter issues before selecting/building the analyser.
5. Test the analyser against the same one or two transcripts in a private/local context.
6. Expand to a few more only after review. Do not process all 47 yet.

The analyser remains **designed but not selected/implemented as an execution module**. The agent instructions and schema are specifications, not a working automated analyser.


### Probe harness CI verification — 2026-11-13

The first CI run for the new probe tests caught a test import/monkeypatch target issue; it did not reach the live adapter. The test was corrected to import and patch `yti.transcript_probe` directly. Latest verified CI run [43463631750](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43463631750) passed on the probe implementation: **37 tests passed**, and the existing five-video sample scoring/report pipeline completed. This validates the bounded runner's mocked behavior and privacy-safe report shape only. It is not live YouTube validation.


## 21. Live transcript challenge and isolated provider diagnostic (2026-11-13)

### Verified live result

- Main commit: 6ca592d3515ba348b570c5122cd6e30450989969.
- Live workflow run: https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43466201180.
- Runner: GitHub-hosted Ubuntu 24.04, Azure westus3.
- Installed yt-dlp: 2026.10.26.
- Selected sample: Norsat International satellite communications webinar, efjBiVN_N3M.
- Extractor response: Sign in to confirm you’re not a bot.
- Result: blocked / ACCESS_CHALLENGE, zero transcript segments, no retry, sanitized report only. Green workflow means the challenge was handled as designed, not that extraction succeeded.

### Isolated diagnostic branch

Branch: diagnostic/youtube-transcript-api-comparison.

This branch adds an optional youtube-transcript-api adapter and a separate manual GitHub Actions workflow. It is not an automatic fallback and does not change the yt-dlp adapter, CLI, or workflow.

- src/yti/transcript_api_adapter.py: normalizes timestamped snippets and classifies blocked/no-caption/provider-error outcomes.
- src/yti/transcript_api_diagnostic.py and scripts/run_transcript_api_diagnostic.py: one selected video, sanitized report.
- .github/workflows/transcript-provider-diagnostic.yml: independent workflow, one-video selection only.
- Optional dependency: pip install -e .[transcript-diagnostic].
- Tests: tests/test_transcript_api_adapter.py and tests/test_transcript_api_diagnostic.py.

Safeguards: no cookies, browser sessions, proxies, CAPTCHA workarounds, media downloads, automatic retry/fallback, or transcript-text artifacts. A second provider may still be blocked by the same runner network; this experiment is comparative evidence, not a bypass strategy.

### Next action

Review diagnostic branch CI. If it passes, merge only after review, then manually run the separate workflow once with norsat-webinar. Inspect the sanitized artifact before deciding anything further. Do not run the second sample or bulk collection yet. Do not start transcript analysis until acquisition is demonstrated on real caption data.

## Cloudflare persistence foundation — 2026-11-13

A separate infrastructure proposal is being developed in the repository under `cloudflare/`. It does not replace GitHub or GitHub Pages and must not deploy the repository root as a Worker.

- `cloudflare/README.md` defines the intended split: GitHub for code/versioning, GitHub Pages for the static UI, Cloudflare Workers for an authenticated API, D1 for private structured persistence, and Python/GitHub Actions for analysis jobs.
- `cloudflare/schema.sql` proposes D1 entities for projects, research runs, canonical videos, project-video membership/review decisions, discovery provenance, transcript revisions, human notes, analysis runs and findings.
- `cloudflare/DATA_MODEL.md` defines Keep / Drop / Review later semantics. Drop excludes a video from further processing but never deletes its record. Manual video links enter the same lifecycle.
- First implementation gate: one canonical video and a manually pasted transcript can be saved and retrieved; revisions are retained; unauthenticated read/write requests fail.
- Keep the first test limited to one video. Do not add bulk imports, analysis UI, or automated provider fallback yet.
- No Worker code, D1 database, Access policy, secret, or Cloudflare deployment has been created at this design stage. The Cloudflare account owner must authorize initial resource creation and secret configuration.

The current extraction experiment is complete enough to pause: the yt-dlp and separate youtube-transcript-api GitHub-hosted tests both encountered YouTube access challenges. This does not prove all networks or hosted providers are blocked. The immediate practical path is manual transcript input with private persistence.


### Second review of Cloudflare persistence proposal — 2026-11-13

A second design review identified and addressed these points on the PR branch:

- Added append-only `video_review_events` so reversible Keep / Drop / Review later decisions actually retain their transition history. The Worker must update `project_videos` and insert the event atomically.
- Corrected the transcript collection experiment notes: both GitHub-hosted extraction approaches have already been run and blocked; the next practical route is manual browser paste, not another provider diagnostic.
- Clarified that Cloudflare Access + browser session/CORS behaviour must be tested from the mobile browser before wiring the GitHub Pages UI. CORS is not authentication.
- The initial deployment is single-user/private. Multi-tenant ownership and authorization are not implied by this schema and would require an explicit design before multiple users are supported.

Remaining implementation gates: execute the full D1 schema against SQLite/D1 in CI; test foreign-key enforcement and atomic review updates; define API payload/size limits and input validation; verify transcript revision semantics (including duplicate content); verify Access-protected API requests from the mobile browser. This PR remains design/schema only and must not be deployed as-is.
