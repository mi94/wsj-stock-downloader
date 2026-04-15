# wsj-stock-downloader

Small Python library and CLI for downloading WSJ historical CSVs and computing returns.

## Current status

The WSJ download endpoint is no longer reliably scriptable because it can return bot-check responses instead of CSV data. This repository now treats the downloader as a thin, replaceable client and keeps the returns-processing code usable as a standalone library.

Example URL shape:

`https://www.wsj.com/market-data/quotes/AAPL/historical-prices/download?num_rows=100000000000000&range_days=100000000000000&startDate=01/01/1970&endDate=01/01/2040`

## Quick start

```bash
git clone git@github.com:mi94/wsj-stock-downloader.git
cd wsj-stock-downloader
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

Create one or more line-delimited ticker-list files inside `tickers/`. The file name becomes the output group name.

Example:

```text
# tickers/example.txt
AAPL
MSFT
index/SPX
```

Run the CLI:

```bash
wsj-stock-downloader --start-date 2010-01-01 --end-date 2023-12-31
```

If the installed script is not on your shell `PATH`, use:

```bash
python -m wsj_stock_downloader.cli --start-date 2010-01-01 --end-date 2023-12-31
```

By default the tool:

- reads ticker lists from `tickers/`
- writes raw CSVs to `data/`
- writes returns CSVs to `returns/`
- leaves existing directories in place unless `--clean` is provided

## Library usage

```python
from pathlib import Path

from wsj_stock_downloader import run_pipeline

result = run_pipeline(
    tickers_dir=Path("tickers"),
    data_dir=Path("data"),
    returns_dir=Path("returns"),
    start_date="2010-01-01",
    end_date="2023-12-31",
    returns_type="daily",
    workers=8,
    clean=False,
)

print(result)
```

If you already have CSV files on disk and only want returns processing:

```python
from pathlib import Path

from wsj_stock_downloader import compute_returns_for_directory

frame = compute_returns_for_directory(
    data_dir=Path("data/example"),
    start_date="2010-01-01",
    end_date="2023-12-31",
    returns_type="cumulative",
)
```

## Notes

- Ticker list files are just organizational buckets. There is no portfolio weighting or aggregation logic per list.
- Symbols that include `/` are stored with `__` in local filenames to avoid collisions and nested path issues.
- `--returns-type daily` computes close-to-close percentage change.
- `--returns-type cumulative` computes price growth relative to the first value in the selected date range.
