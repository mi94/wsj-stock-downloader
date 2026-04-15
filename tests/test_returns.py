import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from wsj_stock_downloader import compute_returns_for_directory, write_returns_outputs


CSV_CONTENT = """Date,Open,High,Low,Close,Volume
01/03/24,100,100,100,100,10
01/04/24,110,110,110,110,10
01/05/24,121,121,121,121,10
"""


class ReturnsTests(unittest.TestCase):
    def test_daily_returns_are_computed_from_sorted_dates(self):
        with TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / "data" / "example"
            data_dir.mkdir(parents=True)
            (data_dir / "AAPL.csv").write_text(CSV_CONTENT)

            frame = compute_returns_for_directory(
                data_dir=data_dir,
                start_date="2024-01-03",
                end_date="2024-01-05",
                returns_type="daily",
            )

            self.assertListEqual(list(frame.columns), ["AAPL"])
            self.assertAlmostEqual(frame.loc["2024-01-03", "AAPL"], 0.0)
            self.assertAlmostEqual(frame.loc["2024-01-04", "AAPL"], 0.10)
            self.assertAlmostEqual(frame.loc["2024-01-05", "AAPL"], 0.10)

    def test_cumulative_returns_start_at_one(self):
        with TemporaryDirectory() as tmp_dir:
            data_dir = Path(tmp_dir) / "data" / "example"
            data_dir.mkdir(parents=True)
            (data_dir / "AAPL.csv").write_text(CSV_CONTENT)

            frame = compute_returns_for_directory(
                data_dir=data_dir,
                start_date="2024-01-03",
                end_date="2024-01-05",
                returns_type="cumulative",
            )

            self.assertAlmostEqual(frame.loc["2024-01-03", "AAPL"], 1.0)
            self.assertAlmostEqual(frame.loc["2024-01-04", "AAPL"], 1.1)
            self.assertAlmostEqual(frame.loc["2024-01-05", "AAPL"], 1.21)

    def test_write_returns_outputs_writes_per_list_and_combined_files(self):
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            first_dir = root / "data" / "growth"
            second_dir = root / "data" / "value"
            first_dir.mkdir(parents=True)
            second_dir.mkdir(parents=True)

            (first_dir / "AAPL.csv").write_text(CSV_CONTENT)
            (second_dir / "MSFT.csv").write_text(CSV_CONTENT)

            written_files = write_returns_outputs(
                data_dir=root / "data",
                returns_dir=root / "returns",
                start_date="2024-01-03",
                end_date="2024-01-05",
                returns_type="daily",
            )

            written_names = sorted(path.name for path in written_files)
            self.assertEqual(written_names, ["all.csv", "growth.csv", "value.csv"])


if __name__ == "__main__":
    unittest.main()
