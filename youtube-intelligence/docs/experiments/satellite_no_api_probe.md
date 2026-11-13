# Satellite no-API search probe

**Status:** Implemented as a local experimental adapter; not yet run against live YouTube. Unit tests use mocked extractor responses. A local run is required to establish whether the extraction path works in the user's environment.

## Purpose

Test whether a small, occasional public YouTube search workflow can collect enough candidate metadata for the satellite research experiment, without a YouTube Data API key or paid hosted service. This is a technical feasibility probe, not a claim that automated extraction is permitted in every context or guaranteed to remain available.

## Conservative first-run limits

- One search query (the first query) per each of the ten satellite ideas.
- Exactly five results per query.
- Sequential requests; ten seconds between uncached query calls.
- yt-dlp request-sleep options enabled.
- No API key, login, browser cookies, proxy, proxy rotation, CAPTCHA workaround, or access-control bypass.
- Zero extractor/network retries.
- Successful query responses cached locally and reused on later runs.
- On HTTP 403/429, verification/sign-in challenge, CAPTCHA, timeout, or non-zero extractor error, stop the entire run. Do not switch identities, IPs, endpoints or tools to continue.

The ten-second pause is a conservative experiment setting, **not a YouTube-approved rate or a guarantee against throttling**. Do not increase volume based on one successful run.

## What is captured

For each returned entry, the adapter stores the video ID/URL, title, channel ID/name where exposed, duration, current view count where exposed, upload date where exposed, idea ID, exact query, source adapter and retrieval timestamp. It does not download video, audio, subtitles or thumbnails.

A single current view count is a snapshot; it is not historical velocity or VPH. Missing fields remain null.

## Run locally

From the youtube-intelligence/ directory, with Python 3.11+ and the project installed:

```bash
python -m pip install -e ".[dev,probe]"
pytest
python -m yti.providers.yt_dlp_probe
```

Output is written under runs/satellite_probe/. The directory is git-ignored. The output JSON contains a run manifest, query-level status, deduplicated video observations and any stop reason. Do not commit raw run output unless it has been reviewed for public-safe content.

## Interpretation

A successful run establishes only that the extractor returned data for this bounded test at that time. It does not establish long-term reliability, permission to scale, or immunity from IP-level throttling. An unsuccessful run is still useful evidence: preserve the error and stop. Do not retry blocked requests or try evasive alternatives.

After the local run, review:
- number of queries attempted and completed;
- unique videos and cross-query duplicates;
- relevance of the first five results per idea;
- completeness of channel/title/date/duration/view fields;
- whether the run stopped due to access restrictions or ordinary extraction errors.

Do not proceed to channel-history collection or transcript retrieval until the search stage has been reviewed.
