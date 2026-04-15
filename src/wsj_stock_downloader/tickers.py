"""Ticker list discovery helpers."""

from __future__ import annotations

from pathlib import Path


def load_ticker_lists(tickers_dir: Path) -> dict[str, list[str]]:
    ticker_lists: dict[str, list[str]] = {}
    if not tickers_dir.exists():
        raise FileNotFoundError(f"Ticker directory does not exist: {tickers_dir}")

    for ticker_file in sorted(tickers_dir.glob("*.txt")):
        symbols = [
            line.strip()
            for line in ticker_file.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if symbols:
            ticker_lists[ticker_file.stem] = symbols

    return ticker_lists
