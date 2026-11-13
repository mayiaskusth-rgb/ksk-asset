# KSK Persistence Data Model

## Entity relationships

- A **project** groups a line of research (for example, Satellites, Barcodes or Camera History).
- A **research run** records one discovery/collection attempt for a project.
- A **video** is canonical across the system and keyed by YouTube video ID.
- **Project-video membership** records how a video entered a project and its human review decision.
- **Research-run-video provenance** records which run/query discovered the video and its returned rank.
- A **transcript** belongs to a canonical video and is revisioned.
- **Video notes** preserve human observations and questions separately from generated findings.
- An **analysis run** records the agent, version, rubric, input transcript and execution status.
- **Findings** store structured output and timestamped evidence linked to an analysis run.

## Review semantics

review_decision values:

- unreviewed: not yet assessed.
- keep: selected for deeper research.
- drop: excluded from future processing, but retained in the database.
- review_later: deferred for a human decision.

A drop is not a delete. Reconsidering a video changes the decision and preserves the prior state in future audit/event support. Reasons use controlled codes where possible; a free-text note provides context.

Suggested reason codes (not yet enforced as a database enum): not_relevant, repetitive, low_substance, poor_quality, outside_scope, other.

## Manual additions

A manually supplied YouTube URL is normalized to a video ID and canonical URL. The video is upserted into videos, then linked to the selected project with added_via = 'manual'. Metadata enrichment is a separate step; a missing metadata field must not prevent the user from saving a valid video reference.

## Transcript contract

The first supported user input is a manually pasted transcript. Each save creates a new transcript revision with:

- source type manual
- language code if known
- status available
- raw transcript text
- optional normalized timestamped segments
- SHA-256 checksum
- creation/retrieval timestamp

A later provider adapter can use the same record with a different source type/provider. Do not assume every transcript has timestamps. Preserve the original text even if segment normalization is unavailable.

## First persistence test

The initial end-to-end test intentionally ignores project review UI, bulk imports, analysis and automated transcript acquisition. It proves only that:

1. a canonical video can be created/retrieved;
2. a manual transcript can be saved as revision 1;
3. a second save creates revision 2;
4. the latest revision can be retrieved by video ID;
5. an unauthenticated request cannot read or write private data.

This test should use a development D1 database and a non-sensitive sample. The Norsat webinar may be used as the video reference, but do not publish its transcript text in the public repository or GitHub Actions artifacts.
