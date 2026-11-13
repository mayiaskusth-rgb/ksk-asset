"""Command-line interface for the MVP."""

from __future__ import annotations

import argparse

from yti.io import load_videos, write_csv
from yti.report import write_report
from yti.scoring import score_videos


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yti", description="KSK YouTube Intelligence")
    commands = parser.add_subparsers(dest="command", required=True)

    score = commands.add_parser("score", help="Score videos against supplied creator baselines")
    score.add_argument("--input", required=True, help="Input JSON video records")
    score.add_argument("--output", required=True, help="Output CSV path")
    score.add_argument("--minimum-baseline-sample", type=int, default=5)

    report = commands.add_parser("report", help="Generate Markdown report from scored CSV")
    report.add_argument("--input", required=True, help="Input scored CSV")
    report.add_argument("--output", required=True, help="Output Markdown path")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "score":
        rows = load_videos(args.input)
        scored = score_videos(rows, minimum_baseline_sample=args.minimum_baseline_sample)
        write_csv(scored, args.output)
        print(f"Scored {len(scored)} videos -> {args.output}")
        return

    if args.command == "report":
        import csv
        from pathlib import Path

        with Path(args.input).open("r", newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        # CSV values are strings; parse the ratio for correct report formatting.
        for row in rows:
            value = row.get("outlier_ratio")
            row["outlier_ratio"] = float(value) if value not in (None, "") else None
        write_report(rows, args.output)
        print(f"Report generated -> {args.output}")


if __name__ == "__main__":
    main()
