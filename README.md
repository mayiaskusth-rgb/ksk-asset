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



## Current platform status — 2026-11-14

This section supersedes the earlier transcript-persistence and authentication status notes below this README's original gallery/engine overview.

### Live transcript workflow

- The Research Run Explorer is published at [GitHub Pages](https://mayiaskusth-rgb.github.io/ksk-asset/research.html).
- Its Transcript tab uses the selected shortlist video's existing YouTube ID and title/channel metadata. The Worker API URL is built into the page; there is no API URL setup field.
- The private API runs as the Cloudflare Worker `ksk-research-api` at `https://ksk-research-api.mayiaskusth.workers.dev`.
- Owner-password login exchanges the password for a 20-minute HMAC-SHA256 signed bearer session. The session token is held in tab-scoped `sessionStorage`; the password is not stored by the page. Worker secrets are `OWNER_PASSWORD` and `SESSION_SECRET`; never commit or share them.
- Login attempts use Cloudflare Workers Rate Limiting: 5 attempts per 60 seconds per client IP per Cloudflare location. This is approximate/eventually consistent and location-local, not a strict global limit.
- D1 database `ksk-research-dev` has its remote migrations applied. The manually gated migration workflow is separate from Worker deployment.
- The user has completed a live browser round trip: save a transcript, refresh/reopen, and retrieve the saved transcript successfully.

### Current transcript save semantics

PR [#21](https://github.com/mayiaskusth-rgb/ksk-asset/pull/21) simplified the editor and API:

- Opening the Transcript tab retrieves the latest saved transcript into the editor.
- A first save creates the transcript record; saving identical text is idempotent.
- Editing and saving updates the current/latest transcript record in place. The current editor does not create a new revision history.
- Older historical D1 rows, if any, are not deleted by this change. The API's current retrieval path returns the latest transcript.
- The UI reports saving, unchanged, saved, updated, and failure states.

### Recent merged implementation

| PR | Change | Status |
|---|---|---|
| [#17](https://github.com/mayiaskusth-rgb/ksk-asset/pull/17) | Initial private transcript persistence and editor | Merged |
| [#18](https://github.com/mayiaskusth-rgb/ksk-asset/pull/18) | Owner-password authentication and signed sessions | Merged |
| [#19](https://github.com/mayiaskusth-rgb/ksk-asset/pull/19) | Login rate limiting | Merged |
| [#20](https://github.com/mayiaskusth-rgb/ksk-asset/pull/20) | Manually gated remote D1 migration workflow | Merged; workflow run and remote schema verified |
| [#21](https://github.com/mayiaskusth-rgb/ksk-asset/pull/21) | Simpler transcript editor and update-in-place save flow | Merged |

PR #21 merge commit: `ac94ad0cdf0ebab3a753643e03418084fdfa44e2`.

### Security and deployment notes

- `/health` is a minimal public liveness endpoint; private API routes require a valid signed session.
- CORS is restricted to the GitHub Pages origin. CORS is not authentication.
- The `workers.dev` endpoint is currently enabled and reachable. Do not describe it as disabled.
- Do not expose unauthenticated private routes, put credentials in the public repository, or repeat automated YouTube transcript extraction attempts. The supported input path for now is manual transcript copy/paste.
- Do not run remote migrations or change deployment/security settings without explicit user approval.

### Documentation ownership

- This root README describes the public gallery, the independent YouTube Intelligence product, and their boundary with the private KSK repository.
- `youtube-intelligence/README.md` describes the Python product.
- `youtube-intelligence/HANDOFF.md` is the detailed engineering handoff and should be checked against live GitHub state before further work.
- `cloudflare/README.md` describes the Worker, D1, authentication, deployment, and API contract.
- The private `kabhi-socha-kya` repository remains the source of truth for KSK editorial workflow and private episode artefacts. There is no automated runtime integration between the two repositories.
