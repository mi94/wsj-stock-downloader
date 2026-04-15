"""Return calculation utilities."""

from __future__ import annotations

from pathlib import Path

from pandas import DataFrame, Series, concat, read_csv, to_datetime


def _load_history(csv_path: Path) -> DataFrame:
    frame = read_csv(csv_path, skipinitialspace=True)
    if "Date" not in frame.columns or "Close" not in frame.columns:
        raise ValueError(f"Missing expected Date/Close columns in {csv_path}")

    frame["Date"] = to_datetime(frame["Date"], format="%m/%d/%y")
    frame = frame.sort_values("Date")
    frame["Date"] = frame["Date"].dt.strftime("%Y-%m-%d")
    return frame.set_index("Date")


def _daily_returns(close: Series) -> Series:
    returns = close / close.shift(1) - 1
    returns.iloc[0] = 0.0
    return returns


def _cumulative_returns(close: Series) -> Series:
    returns = close / close.iloc[0]
    returns.iloc[0] = 1.0
    return returns


def compute_returns_frame(
    csv_path: Path,
    start_date: str,
    end_date: str,
    returns_type: str = "daily",
) -> Series:
    history = _load_history(csv_path)
    filtered = history.loc[(history.index >= start_date) & (history.index <= end_date)]
    if filtered.empty:
        return Series(dtype="float64")

    close = filtered["Close"]
    if returns_type == "cumulative":
        return _cumulative_returns(close)
    return _daily_returns(close)


def compute_returns_for_directory(
    data_dir: Path,
    start_date: str,
    end_date: str,
    returns_type: str = "daily",
) -> DataFrame:
    series_by_symbol: dict[str, Series] = {}
    for csv_path in sorted(data_dir.glob("*.csv")):
        symbol = csv_path.stem
        returns = compute_returns_frame(csv_path, start_date, end_date, returns_type)
        if not returns.empty:
            series_by_symbol[symbol] = returns

    if not series_by_symbol:
        return DataFrame()

    return DataFrame(series_by_symbol)


def write_returns_outputs(
    data_dir: Path,
    returns_dir: Path,
    start_date: str,
    end_date: str,
    returns_type: str = "daily",
) -> list[Path]:
    returns_dir.mkdir(parents=True, exist_ok=True)

    list_frames: list[DataFrame] = []
    written_files: list[Path] = []
    for ticker_list_dir in sorted(path for path in data_dir.iterdir() if path.is_dir()):
        frame = compute_returns_for_directory(
            ticker_list_dir,
            start_date=start_date,
            end_date=end_date,
            returns_type=returns_type,
        )
        if frame.empty:
            continue

        list_frames.append(frame)
        output_path = returns_dir / f"{ticker_list_dir.name}.csv"
        frame.fillna(0).to_csv(output_path, index_label="Date")
        written_files.append(output_path)

    if list_frames:
        output_path = returns_dir / "all.csv"
        concat(list_frames, axis=1).fillna(0).to_csv(output_path, index_label="Date")
        written_files.append(output_path)

    return written_files
