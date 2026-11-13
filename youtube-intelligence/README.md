# YouTube Audience Intelligence Engine

An independent Python research-engineering product for YouTube topic discovery, creator-relative outlier analysis, and audience/storytelling intelligence.

This module lives in the public `ksk-asset` repository but is **not a KSK story-development agent**. See the repository root README for the boundary and [HANDOFF.md](HANDOFF.md) for the full product specification and engineering instructions.

**Current status (2026-11-13):** MVP and Iteration 0 foundation are preserved and merged into `main`. The active design branch is `research/transcript-intelligence-foundation` ([draft PR #11](https://github.com/mayiaskusth-rgb/ksk-asset/pull/11)). It adds transcript-tool reconnaissance, a transcript-intelligence analysis contract, an output-schema proposal, and updated handoff/roadmap notes. The transcript foundation now includes provider-neutral transcript observation/segment records, deterministic WebVTT and YouTube JSON3 parsers, and an optional yt-dlp captions-only adapter. Synthetic tests mock the extractor; no live YouTube retrieval or automated analysis experiment has been run yet. Install the optional adapter dependency with `pip install -e ".[youtube,dev]"`.

**Research Run Explorer:** The static [explorer](../research.html) displays the first bounded satellite run (10 searches, 50 result slots, 47 unique videos), with per-query positions, provenance, metadata, direct YouTube links and an optional embedded player. Transcript and video-analysis sections are explicit placeholders until those stages are implemented.

## Start here

1. Read [HANDOFF.md](HANDOFF.md) before making architectural changes or starting work from a new chat.
2. Inspect the actual repository and current tests; the handoff describes known state but the repository is the source of truth.
3. Preserve the existing MVP and follow the iteration roadmap below.

## Run locally

Requires Python 3.11+.

```bash
cd youtube-intelligence
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\\Scripts\\Activate.ps1

pip install -e ".[dev]"
pytest
yti score --input data/sample_videos.json --output runs/demo/outliers.csv
yti report --input runs/demo/outliers.csv --output runs/demo/report.md
```

## What the MVP does

1. Reads video metadata and creator baseline observations from JSON.
2. Calculates a transparent outlier ratio using candidate views divided by the creator's median comparable-video views.
3. Flags insufficient baseline samples instead of manufacturing a score.
4. Writes a CSV ranking and Markdown summary.

Short-form and long-form videos must be scored separately. Baseline observations must exclude the candidate itself and should represent the same creator and format. This MVP expects the baseline median and sample size to be supplied in the input; baseline collection is a later stage.

Current score bands in the MVP are discovery labels, not universal industry standards:
- Below 3x: ordinary
- 3x or above: candidate
- 5x or above: strong
- 10x or above: exceptional

A views-to-subscriber ratio is a separate metric from creator-relative outlier scoring. Neither metric, by itself, proves why a video succeeded.

## Product boundaries

- This is an independent software product and development lifecycle.
- It is not integrated into KSK's editorial agents, story-development workflow, research pipeline, or orchestration.
- It may eventually provide audience-opportunity evidence that KSK's editorial process can consider. That is a future optional handoff, not automated editorial authority.
- Do not put private KSK scripts, internal agent instructions, private research, unpublished assets, or personal information in this public repository.

## Data, privacy, and platform constraints

- Use synthetic or public, non-sensitive sample data in this public repository.
- Never commit API keys, cookies, private transcripts, personal data, or bulk comments.
- Do not download or redistribute videos, audio, or thumbnails.
- Respect YouTube terms, API policies, rate limits, and source rights.
- The public YouTube API does not expose arbitrary historical daily view counts. A single current view count cannot establish historical velocity.
- Do not invent views-per-hour, historical views, or unavailable engagement metrics.
- Preserve retrieval timestamps, source adapter, query provenance, transcript language/timestamps, and scoring version.
- Treat scores as discovery signals, not causal explanations of success.

## Project layout

- `src/yti/` — Python package, additive contracts, transcript normalization and CLI.
- `data/` — synthetic fixtures only.
- `tests/` — deterministic unit, contract and CLI tests.
- `docs/` — architecture, data contracts, scoring and reuse research.
- `runs/` — local generated output; generated runs are git-ignored.
- `.github/workflows/python-tests.yml` — test suite on pushes and pull requests.
- [`HANDOFF.md`](HANDOFF.md) — complete product vision, architecture, data-source constraints, development expectations, and next-chat instructions.

## Transcript intelligence design

Read these before implementing transcript work:
- [Transcript collection design](docs/experiments/transcript_collection.md) — captions-only acquisition, provenance, status handling and safety boundaries.
- [Transcript tools reconnaissance](docs/experiments/transcript_tools_reconnaissance.md) — public repositories inspected and explicit reuse decisions.
- [Transcript Intelligence Agent](docs/agents/TRANSCRIPT_INTELLIGENCE_AGENT.md) — analysis dimensions, evidence rules and report structure.
- [Transcript analysis output contract](docs/transcript_analysis_schema.md) — proposed structured report fields and pacing semantics.

The intended analysis covers concepts, multi-label content format, narrative mode, hook/open loops/payoff, structure, explanation techniques, tone/rhetoric, speech rate, information density, narrative pace, memorable moments and reusable techniques. These are separate dimensions, not one quality score. Transcript-only analysis must not claim visual editing, music, delivery energy, retention or causal performance effects.

## Roadmap

1. [x] Deterministic outlier scoring and report generation.
2. [x] Automated tests on GitHub Actions.
3. [x] Iteration 0: architecture, data contracts, scoring methodology, and public GitHub/tool landscape review with build-vs-reuse decisions.
4. [ ] YouTube metadata discovery adapter.
5. [ ] Creator baseline builder and format/age-aware comparisons.
6. [ ] Views-to-subscriber and improved creator-relative outlier analysis.
7. [ ] Adaptive research strategist that refines discovery from broad topic briefs.
8. [ ] Transcript adapter with source, language, timestamp provenance, bounded collection and quality checks.
9. [ ] Thumbnail/frame observation workflow.
10. [ ] Comment-theme and audience-question analysis using permitted, privacy-conscious samples.
11. [ ] Transcript intelligence reports and comparative storytelling analysis with timestamped evidence; then evidence-backed opportunity reports.
12. [ ] Reproducible end-to-end experiments on barcode, camera evolution, and satellites.
13. [ ] Reliability improvements: caching, retries, logging, quota/cost controls, and versioned reports.
14. [ ] Consider a dashboard only after the CLI research engine is reliable.

**Immediate next work:** implement and test the smallest captions-only transcript adapter spike behind a provider-neutral contract. First run it against a bounded sample of already-selected satellite videos; compare available caption tracks, transcript quality and failure states. Do not start automated LLM analysis until the collector and normalized transcript artefact are trustworthy.
