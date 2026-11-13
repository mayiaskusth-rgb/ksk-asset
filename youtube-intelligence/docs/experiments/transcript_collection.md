# Transcript Collection — Design and Experiment

**Current implementation:** Optional yt-dlp captions-only adapter and a bounded satellite probe runner are implemented on draft PR #11. **Live retrieval has not yet been run.** The first experiment is opt-in through GitHub Actions; it is not part of ordinary CI.

## First controlled sample

The first selected video is the longest result in the original satellite discovery run:

| Selection | Video | Channel | Duration |
|---|---|---|---:|
| Default | [The Fundamentals of Satellite Communications Webinar](https://www.youtube.com/watch?v=efjBiVN_N3M) | Norsat International | 59:14 |
| Optional second | [The Power of These Satellites Is Deeply Troubling](https://www.youtube.com/watch?v=jo8Z4UzIBQk) | Astrum Extra | 48:17 |

The default experiment runs one video. The optional `both` selection runs the two sequentially. A blocked/rate-limited response stops the sequence immediately. These are selected test cases, not a representative sample of YouTube.

## How to run after the workflow is available on main

1. Open the repository's **Actions** tab.
2. Select **Satellite transcript probe**.
3. Choose `norsat-webinar` for the first one-video test. Choose `both` only after reviewing the first result.
4. Run the workflow and inspect the `satellite-transcript-probe-* ` artifact.

The workflow installs the optional `yt-dlp` extra, calls the same adapter used by the CLI, and writes a sanitized JSON report. The report includes status, language, caption type, format, segment count, last timestamp, source method and retrieval time. It deliberately excludes transcript text, excerpts, checksums and raw subtitle files. Full transcript text stays in runner memory and is not uploaded or committed.

## Adapter behaviour and safeguards

- Inspect available caption tracks; prefer creator-provided captions, then auto-generated captions.
- Use the requested language only; do not silently translate or substitute another explicit regional language.
- Set skip-download for metadata and subtitle retrieval; no video/audio download.
- One selected video at a time; no playlist expansion.
- Zero retries; no cookies, account sessions, proxies or CAPTCHA workarounds.
- Stop after 403/429 or verification/challenge signals.
- Never fabricate transcripts. Record `no_captions`, `blocked` or `failed` explicitly.
- No full transcript is committed to this public repository.

## What this experiment does not prove

A green unit-test run proves the mocked contract and orchestration only. It does not prove live YouTube availability, yt-dlp compatibility with the current YouTube response, transcript completeness, or suitability for analysis. GitHub-hosted runners may themselves be blocked. A blocked result is a valid experiment outcome, not a reason to add bypasses or retries.

## Next review gates

1. Run the default one-video sample and inspect the sanitized report.
2. If successful, compare the optional second sample.
3. Review transcript completeness, language/caption type, timestamp coverage and extraction failures. If full text is needed for analysis, handle it in a private/local environment; do not publish it as a public artifact.
4. Only after the extractor is reliable, select/build the analyser and test it on the same one or two transcripts.
5. Expand to a few more videos only after review and fixes. Do not bulk-process the 47-video discovery set yet.

## Related implementation

- Adapter: `src/yti/transcript_adapter.py`
- Normalization: `src/yti/transcripts.py`
- Local single-video CLI: `yti transcript`
- Bounded probe runner: `scripts/run_transcript_probe.py`
- Probe workflow: `.github/workflows/satellite-transcript-probe.yml`
- Mocked tests: `tests/test_transcript_adapter.py`, `tests/test_transcript_probe.py`
