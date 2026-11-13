"""Run a deliberately bounded transcript experiment on known satellite results.

Only sanitized metadata is written to disk. Transcript text remains in memory and
is never uploaded as a GitHub Actions artifact or committed to the repository.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from yti.transcript_adapter import YtDlpTranscriptAdapter

SAMPLES: dict[str, dict[str, Any]] = {
    "norsat-webinar": {
        "video_id": "efjBiVN_N3M",
        "url": "https://www.youtube.com/watch?v=efjBiVN_N3M",
        "title": "The Fundamentals of Satellite Communications Webinar",
        "channel": "Norsat International",
        "duration_seconds": 3554,
    },
    "astrum-extra": {
        "video_id": "jo8Z4UzIBQk",
        "url": "https://www.youtube.com/watch?v=jo8Z4UzIBQk",
        "title": "The Power of These Satellites Is Deeply Troubling",
        "channel": "Astrum Extra",
        "duration_seconds": 2897,
    },
}


def _safe_record(sample: dict[str, Any], observation: Any) -> dict[str, Any]:
    segment_count = len(observation.segments)
    transcript_end = max(
        (segment.end_seconds for segment in observation.segments), default=0.0
    )
    return {
        **sample,
        "status": observation.status,
        "language": observation.language,
        "caption_type": observation.caption_type,
        "subtitle_format": observation.subtitle_format,
        "segment_count": segment_count,
        "transcript_end_seconds": round(transcript_end, 3),
        "detail_code": observation.detail_code,
        "source_provider": observation.source.provider,
        "source_method": observation.source.method,
        "retrieved_at": observation.source.retrieved_at,
        # Deliberately omit transcript text, excerpts, checksums and raw payloads.
    }


def run_probe(selection: str, output: Path) -> dict[str, Any]:
    if selection not in ("norsat-webinar", "astrum-extra", "both"):
        raise ValueError("unsupported sample selection")
    names = list(SAMPLES) if selection == "both" else [selection]
    adapter = YtDlpTranscriptAdapter()
    records: list[dict[str, Any]] = []
    stop_reason = None

    for name in names:
        sample = SAMPLES[name]
        retrieved_at = datetime.now(timezone.utc).isoformat()
        observation = adapter.fetch(
            video_id=sample["video_id"],
            video_url=sample["url"],
            language="en",
            retrieved_at=retrieved_at,
        )
        records.append(_safe_record(sample, observation))
        if observation.status == "blocked":
            stop_reason = "blocked_response_stop_no_retry"
            break

    report = {
        "schema_version": "1.0",
        "experiment": "satellite-transcript-probe",
        "selection": selection,
        "requested_video_count": len(names),
        "processed_video_count": len(records),
        "stop_reason": stop_reason,
        "raw_transcripts_persisted": False,
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        choices=("norsat-webinar", "astrum-extra", "both"),
        default="norsat-webinar",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = run_probe(args.sample, args.output)
    print(
        f"Processed {report['processed_video_count']}/{report['requested_video_count']} "
        f"selected videos; statuses: "
        + ", ".join(record["status"] for record in report["records"])
    )
    if report["stop_reason"]:
        print(f"Stopped: {report['stop_reason']}")


if __name__ == "__main__":
    main()
