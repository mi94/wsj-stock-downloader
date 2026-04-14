"""WSJ historical data downloader using multiprocessing"""

import os
import shutil
import argparse
from datetime import date
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from multiprocessing import Pool
from sys import stderr
from pandas import DataFrame, concat

from returns import get_returns

DEFAULT_START_DATE = '2000-01-01'
DEFAULT_END_DATE = date.today().strftime('%Y-%m-%d')

def parse_args():
    parser = argparse.ArgumentParser(description='Download WSJ historical data and compute returns.')
    parser.add_argument('--start-date', default=DEFAULT_START_DATE,
                        help='Start date for returns calculation (YYYY-MM-DD). Default: %(default)s')
    parser.add_argument('--end-date', default=DEFAULT_END_DATE,
                        help='End date for returns calculation (YYYY-MM-DD). Default: today')
    parser.add_argument('--returns-type', default='daily', choices=['daily', 'cumulative'],
                        help='daily: day-over-day %% change. cumulative: growth from start date. Default: daily')
    return parser.parse_args()

def clean_directory():
    """Remove and recreate the intended destination directory."""
    if os.path.exists('data'):
        shutil.rmtree('data')
    os.makedirs('data')

    if os.path.exists('returns'):
        shutil.rmtree('returns')
    os.makedirs('returns')

def get_urls_and_paths():
    """Go through all tickers and store their GET URLs and destination directories."""
    # Array to store tuples in (url, path) format.
    urls_and_paths = []

    for file_name in os.listdir('tickers'):
        # Sanity check. Only use text files.
        if file_name.endswith('.txt'):
            # Each txt file defines a named ticker list; create a matching data folder.
            ticker_list = os.path.splitext(file_name)[0]
            os.makedirs('data/' + ticker_list)

            with open('tickers/' + file_name) as input_file:
                for line in input_file.read().splitlines():
                    urls_and_paths.append((
                        'https://www.wsj.com/market-data/quotes/' + line + '/historical-prices/download?num_rows=100000000000000&range_days=100000000000000&startDate=01/01/1970&endDate=01/01/2040',
                        'data/' + ticker_list + '/' + line.split('/')[-1] + '.csv'
                    ))

    return urls_and_paths

def retrieve(url_and_path):
    """Fetch and save data. Skip on HTTP or connection errors."""
    try:
        urlretrieve(url_and_path[0], url_and_path[1])
    except (HTTPError, URLError):
        pass

# Retrieve all data via multiprocessing, then compute returns.
if __name__ == '__main__':
    args = parse_args()
    print(f'Date range: {args.start_date} to {args.end_date}, returns type: {args.returns_type}')

    clean_directory()
    urls_and_paths = get_urls_and_paths()
    total_count = len(urls_and_paths)
    with Pool(processes=24) as p:
        for i, _ in enumerate(p.imap(retrieve, urls_and_paths), 1):
            stderr.write('\rDownloading {0}%'.format(int(100*i/total_count)))
    print('\r')

    returns = []
    for folder_name in os.listdir('data'):
        if folder_name[0] == '.':
            continue
        df_daily = DataFrame.from_dict(get_returns(folder_name, args.start_date, args.end_date, args.returns_type))
        if not df_daily.empty:
            returns.append(df_daily)
            df_daily.fillna(value=0).to_csv('returns/' + folder_name + '.csv', index_label='Date')

    if returns:
        concat(returns, axis=1).fillna(value=0).to_csv('returns/all.csv', index_label='Date')
