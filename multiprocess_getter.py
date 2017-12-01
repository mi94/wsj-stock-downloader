"""WSJ historical data downloader using multiprocessing"""

import os
import shutil
from urllib.request import urlretrieve
from urllib.error import HTTPError
from multiprocessing import Pool
from sys import stderr
from pandas import DataFrame, concat

from returns import get_returns

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
            # Create a folder for each group (each txt file is a group)
            group = os.path.splitext(file_name)[0]

            # Create the folder for storing stock price data.
            os.makedirs('data/' + group)

            # Open the file.
            input_file = open('tickers/' + file_name)

            # For each line (stock), create the GET URL and store the save location.
            for line in input_file.read().splitlines():
                urls_and_paths.append((
                    'http://quotes.wsj.com/' + line + '/historical-prices/download?num_rows=100000000000000&range_days=100000000000000&startDate=01/01/1970&endDate=01/01/2040',
                    'data/' + group + '/' + line.split('/')[-1] + '.csv'
                ))

    return urls_and_paths

def retrieve(url_and_path):
    """Fetch and save data. Ignore with response of 404."""
    try:
        urlretrieve(url_and_path[0], url_and_path[1])
    except HTTPError:
        pass

# Retrieve all data via threading.
if __name__ == '__main__':
    clean_directory()
    urls_and_paths = get_urls_and_paths()
    total_count = len(urls_and_paths)
    with Pool(processes=24) as p:
        for i, _ in enumerate(p.imap(retrieve, urls_and_paths), 1):
            stderr.write('\rDownloading {0}%'.format(int(100*i/total_count)))
    p.close()
    print('\r')

    returns = []
    for folder_name in os.listdir('data'):
        if folder_name[0] == '.':
            continue
        df_daily = DataFrame.from_dict(get_returns(folder_name, '2000-01-01', '2016-12-11'))
        returns.append(df_daily)
        df_daily.fillna(value=0).to_csv('returns/' + folder_name + '.csv')
    concat(returns, axis=1).fillna(value=0).to_csv('returns/all.csv')
