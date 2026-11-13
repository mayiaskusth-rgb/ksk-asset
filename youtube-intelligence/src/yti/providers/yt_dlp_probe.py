"""Conservative, unauthenticated YouTube search probe using yt-dlp.

This is an experimental adapter, not a promise of policy approval or uptime.
It makes sequential public search requests, caches successful queries, and
stops the entire run when access-denial or verification signals appear.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

BLOCK_PATTERNS = (
    r"HTTP Error 403", r"HTTP Error 429", r"too many requests",
    r"sign in to confirm", r"confirm you.re not a bot", r"unusual traffic",
    r"captcha", r"verify (?:that )?you are human", r"temporarily blocked",
    r"access denied",
)
BLOCK_RE = re.compile("|".join(BLOCK_PATTERNS), re.IGNORECASE)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_video(entry: dict[str, Any], query: str, idea_id: str, retrieved_at: str) -> dict[str, Any]:
    video_id = entry.get("id")
    if not video_id:
        return {}
    return {
        "video_id": str(video_id),
        "url": entry.get("url") or f"https://www.youtube.com/watch?v={video_id}",
        "title": entry.get("title"),
        "channel_id": entry.get("channel_id") or entry.get("uploader_id"),
        "channel_title": entry.get("channel") or entry.get("uploader"),
        "duration_seconds": entry.get("duration"),
        "view_count": entry.get("view_count"),
        "upload_date": entry.get("upload_date"),
        "idea_id": idea_id,
        "query": query,
        "source": "yt-dlp/ytsearch",
        "retrieved_at": retrieved_at,
    }


def _cache_path(cache_dir: Path, query: str) -> Path:
    digest = hashlib.sha256(query.strip().casefold().encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}.json"


def run_probe(
    ideas_path: str | Path,
    output_dir: str | Path,
    *,
    max_results: int = 5,
    pause_seconds: float = 10.0,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    sleeper: Callable[[float], None] = time.sleep,
    clock: Callable[[], str] = _utc_now,
    executable: str = "yt-dlp",
) -> dict[str, Any]:
    """Run at most one (first) search query per idea, sequentially."""
    if max_results != 5:
        raise ValueError("The initial probe is deliberately fixed at five results per query.")
    if pause_seconds < 5:
        raise ValueError("pause_seconds must be at least 5 seconds.")
    binary = shutil.which(executable)
    if binary is None and runner is subprocess.run:
        raise FileNotFoundError(
            "yt-dlp was not found. Install it locally with: python -m pip install yt-dlp"
        )

    with Path(ideas_path).open("r", encoding="utf-8") as handle:
        ideas = json.load(handle)
    if not isinstance(ideas, list) or not ideas:
        raise ValueError("Ideas input must be a non-empty JSON list.")

    destination = Path(output_dir)
    cache_dir = destination / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    run_started = clock()
    results: list[dict[str, Any]] = []
    query_log: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    stopped_reason: str | None = None
    request_count = 0

    for idea in ideas:
        idea_id = str(idea.get("idea_id", "unknown"))
        queries = idea.get("search_queries")
        if not isinstance(queries, list) or not queries or not isinstance(queries[0], str):
            query_log.append({"idea_id": idea_id, "status": "skipped", "reason": "missing first search query"})
            continue
        query = queries[0].strip()
        if not query:
            query_log.append({"idea_id": idea_id, "status": "skipped", "reason": "blank first search query"})
            continue

        cached_path = _cache_path(cache_dir, query)
        if cached_path.exists():
            with cached_path.open("r", encoding="utf-8") as handle:
                cached = json.load(handle).get("videos", [])
            query_log.append({"idea_id": idea_id, "query": query, "status": "cached", "video_count": len(cached)})
            for video in cached:
                if video["video_id"] not in seen_ids:
                    seen_ids.add(video["video_id"])
                    results.append(video)
            continue

        if request_count:
            sleeper(pause_seconds)

        command = [
            binary or executable, "--ignore-config", "--no-warnings", "--no-progress",
            "--no-cache-dir", "--skip-download", "--flat-playlist", "--dump-single-json",
            "--playlist-end", str(max_results), "--socket-timeout", "20",
            "--retries", "0", "--extractor-retries", "0", "--fragment-retries", "0",
            "--sleep-requests", "2", "--sleep-interval", "3", "--max-sleep-interval", "5",
            f"ytsearch{max_results}:{query}",
        ]
        request_count += 1
        try:
            completed = runner(command, capture_output=True, text=True, timeout=120, check=False)
        except subprocess.TimeoutExpired:
            query_log.append({"idea_id": idea_id, "query": query, "status": "timeout"})
            stopped_reason = "request timeout; run paused without retry"
            break

        diagnostic = (completed.stderr or "")[-4000:]
        if BLOCK_RE.search(diagnostic):
            query_log.append({
                "idea_id": idea_id, "query": query, "status": "access_blocked",
                "diagnostic": diagnostic,
            })
            stopped_reason = "YouTube access-denial or verification signal; no further requests made"
            break
        if completed.returncode != 0:
            query_log.append({
                "idea_id": idea_id, "query": query, "status": "failed",
                "return_code": completed.returncode, "diagnostic": diagnostic,
            })
            stopped_reason = "non-zero extractor exit; run paused without retry"
            break
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            query_log.append({"idea_id": idea_id, "query": query, "status": "invalid_json"})
            stopped_reason = "extractor returned unparseable output; run paused"
            break

        entries = payload.get("entries") or []
        retrieved_at = clock()
        videos = [
            item for item in (
                _safe_video(entry, query, idea_id, retrieved_at)
                for entry in entries if isinstance(entry, dict)
            ) if item
        ]
        with cached_path.open("w", encoding="utf-8") as handle:
            json.dump({"query": query, "videos": videos}, handle, indent=2, ensure_ascii=False)
        query_log.append({
            "idea_id": idea_id, "query": query, "status": "retrieved",
            "video_count": len(videos), "retrieved_at": retrieved_at,
        })
        for video in videos:
            if video["video_id"] not in seen_ids:
                seen_ids.add(video["video_id"])
                results.append(video)

    manifest = {
        "experiment": "satellite-no-api-search-probe",
        "source": "yt-dlp public ytsearch extractor",
        "started_at": run_started,
        "finished_at": clock(),
        "request_count": request_count,
        "max_results_per_query": max_results,
        "pause_seconds_between_uncached_queries": pause_seconds,
        "authentication": "none",
        "cookies": "not used",
        "proxy": "not configured",
        "retry_policy": "zero retries; stop on block, challenge, timeout, or extractor error",
        "query_log": query_log,
        "unique_video_count": len(results),
        "videos": results,
        "stopped_reason": stopped_reason,
    }
    destination.mkdir(parents=True, exist_ok=True)
    stamp = run_started.replace(":", "").replace("-", "").replace(".", "")
    output_path = destination / f"satellite_probe_{stamp}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)
    manifest["output_file"] = str(output_path)
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Conservative no-API satellite YouTube search probe")
    parser.add_argument("--ideas", default="data/experiments/satellite_ideas.json")
    parser.add_argument("--output-dir", default="runs/satellite_probe")
    parser.add_argument("--pause-seconds", type=float, default=10.0)
    args = parser.parse_args(argv)
    try:
        result = run_probe(args.ideas, args.output_dir, pause_seconds=args.pause_seconds)
    except (FileNotFoundError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "request_count": result["request_count"],
        "unique_video_count": result["unique_video_count"],
        "stopped_reason": result["stopped_reason"],
        "output_file": result["output_file"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
