from yti.scoring import score_video, score_videos


def test_scores_creator_relative_outlier():
    result = score_video({
        "video_id": "a",
        "views": 100_000,
        "creator_baseline_median_views": 20_000,
        "baseline_sample_size": 10,
    })
    assert result["outlier_ratio"] == 5.0
    assert result["outlier_band"] == "strong"
    assert result["score_status"] == "scored"


def test_rejects_small_baseline_sample():
    result = score_video({
        "video_id": "b",
        "views": 100_000,
        "creator_baseline_median_views": 20_000,
        "baseline_sample_size": 3,
    })
    assert result["outlier_ratio"] is None
    assert result["score_status"] == "insufficient_baseline"


def test_rejects_zero_baseline():
    result = score_video({
        "video_id": "c",
        "views": 100,
        "creator_baseline_median_views": 0,
        "baseline_sample_size": 10,
    })
    assert result["score_status"] == "invalid_baseline"


def test_missing_baseline_is_not_guessed():
    result = score_video({"video_id": "d", "views": 100})
    assert result["outlier_ratio"] is None
    assert result["score_status"] == "missing_baseline"


def test_sort_places_highest_scored_first_and_unscored_last():
    rows = score_videos([
        {"video_id": "low", "views": 10, "creator_baseline_median_views": 10, "baseline_sample_size": 10},
        {"video_id": "high", "views": 100, "creator_baseline_median_views": 10, "baseline_sample_size": 10},
        {"video_id": "unknown", "views": 100}
    ])
    assert [row["video_id"] for row in rows] == ["high", "low", "unknown"]
