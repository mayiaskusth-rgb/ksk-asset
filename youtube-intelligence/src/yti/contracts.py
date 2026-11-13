"""Version-1 internal data contracts for source observations and baselines.

These contracts are additive: the existing JSON/CSV MVP remains supported.
Adapters normalize provider responses into these models at their boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Literal

VideoFormat = Literal["short_form", "long_form", "unknown"]


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _require_timestamp(value: str, field: str) -> None:
    _require_text(value, field)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")


@dataclass(frozen=True, slots=True)
class SourceReference:
    provider: str
    retrieved_at: str
    method: str
    query: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.provider, "provider")
        _require_timestamp(self.retrieved_at, "retrieved_at")
        _require_text(self.method, "method")


@dataclass(frozen=True, slots=True)
class VideoObservation:
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    published_at: str | None
    duration_seconds: int | None
    format: VideoFormat
    views: int | None
    observed_at: str
    source: SourceReference

    def __post_init__(self) -> None:
        for field in ("video_id", "title", "channel_id", "channel_title"):
            _require_text(getattr(self, field), field)
        _require_timestamp(self.observed_at, "observed_at")
        if self.published_at is not None:
            _require_timestamp(self.published_at, "published_at")
        if not isinstance(self.source, SourceReference):
            raise ValueError("source must be a SourceReference")
        if self.format not in ("short_form", "long_form", "unknown"):
            raise ValueError("format must be short_form, long_form, or unknown")
        if self.duration_seconds is not None and (
            isinstance(self.duration_seconds, bool)
            or not isinstance(self.duration_seconds, int)
            or self.duration_seconds < 0
        ):
            raise ValueError("duration_seconds must be a non-negative integer or None")
        if self.views is not None and (
            isinstance(self.views, bool)
            or not isinstance(self.views, int)
            or self.views < 0
        ):
            raise ValueError("views must be a non-negative integer or None")


@dataclass(frozen=True, slots=True)
class CreatorBaseline:
    candidate_video_id: str
    channel_id: str
    format: VideoFormat
    median_views: float
    sample_video_ids: tuple[str, ...]
    computed_at: str
    window_days: int | None = None

    @property
    def sample_size(self) -> int:
        return len(self.sample_video_ids)

    def __post_init__(self) -> None:
        _require_text(self.candidate_video_id, "candidate_video_id")
        _require_text(self.channel_id, "channel_id")
        _require_timestamp(self.computed_at, "computed_at")
        if self.format not in ("short_form", "long_form", "unknown"):
            raise ValueError("format must be short_form, long_form, or unknown")
        if (
            isinstance(self.median_views, bool)
            or not isinstance(self.median_views, (int, float))
            or not isfinite(self.median_views)
            or self.median_views < 0
        ):
            raise ValueError("median_views must be a finite non-negative number")
        if self.window_days is not None and (
            isinstance(self.window_days, bool)
            or not isinstance(self.window_days, int)
            or self.window_days <= 0
        ):
            raise ValueError("window_days must be a positive integer")
        if not isinstance(self.sample_video_ids, tuple):
            raise ValueError("sample_video_ids must be a tuple")
        if len(set(self.sample_video_ids)) != len(self.sample_video_ids):
            raise ValueError("sample_video_ids must be unique")
        if self.candidate_video_id in self.sample_video_ids:
            raise ValueError("baseline must exclude the candidate video")
        if any(not isinstance(video_id, str) or not video_id.strip() for video_id in self.sample_video_ids):
            raise ValueError("sample_video_ids cannot contain empty or invalid IDs")
