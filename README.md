# NSEAPI

NSEAPI is a Python package designed for seamless interaction with the National Stock Exchange (NSE) of India. It provides functions to fetch market status, download equity bhavcopy data, and other utilities related to NSE data.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Fetching Market Status](#fetching-market-status)
  - [Downloading Bhavcopy](#downloading-bhavcopy)
  - [Helper Functions](#helper-functions)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

Ensure that you have Python 3.8 or higher installed on your system. Then, install the package using pip:

```bash
pip install nseapi
```

## Usage

### Fetching Market Status

To fetch the current market status, use the `get_market_status` function:

```python
from nseapi.market import get_market_status

market_status = get_market_status()
print("Market Status:", market_status)
```

### Downloading Bhavcopy

To download the equity bhavcopy for a specific date, use the `download_bhavcopy` function:

```python
from nseapi.market import download_bhavcopy
from datetime import datetime
import os

# Set the date for the bhavcopy
date = datetime(2023, 12, 26)

# Download the bhavcopy
download_bhavcopy(date, download_folder='downloads')

# Verify the file download
file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
file_path = os.path.join('downloads', file_name)
print(f"Bhavcopy file downloaded at: {file_path}")
```

### Helper Functions

The package also provides helper functions for specific tasks. For instance, `fetch_data_from_nse` allows you to retrieve data from a specific NSE API endpoint:

```python
from nseapi.helpers import fetch_data_from_nse

endpoint = "marketStatus"
data = fetch_data_from_nse(endpoint)
print("Data from NSE:", data)
```

## Project Structure

The project is organized as follows:

```
nseapi/
├── src/
│   ├── __init__.py
│   ├── market.py        # Functions to fetch market status and download bhavcopy
│   └── helpers.py       # Helper functions for internal use
├── tests/
│   ├── __init__.py
│   └── test_market.py   # Unit tests for market functions
├── setup.py             # Package setup configuration
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
