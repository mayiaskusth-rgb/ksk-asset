# Satellite research experiment — stage 1: idea generation

**Run type:** Prompt dry run using the ChatGPT model; not yet an API-backed execution from the Python package.  
**Input:** `Satellites`  
**Requested output:** 10 independently searchable, non-overlapping research ideas.  
**Saved output:** [`data/experiments/satellite_ideas.json`](../../data/experiments/satellite_ideas.json)

## What this experiment tests

The first stage receives only a broad subject. It must not receive a predefined audience, geography, language, story arc, preferred angle, or examples of the desired output. The purpose is to test whether the model can independently decompose a broad subject into distinct research directions.

The current implementation in `src/yti/ideas.py` defines:
- A provider-neutral prompt builder.
- A strict JSON response parser.
- A typed `ResearchIdea` record.
- Structural validation for exact idea count, required fields, distinct IDs/titles/questions/lenses, and unique search queries.

It does **not** yet call an LLM provider. That is intentionally separated from prompt design and response validation.

## Initial output

Ten lenses were generated:

1. Orbital physics — why satellites stay in orbit.
2. Positioning and navigation — how GPS satellites locate us.
3. Radio communications — how satellites communicate with Earth.
4. Failure and reliability — what happens when satellites fail.
5. Orbital environment — space debris and collision risk.
6. Earth observation — how satellites observe changes on Earth.
7. Launch and deployment — how satellites reach their orbits.
8. Economics and ownership — who owns and pays for satellites.
9. Surveillance and limits — what imaging satellites can actually see.
10. Systemic dependency — what would happen if satellites disappeared.

## Initial quality review

**Promising**
- The output spans physics, infrastructure, operations, environment, business and societal dependence.
- Most ideas are phrased as questions that can be investigated through YouTube search.
- No scripts or story arcs were generated.
- Each idea has two query formulations to test retrieval sensitivity.

**Potential overlap / issues to review**
- Ideas 2 and 3 are adjacent because both involve signals. Keep them separate only if search results reveal distinct positioning versus communication content.
- Ideas 6 and 9 are adjacent because both involve imaging. Earth observation and surveillance have different purposes, but videos may overlap.
- Ideas 4 and 5 may overlap in videos about failed satellites becoming debris.
- Idea 10 is a broad synthesis question. It may produce speculative explainers rather than a distinct body of evidence.
- Some generated queries may be too broad or return results about unrelated space topics. Search relevance must be measured, not assumed.

## What to tune after search

Do not tune the prompt just because two ideas sound similar. First run the queries and inspect:
- Relevant-result rate in the first 20–30 results.
- Number of unique videos after cross-query deduplication.
- Whether two ideas retrieve substantially the same videos/channels.
- Whether a query is dominated by Shorts, news, institutional explainers, or unrelated results.
- Whether the results include enough channels with comparable uploads to calculate creator-relative baselines.

If two ideas return nearly the same video set, ask the ideation stage to differentiate their scope or merge them. If a query returns weak results, refine the query rather than rewriting the idea immediately.

## Next execution stages

1. Add a configured LLM provider adapter and persist the prompt/model/version with each run.
2. Run these 20 queries through the YouTube search adapter (two per idea), collect 20–30 results per query, and deduplicate by video ID.
3. Hydrate metadata and preserve observed-at timestamps and query provenance.
4. Retrieve creator uploads and calculate comparable baselines before ranking outliers.
5. Select a transcript shortlist only after scoring and baseline-confidence checks.

## Current status

- Prompt design: drafted and exercised in a model dry run.
- Structured response contract and parser: implemented.
- Automated unit tests: added; CI result pending.
- LLM API execution: not implemented.
- YouTube search and metadata collection: not implemented.
- Outlier selection and transcript analysis: not implemented.

No claim is made that these ten ideas are popular or that their videos are successful. The next stage must validate them against YouTube evidence.
