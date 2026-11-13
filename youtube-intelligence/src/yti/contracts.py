"""Version-1 internal data contracts for source observations and baselines.

These contracts are additive: the existing JSON/CSV MVP remains supported.
Adapters should normalize provider responses into these models at their boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

VideoFormat = Literal["short_form", "long_form", "unknown"]


@dataclass(frozen=True, slots=True)
class SourceReference:
    provider: str
    retrieved_at: str
    method: str
    query: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        for name in ("provider", "retrieved_at", "method"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")


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
        for name in ("video_id", "title", "channel_id", "channel_title", "observed_at"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.format not in ("short_form", "long_form", "unknown"):
            raise ValueError("format must be short_form, long_form, or unknown")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("duration_seconds cannot be negative")
        if self.views is not None and self.views < 0:
            raise ValueError("views cannot be negative")


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
        for name in ("candidate_video_id", "channel_id", "computed_at"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.format not in ("short_form", "long_form", "unknown"):
            raise ValueError("format must be short_form, long_form, or unknown")
        if self.median_views < 0:
            raise ValueError("median_views cannot be negative")
        if self.window_days is not None and self.window_days <= 0:
            raise ValueError("window_days must be positive")
        if len(set(self.sample_video_ids)) != len(self.sample_video_ids):
            raise ValueError("sample_video_ids must be unique")
        if self.candidate_video_id in self.sample_video_ids:
            raise ValueError("baseline must exclude the candidate video")
        if any(not video_id.strip() for video_id in self.sample_video_ids):
            raise ValueError("sample_video_ids cannot contain empty IDs")
