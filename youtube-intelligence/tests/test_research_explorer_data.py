import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]  # Repository root for public research fixtures
RUN_INDEX = REPO_ROOT / "research-runs" / "index.json"
EXPLORER_PAGE = REPO_ROOT / "research.html"


def test_research_run_registry_points_to_valid_run_files():
    registry = json.loads(RUN_INDEX.read_text(encoding="utf-8"))
    assert registry["schema_version"] == "1.0"
    assert registry["runs"]

    for run_ref in registry["runs"]:
        run_path = (REPO_ROOT / run_ref["path"].removeprefix("./")).resolve()
        assert run_path.is_file()
        run = json.loads(run_path.read_text(encoding="utf-8"))
        assert run["run_id"] == run_ref["run_id"]
        assert run["unique_videos"] == run_ref["unique_videos"]


def test_satellite_run_preserves_query_positions_and_deduplication():
    registry = json.loads(RUN_INDEX.read_text(encoding="utf-8"))
    run_path = REPO_ROOT / registry["runs"][0]["path"].removeprefix("./")
    run = json.loads(run_path.read_text(encoding="utf-8"))

    video_ids = [video["id"] for video in run["videos"]]
    assert len(video_ids) == len(set(video_ids)) == 47
    assert len(run["queries"]) == 10
    assert [query["idea_id"] for query in run["queries"]] == [f"sat-{i:02d}" for i in range(1, 11)]
    assert sum(len(query["results"]) for query in run["queries"]) == 50

    known_ids = set(video_ids)
    for query in run["queries"]:
        assert len(query["results"]) == 5
        assert [item["rank"] for item in query["results"]] == [1, 2, 3, 4, 5]
        assert all(item["id"] in known_ids for item in query["results"])

    repeated = {
        item["id"]
        for query in run["queries"]
        for item in query["results"]
    }
    assert len(repeated) < 50
    assert run["minimum_view_filter"] is None
    assert run["transcripts"] == "not collected"
    assert run["analysis"] == "not started"


def test_explorer_has_direct_link_and_opt_in_player_placeholders():
    page = EXPLORER_PAGE.read_text(encoding="utf-8")
    assert "research-runs/index.json" in page
    assert "youtube-nocookie.com/embed/" in page
    assert "Open on YouTube" in page
    assert "Paste the transcript copied from YouTube." in page
    assert "Save transcript to Cloudflare" in page
    assert "Retrieve saved transcript" in page
    assert "Not analysed yet" in page
