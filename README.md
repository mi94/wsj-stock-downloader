# wsj-stock-downloader

## Basic Information

This is a Python 3 script that downloads all available historical data for a given list of tickers and then processes returns for a desired date set.

### Current status
The original workflow assumed that the WSJ historical-prices download URL behaved like a plain CSV endpoint for scripted clients. That no longer appears to be true.

As of April 13, 2026:

- Opening a download URL in the browser can still work interactively.
- Direct scripted requests from tools like Python `urllib`, `curl`, and headless Chromium can return a WSJ bot-check or challenge response instead of CSV data.
- Because of that, this repository should currently be treated as a historical snapshot of the old approach rather than a verified working downloader.

Example URL shape:

`https://www.wsj.com/market-data/quotes/AAPL/historical-prices/download?num_rows=100000000000000&range_days=100000000000000&startDate=01/01/1970&endDate=01/01/2040`

## Usage

### Clone the repository

`git clone git@github.com:mi94/wsj-stock-downloader.git`

### Create ticker lists
In the `tickers` folder, add as many text files as desired. Each file is a **ticker list** — a named collection of tickers that will be downloaded and processed together. Each text file contains a line-delimited list of tickers.

Ticker lists are purely an organizational convenience: they control how raw data is grouped into subfolders and how per-list returns CSVs are named. There is no portfolio math applied at the list level — no weighting, no aggregation. If you only want one bucket, one file is fine. If you want to keep indexes, domestic equities, and foreign stocks in separate outputs, use separate files.

Make sure to take the ticker AND any prefixes (examples shown with indexes and foreign indexes) from the URL on WSJ (e.g. http://quotes.wsj.com/index/SPX would be `index/SPX`).

### Running the program
Navigate to the directory and run:

```
python download.py
```

The returns date range defaults to `2000-01-01` through today, and the returns type defaults to `daily`. All three can be overridden:

```
python download.py --start-date 2010-01-01 --end-date 2023-12-31 --returns-type cumulative
```

`--returns-type daily` (default): each value is the day-over-day percentage change.

`--returns-type cumulative`: each value is the price expressed as a multiple of the starting price — i.e. growth from `--start-date`. The oldest date in the range is always 1.0.

### Data directory
A `data` directory will be created and populated with raw data for each ticker, organized into one subfolder per ticker list.

### Returns directory
A `returns` directory will be created and populated with one CSV per ticker list, where each column is a ticker from that list. A combined `all.csv` is also written, merging all ticker lists into one.
