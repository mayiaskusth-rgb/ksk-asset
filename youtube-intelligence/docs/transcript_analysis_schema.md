# Transcript Analysis Output Schema — v0.1

**Status:** Conceptual contract for pilot reports; not yet a validated JSON Schema or implemented Python model.

The first implementation should prefer a readable Markdown report plus a small structured JSON record. Keep the schema provider-neutral and additive.

## Required top-level sections

| Field | Type | Required | Notes |
|---|---|---:|---|
| schema_version | string | yes | `0.1` |
| analysis_id | string | yes | Stable run-local identifier |
| video_id | string | yes | YouTube video ID |
| source | object | yes | Video and transcript provenance |
| transcript_quality | object | yes | Completeness, status, language and timestamp quality |
| overview | object | yes | Summary, central question and thesis |
| concepts | array | yes | Concepts with importance and evidence |
| format_labels | array | yes | Multi-label classification with reasons |
| narrative_mode | object | yes | Structural pattern and evidence |
| hook | object | yes | Opening move, curiosity mechanism, promise/payoff |
| structure | array | yes | Timestamped sections and roles |
| techniques | array | yes | Explanation/rhetorical techniques with evidence |
| tone | array | yes | Textual tone/rhetoric observations |
| pacing | object | yes | Speech rate, information density and narrative pace kept distinct |
| strong_moments | array | yes | Up to five moments |
| reusable_learnings | array | yes | Principle, adaptation and caveat |
| opportunity_hypotheses | array | yes | Explicitly tentative, evidence-linked |
| limitations | array | yes | Missing data and uncertainty |
| confidence | object | yes | Basis and per-finding confidence; no opaque quality score |

## Evidence object

Each evidence item should contain:
- `start_seconds`: numeric timestamp.
- `end_seconds`: numeric timestamp or null.
- `transcript_excerpt`: optional short excerpt; prefer a paraphrase field in public reports.
- `paraphrase`: concise description of the relevant source content.
- `evidence_type`: transcript / chapter / visual_observation / audio_measurement / metadata.
- `source_ref`: identifier of the segment or observation.

Evidence must point to a real segment/observation. Never fabricate timestamps to fill a schema.

## Pacing rules

- `speech_rate_wpm` may be null.
- Include calculation window, word-count method, timestamp source and timing-quality caveat.
- `information_density` is qualitative in v0.1 (low / medium / high) with explanation and evidence.
- `narrative_pace` describes transitions and beat frequency qualitatively.
- Do not combine these into one score.

## Example format label

```json
{
  "label": "mystery_reveal",
  "reason": "The opening raises a concrete question and delays the explanation.",
  "evidence": [
    {
      "start_seconds": 12.0,
      "end_seconds": 28.0,
      "paraphrase": "The narrator introduces an unexpected observation and asks why it happens.",
      "evidence_type": "transcript",
      "source_ref": "segment-0004"
    }
  ],
  "confidence": "medium"
}
```

## Deliberate exclusions in v0.1

- No single video-quality score.
- No retention, CTR, watch-time or causal-performance claims.
- No visual or audio claims unless those observations are separately supplied.
- No automatic fact-check verdict; factual verification is a separate task.
- No script generation or imitation of a creator's distinctive expression.
- No publication of full transcript text.
