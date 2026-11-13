from yti.contracts import SourceReference
from yti.transcripts import TranscriptObservation, TranscriptSegment
from yti.transcript_api_diagnostic import run_diagnostic


class FakeAdapter:
    def fetch(self, **kwargs):
        return TranscriptObservation(
            video_id=kwargs["video_id"],
            status="retrieved",
            source=SourceReference(
                provider="youtube-transcript-api",
                retrieved_at=kwargs["retrieved_at"],
                method="direct_caption_fetch",
                url=kwargs["video_url"],
            ),
            language="en",
            caption_type="creator_provided",
            segments=(TranscriptSegment(0.0, 1.0, "Private words must not be saved."),),
        )


def test_diagnostic_is_one_video_and_sanitizes_transcript(monkeypatch, tmp_path):
    monkeypatch.setattr("yti.transcript_api_diagnostic.YouTubeTranscriptApiAdapter", FakeAdapter)
    report = run_diagnostic("norsat-webinar", tmp_path / "report.json")
    saved = (tmp_path / "report.json").read_text(encoding="utf-8")
    assert report["requested_video_count"] == 1
    assert report["automatic_fallback"] is False
    assert report["records"][0]["source_provider"] == "youtube-transcript-api"
    assert "Private words" not in saved


def test_diagnostic_rejects_unknown_sample(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="unsupported sample"):
        run_diagnostic("all", tmp_path / "report.json")
