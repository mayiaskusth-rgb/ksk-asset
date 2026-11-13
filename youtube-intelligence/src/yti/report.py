"""Human-readable report generation."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_report(rows: list[dict[str, Any]]) -> str:
    scored = [row for row in rows if row.get("outlier_ratio") is not None]
    lines = [
        "# YouTube Outlier Research — Scoring Results",
        "",
        f"Videos analysed: **{len(rows)}**",
        f"Videos with valid scores: **{len(scored)}**",
        "",
        "> Scores compare a video's observed views with a supplied creator-relative",
        "> median baseline. They do not establish why a video performed well.",
        "",
        "| Video | Channel | Format | Views | Baseline median | Ratio | Band |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        ratio = row.get("outlier_ratio")
        ratio_text = f'{ratio:.2f}x' if isinstance(ratio, (int, float)) else "—"
        lines.append(
            "| {title} | {channel} | {format} | {views} | {baseline} | {ratio} | {band} |".format(
                title=str(row.get("title", row.get("video_id", "Untitled"))).replace("|", "\\|"),
                channel=str(row.get("channel_name", "Unknown")).replace("|", "\\|"),
                format=row.get("format", "unknown"),
                views=row.get("views", "—"),
                baseline=row.get("creator_baseline_median_views", "—"),
                ratio=ratio_text,
                band=row.get("outlier_band", "unscored"),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation cautions",
            "",
            "- Compare Shorts and long-form videos separately.",
            "- Baseline sample size and eligibility must be checked.",
            "- Upload age, topic timing, creator reach and external promotion can confound comparisons.",
            "- An outlier is a candidate for qualitative analysis, not proof of a repeatable formula.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(rows: list[dict[str, Any]], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_report(rows), encoding="utf-8")
