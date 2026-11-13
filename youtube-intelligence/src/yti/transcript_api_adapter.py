"""Isolated diagnostic adapter using youtube-transcript-api.

This provider is intentionally separate from the production yt-dlp adapter.
It fetches one selected video's requested-language captions and normalizes
timestamped snippets into the shared transcript contract.
"""
from __future__ import annotations

from yti.contracts import SourceReference
from yti.transcripts import TranscriptObservation, TranscriptSegment


class YouTubeTranscriptApiAdapter:
    provider = "youtube-transcript-api"

    def fetch(self, *, video_id: str, video_url: str, language: str, retrieved_at: str) -> TranscriptObservation:
        source = SourceReference(
            provider=self.provider,
            retrieved_at=retrieved_at,
            method="direct_caption_fetch",
            url=video_url,
        )
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            fetched = YouTubeTranscriptApi().fetch(video_id, languages=[language])
            segments = tuple(
                TranscriptSegment(float(item.start), float(item.duration), str(item.text))
                for item in fetched
                if str(item.text).strip()
            )
            if not segments:
                return TranscriptObservation(
                    video_id=video_id, status="no_captions", source=source,
                    language=language, detail_code="EMPTY_TRANSCRIPT",
                )
            return TranscriptObservation(
                video_id=video_id,
                status="retrieved",
                source=source,
                language=getattr(fetched, "language_code", language),
                caption_type="auto_generated" if getattr(fetched, "is_generated", False) else "creator_provided",
                segments=segments,
            )
        except Exception as exc:
            error_name = type(exc).__name__.lower()
            message = str(exc).lower()
            if any(token in error_name or token in message for token in (
                "ipblocked", "requestblocked", "toomanyrequests", "too many requests",
                "429", "http 403", "forbidden", "not a bot", "captcha", "sign in to confirm",
            )):
                status, code = "blocked", "ACCESS_CHALLENGE_OR_RATE_LIMIT"
            elif any(token in error_name for token in ("transcriptsdisabled", "notranscriptfound", "videounavailable")):
                status, code = "no_captions", "NO_CAPTION_TRACK"
            else:
                status, code = "failed", "PROVIDER_ERROR"
            return TranscriptObservation(
                video_id=video_id, status=status, source=source,
                language=language, detail_code=code,
            )
