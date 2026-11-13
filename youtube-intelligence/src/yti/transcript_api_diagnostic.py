"""One-video, separate-provider diagnostic; never falls back automatically."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from yti.transcript_api_adapter import YouTubeTranscriptApiAdapter
from yti.transcript_probe import SAMPLES, _safe_record


def run_diagnostic(sample_name: str, output: Path) -> dict:
    if sample_name not in SAMPLES:
        raise ValueError("unsupported sample selection")
    sample = SAMPLES[sample_name]
    observation = YouTubeTranscriptApiAdapter().fetch(
        video_id=sample["video_id"],
        video_url=sample["url"],
        language="en",
        retrieved_at=datetime.now(timezone.utc).isoformat(),
    )
    report = {
        "schema_version": "1.0",
        "experiment": "youtube-transcript-api-isolated-diagnostic",
        "selection": sample_name,
        "requested_video_count": 1,
        "processed_video_count": 1,
        "automatic_fallback": False,
        "raw_transcripts_persisted": False,
        "records": [_safe_record(sample, observation)],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", choices=tuple(SAMPLES), default="norsat-webinar")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = run_diagnostic(args.sample, args.output)
    print(f"Diagnostic provider status: {report['records'][0]['status']}")


if __name__ == "__main__":
    main()
