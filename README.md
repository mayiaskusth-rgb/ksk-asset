# KSK Asset Gallery & YouTube Intelligence

This public repository contains two deliberately separate components:

1. **KSK Asset Gallery** — a static, public-safe gallery for selected visual-asset references used by Kabhi Socha Kya.
2. **YouTube Audience Intelligence Engine** — an independent Python research-engineering product for YouTube topic discovery, creator-relative outlier analysis, and audience/storytelling insights.

These components share a public repository for convenience, not a runtime dependency or a combined product architecture.

## Relationship to the private KSK repository

The private [Kabhi Socha Kya repository](https://github.com/mayiaskusth-rgb/kabhi-socha-kya) owns KSK's editorial and production system: topic discovery, creative thinking lenses, research and challenge, story architecture, scripts, reviews, visual planning, approval gates, and private episode artefacts.

The YouTube Intelligence Engine in this repository is an **independent software product**. It is not a KSK agent and is not part of KSK's story-development orchestration. Its future audience-opportunity reports may be considered by KSK's editorial process, but no automated integration or editorial authority is implied.

Keep private scripts, internal agent instructions, private research notes, unpublished assets, credentials, and personal data out of this public repository.

## Component 1: KSK Asset Gallery

- `index.html` renders the gallery.
- `assets.json` is a curated, publishable display index.
- Preview media remains hosted by original providers; this repository does not redistribute downloaded media.
- The authoritative asset registry and detailed internal workflow remain in the private KSK repository.

### Local preview

```bash
python -m http.server 8000
```

Open http://localhost:8000/.

### GitHub Pages

The existing [Visual Asset Library](index.html) remains the home page. The additive [YouTube Research Run Explorer](research.html) is a separate page; neither page replaces the other.

This repository includes a GitHub Actions deployment workflow at `.github/workflows/pages.yml`. In Settings → Pages, choose **GitHub Actions** as the deployment source if prompted.

Expected site URL: https://mayiaskusth-rgb.github.io/ksk-asset/

### Gallery publishing policy

Only publish records intentionally selected for public display. Check that metadata contains no private notes, internal paths, credentials, or confidential workflow details. A gallery card is not rights clearance: assess each asset for intended use and distribution territory.

Original asset and rights pages are linked on every card. Remote previews may fail if a source blocks hotlinking; source links remain available.

## Component 2: YouTube Audience Intelligence Engine

The Python project lives in [`youtube-intelligence/`](youtube-intelligence/).

Its purpose is to discover audience demand, identify videos that outperform their creators' normal performance, analyze storytelling and audience signals, and produce evidence-backed opportunity reports.

**Current status:** The existing MVP and Iteration 0 foundation are preserved. PR #1 and the research-explorer/layout PRs are merged into `main`. Draft PR [#11](https://github.com/mayiaskusth-rgb/ksk-asset/pull/11) on `research/transcript-intelligence-foundation` adds transcript-tool reconnaissance, collection boundaries, an evidence-backed analysis rubric, WebVTT/JSON3 normalization, an optional captions-only yt-dlp adapter, and a one-video local CLI command with mocked tests. Live YouTube retrieval and automated analysis remain unvalidated/not implemented.

Start with:
- [YouTube Intelligence README](youtube-intelligence/README.md) — current capabilities, setup, and roadmap.
- [Engineering handoff](youtube-intelligence/HANDOFF.md) — authoritative product vision, architecture, constraints, iteration plan, and instructions for a new engineering chat.
- [Architecture and data contracts](youtube-intelligence/docs/architecture.md) and [reuse research](youtube-intelligence/docs/repo_landscape.md) — Iteration 0 engineering decisions.

The engine must be developed and tested as a Python product. Manual web searches by an assistant are not a substitute for its discovery pipeline. Preserve the existing MVP and build iteratively.

