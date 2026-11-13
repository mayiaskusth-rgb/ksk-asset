# YouTube Audience Intelligence Engine — Engineering Handoff

**Purpose:** This is the authoritative product and engineering handoff for the independent YouTube research module in this repository. A new ChatGPT engineering chat should read this file and the current code before making changes.

**Start command for the next chat:** “Read the handoff and repository state, verify the Iteration 0 PR status, then plan Iteration 1.”

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


---

## 13. Active experiment override — satellite pipeline (2026-11-13)

This section supersedes the earlier multi-topic benchmark sequence for the immediate next work. The first end-to-end experiment is **Satellites** only. Do not run barcode or camera topics in this phase.

### Research brief

The first-stage input is deliberately the single word:

\`Satellites\`

Do not supply a target audience, geography, language, predefined application, narrative, or story arc to the idea generator. The first stage must independently generate ten distinct, non-overlapping, independently searchable research ideas. It should return structured ideas and two search-query formulations per idea. These are hypotheses, not claims about popularity or demand.

### Current experiment artifacts

- \`src/yti/ideas.py\`: provider-neutral prompt builder and strict JSON parser/validator.
- \`tests/test_ideas.py\`: tests for prompt constraints, exact count, required uniqueness and malformed output.
- \`data/experiments/satellite_ideas.json\`: first structured ten-idea output.
- \`docs/experiments/satellite_idea_generation.md\`: dry-run method, initial quality review, overlap risks and tuning criteria.

**Honest status:** The first idea list was generated as a ChatGPT model dry run and then saved as a structured fixture. The Python module currently builds the prompt and validates model output; it does not yet invoke an LLM API. GitHub CI verification is pending. Do not describe this as a fully automated LLM pipeline.

### Agreed pipeline order

1. Narrow brief \`Satellites\` → generate 10 distinct ideas.
2. Search YouTube using two queries per idea (20 queries total); collect 20–30 results per query, preserving query provenance and retrieval timestamps.
3. Deduplicate by video ID and hydrate available metadata.
4. Retrieve comparable uploads from each candidate's channel.
5. Calculate creator-relative outlier scores using comparable format/age cohorts and a candidate-excluding median baseline. Keep low-sample candidates unscored or low-confidence.
6. Select a shortlist for transcript retrieval.
7. Analyze transcript themes, hooks, explanatory techniques, narrative structure and examples, with timestamped evidence.
8. Produce a comparative report across the selected videos.

Video/frame analysis is deferred. Comment analysis is also deferred until the first pipeline demonstrates value.

### Tuning gates

Do not tune idea generation based only on how the ideas sound. After YouTube discovery, evaluate:
- relevance rate among the first 20–30 results per query;
- unique videos after cross-query deduplication;
- overlap between result sets for different ideas;
- query result composition (Shorts/long-form, news, institutional channels, unrelated results);
- whether creators have enough comparable uploads to support a reliable baseline.

If two ideas return nearly identical video sets, refine their scope or merge them. If a query is weak, refine the query before rewriting the idea. Keep an audit trail of prompt version, model, input, raw response, parsed ideas and reviewer changes.

### Next engineering increment

Implement a configurable LLM provider adapter and persist prompt/model/run metadata. Then implement official YouTube Data API search and metadata hydration with quota accounting. For the first run, 20 search queries are within the documented default 100 \`search.list\` calls/day bucket, but pagination and retries consume additional calls. Keep result counts configurable and record partial failures.

Do not proceed to transcript analysis until the outlier shortlist is based on actual creator baselines, not absolute views or YouTube search rank.


## 14. Active no-API search probe — safety and execution contract (2026-11-13)

The user has chosen to test a conservative no-API extraction path for the satellite experiment. The intent is occasional research during development, with the option to replace the adapter with the official YouTube API later. Do not treat this intent as permission to bypass platform restrictions.

### Implemented probe

- Adapter: `src/yti/providers/yt_dlp_probe.py`
- Tests: `tests/test_yt_dlp_probe.py`
- Experiment notes: `docs/experiments/satellite_no_api_probe.md`
- Optional dependency: `pip install -e ".[probe]"`
- Local command from this module directory: `python -m yti.providers.yt_dlp_probe`

### Hard safeguards

1. One first-choice query per idea (ten queries maximum in the initial run).
2. Exactly five search results per query.
3. Sequential query execution; ten-second pause between uncached queries.
4. yt-dlp request sleep settings enabled.
5. No API key, login, browser cookies, proxy, proxy rotation, CAPTCHA workaround, or access-control bypass.
6. Zero retries.
7. Successful queries are cached locally and not fetched again on later runs.
8. HTTP 403/429, sign-in/verification/CAPTCHA challenge, timeout, or extractor error stops the entire run. No alternate identity, IP, endpoint, or extraction tool may be used to continue after a block.
9. Do not download video, audio, subtitles, or thumbnails in this probe.
10. Preserve query provenance, retrieval timestamp, returned metadata, request count, and stop reason. Local raw run outputs are git-ignored and must be reviewed before any sharing.

The ten-second pause is a conservative experiment setting, not an approved platform rate or a guarantee against throttling. Anonymous access does not guarantee that an IP will not be throttled.

### Current honest status

The adapter and mocked unit tests are implemented. **No live YouTube extraction has been executed from the engineering environment.** The user must run the command locally and share the generated JSON/report or terminal output for empirical evaluation. Do not describe the extractor as working until that evidence is reviewed.

### Next action

Run the bounded probe once in the user's local environment. Evaluate query success/failure, relevant-result rate, unique videos, cross-query duplicates, metadata completeness, and stop reason. Do not expand volume, collect channel histories, or retrieve transcripts until this first search stage is reviewed. If any access restriction is encountered, stop and document it; do not retry or evade it.

This no-API probe is an experimental source adapter. Keep the existing scoring MVP and all provider-neutral contracts intact. The official YouTube API can be implemented later as a separate adapter without changing downstream contracts.
