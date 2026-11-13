# YouTube Audience Intelligence Engine

An independent Python research-engineering product for YouTube topic discovery, creator-relative outlier analysis, and audience/storytelling intelligence.

This module lives in the public `ksk-asset` repository but is **not a KSK story-development agent**. See the repository root README for the boundary and [HANDOFF.md](HANDOFF.md) for the full product specification and engineering instructions.

**Current status:** MVP foundation. The first executable stage uses a local fixture dataset and deterministic scoring. Live YouTube discovery, channel-baseline collection, transcript/comment analysis, adaptive research, and full opportunity reporting are future iterations.

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

- `src/yti/` — Python package and CLI.
- `data/` — synthetic fixtures only.
- `tests/` — deterministic unit and CLI tests.
- `runs/` — local generated output; generated runs are git-ignored.
- `.github/workflows/python-tests.yml` — test suite on pushes and pull requests.
- [`HANDOFF.md`](HANDOFF.md) — complete product vision, architecture, data-source constraints, development expectations, and next-chat instructions.

## Roadmap

1. [x] Deterministic outlier scoring and report generation.
2. [x] Automated tests on GitHub Actions.
3. [ ] Iteration 0: architecture, data contracts, source-adapter contracts, scoring methodology, and tool evaluation.
4. [ ] YouTube metadata discovery adapter.
5. [ ] Creator baseline builder and format/age-aware comparisons.
6. [ ] Views-to-subscriber and improved creator-relative outlier analysis.
7. [ ] Adaptive research strategist that refines discovery from broad topic briefs.
8. [ ] Transcript adapter with source, language, and timestamp provenance.
9. [ ] Thumbnail/frame observation workflow.
10. [ ] Comment-theme and audience-question analysis using permitted, privacy-conscious samples.
11. [ ] Comparative storytelling analysis and evidence-backed opportunity reports.
12. [ ] Reproducible end-to-end experiments on barcode, camera evolution, and satellites.
13. [ ] Reliability improvements: caching, retries, logging, quota/cost controls, and versioned reports.
14. [ ] Consider a dashboard only after the CLI research engine is reliable.
