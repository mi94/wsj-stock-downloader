"""Top-level workflow orchestration."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .downloader import download_ticker_lists
from .returns import write_returns_outputs
from .tickers import load_ticker_lists


@dataclass(frozen=True)
class RunResult:
    downloaded_count: int
    failed_downloads: int
    return_files_written: int
    errors: list[str]


def _reset_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def run_pipeline(
    tickers_dir: Path,
    data_dir: Path,
    returns_dir: Path,
    start_date: str,
    end_date: str,
    returns_type: str = "daily",
    workers: int = 8,
    clean: bool = False,
) -> RunResult:
    if clean:
        _reset_directory(data_dir)
        _reset_directory(returns_dir)
    else:
        data_dir.mkdir(parents=True, exist_ok=True)
        returns_dir.mkdir(parents=True, exist_ok=True)

    ticker_lists = load_ticker_lists(tickers_dir)
    download_results = download_ticker_lists(ticker_lists, data_dir, workers=workers)
    written_files = write_returns_outputs(
        data_dir=data_dir,
        returns_dir=returns_dir,
        start_date=start_date,
        end_date=end_date,
        returns_type=returns_type,
    )

    errors = [
        f"{result.task.symbol}: {result.error}"
        for result in download_results
        if not result.success
    ]

    return RunResult(
        downloaded_count=sum(1 for result in download_results if result.success),
        failed_downloads=sum(1 for result in download_results if not result.success),
        return_files_written=len(written_files),
        errors=errors,
    )
