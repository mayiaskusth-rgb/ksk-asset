import pytest

from yti.contracts import CreatorBaseline, SourceReference, VideoObservation


def test_video_observation_preserves_observation_provenance():
    source = SourceReference(
        provider="fixture",
        retrieved_at="2026-11-13T10:00:00Z",
        method="local_json",
        query="barcode",
    )
    video = VideoObservation(
        video_id="abc123",
        title="How barcodes work",
        channel_id="channel-1",
        channel_title="Everyday Systems",
        published_at="2026-10-01T00:00:00Z",
        duration_seconds=420,
        format="long_form",
        views=12000,
        observed_at="2026-11-13T10:00:00Z",
        source=source,
    )
    assert video.source.provider == "fixture"
    assert video.views == 12000
    assert video.format == "long_form"


def test_video_observation_rejects_negative_counts():
    with pytest.raises(ValueError, match="views"):
        VideoObservation(
            video_id="abc123", title="Title", channel_id="c1",
            channel_title="Channel", published_at=None, duration_seconds=10,
            format="short_form", views=-1, observed_at="2026-11-13T10:00:00Z",
            source=SourceReference("fixture", "2026-11-13T10:00:00Z", "test"),
        )


def test_video_observation_requires_timezone_aware_observation_time():
    with pytest.raises(ValueError, match="timezone"):
        VideoObservation(
            video_id="abc123", title="Title", channel_id="c1",
            channel_title="Channel", published_at=None, duration_seconds=10,
            format="short_form", views=1, observed_at="2026-11-13T10:00:00",
            source=SourceReference("fixture", "2026-11-13T10:00:00Z", "test"),
        )


def test_creator_baseline_excludes_candidate_and_counts_unique_peers():
    baseline = CreatorBaseline(
        candidate_video_id="candidate",
        channel_id="channel-1",
        format="long_form",
        median_views=5000,
        sample_video_ids=("peer-1", "peer-2", "peer-3", "peer-4", "peer-5"),
        computed_at="2026-11-13T10:00:00Z",
        window_days=365,
    )
    assert baseline.sample_size == 5


def test_creator_baseline_rejects_candidate_leakage():
    with pytest.raises(ValueError, match="exclude the candidate"):
        CreatorBaseline(
            candidate_video_id="candidate",
            channel_id="channel-1",
            format="long_form",
            median_views=5000,
            sample_video_ids=("candidate", "peer-2"),
            computed_at="2026-11-13T10:00:00Z",
        )


def test_creator_baseline_rejects_duplicate_comparison_videos():
    with pytest.raises(ValueError, match="unique"):
        CreatorBaseline(
            candidate_video_id="candidate",
            channel_id="channel-1",
            format="long_form",
            median_views=5000,
            sample_video_ids=("peer-1", "peer-1"),
            computed_at="2026-11-13T10:00:00Z",
        )


def test_creator_baseline_rejects_non_finite_median():
    with pytest.raises(ValueError, match="finite"):
        CreatorBaseline(
            candidate_video_id="candidate",
            channel_id="channel-1",
            format="long_form",
            median_views=float("nan"),
            sample_video_ids=("peer-1",),
            computed_at="2026-11-13T10:00:00Z",
        )
