# KSK YouTube Intelligence

A public experimental Python pipeline for repeatable YouTube topic research and outlier analysis.

**Current status:** MVP foundation. The first executable stage uses a local fixture dataset and deterministic scoring. Live YouTube discovery, transcript collection, visual analysis and LLM synthesis are future adapters.

## Run locally

Requires Python 3.11+.

```bash
cd youtube-intelligence
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

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

## Data and privacy

- Use synthetic or public, non-sensitive sample data in this public repository.
- Never commit API keys, cookies, private transcripts, personal data or bulk comments.
- Do not download or redistribute videos, audio or thumbnails.
- Respect YouTube terms, API policies, rate limits and source rights.
- Treat scores as discovery signals, not causal explanations of success.

## Project layout

- `src/yti/` — Python package and CLI.
- `data/` — synthetic fixtures only.
- `tests/` — deterministic unit and CLI tests.
- `runs/` — local generated output; generated runs are git-ignored.
- `.github/workflows/python-tests.yml` — test suite on pushes and pull requests.

## Roadmap

1. [x] Deterministic outlier scoring and report generation.
2. [x] Automated tests on GitHub Actions.
3. [ ] YouTube metadata discovery adapter.
4. [ ] Creator baseline builder and format/age-aware comparisons.
5. [ ] Transcript adapter with source and timestamp provenance.
6. [ ] Thumbnail/frame observation workflow.
7. [ ] Comment-theme analysis using permitted, privacy-conscious samples.
8. [ ] LLM analysis with versioned prompts and evidence references.
9. [ ] Public-safe run publishing into the research gallery.
10. [ ] Dashboard and end-to-end topic research workflow.
