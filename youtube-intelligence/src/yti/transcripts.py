"""Provider-neutral transcript records and deterministic subtitle normalization.

This module deliberately performs no network access. Source adapters retrieve caption
payloads; these parsers normalize them without changing cue timestamps.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from typing import Literal

from yti.contracts import SourceReference

TranscriptStatus = Literal["retrieved", "no_captions", "unavailable", "blocked", "failed"]
CaptionType = Literal["creator_provided", "auto_generated", "translated", "unknown"]
SubtitleFormat = Literal["vtt", "json3"]


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    start_seconds: float
    duration_seconds: float
    text: str

    def __post_init__(self) -> None:
        if self.start_seconds < 0:
            raise ValueError("start_seconds must be non-negative")
        if self.duration_seconds < 0:
            raise ValueError("duration_seconds must be non-negative")
        if not self.text.strip():
            raise ValueError("segment text must be non-empty")

    @property
    def end_seconds(self) -> float:
        return self.start_seconds + self.duration_seconds


@dataclass(frozen=True, slots=True)
class TranscriptObservation:
    video_id: str
    status: TranscriptStatus
    source: SourceReference
    language: str | None = None
    caption_type: CaptionType = "unknown"
    subtitle_format: SubtitleFormat | None = None
    segments: tuple[TranscriptSegment, ...] = ()
    content_sha256: str | None = None
    detail_code: str | None = None

    def __post_init__(self) -> None:
        if not self.video_id.strip():
            raise ValueError("video_id must be non-empty")
        if self.status not in ("retrieved", "no_captions", "unavailable", "blocked", "failed"):
            raise ValueError("unsupported transcript status")
        if self.caption_type not in ("creator_provided", "auto_generated", "translated", "unknown"):
            raise ValueError("unsupported caption_type")
        if self.subtitle_format not in (None, "vtt", "json3"):
            raise ValueError("unsupported subtitle_format")
        if self.status == "retrieved" and not self.segments:
            raise ValueError("retrieved transcript must contain segments")
        if self.status != "retrieved" and self.segments:
            raise ValueError("non-retrieved transcript cannot contain segments")
        if self.content_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", self.content_sha256):
            raise ValueError("content_sha256 must be a lowercase SHA-256 hex digest")


_TIMESTAMP = re.compile(r"^(?:(\d{2,}):)?([0-5]?\d):([0-5]\d)[.,](\d{1,3})$")


def _seconds(value: str) -> float:
    match = _TIMESTAMP.match(value.strip())
    if not match:
        raise ValueError(f"invalid subtitle timestamp: {value!r}")
    hours, minutes, seconds, millis = match.groups()
    fraction = int(millis.ljust(3, "0")) / 1000
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds) + fraction


def _clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _build_segments(items: list[TranscriptSegment]) -> tuple[TranscriptSegment, ...]:
    ordered = sorted(items, key=lambda item: item.start_seconds)
    return tuple(ordered)


def parse_vtt(payload: str) -> tuple[TranscriptSegment, ...]:
    """Parse WebVTT cues, ignoring headers, cue identifiers and cue settings."""
    lines = payload.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    segments: list[TranscriptSegment] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "-->" not in line:
            i += 1
            continue
        left, right = (part.strip().split()[0] for part in line.split("-->", 1))
        start, end = _seconds(left), _seconds(right)
        if end < start:
            raise ValueError("subtitle cue end precedes start")
        i += 1
        text_lines: list[str] = []
        while i < len(lines) and lines[i].strip():
            text_lines.append(lines[i].strip())
            i += 1
        text = _clean_text(" ".join(text_lines))
        if text:
            segments.append(TranscriptSegment(start, end - start, text))
    return _build_segments(segments)


def parse_json3(payload: str) -> tuple[TranscriptSegment, ...]:
    """Parse YouTube JSON3 events while preserving event start and duration."""
    document = json.loads(payload)
    events = document.get("events", [])
    if not isinstance(events, list):
        raise ValueError("JSON3 events must be a list")
    segments: list[TranscriptSegment] = []
    for event in events:
        if not isinstance(event, dict) or "tStartMs" not in event:
            continue
        parts = event.get("segs", [])
        if not isinstance(parts, list):
            continue
        text = _clean_text("".join(
            part.get("utf8", "") for part in parts if isinstance(part, dict)
        ))
        if not text:
            continue
        start = float(event["tStartMs"]) / 1000
        duration = float(event.get("dDurationMs", 0)) / 1000
        segments.append(TranscriptSegment(start, duration, text))
    return _build_segments(segments)


def transcript_checksum(segments: tuple[TranscriptSegment, ...]) -> str:
    """Return a stable checksum over normalized timing and text, not raw source bytes."""
    canonical = "\n".join(
        f"{segment.start_seconds:.3f}\t{segment.duration_seconds:.3f}\t{segment.text}"
        for segment in segments
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_transcript_observation(
    *,
    video_id: str,
    source: SourceReference,
    segments: tuple[TranscriptSegment, ...],
    language: str | None,
    caption_type: CaptionType,
    subtitle_format: SubtitleFormat,
) -> TranscriptObservation:
    if not segments:
        return TranscriptObservation(
            video_id=video_id, status="no_captions", source=source,
            language=language, caption_type=caption_type, subtitle_format=subtitle_format,
        )
    return TranscriptObservation(
        video_id=video_id, status="retrieved", source=source,
        language=language, caption_type=caption_type, subtitle_format=subtitle_format,
        segments=segments, content_sha256=transcript_checksum(segments),
    )
