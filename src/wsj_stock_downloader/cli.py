"""Command-line interface for the downloader."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .workflow import run_pipeline

DEFAULT_START_DATE = "2000-01-01"
DEFAULT_END_DATE = date.today().strftime("%Y-%m-%d")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download WSJ historical data and compute returns."
    )
    parser.add_argument(
        "--tickers-dir",
        type=Path,
        default=Path("tickers"),
        help="Directory containing line-delimited ticker list files.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Directory where raw CSV downloads are stored.",
    )
    parser.add_argument(
        "--returns-dir",
        type=Path,
        default=Path("returns"),
        help="Directory where computed returns CSVs are written.",
    )
    parser.add_argument(
        "--start-date",
        default=DEFAULT_START_DATE,
        help="Start date for returns calculation (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        default=DEFAULT_END_DATE,
        help="End date for returns calculation (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--returns-type",
        default="daily",
        choices=["daily", "cumulative"],
        help="Type of returns to compute.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Maximum concurrent download workers.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing data and returns directories before running.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_pipeline(
        tickers_dir=args.tickers_dir,
        data_dir=args.data_dir,
        returns_dir=args.returns_dir,
        start_date=args.start_date,
        end_date=args.end_date,
        returns_type=args.returns_type,
        workers=args.workers,
        clean=args.clean,
    )

    print(
        "Completed run:"
        f" downloaded={result.downloaded_count}"
        f" failed={result.failed_downloads}"
        f" return_files={result.return_files_written}"
    )

    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"  - {error}")

    return 0 if not result.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
