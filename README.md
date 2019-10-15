# wsj-stock-downloader

## Basic Information

This is a Python 3 script that downloads all available historical data for a given list of tickers and then processes returns for a desired date set.

## Usage

### Clone the repository

`git clone git@github.com:mi94/wsj-stock-downloader.git`

### Create list of tickers to download data for
In the `tickers` folder, add as many text files as desired to split your stocks into groups (e.g. separate portfolios). Each text file will have a line-delimited list of tickers. Make sure to take the ticker AND any prefixes (examples shown with indexes and foreign indexes) from the URL on WSJ (e.g. http://quotes.wsj.com/index/SPX would be `index/SPX`).

### Running the program
Navigate to the directory and run `python multiprocess_getter.py`.

### Data directory
A `data` directory will be created and will be populated with raw data for each ticker. Each group will have its own folder.

### Returns directory
A `returns` directory will be created and will be populated with each group's returns. Each group will have its own CSV file, where each column was a ticker in the group `.txt` file. There will also be a CSV of all of the individual CSV's merged into one, named `all.csv`.
