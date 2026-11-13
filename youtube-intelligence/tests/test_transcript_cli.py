import json

from yti.cli import main
from yti.transcripts import TranscriptObservation, TranscriptSegment
from yti.contracts import SourceReference


def test_transcript_cli_writes_private_local_json(monkeypatch, tmp_path):
    from yti.transcript_adapter import YtDlpTranscriptAdapter

    def fake_fetch(self, **kwargs):
        return TranscriptObservation(
            video_id=kwargs["video_id"],
            status="retrieved",
            source=SourceReference(
                provider="fake", retrieved_at=kwargs["retrieved_at"],
                method="test", url=kwargs["video_url"],
            ),
            language=kwargs["language"],
            caption_type="creator_provided",
            subtitle_format="vtt",
            segments=(TranscriptSegment(0.0, 1.0, "Fixture transcript"),),
        )

    monkeypatch.setattr(YtDlpTranscriptAdapter, "fetch", fake_fetch)
    output = tmp_path / "private" / "transcript.json"
    monkeypatch.setattr(
        "sys.argv",
        ["yti", "transcript", "--video-id", "abc123",
         "--url", "https://www.youtube.com/watch?v=abc123",
         "--language", "en", "--output", str(output)],
    )

    main()

    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["status"] == "retrieved"
    assert result["segments"][0]["text"] == "Fixture transcript"
    assert result["source"]["provider"] == "fake"
