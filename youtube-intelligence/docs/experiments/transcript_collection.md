# Transcript Collection — Design and Experiment

**Current implementation:** The yt-dlp captions-only adapter and bounded satellite probe are merged into main. The first live run (GitHub Actions run 43466201180) was blocked by YouTube with a sign-in/bot-verification challenge. The separate youtube-transcript-api diagnostic is also merged into main and its live run (43468626904) was blocked with an access-challenge/rate-limit result. Both workflows handled the blocks safely and uploaded only sanitized reports. Neither approach retrieved transcript text. Manual browser copy/paste with private persistence is now the next practical path; further extractor tests are paused.

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


## Live experiment result — 2026-11-13

The first yt-dlp run used GitHub-hosted Ubuntu 24.04 (Azure westus3) and yt-dlp 2026.10.26. YouTube returned: Sign in to confirm you’re not a bot. No transcript segments were returned, no retry was attempted, and no raw transcript was uploaded. This establishes that this particular hosted-runner request was challenged; it does not establish that all videos or networks are blocked.

## Separate provider diagnostic

A second manual workflow, Transcript provider diagnostic (separate), uses the open-source youtube-transcript-api package independently against one selected sample. It is not called by the yt-dlp adapter or probe and never runs automatically after a block.

- Workflow: .github/workflows/transcript-provider-diagnostic.yml
- Adapter: src/yti/transcript_api_adapter.py
- Runner: src/yti/transcript_api_diagnostic.py
- Optional install: pip install -e .[transcript-diagnostic]
- The workflow defaults to the same Norsat video and permits the Astrum sample as a separate one-video choice.
- It uploads only sanitized metadata/status; transcript text is not persisted.
- No browser cookies, account sessions, proxies, CAPTCHA workarounds or automatic retry/fallback.
- A block from both providers would be evidence about this runner, not proof that every network is blocked.

The Norsat sample was tested once with each independent provider approach. Both were blocked from GitHub-hosted runners. Do not repeat these tests or expand to the second sample now. Use a manual browser transcript paste for the first end-to-end persistence and analysis experiment.

## Live provider comparison result — 2026-11-13

The separate `youtube-transcript-api` diagnostic was run against the same Norsat webinar sample (video ID `efjBiVN_N3M`). It completed safely but returned `blocked` with detail code `ACCESS_CHALLENGE_OR_RATE_LIMIT`, zero segments and no transcript text persisted. The diagnostic uploaded only a sanitized report. Together with the earlier yt-dlp result (YouTube sign-in/bot challenge), this indicates that GitHub-hosted runner access is currently unsuitable for our first transcript test. It does not establish that all networks or hosted transcript APIs are blocked.

Decision: pause further extractor/provider experiments. Use a manual browser transcript paste as the next input path and store it privately. Evaluate hosted providers separately only when there is a clear reason and cost/security review.
