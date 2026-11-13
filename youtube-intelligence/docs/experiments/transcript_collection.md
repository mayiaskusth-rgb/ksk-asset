# Transcript Collection — Design Note

**Status:** Planned; not yet implemented  
**Current search adapter:** yt-dlp  
**Constraint:** No paid transcript API and no video/audio download in the first pass. See [transcript tools reconnaissance](transcript_tools_reconnaissance.md) for the point-in-time repo review and license decisions.

## Preferred first route: yt-dlp subtitle extraction

**Selection status:** Preferred prototype, not yet implemented or validated. Keep it behind a provider-neutral adapter and test parsing/normalization locally before any live collection.

The existing probe already uses yt-dlp for public search metadata. It can be extended for selected video URLs to inspect available captions and, when available, save subtitle files without downloading the video:

- Inspect caption tracks: \`yt-dlp --list-subs VIDEO_URL\`
- Creator-provided captions: \`--write-subs\`
- Automatically generated captions: \`--write-auto-subs\`
- Restrict languages: \`--sub-langs "en.*,en"\`
- Avoid video download: \`--skip-download\`
- Prefer a parseable subtitle format: \`--sub-format "vtt/best"\`

Official yt-dlp options reference: https://github.com/yt-dlp/yt-dlp#subtitle-options

## Alternative: youtube-transcript-api

The open-source \`youtube-transcript-api\` package can retrieve available YouTube transcript tracks and timed snippets without downloading video. It relies on YouTube's web interfaces and may be rate-limited or blocked, especially from cloud-hosted IPs.

Repository: https://github.com/jdepoix/youtube-transcript-api

Use it as a separately selectable adapter after a small test. Do not build the system around it as the only source.

## Required transcript record

- video_id and canonical video URL
- source adapter and adapter version
- language code
- caption type: creator-provided / auto-generated / translated / unknown
- retrieval timestamp
- transcript status: retrieved / no captions / unavailable / blocked / failed
- timestamped segments (start, duration/end, text)
- raw subtitle file path and normalized transcript path
- content checksum and normalization version

## Safety and operating rules

- Do not download video or audio as part of transcript retrieval.
- Do not use cookies, account sessions, proxies, proxy rotation, CAPTCHA bypasses, or access-control workarounds.
- Use a bounded, sequential batch with caching and zero retries initially.
- Stop on 403/429, verification/challenge signals, or repeated extractor errors.
- Do not commit full transcripts to this public repository. Keep local/private run artefacts out of Git; public fixtures should be synthetic or short and rights-safe.
- Never fabricate a transcript when captions are unavailable. Mark it unavailable and keep the analysis placeholder.
- Respect source terms, copyright and applicable platform policies. Transcript availability does not itself grant republication rights.


## First-pass implementation boundary

- Input: one explicitly selected video ID/URL and a bounded language preference.
- Output: normalized transcript observation with explicit status and provenance, plus timestamped segments only when retrieval succeeds.
- Preserve both raw-caption timing and normalized segment timing; never silently shift timestamps during cleanup.
- Prefer creator-provided captions when available; otherwise record auto-generated captions. Do not silently substitute translated captions.
- Treat subtitle format as an implementation detail. Normalize VTT/JSON3/SRT into the same internal segment representation while retaining source format metadata.
- Unit tests use synthetic subtitle fixtures and cover rolling-caption duplication, cue overlap, empty captions, malformed timestamps, Unicode, missing language and unavailable-track states.
- The live experiment is a small sequential sample of already-selected satellite videos, not a broad channel crawl. Cache each result and stop on access challenges or rate limits.
- The first pass does not run speech-to-text fallback. If captions are unavailable, record that honestly; do not download audio to fill the gap.


## Implementation status update (2026-11-13)

The first local normalization slice is now implemented on draft PR #11 in `src/yti/transcripts.py`:
- provider-neutral transcript observation and segment records;
- deterministic WebVTT and JSON3 parsers;
- normalized-content checksum;
- explicit no-captions state for empty parsed content;
- synthetic tests, with no network dependency.

This is not yet a YouTube collector. Track discovery, caption selection, retrieval, error mapping, caching and live satellite sampling remain future work. See the latest dated section in `HANDOFF.md`.
