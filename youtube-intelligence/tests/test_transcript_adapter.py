from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from yti.transcript_adapter import YtDlpTranscriptAdapter


class FakeYDL:
    calls = []
    info = {
        "subtitles": {"en": [{"ext": "vtt"}]},
        "automatic_captions": {"en": [{"ext": "vtt"}]},
    }

    def __init__(self, options):
        self.options = options
        self.__class__.calls.append(options)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def extract_info(self, url, download=False):
        if download:
            output = Path(self.options["outtmpl"]["subtitle"].replace("%(id)s.%(ext)s", "vid.vtt"))
            output.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nHello", encoding="utf-8")
            return {"requested_subtitles": {"en": {"ext": "vtt"}}}
        return self.info


def test_adapter_prefers_creator_captions_and_sets_skip_download(monkeypatch):
    FakeYDL.calls.clear()
    monkeypatch.setattr(YtDlpTranscriptAdapter, "_yt_dlp", staticmethod(lambda: SimpleNamespace(YoutubeDL=FakeYDL)))
    result = YtDlpTranscriptAdapter().fetch(
        video_id="vid", video_url="https://www.youtube.com/watch?v=vid",
        language="en", retrieved_at="2026-11-13T10:00:00Z",
    )
    assert result.status == "retrieved"
    assert result.caption_type == "creator_provided"
    assert result.segments[0].text == "Hello"
    assert FakeYDL.calls[0]["skip_download"] is True\n    assert FakeYDL.calls[0]["noplaylist"] is True
    assert FakeYDL.calls[1]["skip_download"] is True
    assert FakeYDL.calls[1]["writesubtitles"] is True
    assert FakeYDL.calls[1]["writeautomaticsub"] is False
    assert FakeYDL.calls[1]["retries"] == 0


def test_adapter_does_not_fall_back_to_other_languages(monkeypatch):
    class NoEnglish(FakeYDL):
        info = {"subtitles": {"fr": [{"ext": "vtt"}]}, "automatic_captions": {}}
    monkeypatch.setattr(YtDlpTranscriptAdapter, "_yt_dlp", staticmethod(lambda: SimpleNamespace(YoutubeDL=NoEnglish)))
    result = YtDlpTranscriptAdapter().fetch(
        video_id="vid", video_url="https://www.youtube.com/watch?v=vid",
        language="en", retrieved_at="2026-11-13T10:00:00Z",
    )
    assert result.status == "no_captions"
    assert result.detail_code == "NO_MATCHING_CAPTION_TRACK"


def test_adapter_maps_rate_limit_without_retry(monkeypatch):
    class RateLimited(FakeYDL):
        def extract_info(self, url, download=False):
            raise RuntimeError("HTTP Error 429: Too Many Requests")
    monkeypatch.setattr(YtDlpTranscriptAdapter, "_yt_dlp", staticmethod(lambda: SimpleNamespace(YoutubeDL=RateLimited)))
    result = YtDlpTranscriptAdapter().fetch(
        video_id="vid", video_url="https://www.youtube.com/watch?v=vid",
        language="en", retrieved_at="2026-11-13T10:00:00Z",
    )
    assert result.status == "blocked"
    assert result.detail_code == "RATE_LIMITED"


def test_adapter_rejects_non_youtube_urls():
    import pytest
    with pytest.raises(ValueError, match="YouTube URL"):
        YtDlpTranscriptAdapter().fetch(
            video_id="vid", video_url="https://example.com/video",
            language="en", retrieved_at="2026-11-13T10:00:00Z",
        )


def test_adapter_uses_auto_captions_only_when_creator_track_absent(monkeypatch):
    class AutomaticOnly(FakeYDL):
        info = {"subtitles": {}, "automatic_captions": {"en": [{"ext": "vtt"}]}}
    monkeypatch.setattr(YtDlpTranscriptAdapter, "_yt_dlp", staticmethod(lambda: SimpleNamespace(YoutubeDL=AutomaticOnly)))
    result = YtDlpTranscriptAdapter().fetch(
        video_id="vid", video_url="https://www.youtube.com/watch?v=vid",
        language="en", retrieved_at="2026-11-13T10:00:00Z",
    )
    assert result.status == "retrieved"
    assert result.caption_type == "auto_generated"
    assert AutomaticOnly.calls[-1]["writesubtitles"] is False
    assert AutomaticOnly.calls[-1]["writeautomaticsub"] is True


def test_language_match_does_not_cross_requested_region():
    assert YtDlpTranscriptAdapter._language_match(["en-GB", "en-US"], "en") == "en-GB"
    assert YtDlpTranscriptAdapter._language_match(["en-GB"], "en-US") is None
