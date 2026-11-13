"""Creator-relative outlier scoring with explicit baseline quality checks."""

from __future__ import annotations

from typing import Any


def score_video(
    video: dict[str, Any],
    *,
    minimum_baseline_sample: int = 5,
) -> dict[str, Any]:
    """Return a scored copy of a video record.

    The caller must supply a baseline computed from eligible videos by the
    same creator and format, excluding the candidate itself.
    """
    result = dict(video)
    baseline = video.get("creator_baseline_median_views")
    sample_size = video.get("baseline_sample_size")

    if baseline is None or sample_size is None:
        result.update(
            outlier_ratio=None,
            score_status="missing_baseline",
            outlier_band="unscored",
        )
        return result

    if not isinstance(baseline, (int, float)) or baseline <= 0:
        result.update(
            outlier_ratio=None,
            score_status="invalid_baseline",
            outlier_band="unscored",
        )
        return result

    if not isinstance(sample_size, int) or sample_size < minimum_baseline_sample:
        result.update(
            outlier_ratio=None,
            score_status="insufficient_baseline",
            outlier_band="low_confidence",
        )
        return result

    views = video.get("views")
    if not isinstance(views, (int, float)) or views < 0:
        result.update(
            outlier_ratio=None,
            score_status="invalid_views",
            outlier_band="unscored",
        )
        return result

    ratio = views / baseline
    if ratio >= 10:
        band = "exceptional"
    elif ratio >= 5:
        band = "strong"
    elif ratio >= 3:
        band = "candidate"
    else:
        band = "ordinary"

    result.update(
        outlier_ratio=round(ratio, 3),
        score_status="scored",
        outlier_band=band,
    )
    return result


def score_videos(
    videos: list[dict[str, Any]],
    *,
    minimum_baseline_sample: int = 5,
) -> list[dict[str, Any]]:
    """Score records and sort scored records first, descending by ratio."""
    scored = [
        score_video(video, minimum_baseline_sample=minimum_baseline_sample)
        for video in videos
    ]
    return sorted(
        scored,
        key=lambda row: (
            row["outlier_ratio"] is not None,
            row["outlier_ratio"] or -1,
        ),
        reverse=True,
    )
