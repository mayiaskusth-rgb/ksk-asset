import json
import subprocess
from pathlib import Path

import pytest

from yti.providers.yt_dlp_probe import run_probe


def write_ideas(path: Path):
    path.write_text(json.dumps([
        {"idea_id": "sat-01", "search_queries": ["query one", "ignored second query"]},
        {"idea_id": "sat-02", "search_queries": ["query two", "ignored alternative"]},
    ]), encoding="utf-8")


def completed(payload, returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=["yt-dlp"], returncode=returncode,
        stdout=json.dumps(payload), stderr=stderr
    )


def test_runs_sequentially_first_query_only_and_deduplicates(tmp_path):
    ideas = tmp_path / "ideas.json"
    write_ideas(ideas)
    calls, sleeps = [], []

    def fake_runner(command, **kwargs):
        calls.append((command, kwargs))
        return completed({"entries": [
            {"id": "same-video", "title": "Example", "view_count": 100}
        ]})

    result = run_probe(
        ideas, tmp_path / "out", runner=fake_runner,
        sleeper=sleeps.append, clock=lambda: "2026-11-13T10:00:00+00:00",
    )
    assert len(calls) == 2
    assert sleeps == [10.0]
    assert result["request_count"] == 2
    assert result["unique_video_count"] == 1
    assert [item["query"] for item in result["videos"]] == ["query one"]
    assert all("--cookies" not in arg for arg in calls[0][0])
    assert "--proxy" not in calls[0][0]
    assert calls[0][0][-1] == "ytsearch5:query one"
    assert calls[0][0][calls[0][0].index("--retries") + 1] == "0"


def test_access_block_stops_entire_run_without_retry(tmp_path):
    ideas = tmp_path / "ideas.json"
    write_ideas(ideas)
    calls = []

    def fake_runner(command, **kwargs):
        calls.append(command)
        return completed({}, returncode=1, stderr="ERROR: HTTP Error 429: Too Many Requests")

    result = run_probe(ideas, tmp_path / "out", runner=fake_runner, sleeper=lambda _: None)
    assert len(calls) == 1
    assert result["request_count"] == 1
    assert result["stopped_reason"].startswith("YouTube access-denial")
    assert result["query_log"][0]["status"] == "access_blocked"


def test_verification_challenge_stops_run(tmp_path):
    ideas = tmp_path / "ideas.json"
    write_ideas(ideas)

    def fake_runner(command, **kwargs):
        return completed({}, returncode=1, stderr="Sign in to confirm you're not a bot")

    result = run_probe(ideas, tmp_path / "out", runner=fake_runner, sleeper=lambda _: None)
    assert result["request_count"] == 1
    assert result["stopped_reason"] is not None


def test_successful_query_is_cached_across_runs(tmp_path):
    ideas = tmp_path / "ideas.json"
    write_ideas(ideas)
    calls = []

    def fake_runner(command, **kwargs):
        calls.append(command)
        return completed({"entries": [{"id": "video-1", "title": "Example"}]})

    run_probe(ideas, tmp_path / "out", runner=fake_runner, sleeper=lambda _: None)
    result = run_probe(ideas, tmp_path / "out", runner=fake_runner, sleeper=lambda _: None)
    assert len(calls) == 2
    assert result["request_count"] == 0
    assert result["query_log"][0]["status"] == "cached"


def test_rejects_aggressive_settings(tmp_path):
    ideas = tmp_path / "ideas.json"
    write_ideas(ideas)
    with pytest.raises(ValueError, match="fixed at five"):
        run_probe(ideas, tmp_path / "out", max_results=25, runner=lambda *a, **k: None)
    with pytest.raises(ValueError, match="at least 5"):
        run_probe(ideas, tmp_path / "out", pause_seconds=1, runner=lambda *a, **k: None)
