"""Tools for calculating returns"""

import os
from multiprocessing import Pool
from functools import partial, reduce
from pandas import read_csv, to_datetime

# Merge objects
def merge(dct1, dct2):
    """Merges two dictionaries"""
    return {**dct1, **dct2}

def cumulative_returns_helper(start_date, end_date, ticker_list, file_name):
    """Helper function for calculating cumulative returns.
    Each price is expressed as a multiple of the starting price (oldest date in range = 1.0).
    """
    ticker_list_dict = {}
    ticker = file_name[:-4]

    ticker_df = read_csv('./data/' + ticker_list + '/' + file_name, skipinitialspace=True)

    # Change the date format to YYYY-MM-DD (WSJ exports MM/DD/YY)
    ticker_df['Date'] = to_datetime(ticker_df['Date'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
    ticker_df = ticker_df.set_index('Date')

    df_dates = ticker_df.loc[(ticker_df.index >= start_date) & (ticker_df.index <= end_date)]

    close = df_dates['Close']
    returns = close / close.iloc[-1]
    returns.iloc[-1] = 1.0

    ticker_list_dict.update({ticker: returns.dropna().to_dict()})
    return ticker_list_dict

def daily_returns_helper(start_date, end_date, ticker_list, file_name):
    """Helper function for calculating daily returns.
    Each value is the percentage change from the prior trading day.
    """
    ticker_list_dict = {}
    ticker = file_name[:-4]
    ticker_df = read_csv('./data/' + ticker_list + '/' + file_name, skipinitialspace=True)

    # Change the date format to YYYY-MM-DD (WSJ exports MM/DD/YY)
    ticker_df['Date'] = to_datetime(ticker_df['Date'], format='%m/%d/%y').dt.strftime('%Y-%m-%d')
    ticker_df = ticker_df.set_index('Date')

    # Select the date range desired
    ticker_df_dates = ticker_df.loc[(ticker_df.index >= start_date) & (ticker_df.index <= end_date)]

    if len(ticker_df_dates) > 0:
        close = ticker_df_dates['Close']
        returns = close / close.shift(-1) - 1
        returns.iloc[-1] = 0.0
        ticker_list_dict.update({ticker: returns.to_dict()})
    return ticker_list_dict

def get_returns(ticker_list, start_date, end_date, returns_type='daily'):
    """Compute returns for all CSVs in a ticker list folder.
    returns_type: 'daily' for day-over-day % change, 'cumulative' for growth from start date.
    """
    ticker_list = ticker_list.lower()

    returns_helper_function = daily_returns_helper
    if returns_type == 'cumulative':
        returns_helper_function = cumulative_returns_helper

    files = [f for f in os.listdir('./data/' + ticker_list) if f.endswith('.csv')]
    if not files:
        print('No data files found for:', ticker_list)
        return {}

    with Pool(processes=24) as pool:
        dicts = pool.map(
            partial(returns_helper_function, start_date, end_date, ticker_list),
            files
        )
    print('Processing data for:', ticker_list)
    return reduce(merge, dicts)
