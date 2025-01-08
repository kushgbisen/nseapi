# NSEAPI


NSEAPI is a Python package designed for seamless interaction with the National Stock Exchange (NSE) of India. It provides a robust and easy-to-use interface to fetch market data, download historical bhavcopies, retrieve stock quotes, analyze option chains, and more. This package is ideal for developers, traders, and analysts who need programmatic access to NSE data.

---

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
  - [Fetching Holidays](#fetching-holidays)
  - [Fetching Bulk Deals](#fetching-bulk-deals)
  - [Fetching FII/DII Trading Activity](#fetching-fiidii-trading-activity)
  - [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

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

---

## Usage

### Fetching Market Status

The `get_market_status` function retrieves the current market status, including whether the market is open or closed.

```python
from nseapi import get_market_status

# Fetch market status
market_status = get_market_status()
print("Market Status:", market_status)

```

---

### Downloading Bhavcopy

The `get_bhavcopy` function downloads various types of bhavcopy reports (e.g., equity, delivery, indices, FnO, priceband, PR, CM MII) for a specific date. The file is saved in the specified directory.

```python
from nseapi import get_bhavcopy

from datetime import datetime


# Download equity bhavcopy
date = datetime(2023, 12, 26)
get_bhavcopy("equity", date, download_dir='downloads')

# Download FnO bhavcopy
get_bhavcopy("fno", date, download_dir='downloads')


# Download priceband report
get_bhavcopy("priceband", date, download_dir='downloads')
```

---

### Fetching Stock Quotes

The `get_stock_quote` function fetches the stock quote for a specific symbol, including the current price, open, high, low, close, and volume.


```python
from nseapi import get_stock_quote

symbol = "INFY"
quote = get_stock_quote(symbol)
print("Stock Quote:", quote)
```

---

### Retrieving Option Chain Data

The `get_option_chain` function retrieves the option chain data for a specific stock or index. This includes details about call and put options, strike prices, and open interest.


```python
from nseapi import get_option_chain

# For a stock
symbol = "RELIANCE"
option_chain = get_option_chain(symbol)

print("Option Chain for RELIANCE:", option_chain)

# For an index
symbol = "NIFTY"
option_chain = get_option_chain(symbol, is_index=True)
print("Option Chain for NIFTY:", option_chain)
```


---

### Fetching Corporate Actions

The `get_corporate_actions` function fetches forthcoming corporate actions (e.g., dividends, stock splits) for a specific segment or symbol. You can filter the results by date range.


```python
from nseapi import get_corporate_actions
from datetime import datetime

# Fetch corporate actions for equities
actions = get_corporate_actions(segment="equities")
print("Corporate Actions:", actions)

# Fetch corporate actions for a specific symbol and date range
from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 12, 31)
actions = get_corporate_actions(
    segment="equities",
    symbol="HDFCBANK",

    from_date=from_date,
    to_date=to_date
)
print("Filtered Corporate Actions:", actions)
```


---

### Fetching Corporate Announcements

The `get_announcements` function fetches corporate announcements for a specific segment or symbol. You can filter the results by date range and include only FnO stocks.

```python
from nseapi import get_announcements
from datetime import datetime

# Fetch corporate announcements for equities
announcements = get_announcements(index="equities")
print("Corporate Announcements:", announcements)

# Fetch corporate announcements for a specific symbol and date range

from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 12, 31)
announcements = get_announcements(
    index="equities",
    symbol="HDFCBANK",

    from_date=from_date,
    to_date=to_date
)
print("Filtered Corporate Announcements:", announcements)
```

---


### Fetching All Indices

The `get_all_indices` function fetches data for all NSE indices, including the last price, change, and percentage change.

```python
from nseapi import get_all_indices

indices = get_all_indices()
print("All Indices:", indices)
```

---


### Fetching Holidays


The `get_holidays` function fetches the list of trading or clearing holidays from the NSE. You can specify the type of holiday list to fetch (trading or clearing).

```python

from nseapi import get_holidays

# Fetch trading holidays
trading_holidays = get_holidays(holiday_type="trading")
print("Trading Holidays:", trading_holidays)

# Fetch clearing holidays
clearing_holidays = get_holidays(holiday_type="clearing")
print("Clearing Holidays:", clearing_holidays)

```

---

### Fetching Bulk Deals

The `bulk_deals` function fetches bulk deals data for a specified date range.

```python
from nseapi import bulk_deals
from datetime import datetime

from_date = datetime(2023, 1, 1)

to_date = datetime(2023, 12, 31)
bulk_deals_data = bulk_deals(from_date, to_date)

print("Bulk Deals:", bulk_deals_data)
```

---

### Fetching FII/DII Trading Activity

The `get_fii_dii_data` function fetches trading activity data for Foreign Institutional Investors (FII) and Domestic Institutional Investors (DII).

```python
from nseapi import get_fii_dii_data

# Fetch FII/DII trading activity
fii_dii_data = get_fii_dii_data()
print("FII/DII Trading Activity:", fii_dii_data)
```


---

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

---

## Troubleshooting

### Common Issues

- **API Errors**: Ensure you have a stable internet connection and are not hitting rate limits. If the issue persists, check the NSE website for API status.
- **Invalid Symbols**: Verify that the symbol you’re using is valid and supported by the NSE.

- **File Download Failures**: Ensure the specified download directory exists and is writable.

---

## Project Structure


The project is organized as follows:

```
./
├── .gitignore                # Specifies files and directories to ignore in Git

├── .pre-commit-config.yaml   # Configuration for pre-commit hooks
├── LICENSE                   # License file for the project (MIT License)
├── README.md                 # Project documentation
├── requirements.txt          # Lists project dependencies
├── setup.py                  # Package setup configuration
├── src/                      # Source code directory
│   └── nseapi/               # Main package directory
│       ├── __init__.py       # Package initialization file
└── tests/                    # Unit tests directory
    └── test_nseapi.py        # Tests for market-related functions
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
