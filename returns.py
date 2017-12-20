"""Tools for calculating returns"""

import os
from multiprocessing import Pool
from functools import partial, reduce
from pandas import read_csv, to_datetime

# Merge objects
def merge(dct1, dct2):
    """Merges two dictionaries"""
    return {**dct1, **dct2}

def rolling_returns_helper(start_date, end_date, group, file_name):
    """Helper function for calculating cumulative returns"""
    group_dict = {}
    ticker = file_name[:-4]

    data_frame = read_csv('./data/' + group + '/' + file_name).set_index('Date')
    df_dates = data_frame.select(lambda date: start_date <= date <= end_date, axis=0)

    close = df_dates['Adj Close']
    last_index = len(close) - 1
    returns = close/close[last_index]
    returns[-1] = 1.0

    group_dict.update({ticker: returns.dropna().to_dict()})
    return group_dict

def daily_returns_helper(start_date, end_date, group, file_name):
    """Helper function for calculating daily returns"""
    group_dict = {}
    ticker = file_name[:-4]
    ticker_df = read_csv('./data/' + group + '/' + file_name, skipinitialspace=True)

    # Change the date format to YYYY-MM-DD
    ticker_df['Date'] = to_datetime(ticker_df['Date']).dt.strftime('%Y-%m-%d')
    ticker_df = ticker_df.set_index('Date')

    # Select the date range desired
    ticker_df_dates = ticker_df.select(lambda date: start_date <= date <= end_date, axis=0)

    if len(ticker_df_dates) > 0:
        close = ticker_df_dates['Close']
        returns = close/close.shift(-1) - 1
        returns[-1] = 0.0
        group_dict.update({ticker: returns.to_dict()})
    return group_dict

def get_returns(group, start_date, end_date, returns_type='daily'):
    """Function that either returns daily or cumulative returns"""
    group = group.lower()

    returns_helper_function = daily_returns_helper
    if returns_type == 'rolling':
        returns_helper_function = rolling_returns_helper

    pool = Pool(processes=24)
    dicts = pool.map(
        partial(returns_helper_function, start_date, end_date, group),
        os.listdir('./data/' + group)
    )
    pool.close()
    print('Processing data for:', group)
    return reduce(merge, dicts)
