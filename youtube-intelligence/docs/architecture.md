# Architecture and boundaries (Iteration 0)

**Status:** Proposed v1 foundation, 2026-11-13. This document defines seams; it does not claim that future modules already exist.

## Product boundary

The YouTube Audience Intelligence Engine is an independent Python product in this public repository. The KSK editorial repository remains separate. Any future audience-opportunity report is an optional evidence input to a human editorial process; it is not an automated KSK agent or an editorial decision-maker.

## Logical pipeline

```text
Research brief
   |
Research strategist (later; broad topic/audience only)
   |
Discovery adapters ----> normalized observations + provenance
   |                                  |
Channel uploads adapter               |
   |                                  v
Creator baseline builder ------> outlier scoring (existing MVP)
                                      |
Transcript / thumbnail / comment adapters (later)
   |                                  |
Content + audience analysis ----------+
   |
Comparative synthesis
   |
Audience Opportunity Report
```

The first implementation milestone remains the existing deterministic score/report CLI. The diagram is a target decomposition, not a claim of current completeness.

## Module responsibilities

| Boundary | Responsibility | Iteration |
|---|---|---|
| `yti.contracts` | Provider-neutral observations, source provenance, creator baseline | 0 (introduced) |
| `yti.sources` | Replaceable discovery/channel/transcript/comment adapters | 1+ |
| `yti.discovery` | Topic query planning, candidate retrieval, deduplication | 1, 4 |
| `yti.channel` | Upload retrieval and comparable-upload selection | 2 |
| `yti.scoring` | Creator-relative outlier calculation; preserve current module | MVP, 3 |
| `yti.content` | Transcript/title/thumbnail evidence extraction | 5 |
| `yti.audience` | Privacy-conscious comment themes and questions | 6 |
| `yti.synthesis` | Cross-video patterns and opportunity hypotheses | 7 |
| `yti.reporting` | Evidence-linked report generation; preserve current report | MVP, 7 |
| `yti.runs` | Reproducible run config, manifests, cache and outputs | 1+ |

Do not create empty packages for every future module. Add each boundary when its first vertical slice is ready.

## Source adapter contract

Adapters own provider-specific authentication, request parameters, pagination, retries, throttling and response parsing. They return provider-neutral records plus source metadata. They must not call LLMs or decide editorial relevance.

Every observation should retain:
- provider and retrieval method;
- retrieval timestamp (UTC ISO-8601);
- original query or channel/video identifier;
- canonical source URL and provider IDs;
- fields actually observed, including explicit missing values;
- API/library version or adapter version where available.

Capability declarations must distinguish supported, unsupported and unavailable fields. Never silently synthesize historical metrics.

## Data flow and persistence

- Raw provider responses: optional, bounded, and stored only where terms and privacy permit.
- Normalized metadata observations: versioned, append-only snapshots with retrieval time.
- Derived baselines/scores: recomputable outputs tied to input observation IDs and scoring version.
- Transcripts/comments: separate retention policy, source/language/timestamp provenance, least data necessary.
- Run manifest: brief, queries, source adapters/versions, time window, geography/language, retrieved IDs, failures, scoring version, generated artifacts.

For the initial CLI, local JSON fixtures and CSV/Markdown outputs remain supported. SQLite is a candidate local persistence layer, not a commitment until a tested need appears.

## Provider strategy

1. Official YouTube Data API is the default candidate for search and public metadata where its fields and quota fit.
2. Direct Python libraries may be wrapped behind our contracts for transcript or collection tasks after terms, reliability and maintenance review.
3. MCP is an optional integration surface for an agent client, not the internal architecture. Prefer direct Python calls for deterministic pipeline execution; use MCP only when a specific tool adds value.
4. Keep providers replaceable. No provider-specific response objects should leak into scoring or reports.

## Non-functional constraints

- Python 3.11+, standard library for contracts and scoring core.
- No API key, cookie, private transcript, personal data or bulk comment fixture in this public repository.
- No video/audio downloads or thumbnail redistribution.
- Rate limits, quotas, retries and caching belong in source adapters.
- Tests use deterministic fixtures; live smoke tests are opt-in and never required for ordinary unit CI.
- Reports separate observed facts, derived metrics and model-generated hypotheses.
- Every score must expose its baseline, sample size, comparability cohort and limitations.
