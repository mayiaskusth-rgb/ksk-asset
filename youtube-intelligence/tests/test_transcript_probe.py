from yti.contracts import SourceReference
from yti.transcripts import TranscriptObservation, TranscriptSegment
from yti.transcript_probe import run_probe


class FakeAdapter:
    calls = []

    def fetch(self, **kwargs):
        self.calls.append(kwargs)
        return TranscriptObservation(
            video_id=kwargs["video_id"],
            status="retrieved",
            source=SourceReference(
                provider="fake-yt-dlp",
                retrieved_at=kwargs["retrieved_at"],
                method="captions_only",
                url=kwargs["video_url"],
            ),
            language="en",
            caption_type="auto_generated",
            subtitle_format="vtt",
            segments=(
                TranscriptSegment(0.0, 2.0, "A private transcript sentence."),
                TranscriptSegment(2.0, 3.0, "Another private sentence."),
            ),
        )


def test_probe_defaults_to_one_selected_long_video(monkeypatch, tmp_path):
    FakeAdapter.calls.clear()
    monkeypatch.setattr("yti.transcript_probe.YtDlpTranscriptAdapter", FakeAdapter)
    output = tmp_path / "report.json"

    report = run_probe("norsat-webinar", output)

    assert report["requested_video_count"] == 1
    assert report["processed_video_count"] == 1
    assert report["records"][0]["video_id"] == "efjBiVN_N3M"
    assert report["records"][0]["duration_seconds"] == 3554
    assert report["records"][0]["segment_count"] == 2
    assert len(FakeAdapter.calls) == 1
    serialized = output.read_text(encoding="utf-8")
    assert "A private transcript sentence" not in serialized
    assert "Another private sentence" not in serialized
    assert "content_sha256" not in serialized


def test_probe_both_is_sequential_and_stops_on_block(monkeypatch, tmp_path):
    class BlockOnFirst(FakeAdapter):
        def fetch(self, **kwargs):
            self.calls.append(kwargs)
            return TranscriptObservation(
                video_id=kwargs["video_id"],
                status="blocked",
                source=SourceReference(
                    provider="fake-yt-dlp",
                    retrieved_at=kwargs["retrieved_at"],
                    method="captions_only",
                    url=kwargs["video_url"],
                ),
                language="en",
                detail_code="RATE_LIMITED",
            )

    BlockOnFirst.calls.clear()
    monkeypatch.setattr("yti.transcript_probe.YtDlpTranscriptAdapter", BlockOnFirst)
    report = run_probe("both", tmp_path / "report.json")

    assert report["requested_video_count"] == 2
    assert report["processed_video_count"] == 1
    assert report["stop_reason"] == "blocked_response_stop_no_retry"
    assert len(BlockOnFirst.calls) == 1
    assert report["records"][0]["status"] == "blocked"


def test_probe_rejects_unknown_sample(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="unsupported sample"):
        run_probe("all-videos", tmp_path / "report.json")
