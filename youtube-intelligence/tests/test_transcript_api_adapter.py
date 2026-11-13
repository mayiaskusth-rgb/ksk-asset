from types import SimpleNamespace

from yti.transcript_api_adapter import YouTubeTranscriptApiAdapter


class FakeFetched(list):
    language_code = "en"
    is_generated = False


def test_adapter_normalizes_timestamped_snippets(monkeypatch):
    class FakeApi:
        def fetch(self, video_id, languages):
            assert video_id == "efjBiVN_N3M"
            assert languages == ["en"]
            return FakeFetched([SimpleNamespace(start=1.25, duration=2.0, text="Hello")])

    monkeypatch.setitem(
        __import__("sys").modules,
        "youtube_transcript_api",
        SimpleNamespace(YouTubeTranscriptApi=FakeApi),
    )
    result = YouTubeTranscriptApiAdapter().fetch(
        video_id="efjBiVN_N3M",
        video_url="https://www.youtube.com/watch?v=efjBiVN_N3M",
        language="en",
        retrieved_at="2026-11-13T10:00:00+00:00",
    )
    assert result.status == "retrieved"
    assert result.segments[0].start_seconds == 1.25
    assert result.caption_type == "creator_provided"


def test_adapter_classifies_ip_block(monkeypatch):
    class IpBlocked(Exception):
        pass

    class FakeApi:
        def fetch(self, video_id, languages):
            raise IpBlocked("request blocked")

    monkeypatch.setitem(
        __import__("sys").modules,
        "youtube_transcript_api",
        SimpleNamespace(YouTubeTranscriptApi=FakeApi),
    )
    result = YouTubeTranscriptApiAdapter().fetch(
        video_id="efjBiVN_N3M",
        video_url="https://www.youtube.com/watch?v=efjBiVN_N3M",
        language="en",
        retrieved_at="2026-11-13T10:00:00+00:00",
    )
    assert result.status == "blocked"
    assert result.detail_code == "ACCESS_CHALLENGE_OR_RATE_LIMIT"
