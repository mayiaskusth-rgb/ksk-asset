# Transcript Tools Reconnaissance — 2026-11-13

**Purpose:** Narrow technical reconnaissance for the transcript collection and transcript-intelligence stages. This is a point-in-time review of public GitHub default-branch metadata and selected source files. It is not a runtime test or a license/legal opinion.

## Candidates inspected

### 1. [youtube-transcript-extractor](https://github.com/GregHabiskis/youtube-transcript-extractor)

- Repository describes a local-friendly FastAPI/React app using yt-dlp's Python API.
- Claims captions-only retrieval (no video/audio download), creator captions preferred over auto captions, JSON3 with WebVTT/SRT fallback, deterministic rolling-caption cleanup and timestamp preservation.
- Source tree includes backend, tests and a Python package.
- Repository metadata showed no declared license; pyproject requires Python >=3.14,<3.15, while our package currently targets Python 3.11+.
- **Decision: borrow design only / prototype the ideas.** Do not copy or depend on the code unless a clear license is added and compatibility is addressed. The useful concepts are caption-track selection, deterministic cleanup and timing-preserving normalization.

### 2. [analyze-video](https://github.com/eruto-skills/analyze-video)

- MIT license is present in the repository.
- Its skill reads the full narration, creates macro and micro structure maps, and analyzes hook, information density, hedging, credibility, re-engagement, memorable phrases, throughline, contrast and closing.
- It explicitly keeps analysis descriptive and unscored, uses quote/timestamp evidence, and offers comparison mode.
- It is a Claude Code/Codex-oriented skill, not a Python library or an automated model service.
- **Decision: borrow analytical design, do not adopt as a runtime dependency.** Its axes inform our rubric, but our contract expands concept mapping, multi-label format, explanation design, separate pacing dimensions, evidence confidence and no unsupported retention claims. Preserve license attribution if any code or text is copied; this work only records design observations.

### 3. [youtube-transcriber](https://github.com/nickholdenproper/youtube-transcriber)

- Repository describes a Python CLI/GUI/API pipeline using yt-dlp captions, local faster-whisper fallback, Ollama context analysis, optional frame analysis and audio/voice measurements.
- README describes timestamped transcript, chapters, topics, people, tools and quotes, with reconciliation checks between transcript and secondary observations.
- Repository metadata identifies a custom "Free-to-Use License 1.0" / NOASSERTION; the license text restricts standalone resale. This is not a permissive OSI license.
- Its fallback downloads audio, and its default analysis can call Ollama cloud; both conflict with our first-pass constraints (captions-only, no paid/cloud LLM dependency, no media download).
- **Decision: borrow architecture ideas only; do not adopt or copy code.** Particularly useful ideas: separate transcript, visual and voice evidence streams; reconciliation against transcript timestamps; warnings for incomplete chapter coverage. Local Whisper fallback is a possible later, separately approved capability only if media-download policy and cost constraints are revisited.

## First-pass choice

1. Keep yt-dlp as the existing metadata/search tool and prototype its subtitle-only capability behind a dedicated transcript adapter.
2. Keep transcript acquisition independent from analysis. The collector returns a normalized transcript or a truthful unavailable/blocked status.
3. Do not add Whisper/audio download, Ollama, hosted transcript APIs, MCP server, database, embeddings or a new dashboard in this iteration.
4. Compare only a tiny bounded sample of already selected satellite videos; cache results and stop on 403/429/challenge signals. No cookies, proxies, CAPTCHA bypasses or retries.
5. Use manual/model-assisted analysis for the first pilot; do not add paid LLM API calls.

## Research gaps / next inspections

- Inspect the extractor's actual subtitle selection and rolling-caption cleanup tests before deciding whether to reproduce the algorithm.
- Inspect analyze-video's detailed axis references and QA checklist before finalizing our v0.1 prompt; avoid copying large text blocks.
- Validate our own transcript quality checks on real VTT/JSON3 samples without publishing transcript text.
- Revisit license and maintenance status immediately before any dependency or code reuse.
