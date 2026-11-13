"""Optional yt-dlp captions-only adapter.

Network access is explicit at the call site. This adapter never downloads media,
uses no cookies/proxies, performs no retries, and stops by returning a status.
Install with the package's optional youtube extra.
"""
from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

from yti.contracts import SourceReference
from yti.transcripts import (
    CaptionType,
    TranscriptObservation,
    parse_json3,
    parse_vtt,
    make_transcript_observation,
)


class YtDlpTranscriptAdapter:
    """Retrieve one selected caption track through yt-dlp's Python API."""

    def __init__(self, *, socket_timeout: int = 20) -> None:
        if socket_timeout < 1:
            raise ValueError("socket_timeout must be positive")
        self.socket_timeout = socket_timeout

    @staticmethod
    def _yt_dlp():
        try:
            import yt_dlp
        except ImportError as exc:
            raise RuntimeError(
                "yt-dlp is optional; install with pip install -e '.[youtube]'"
            ) from exc
        return yt_dlp

    @staticmethod
    def _language_match(available: list[str], requested: str) -> str | None:
        # Exact match first, then a regional variant of the requested base language.
        if requested in available:
            return requested
        prefix = requested.split("-", 1)[0].lower() + "-"
        return next((lang for lang in sorted(available) if lang.lower().startswith(prefix)), None)

    @classmethod
    def _select_track(cls, info: dict[str, Any], requested_language: str):
        manual = info.get("subtitles") or {}
        automatic = info.get("automatic_captions") or {}
        for tracks, caption_type in (
            (manual, "creator_provided"),
            (automatic, "auto_generated"),
        ):
            language = cls._language_match(list(tracks), requested_language)
            if language:
                # Do not ask yt-dlp to translate; use only the exact selected language key.
                return language, caption_type
        return None, None

    def fetch(
        self,
        *,
        video_id: str,
        video_url: str,
        language: str = "en",
        retrieved_at: str,
    ) -> TranscriptObservation:
        if not video_id.strip() or not video_url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            raise ValueError("a video ID and supported YouTube URL are required")
        if not re.fullmatch(r"[A-Za-z0-9-]{2,20}", language):
            raise ValueError("language must be a BCP-47-like language code")

        source = SourceReference(
            provider="yt-dlp", retrieved_at=retrieved_at,
            method="captions_only", url=video_url,
        )
        ydl_module = self._yt_dlp()
        common = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
            "socket_timeout": self.socket_timeout,
            "retries": 0,
            "fragment_retries": 0,
            "extractor_retries": 0,
        }
        try:
            with ydl_module.YoutubeDL(common) as ydl:
                info = ydl.extract_info(video_url, download=False)
            selected_language, caption_type = self._select_track(info or {}, language)
            if not selected_language:
                return TranscriptObservation(
                    video_id=video_id, status="no_captions", source=source,
                    language=language, detail_code="NO_MATCHING_CAPTION_TRACK",
                )

            with tempfile.TemporaryDirectory(prefix="yti-captions-") as temp_dir:
                output_template = str(Path(temp_dir) / "%(id)s.%(ext)s")
                options = {
                    **common,
                    "writesubtitles": caption_type == "creator_provided",
                    "writeautomaticsub": caption_type == "auto_generated",
                    "subtitleslangs": [selected_language],
                    "subtitlesformat": "json3/vtt/best",
                    "outtmpl": {"subtitle": output_template},
                }
                with ydl_module.YoutubeDL(options) as ydl:
                    downloaded_info = ydl.extract_info(video_url, download=True)
                requested = (downloaded_info or {}).get("requested_subtitles") or {}
                track = requested.get(selected_language) or {}
                extension = track.get("ext")
                candidates = list(Path(temp_dir).glob(f"*.{extension}")) if extension else []
                if not candidates:
                    candidates = list(Path(temp_dir).glob("*.json3")) + list(Path(temp_dir).glob("*.vtt"))
                if not candidates:
                    return TranscriptObservation(
                        video_id=video_id, status="failed", source=source,
                        language=selected_language, caption_type=caption_type,
                        detail_code="SUBTITLE_FILE_NOT_CREATED",
                    )
                caption_path = candidates[0]
                payload = caption_path.read_text(encoding="utf-8-sig")
                if caption_path.suffix.lower() == ".json3":
                    segments = parse_json3(payload)
                    subtitle_format = "json3"
                elif caption_path.suffix.lower() == ".vtt":
                    segments = parse_vtt(payload)
                    subtitle_format = "vtt"
                else:
                    return TranscriptObservation(
                        video_id=video_id, status="failed", source=source,
                        language=selected_language, caption_type=caption_type,
                        detail_code="UNSUPPORTED_SUBTITLE_FORMAT",
                    )
                return make_transcript_observation(
                    video_id=video_id, source=source, segments=segments,
                    language=selected_language, caption_type=caption_type,
                    subtitle_format=subtitle_format,
                )
        except Exception as exc:  # map errors; do not retry or expose raw exception text
            message = str(exc).lower()
            if any(token in message for token in ("429", "too many requests", "rate limit")):
                status, code = "blocked", "RATE_LIMITED"
            elif any(token in message for token in ("403", "forbidden", "captcha", "verify you are", "not a bot", "sign in to confirm", "challenge")):
                status, code = "blocked", "ACCESS_CHALLENGE"
            else:
                status, code = "failed", "EXTRACTION_FAILED"
            return TranscriptObservation(
                video_id=video_id, status=status, source=source,
                language=language, detail_code=code,
            )
