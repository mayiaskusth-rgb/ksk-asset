# Data contracts (Iteration 0)

**Contract version:** 1  
**Implementation:** `src/yti/contracts.py` (additive; not yet wired into the MVP CLI).

## Core records

### VideoObservation

One observation of a public video at a particular retrieval time.

| Field | Type | Meaning |
|---|---|---|
| video_id | string | Stable YouTube video identifier |
| title | string | Observed title |
| channel_id / channel_title | string | Creator identity |
| published_at | ISO-8601 string or null | Original publish timestamp if exposed |
| duration_seconds | integer or null | Duration; used to support format/length comparisons |
| format | short_form / long_form / unknown | Explicitly derived format classification |
| views | non-negative integer or null | Observed view count, not historical view count |
| observed_at | ISO-8601 string | When this metric snapshot was retrieved |
| source | SourceReference | Provider and retrieval provenance |

Missing metrics remain null. A missing value is not zero.

### SourceReference

Records provider, retrieval timestamp, method, optional query, and canonical URL. Later adapters should add a stable adapter/version identifier and request parameters to run manifests.

### CreatorBaseline

A candidate-specific comparison set: creator/channel, format, median views, unique peer video IDs, computation timestamp, and optional time window. The candidate itself must never appear in its own baseline. Shorts and long-form must not be mixed. A low sample is retained as low-confidence input; the scorer decides whether it is scoreable.

## Compatibility

The existing MVP JSON fixture shape is intentionally unchanged:
- `views`
- `creator_baseline_median_views`
- `baseline_sample_size`
- `format`

The new records define the normalized internal boundary for future adapters. An explicit conversion layer will bridge normalized observations to the existing scoring input; do not break existing CLI users.

## Validation rules

- IDs and provenance identifiers are non-empty.
- Counts and durations cannot be negative.
- Missing counts are null, never fabricated.
- Format is one of the declared values.
- Baseline peer IDs are unique and exclude the candidate.
- Baseline sample size is derived from the peer ID list, not separately supplied.
- Baselines must preserve creator, format and time-window eligibility decisions.

## Future extension points

Add schema versioning and serialization only when the first persisted live run requires it. Do not add Pydantic or a database dependency merely for these initial standard-library records.
