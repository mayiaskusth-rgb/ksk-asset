import json

import pytest

from yti.contracts import SourceReference
from yti.transcripts import (
    TranscriptObservation,
    TranscriptSegment,
    make_transcript_observation,
    parse_json3,
    parse_vtt,
    transcript_checksum,
)

SOURCE = SourceReference(
    provider="fixture", retrieved_at="2026-11-13T10:00:00Z",
    method="local_fixture", url="https://youtube.com/watch?v=abc123",
)


def test_parse_vtt_preserves_timestamps_and_cleans_markup():
    payload = """WEBVTT

cue-1
00:00:01.200 --> 00:00:03.500 align:start
<c>First &amp; clear</c>
line two

00:00:05.000 --> 00:00:06.000
Second cue
"""
    segments = parse_vtt(payload)
    assert segments == (
        TranscriptSegment(1.2, 2.3, "First & clear line two"),
        TranscriptSegment(5.0, 1.0, "Second cue"),
    )


def test_parse_vtt_accepts_minute_timestamp_and_sorts_cues():
    payload = """WEBVTT

00:01.500 --> 00:02.000
Later

00:00.000 --> 00:00.500
Earlier
"""
    assert [item.start_seconds for item in parse_vtt(payload)] == [0.0, 1.5]


def test_parse_vtt_rejects_invalid_or_reversed_timestamps():
    with pytest.raises(ValueError, match="invalid subtitle timestamp"):
        parse_vtt("00:99:99.000 --> 00:99:99.500\nBad")
    with pytest.raises(ValueError, match="precedes"):
        parse_vtt("00:00:03.000 --> 00:00:02.000\nBad")


def test_parse_json3_preserves_offsets_and_joins_segments():
    payload = json.dumps({"events": [
        {"tStartMs": 1250, "dDurationMs": 2200, "segs": [{"utf8": "Hello "}, {"utf8": "world"}]},
        {"tStartMs": 4000, "dDurationMs": 900, "segs": [{"utf8": "Again"}]},
        {"segs": [{"utf8": "header"}]},
    ]})
    segments = parse_json3(payload)
    assert segments == (
        TranscriptSegment(1.25, 2.2, "Hello world"),
        TranscriptSegment(4.0, 0.9, "Again"),
    )


def test_empty_caption_payload_returns_empty_segments():
    assert parse_vtt("WEBVTT\n\n") == ()
    assert parse_json3('{"events": []}') == ()


def test_observation_records_provenance_and_stable_checksum():
    segments = parse_vtt("WEBVTT\n\n00:00.000 --> 00:01.000\nHello")
    observation = make_transcript_observation(
        video_id="abc123", source=SOURCE, segments=segments, language="en",
        caption_type="creator_provided", subtitle_format="vtt",
    )
    assert observation.status == "retrieved"
    assert observation.source.provider == "fixture"
    assert observation.content_sha256 == transcript_checksum(segments)
    assert len(observation.content_sha256) == 64


def test_empty_transcript_is_explicit_no_captions_status():
    observation = make_transcript_observation(
        video_id="abc123", source=SOURCE, segments=(), language="en",
        caption_type="auto_generated", subtitle_format="vtt",
    )
    assert observation.status == "no_captions"
    assert observation.segments == ()


def test_transcript_observation_rejects_segments_for_blocked_status():
    with pytest.raises(ValueError, match="cannot contain segments"):
        TranscriptObservation(
            video_id="abc123", status="blocked", source=SOURCE,
            segments=(TranscriptSegment(0, 1, "secret"),),
        )


def test_transcript_observation_requires_segments_when_retrieved():
    with pytest.raises(ValueError, match="must contain segments"):
        TranscriptObservation(video_id="abc123", status="retrieved", source=SOURCE)


def test_segment_rejects_negative_time_and_empty_text():
    with pytest.raises(ValueError):
        TranscriptSegment(-1, 1, "text")
    with pytest.raises(ValueError):
        TranscriptSegment(0, 1, "  ")
