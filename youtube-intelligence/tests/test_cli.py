import csv

from yti.cli import main


def test_score_cli_writes_csv(tmp_path, monkeypatch):
    source = tmp_path / "videos.json"
    source.write_text(
        '[{"video_id":"x","views":500,"creator_baseline_median_views":100,"baseline_sample_size":8}]',
        encoding="utf-8",
    )
    output = tmp_path / "out.csv"
    monkeypatch.setattr(
        "sys.argv",
        ["yti", "score", "--input", str(source), "--output", str(output)],
    )

    main()

    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["outlier_ratio"] == "5.0"
    assert rows[0]["outlier_band"] == "strong"
