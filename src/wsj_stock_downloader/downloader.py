"""Download planning and execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve


@dataclass(frozen=True)
class DownloadTask:
    ticker_list: str
    symbol: str
    url: str
    destination: Path


@dataclass(frozen=True)
class DownloadResult:
    task: DownloadTask
    success: bool
    error: str | None = None


def build_download_url(symbol: str) -> str:
    return (
        "https://www.wsj.com/market-data/quotes/"
        f"{symbol}/historical-prices/download"
        "?num_rows=100000000000000"
        "&range_days=100000000000000"
        "&startDate=01/01/1970"
        "&endDate=01/01/2040"
    )


def _safe_symbol_filename(symbol: str) -> str:
    return symbol.replace("/", "__")


def plan_downloads(ticker_lists: dict[str, list[str]], data_dir: Path) -> list[DownloadTask]:
    tasks: list[DownloadTask] = []
    for ticker_list, symbols in ticker_lists.items():
        list_dir = data_dir / ticker_list
        list_dir.mkdir(parents=True, exist_ok=True)
        for symbol in symbols:
            tasks.append(
                DownloadTask(
                    ticker_list=ticker_list,
                    symbol=symbol,
                    url=build_download_url(symbol),
                    destination=list_dir / f"{_safe_symbol_filename(symbol)}.csv",
                )
            )
    return tasks


def download_one(task: DownloadTask) -> DownloadResult:
    try:
        urlretrieve(task.url, task.destination)
    except (HTTPError, URLError) as exc:
        return DownloadResult(task=task, success=False, error=str(exc))
    return DownloadResult(task=task, success=True)


def download_all(tasks: list[DownloadTask], workers: int = 8) -> list[DownloadResult]:
    if not tasks:
        return []

    max_workers = max(1, min(workers, len(tasks)))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(download_one, tasks))


def download_ticker_lists(
    ticker_lists: dict[str, list[str]],
    data_dir: Path,
    workers: int = 8,
) -> list[DownloadResult]:
    """Download CSVs for the provided ticker lists into ``data_dir``.

    This is the reusable library-level entry point for callers who want to
    control ticker discovery themselves without running the full pipeline.
    """
    tasks = plan_downloads(ticker_lists, data_dir)
    return download_all(tasks, workers=workers)
