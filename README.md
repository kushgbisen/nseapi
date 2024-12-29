# NSEAPI

NSEAPI is a Python package designed for seamless interaction with the National Stock Exchange (NSE) of India. It provides a robust and easy-to-use interface to fetch market data, download historical bhavcopies, retrieve stock quotes, analyze option chains, and more. This package is ideal for developers, traders, and analysts who need programmatic access to NSE data.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Fetching Market Status](#fetching-market-status)
  - [Downloading Bhavcopy](#downloading-bhavcopy)
  - [Fetching Stock Quotes](#fetching-stock-quotes)
  - [Retrieving Option Chain Data](#retrieving-option-chain-data)
  - [Fetching Corporate Actions](#fetching-corporate-actions)
  - [Fetching Corporate Announcements](#fetching-corporate-announcements)
  - [Fetching All Indices](#fetching-all-indices)
  - [Helper Functions](#helper-functions)
  - [Logging](#logging)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

To install the NSEAPI package, ensure that you have Python 3.8 or higher installed on your system. Then, use `pip` to install the package:

```bash
pip install nseapi
```

Alternatively, you can clone the repository and install it locally:

```bash
git clone https://github.com/kushgbisen/nseapi.git
cd nseapi
pip install .
```

## Usage

### Fetching Market Status

The `get_market_status` function retrieves the current market status, including whether the market is open or closed.

```python
from nseapi.market import get_market_status

market_status = get_market_status()
print("Market Status:", market_status)
```

### Downloading Bhavcopy

The `download_bhavcopy` function downloads the equity bhavcopy (a daily report of stock prices) for a specific date. The file is saved in the specified directory.

```python
from nseapi.market import download_bhavcopy
from datetime import datetime
import os

# Set the date for the bhavcopy
date = datetime(2023, 12, 26)

# Download the bhavcopy
download_bhavcopy(date, download_dir='downloads')

# Verify the file download
file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
file_path = os.path.join('downloads', file_name)
print(f"Bhavcopy file downloaded at: {file_path}")
```

### Fetching Stock Quotes

The `get_stock_quote` function fetches the stock quote for a specific symbol, including the current price, open, high, low, close, and volume.

```python
from nseapi.market import get_stock_quote

symbol = "INFY"
quote = get_stock_quote(symbol)
print("Stock Quote:", quote)
```

### Retrieving Option Chain Data

The `get_option_chain` function retrieves the option chain data for a specific stock or index. This includes details about call and put options, strike prices, and open interest.

```python
from nseapi.market import get_option_chain

# For a stock
symbol = "RELIANCE"
option_chain = get_option_chain(symbol)
print("Option Chain for RELIANCE:", option_chain)

# For an index
symbol = "NIFTY"
option_chain = get_option_chain(symbol, is_index=True)
print("Option Chain for NIFTY:", option_chain)
```

### Fetching Corporate Actions

The `get_corporate_actions` function fetches forthcoming corporate actions (e.g., dividends, stock splits) for a specific segment or symbol.

```python
from nseapi.market import get_corporate_actions
from datetime import datetime

# Fetch corporate actions for equities
actions = get_corporate_actions(segment="equities")
print("Corporate Actions:", actions)

# Fetch corporate actions for a specific symbol and date range
from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 12, 31)
actions = get_corporate_actions(segment="equities", symbol="HDFCBANK", from_date=from_date, to_date=to_date)
print("Filtered Corporate Actions:", actions)
```

### Fetching Corporate Announcements

The `get_announcements` function fetches corporate announcements for a specific segment or symbol.

```python
from nseapi.market import get_announcements
from datetime import datetime

# Fetch corporate announcements for equities
announcements = get_announcements(index="equities")
print("Corporate Announcements:", announcements)

# Fetch corporate announcements for a specific symbol and date range
from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 12, 31)
announcements = get_announcements(index="equities", symbol="HDFCBANK", from_date=from_date, to_date=to_date)
print("Filtered Corporate Announcements:", announcements)
```

### Fetching All Indices

The `get_all_indices` function fetches data for all NSE indices, including the last price, change, and percentage change.

```python
from nseapi.market import get_all_indices

indices = get_all_indices()
print("All Indices:", indices)
```

### Helper Functions

The package also provides helper functions for specific tasks. For instance, `fetch_data_from_nse` allows you to retrieve data from a specific NSE API endpoint.

```python
from nseapi.helpers import fetch_data_from_nse

endpoint = "marketStatus"
data = fetch_data_from_nse(endpoint)
print("Data from NSE:", data)
```

### Logging

The package includes built-in logging functionality that tracks API interactions:
- **Debug level:** Records API request attempts.
- **Info level:** Logs successful responses.
- **Error level:** Captures failed requests with details.

Logs are written to `nseapi.log` in the current working directory. Example log output:

```
2024-12-27 06:53:03 - INFO - Successfully fetched data from marketStatus
2024-12-27 06:53:04 - ERROR - Failed to fetch data from invalid_endpoint: 404 Client Error
```

## Project Structure

The project is organized as follows:

```
./
├── .gitignore                # Specifies files and directories to ignore in Git
├── .pre-commit-config.yaml   # Configuration for pre-commit hooks
├── install-hooks.sh*         # Script to install pre-commit hooks (executable)
├── LICENSE                   # License file for the project (MIT License)
├── README.md                 # Project documentation
├── requirements.txt          # Lists project dependencies (currently only `requests`)
├── setup.py                  # Package setup configuration
├── scripts/                  # Directory for scripts
│   └── hooks/                # Directory for Git hooks
│       └── pre-commit*       # Pre-commit hook script (executable)
├── src/                      # Source code directory
│   └── nseapi/               # Main package directory
│       ├── __init__.py       # Package initialization file
│       ├── helpers.py        # Helper functions (e.g., API requests, logging)
│       └── market.py         # Core functionality (e.g., market status, bhavcopy)
└── tests/                    # Unit tests directory
    ├── __init__.py           # Initialization file for tests
    ├── test_helpers.py       # Tests for helper functions
    └── test_market.py        # Tests for market-related functions
```
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
