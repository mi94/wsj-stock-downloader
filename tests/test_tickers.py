import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from wsj_stock_downloader import load_ticker_lists


class TickerLoadingTests(unittest.TestCase):
    def test_load_ticker_lists_ignores_comments_and_blank_lines(self):
        with TemporaryDirectory() as tmp_dir:
            tickers_dir = Path(tmp_dir) / "tickers"
            tickers_dir.mkdir()
            (tickers_dir / "example.txt").write_text(
                "# comment\n\nAAPL\nMSFT\nindex/SPX\n"
            )

            ticker_lists = load_ticker_lists(tickers_dir)

            self.assertEqual(
                ticker_lists,
                {"example": ["AAPL", "MSFT", "index/SPX"]},
            )

    def test_load_ticker_lists_requires_existing_directory(self):
        with TemporaryDirectory() as tmp_dir:
            with self.assertRaises(FileNotFoundError):
                load_ticker_lists(Path(tmp_dir) / "missing")


if __name__ == "__main__":
    unittest.main()
