# YouTube Audience Intelligence Engine — Engineering Handoff

**Purpose:** This is the authoritative product and engineering handoff for the independent YouTube research module in this repository. A new ChatGPT engineering chat should read this file and the current code before making changes.

**Start command for the next chat:** “Go. Read the handoff and repository state, then start Iteration 0.”

**Repository:** [mayiaskusth-rgb/ksk-asset](https://github.com/mayiaskusth-rgb/ksk-asset)  
**Module:** `youtube-intelligence/`  
**Status:** Existing Python MVP; further development not yet started from this handoff.

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
- `youtube-intelligence/src/yti/scoring.py`
- `youtube-intelligence/src/yti/io.py`
- `youtube-intelligence/src/yti/report.py`
- `youtube-intelligence/src/yti/cli.py`
- `youtube-intelligence/data/sample_videos.json`
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

## 8. Benchmark topics

Use these three initial benchmark subjects:

1. **How barcodes work**
2. **The evolution of smartphone photography and cameras**
3. **Satellites and their role in everyday life**

These represent different kinds of subjects. Give the system only the broad subject and target audience. Do not provide finished story arcs.

Compare discovery quality, outlier quality, audience insights, evidence coverage, and whether the resulting opportunities are genuinely useful.

## 9. Iteration roadmap

Every iteration requires: objective, acceptance criteria, implementation, tests, real experiment where applicable, failure analysis, documentation, and a verified commit.

### Iteration 0 — Architecture and data contracts
- Audit existing code, tests, README, workflow, and repository state.
- Investigate relevant outlier tools/extensions, MCP servers, and reusable libraries.
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

## 10. Engineering quality bar

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

## 11. First instruction to the next engineering chat

**Go. Read this handoff and inspect the current repository. Start Iteration 0.**

Specifically:
1. Inspect the current `main` branch and the existing `youtube-intelligence/` implementation.
2. Confirm the actual repository state, tests, CI, and current scoring behavior.
3. Investigate relevant outlier extensions/tools and open-source MCP or Python projects.
4. Identify what can be reused and what should remain our own implementation.
5. Define the architecture, data contracts, source-adapter contracts, and scoring methodology.
6. Add Iteration 0 documents and tests in the repository.
7. Update the relevant READMEs and roadmap.
8. Commit the documentation/engineering foundation on a dedicated feature branch unless the user explicitly requests otherwise.
9. Report actual changes, commit SHA, test results, and remaining gaps.

Do not implement every module immediately. Establish a sound foundation first, preserve the existing MVP, and build iteratively.
