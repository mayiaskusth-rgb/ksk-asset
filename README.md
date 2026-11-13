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

**Current status (2026-11-13):** The Python MVP, bounded discovery workflow, Research Run Explorer and transcript-intelligence foundation are merged into `main`. PR #12 added a separate `youtube-transcript-api` diagnostic; it was merged and tested independently. Both the yt-dlp captions-only probe and the separate `youtube-transcript-api` diagnostic were safely blocked by YouTube access challenges from GitHub-hosted runners. Neither retrieved transcript text. Do not interpret successful workflow completion as successful transcript acquisition. The next experiment is a manual browser copy/paste path, backed by private persistence; hosted transcript APIs can be evaluated separately later.

Start with:
- [YouTube Intelligence README](youtube-intelligence/README.md) — current capabilities, setup, and roadmap.
- [Engineering handoff](youtube-intelligence/HANDOFF.md) — authoritative product vision, architecture, constraints, iteration plan, and instructions for a new engineering chat.
- [Architecture and data contracts](youtube-intelligence/docs/architecture.md) and [reuse research](youtube-intelligence/docs/repo_landscape.md) — Iteration 0 engineering decisions.

The engine must be developed and tested as a Python product. Manual web searches by an assistant are not a substitute for its discovery pipeline. Preserve the existing MVP and build iteratively.



## Private persistence API (Cloudflare)

A first private persistence API implementation is available for review in draft PR [#14](https://github.com/mayiaskusth-rgb/ksk-asset/pull/14), with local D1 contract tests proposed in draft PR [#16](https://github.com/mayiaskusth-rgb/ksk-asset/pull/16). Neither PR is merged or deployed.

The Worker currently provides health, canonical video save/retrieval, and manually pasted transcript revision endpoints. Private routes currently require Cloudflare Access JWT validation. The owner has created the development D1 database, but has not created an Access application or deployed/migrated the Worker. The Access onboarding prompted for payment details; do not ask the owner to provide card details. A secure owner-only authentication approach compatible with the account constraints is still a prerequisite. See [Cloudflare setup and API notes](cloudflare/README.md) and the dated checkpoint in [the engineering handoff](youtube-intelligence/HANDOFF.md).
