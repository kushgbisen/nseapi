from datetime import datetime, date, timedelta
from pathlib import Path
import requests
import zipfile
import json

import os
import gzip
import shutil
from typing import List, Dict, Literal, Optional, Any, Tuple
from functools import lru_cache
import logging
from time import sleep

# Initialize a session for all requests
session = requests.Session()

session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/118.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=HDFCBANK",
    }
)


# Set up logging

logger = logging.getLogger("NSEIndia")
logger.setLevel(logging.INFO)
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)
if not logger.handlers:
    handler = logging.FileHandler(logs_dir / "nseapi.log")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


# Fetch cookies required for API access
def _fetch_cookies():
    """Fetch and return cookies from NSE website for API authentication.
    
    This internal function makes a request to the NSE option-chain page
    to obtain the necessary session cookies required for subsequent API calls.
    
    Returns:
        requests.cookies.RequestsCookieJar: Session cookies for NSE API access
    """
    # Get cookies from option-chain page as it sets the required cookies for equity APIs
    session.get("https://www.nseindia.com/option-chain")
    return session.cookies


def fetch_data_from_nse(endpoint, params=None, retries=3, delay=2, timeout=10):
    """Fetch data from a given NSE endpoint with retry logic and caching.

    Args:
        endpoint (str): The API endpoint to fetch data from.
        params (dict, optional): Query parameters for the request. Defaults to None.
        retries (int, optional): Number of retry attempts. Defaults to 3.
        delay (int, optional): Delay between retries in seconds. Defaults to 2.
        timeout (int, optional): Timeout for the request in seconds. Defaults to 10.

    Returns:
        dict: JSON response from the API.

    Raises:
        requests.RequestException: If the request fails after all retries.
    """
    base_url = "https://www.nseindia.com/api"
    url = f"{base_url}/{endpoint}"

    for attempt in range(retries):
        try:
            logger.debug(f"Attempt {attempt + 1}: Making request to: {url}")
            
            # Refresh cookies on first attempt or after failure
            if attempt == 0 or attempt > 0:
                _fetch_cookies()
            
            response = session.get(
                url,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()

            logger.info(f"Successfully fetched data from {endpoint}")
            return response.json()
            
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries - 1:
                sleep(delay)
            else:
                logger.error(
                    f"Failed to fetch data from {endpoint} after {retries} attempts: {str(e)}"
                )
                raise


def get_market_status() -> Dict:
    """Fetch the current market status.


    Returns:
        Dict: A dictionary containing the market status.
    """
    endpoint = "marketStatus"
    try:
        return fetch_data_from_nse(endpoint)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch market status: {e}")


def get_bhavcopy(
    bhavcopy_type: Literal[
        "equity", "delivery", "indices", "fno", "priceband", "pr", "cm_mii"
    ],
    date: datetime,
    download_dir: str = None,
) -> Path:
    """Download the specified type of bhavcopy report for the given date.

    Args:

        bhavcopy_type: Type of bhavcopy to download. Options: "equity", "delivery", 
                     "indices", "fno", "priceband", "pr", "cm_mii".
        date: The date for which to download the bhavcopy.

        download_dir: Directory to save the file. Defaults to the current directory.

    Returns:
        Path: Path to the downloaded file.

    Raises:
        ValueError: If the folder is not a directory or the bhavcopy_type is invalid.
        FileNotFoundError: If the download fails or the file is corrupted.
        RuntimeError: If the report is unavailable or not yet updated.
    """
    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    # Define URLs for each bhavcopy type
    if bhavcopy_type == "equity":
        if date.year >= 2024:
            url = (f"https://nsearchives.nseindia.com/content/cm/"
                   f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv.zip")
        else:
            url = (f"https://nsearchives.nseindia.com/content/historical/"
                   f"EQUITIES/{date.strftime('%Y')}/{date.strftime('%b').upper()}/"
                   f"cm{date.strftime('%d%b%Y').upper()}bhav.csv.zip")
    elif bhavcopy_type == "delivery":
        url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date.strftime('%d%m%Y')}.csv"
    elif bhavcopy_type == "indices":

        url = f"https://www1.nseindia.com/content/indices/ind_close_all_{date.strftime('%d%m%Y')}.csv"
    elif bhavcopy_type == "fno":
        url = (f"https://nsearchives.nseindia.com/content/fo/"
               f"BhavCopy_NSE_FO_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv.zip")
    elif bhavcopy_type == "priceband":
        url = f"https://nsearchives.nseindia.com/content/equities/sec_list_{date.strftime('%d%m%Y')}.csv"
    elif bhavcopy_type == "pr":
        url = f"https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR{date.strftime('%d%m%y')}.zip"
    elif bhavcopy_type == "cm_mii":
        url = f"https://nsearchives.nseindia.com/content/cm/NSE_CM_security_{date.strftime('%d%m%Y')}.csv.gz"
    else:
        raise ValueError(f"Invalid bhavcopy_type: {bhavcopy_type}")

    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()

        file_name = f"{bhavcopy_type}_bhavcopy_{date.strftime('%Y%m%d')}"
        file_path = target_directory / file_name

        # Save the file
        if bhavcopy_type in ["equity", "fno", "pr"]:

            file_path = file_path.with_suffix(".zip")
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Extract the zip file
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(target_directory)
                extracted_file_name = zip_ref.namelist()[0]

                extracted_file_path = target_directory / extracted_file_name

            # Rename the extracted file
            new_file_name = f"{bhavcopy_type}_bhavcopy_{date.strftime('%Y%m%d')}.csv"
            new_file_path = target_directory / new_file_name

            if extracted_file_path != new_file_path:

                os.rename(extracted_file_path, new_file_path)

            # Clean up the zip file
            os.remove(file_path)
            return new_file_path

        elif bhavcopy_type == "cm_mii":
            file_path = file_path.with_suffix(".gz")
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Extract the gz file
            csv_path = (
                target_directory
                / f"{bhavcopy_type}_bhavcopy_{date.strftime('%Y%m%d')}.csv"
            )
            with gzip.open(file_path, "rb") as gz_file:
                with open(csv_path, "wb") as csv_file:
                    shutil.copyfileobj(gz_file, csv_file)

            # Clean up the gz file

            os.remove(file_path)
            return csv_path

        else:
            file_path = file_path.with_suffix(".csv")

            with open(file_path, "wb") as file:

                file.write(response.content)
            return file_path

    except requests.exceptions.RequestException as e:
        raise FileNotFoundError(f"Failed to download {bhavcopy_type} bhavcopy: {e}")
    except (zipfile.BadZipFile, gzip.BadGzipFile) as e:

        raise RuntimeError(f"Invalid file received: {e}")
    except OSError as e:
        raise RuntimeError(f"File operation failed: {e}")


def get_stock_quote(symbol: str) -> Dict:
    """Fetch the stock quote for a specific symbol.

    Args:
        symbol (str): The stock symbol (e.g., "INFY", "RELIANCE").


    Returns:
        Dict: A dictionary containing the stock quote data.


    Raises:

        ValueError: If the symbol is invalid or not found.
        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "quote-equity"
    params = {"symbol": symbol}
    try:
        data = fetch_data_from_nse(endpoint, params=params)

        # Handle None response (invalid symbol case)
        if data is None:
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if not data.get("info", {}).get("symbol"):
            raise ValueError(f"Invalid symbol: {symbol}")

        return {
            "symbol": data["info"]["symbol"],
            "company_name": data["info"].get("companyName", "N/A"),
            "current_price": data["priceInfo"]["lastPrice"],
            "open": data["priceInfo"].get("open", 0),
            "high": data["priceInfo"].get("intraDayHighLow", {}).get("max", 0),
            "low": data["priceInfo"].get("intraDayHighLow", {}).get("min", 0),
            "close": data["priceInfo"].get("close", 0),
            "volume": data.get("preOpenMarket", {}).get("totalTradedVolume", 0),
            "52_week_high": data["priceInfo"].get("weekHighLow", {}).get("max", 0),
            "52_week_low": data["priceInfo"].get("weekHighLow", {}).get("min", 0),
            "market_cap": data.get("securityInfo", {}).get("issuedSize", "N/A"),
        }
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 404:
            raise ValueError(f"Invalid symbol: {symbol}")
        raise Exception(f"Failed to fetch stock quote: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")


def get_option_chain(symbol: str, is_index: bool = False) -> Dict:
    """Fetch the option chain for a specific stock or index.

    Args:

        symbol (str): The stock or index symbol (e.g., "NIFTY", "BANKNIFTY", "RELIANCE").
        is_index (bool): Whether the symbol is an index. Defaults to False.

    Returns:
        Dict: A dictionary containing the option chain data.

    Raises:
        ValueError: If the symbol is invalid or not found.
        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "option-chain-indices" if is_index else "option-chain-equities"
    params = {"symbol": symbol}

    try:
        data = fetch_data_from_nse(endpoint, params=params)

        # Handle None response (invalid symbol case)
        if data is None:
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if not data.get("records"):
            raise ValueError(f"Invalid symbol: {symbol}")

        return data
    except requests.exceptions.HTTPError as e:
        if e.response and e.response.status_code == 404:
            raise ValueError(f"Invalid symbol: {symbol}")
        raise Exception(f"Failed to fetch option chain: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")


def get_all_indices() -> List[Dict]:
    """Fetch data for all NSE indices.

    Returns:

        List[Dict]: A list of dictionaries containing index data.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "allIndices"
    try:
        data = fetch_data_from_nse(endpoint)

        indices = []
        for index in data.get("data", []):
            indices.append(
                {
                    "name": index.get("index"),
                    "last_price": index.get("last"),
                    "change": index.get("variation"),
                    "percent_change": index.get("percentChange"),
                    "high": index.get("high"),
                    "low": index.get("low"),
                    "open": index.get("open"),
                    "previous_close": index.get("previousClose"),
                }
            )
        return indices

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch all indices: {e}")


def get_corporate_actions(
    segment: Literal["equities", "sme", "debt", "mf"] = "equities",
    symbol: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[Dict]:
    """Fetch forthcoming corporate actions.

    Args:

        segment (str): Market segment (equities, sme, debt, mf). Defaults to "equities".
        symbol (str, optional): Stock symbol to filter results.
        from_date (datetime, optional): Start date for filtering.
        to_date (datetime, optional): End date for filtering.


    Returns:
        List[Dict]: List of corporate actions.

    Raises:
        ValueError: If `from_date` is greater than `to_date`.
    """
    endpoint = "corporates-corporateActions"
    params = {"index": segment}
    if symbol:
        params["symbol"] = symbol
    if from_date and to_date:
        if from_date > to_date:
            raise ValueError("'from_date' cannot be greater than 'to_date'")
        params.update(
            {
                "from_date": from_date.strftime("%d-%m-%Y"),
                "to_date": to_date.strftime("%d-%m-%Y"),
            }
        )

    try:
        return fetch_data_from_nse(endpoint, params=params)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch corporate actions: {e}")


def get_announcements(
    index: Literal["equities", "sme", "debt", "mf", "invitsreits"] = "equities",
    symbol: Optional[str] = None,
    fno: bool = False,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> List[Dict]:
    """Fetch corporate announcements.

    Args:
        index (str): Market segment (equities, sme, debt, mf, invitsreits). Defaults to "equities".
        symbol (str, optional): Stock symbol to filter results.
        fno (bool, optional): Whether to include only FnO stocks. Defaults to False.

        from_date (datetime, optional): Start date for filtering.
        to_date (datetime, optional): End date for filtering.

    Returns:
        List[Dict]: List of corporate announcements.


    Raises:

        ValueError: If `from_date` is greater than `to_date`.
    """
    endpoint = "corporate-announcements"
    params = {"index": index}

    if symbol:
        params["symbol"] = symbol

    if fno:
        params["fo_sec"] = True
    if from_date and to_date:
        if from_date > to_date:
            raise ValueError("'from_date' cannot be greater than 'to_date'")
        params.update(
            {
                "from_date": from_date.strftime("%d-%m-%Y"),
                "to_date": to_date.strftime("%d-%m-%Y"),
            }
        )

    try:
        return fetch_data_from_nse(endpoint, params=params)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch corporate announcements: {e}")


def get_holidays(
    holiday_type: Literal["trading", "clearing"] = "trading"
) -> Dict[str, List[Dict]]:
    """Fetch NSE holiday lists for trading or clearing.

    Args:
        holiday_type (Literal["trading", "clearing"]): Type of holiday list to fetch. Defaults to "trading".

    Returns:
        Dict[str, List[Dict]]: A dictionary containing holiday lists for different market segments.

    Raises:
        ValueError: If `holiday_type` is not "trading" or "clearing".
        Exception: If the API request fails.
    """
    if holiday_type not in ["trading", "clearing"]:
        raise ValueError("holiday_type must be 'trading' or 'clearing'")

    endpoint = "holiday-master"
    params = {"type": holiday_type}

    try:
        data = fetch_data_from_nse(endpoint, params=params)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch holiday information: {e}")


def bulk_deals(from_date: datetime, to_date: datetime) -> List[Dict]:
    """Download the bulk deals report for the specified date range."""
    if (to_date - from_date).days > 365:
        raise ValueError("The date range cannot exceed one year.")

    endpoint = "historical/bulk-deals"
    params = {
        "from": from_date.strftime('%d-%m-%Y'),
        "to": to_date.strftime('%d-%m-%Y')
    }

    try:
        data = fetch_data_from_nse(endpoint, params=params)

        # Handle case where data is already a list (mocked response)
        if isinstance(data, list):
            return data
        
        if not data.get("data"):
            raise RuntimeError(
                "No bulk deals data available for the specified date range."
            )

        return data["data"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download bulk deals: {e}")


def get_fii_dii_data() -> List[Dict]:
    """Fetch FII (Foreign Institutional Investors) and DII (Domestic Institutional Investors) trading activity data.

    Returns:
        List[Dict]: A list of dictionaries containing FII/DII trading activity data.

    Raises:
        requests.exceptions.RequestException: If the API request fails.

    """
    endpoint = "fiidiiTradeReact"
    try:
        data = fetch_data_from_nse(endpoint)
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch FII/DII data: {e}")


def get_top_gainers() -> Dict:
    """Fetch the top gainers data from NSE.

    Returns:
        Dict: A dictionary containing the top gainers data.
    """

    endpoint = "live-analysis-variations"
    params = {"index": "gainers"}
    try:
        data = fetch_data_from_nse(endpoint, params=params)

        return data
    except Exception as e:
        raise Exception(f"Failed to fetch top gainers: {e}")


def get_top_losers() -> Dict:
    """Fetch the top losers data from NSE.

    Returns:
        Dict: A dictionary containing the top losers data.
    """
    endpoint = "live-analysis-variations"
    params = {"index": "loosers"}
    try:
        data = fetch_data_from_nse(endpoint, params=params)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch top losers: {e}")


def get_regulatory_status() -> Dict:
    """Fetch the regulatory module status from NSE.

    Returns:
        Dict: A dictionary containing the regulatory module status.
    """

    endpoint = "regulatorymodulestatus"
    try:

        data = fetch_data_from_nse(endpoint)
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch regulatory status: {e}")


def get_most_active_equities(index: Literal["volume", "value"]) -> List[Dict]:
    """
    Fetch the most active equities based on volume or value.

    Args:
        index (Literal["volume", "value"]): The index to filter by (volume or value).

    Returns:
        List[Dict]: A list of dictionaries containing the most active equities data.

    Raises:
        ValueError: If the index is not "volume" or "value".
        requests.exceptions.RequestException: If the API request fails.
    """
    if index not in ["volume", "value"]:
        raise ValueError("index must be 'volume' or 'value'")

    endpoint = "live-analysis-most-active-securities"
    params = {"index": index}
    response = fetch_data_from_nse(endpoint, params=params)
    return response.get("data", [])


def get_most_active_sme(index: Literal["volume", "value"]) -> List[Dict]:
    """
    Fetch the most active SME securities based on volume or value.


    Args:
        index (Literal["volume", "value"]): The index to filter by (volume or value).

    Returns:
        List[Dict]: A list of dictionaries containing the most active SME securities data.

    Raises:
        ValueError: If the index is not "volume" or "value".
        requests.exceptions.RequestException: If the API request fails.
    """
    if index not in ["volume", "value"]:
        raise ValueError("index must be 'volume' or 'value'")

    endpoint = "live-analysis-most-active-sme"
    params = {"index": index}
    response = fetch_data_from_nse(endpoint, params=params)
    return response.get("data", [])


def get_most_active_etf(index: Literal["volume", "value"]) -> List[Dict]:
    """
    Fetch the most active ETFs based on volume or value.

    Args:
        index (Literal["volume", "value"]): The index to filter by (volume or value).


    Returns:
        List[Dict]: A list of dictionaries containing the most active ETF data.


    Raises:

        ValueError: If the index is not "volume" or "value".
        requests.exceptions.RequestException: If the API request fails.

    """
    if index not in ["volume", "value"]:
        raise ValueError("index must be 'volume' or 'value'")

    endpoint = "live-analysis-most-active-etf"
    params = {"index": index}
    response = fetch_data_from_nse(endpoint, params=params)
    return response.get("data", [])


def get_volume_gainers() -> List[Dict]:
    """

    Fetch the list of securities with the highest volume gain compared to their average volume.

    Returns:
        List[Dict]: A list of dictionaries containing the volume gainers data.

    Raises:
        requests.exceptions.RequestException: If the API request fails.

    """
    endpoint = "live-analysis-volume-gainers"
    response = fetch_data_from_nse(endpoint)
    return response.get("data", [])


def get_all_indices_performance() -> Dict:
    """
    Fetch performance data for all NSE indices.

    Returns:
        Dict: A dictionary containing performance data for all indices, including:
              - data: List of index performance details.
              - timestamp: Timestamp of the data.
              - advances: Number of advancing stocks.
              - declines: Number of declining stocks.
              - unchanged: Number of unchanged stocks.

              - dates: Key historical dates.
              - date30dAgo: Date 30 days ago.
              - date365dAgo: Date 365 days ago.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "allIndices"
    return fetch_data_from_nse(endpoint)


def get_price_band_hitters(
    band_type: Literal["upper", "lower", "both"] = "upper",
    category: Literal["AllSec", "SecGtr20", "SecLwr20"] = "AllSec",
) -> Dict:
    """
    Fetch stocks that have hit their upper, lower, or both price bands.


    Args:
        band_type (Literal["upper", "lower", "both"]): Type of price band to fetch (upper, lower, or both).
        category (Literal["AllSec", "SecGtr20", "SecLwr20"]): Category of securities to fetch.

    Returns:
        Dict: A dictionary containing the price band hitters data.


    Raises:
        ValueError: If the band_type or category is invalid.
        requests.exceptions.RequestException: If the API request fails.

    """
    if band_type not in ["upper", "lower", "both"]:
        raise ValueError("band_type must be 'upper', 'lower', or 'both'")
    if category not in ["AllSec", "SecGtr20", "SecLwr20"]:

        raise ValueError("category must be 'AllSec', 'SecGtr20', or 'SecLwr20'")

    endpoint = "live-analysis-price-band-hitter"
    try:
        data = fetch_data_from_nse(endpoint)
        if band_type == "both":
            return data["count"]  # Return counts for both upper and lower bands
        return data[band_type][category]

    except Exception as e:
        logger.error(f"Failed to fetch price band hitters: {e}")
        raise


def get_52_week_high() -> Dict[str, List[Dict]]:
    """
    Fetch the list of stocks hitting 52-week highs.

    Returns:
        Dict[str, List[Dict]]: A dictionary containing:
            - "data": List of stocks hitting 52-week highs.

            - "timestamp": Timestamp of the data.

    """
    endpoint = "live-analysis-data-52weekhighstock"
    response = fetch_data_from_nse(endpoint)
    return {
        "data": response.get("data", []),
        "timestamp": response.get("timestamp", "N/A"),
    }


def get_52_week_low() -> Dict[str, List[Dict]]:
    """
    Fetch the list of stocks hitting 52-week lows.


    Returns:
        Dict[str, List[Dict]]: A dictionary containing:
            - "data": List of stocks hitting 52-week lows.
            - "timestamp": Timestamp of the data.
    """
    endpoint = "live-analysis-data-52weeklowstock"
    response = fetch_data_from_nse(endpoint)
    return {
        "data": response.get("data", []),
        "timestamp": response.get("timestamp", "N/A"),
    }


def get_52_week_counts() -> Dict[str, int]:
    """
    Fetch the counts of stocks hitting 52-week highs and lows.

    Returns:
        Dict[str, int]: A dictionary containing:
            - "high": Number of stocks hitting 52-week highs.
            - "low": Number of stocks hitting 52-week lows.
    """
    endpoint = "live-analysis-52weekhighstock"
    response = fetch_data_from_nse(endpoint)
    return {"high": response.get("high", 0), "low": response.get("low", 0)}


def get_52_week_data_by_symbol(symbol: str) -> List[Dict]:
    """
    Fetch 52-week high and low data for a specific symbol.


    Args:
        symbol (str): The stock symbol (e.g., "INFY", "RELIANCE").

    Returns:
        List[Dict]: A list of dictionaries containing 52-week high/low data for the symbol.

    Raises:
        ValueError: If the symbol is invalid or not found.
        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "live-analysis-52Week/search"
    params = {"sym": symbol}

    try:
        response = fetch_data_from_nse(endpoint, params=params)
        if not response:
            raise ValueError(f"No data found for symbol: {symbol}")
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:

            raise ValueError(f"Invalid symbol: {symbol}")
        raise Exception(f"Failed to fetch 52-week data: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")


def get_large_deals() -> Dict:
    """
    Fetch bulk deals, short deals, and block deals data from NSE.

    Returns:
        Dict: A dictionary containing bulk deals, short deals, and block deals data.
              Example:
              {
                  "as_on_date": "08-Jan-2025",
                  "bulk_deals": [
                      {
                          "symbol": "AARTECH",
                          "name": "Aartech Solonics Limited",
                          "client_name": "KABRA  PRIYA",
                          "buy_sell": "BUY",
                          "quantity": 688214,
                          "watp": 98.76
                      },
                      ...
                  ],
                  "short_deals": [
                      {
                          "symbol": "LICI",

                          "name": "LIFE INSURA CORP OF INDIA",
                          "quantity": 27600,
                          "watp": null
                      },
                      ...
                  ],

                  "block_deals": [
                      {
                          "symbol": "WANBURY",
                          "name": "Wanbury Limited",
                          "client_name": "BHATIA SURESH",
                          "buy_sell": "SELL",
                          "quantity": 352421,
                          "watp": 283.78

                      },
                      ...

                  ],
                  "total_bulk_deals": 78,

                  "total_short_deals": 16,
                  "total_block_deals": 2
              }


    Raises:

        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "snapshot-capital-market-largedeal"
    try:
        data = fetch_data_from_nse(endpoint)
        return {
            "as_on_date": data.get("as_on_date"),
            "bulk_deals": data.get("BULK_DEALS_DATA", []),
            "short_deals": data.get("SHORT_DEALS_DATA", []),
            "block_deals": data.get("BLOCK_DEALS_DATA", []),
            "total_bulk_deals": data.get("BULK_DEALS", 0),
            "total_short_deals": data.get("SHORT_DEALS", 0),
            "total_block_deals": data.get("BLOCK_DEALS", 0),
        }
    except requests.exceptions.RequestException as e:

        raise Exception(f"Failed to fetch large deals data: {e}")


def get_advance_data(symbol: Optional[str] = None) -> Dict:
    """
    Fetch data for stocks that have advanced in price.


    Args:
        symbol (str, optional): The stock symbol (e.g., "INFY"). If provided, fetches data for the specific symbol.
                               If None, fetches data for all advancing stocks.

    Returns:
        Dict: A dictionary containing:

            - "count": Counts of advances, declines, and unchanged stocks (only when symbol is None).
            - "data": List of dictionaries with detailed stock data.
    """
    endpoint = "live-analysis-advance"
    params = {"symbol": symbol} if symbol else None
    try:
        data = fetch_data_from_nse(endpoint, params=params)
        if symbol:
            return data  # Returns a list of data for the specific symbol
        return {
            "count": data.get("advance", {}).get("count", {}),
            "data": data.get("advance", {}).get("data", []),
        }
    except Exception as e:
        raise Exception(f"Failed to fetch advance data: {e}")


def get_decline_data(symbol: Optional[str] = None) -> Dict:
    """
    Fetch data for stocks that have declined in price.

    Args:
        symbol (str, optional): The stock symbol (e.g., "INFY"). If provided, fetches data for the specific symbol.
                               If None, fetches data for all declining stocks.

    Returns:
        Dict: A dictionary containing:
            - "count": Counts of advances, declines, and unchanged stocks (only when symbol is None).
            - "data": List of dictionaries with detailed stock data.
    """
    endpoint = "live-analysis-decline"
    params = {"symbol": symbol} if symbol else None
    try:
        data = fetch_data_from_nse(endpoint, params=params)

        if symbol:
            return data  # Returns a list of data for the specific symbol
        return {
            "count": data.get("decline", {}).get("count", {}),
            "data": data.get("decline", {}).get("data", []),
        }
    except Exception as e:

        raise Exception(f"Failed to fetch decline data: {e}")


def get_unchanged_data(symbol: Optional[str] = None) -> Dict:
    """

    Fetch data for stocks that have remained unchanged in price.

    Args:
        symbol (str, optional): The stock symbol (e.g., "INFY"). If provided, fetches data for the specific symbol.

                               If None, fetches data for all unchanged stocks.

    Returns:
        Dict: A dictionary containing:
            - "count": Counts of advances, declines, and unchanged stocks (only when symbol is None).
            - "data": List of dictionaries with detailed stock data.
            - "timestamp": Timestamp of the data.
            - "message": A message indicating the status of the response (e.g., "No unchanged stocks found").

    Raises:
        Exception: If the API request fails.
    """
    endpoint = "live-analysis-unchanged"
    params = {"symbol": symbol} if symbol else None
    try:
        data = fetch_data_from_nse(endpoint, params=params)
        if symbol:
            if not data:
                return {"message": f"No unchanged data found for symbol: {symbol}"}
            return data
        if not data.get("Unchange", {}).get("data"):
            return {
                "message": "No unchanged stocks found",
                "count": {},
                "data": [],
                "timestamp": data.get("timestamp", "N/A"),
            }
        return {
            "count": data.get("Unchange", {}).get("count", {}),
            "data": data.get("Unchange", {}).get("data", []),
            "timestamp": data.get("timestamp", "N/A"),
        }
    except Exception as e:
        raise Exception(f"Failed to fetch unchanged data: {e}")


def get_stocks_traded() -> Dict[str, Any]:
    """
    Fetch data for all stocks traded on the NSE.

    Returns:
        Dict[str, Any]: A dictionary containing the total count and data for all stocks traded.
    """
    endpoint = "live-analysis-stocksTraded"
    try:
        data = fetch_data_from_nse(endpoint)
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch stocks traded data: {e}")


def get_stocks_traded_by_symbol(symbol: str) -> List[Dict[str, Any]]:
    """
    Fetch data for a specific stock symbol traded on the NSE.


    Args:
        symbol (str): The stock symbol (e.g., "TCS", "INFY").

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing data for the specified stock symbol.

    Raises:
        ValueError: If the symbol is invalid or not found.
        requests.exceptions.RequestException: If the API request fails.
    """
    endpoint = "live-analysis-stocksTraded"
    params = {"symbol": symbol}
    try:
        data = fetch_data_from_nse(endpoint, params=params)

        if not data:

            raise ValueError(f"No data found for symbol: {symbol}")

        return data
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Invalid symbol: {symbol}")
        raise Exception(f"Failed to fetch stocks traded data: {e}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")


__version__ = "0.1.0"
def _split_date_range(
    from_date: date, to_date: date, max_chunk_size: int = 100
) -> List[Tuple[date, date]]:
    """
    Split a date range into smaller chunks for API requests.
    
    Args:
        from_date (date): The starting date of the range
        to_date (date): The ending date of the range  
        max_chunk_size (int): Maximum days per chunk. Defaults to 100.
        
    Returns:
        List[Tuple[date, date]]: List of date range tuples
        
    Raises:
        ValueError: If from_date is greater than to_date
    """
    if from_date > to_date:
        raise ValueError("from_date cannot be greater than to_date")
    
    chunks = []
    current_start = from_date
    
    while current_start <= to_date:
        # Calculate end of current chunk (inclusive)
        current_end = current_start + timedelta(days=max_chunk_size - 1)
        
        # Don't exceed the final date
        if current_end > to_date:
            current_end = to_date
            
        chunks.append((current_start, current_end))
        
        # Start next chunk the day after current end
        current_start = current_end + timedelta(days=1)
        
    return chunks


def get_fno_lot_sizes() -> Dict[str, int]:
    """
    Get the lot sizes of F&O (Futures & Options) stocks.
    
    Returns a dictionary mapping stock symbols to their respective lot sizes
    for derivatives trading.
    
    Returns:
        Dict[str, int]: Dictionary with symbol codes as keys and lot sizes as values
        
    Raises:
        Exception: If API request fails or data cannot be parsed
        
    Example:
        >>> lot_sizes = get_fno_lot_sizes()
        >>> print(lot_sizes['HDFCBANK'])  # 550 (example lot size)
        >>> print(lot_sizes['RELIANCE'])  # 250 (example lot size)
    """
    try:
        # F&O lot sizes are available from NSE archives
        url = "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv"
        
        # Make direct request to get CSV data
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        content = response.content
        if not content:
            raise Exception("No data received from F&O lot sizes endpoint")
        
        # Parse CSV content
        lot_sizes = {}
        lines = content.strip().split(b"\n")
        
        # Skip header line and process data
        for line in lines[1:]:  # Skip first line (header)
            if not line.strip():
                continue
                
            try:
                # CSV format: UNDERLYING,SYMBOL,LOT_SIZE,TICK_SIZE,etc
                parts = line.split(b",")
                if len(parts) >= 3:
                    underlying = parts[0].strip().decode('utf-8')
                    lot_size_str = parts[2].strip().decode('utf-8')
                    
                    # Convert to integer
                    lot_size = int(lot_size_str)
                    
                    # Use underlying (cleaner symbol) as key
                    clean_symbol = underlying.replace('-', '').replace('_', '')
                    lot_sizes[clean_symbol] = lot_size
                    
            except (ValueError, UnicodeDecodeError, IndexError):
                # Skip malformed lines
                continue
        
        if not lot_sizes:
            raise Exception("No valid lot size data found")
            
        logger.info(f"Successfully fetched lot sizes for {len(lot_sizes)} F&O symbols")
        return lot_sizes
        
    except Exception as e:
        raise Exception(f"Failed to fetch F&O lot sizes: {e}")


def get_historical_index_data(
    index: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> Dict[str, List[Dict]]:
    """
    Download historical index data within a given date range.
    
    Returns both price and turnover data for the specified index.
    
    Args:
        index (str): Index name (e.g., "NIFTY 50", "NIFTY BANK", "NIFTY IT")
        from_date (date, optional): Start date. Defaults to 30 days before to_date.
        to_date (date, optional): End date. Defaults to today.
        
    Returns:
        Dict[str, List[Dict]]: Dictionary with 'price' and 'turnover' keys containing historical data
        
    Raises:
        ValueError: If from_date > to_date or invalid parameters
        TypeError: If date parameters are not date objects
        Exception: If API request fails
        
    Example:
        >>> data = get_historical_index_data("NIFTY 50")
        >>> print(len(data['price']))     # Number of price records
        >>> print(data['price'][0].keys()) # Available fields in price data
    """
    if not index or not index.strip():
        raise ValueError("Index name cannot be empty")
    
    # Validate date parameters
    if from_date and not isinstance(from_date, date):
        raise TypeError("from_date must be a datetime.date object")
    if to_date and not isinstance(to_date, date):
        raise TypeError("to_date must be a datetime.date object")
        
    # Set default dates
    if not to_date:
        to_date = date.today()
    if not from_date:
        from_date = to_date - timedelta(days=30)
        
    if from_date > to_date:
        raise ValueError("from_date cannot be greater than to_date")
    
    # Split into chunks for large date ranges
    date_chunks = _split_date_range(from_date, to_date, max_chunk_size=365)
    all_price_data = []
    all_turnover_data = []
    
    for chunk_start, chunk_end in date_chunks:
        endpoint = "historical/indicesHistory"
        params = {
            "indexType": index.upper(),
            "from": chunk_start.strftime("%d-%m-%Y"),
            "to": chunk_end.strftime("%d-%m-%Y")
        }
        
        try:
            logger.debug(f"Fetching index data for {index} from {chunk_start} to {chunk_end}")
            response = fetch_data_from_nse(endpoint, params=params)
            
            if response and "data" in response:
                data = response["data"]
                
                # Extract price and turnover data
                if "indexCloseOnlineRecords" in data:
                    all_price_data.extend(data["indexCloseOnlineRecords"])
                    
                if "indexTurnoverRecords" in data:
                    all_turnover_data.extend(data["indexTurnoverRecords"])
            
        except Exception as e:
            logger.warning(f"Failed to fetch index data chunk for {index}: {e}")
            continue
    
    if not all_price_data and not all_turnover_data:
        raise Exception(f"No historical data found for index: {index}")
        
    return {
        "price": all_price_data,
        "turnover": all_turnover_data
    }


def get_equity_metadata(symbol: str) -> Dict:
    """
    Get detailed metadata information for an equity symbol.
    
    Provides comprehensive information including company name, industry, ISIN code,
    current status, market segment, and other metadata.
    
    Args:
        symbol (str): Stock symbol (e.g., "HDFCBANK", "TCS", "RELIANCE")
        
    Returns:
        Dict: Dictionary containing detailed equity metadata
        
    Raises:
        ValueError: If symbol is empty or invalid
        Exception: If API request fails
        
    Example:
        >>> metadata = get_equity_metadata("HDFCBANK")
        >>> print(metadata['companyName'])  # 'HDFC Bank Limited'
        >>> print(metadata['industry'])     # 'Private Sector Bank'
    """
    if not symbol or not symbol.strip():
        raise ValueError("Symbol cannot be empty")
    
    endpoint = "equity-meta-info"
    params = {"symbol": symbol.strip().upper()}
    
    try:
        data = fetch_data_from_nse(endpoint, params=params)
        
        if not data:
            raise ValueError(f"No metadata found for symbol: {symbol}")
        
        # Check if we got valid data by looking for key fields
        if not data.get("symbol") or not data.get("companyName"):
            raise ValueError(f"Invalid or delisted symbol: {symbol}")
            
        return data
        
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            raise ValueError(f"Symbol not found: {symbol}")
        raise Exception(f"Failed to fetch metadata for '{symbol}': {e}")


def get_symbol_lookup(query: str) -> Dict:
    """
    Search for stock symbols by company name or look up company name by stock symbol.
    
    Args:
        query (str): Company name or stock symbol to search for
        
    Returns:
        Dict: Dictionary containing search results with 'symbols' key containing list of matches
        
    Raises:
        ValueError: If query is empty or invalid
        Exception: If API request fails
        
    Example:
        >>> result = get_symbol_lookup("hdfc bank")
        >>> print(result['symbols'][0]['symbol'])  # 'HDFCBANK'
        >>> print(result['symbols'][0]['symbol_info'])  # 'HDFC Bank Limited'
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    endpoint = "search/autocomplete"
    params = {"q": query.strip()}
    
    try:
        data = fetch_data_from_nse(endpoint, params=params)
        
        if not data:
            return {"symbols": []}
        
        # Ensure we return a consistent structure
        if "symbols" not in data:
            data["symbols"] = []
            
        return data
        
    except Exception as e:
        raise Exception(f"Failed to search for symbol '{query}': {e}")


def get_historical_equity_data(
    symbol: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    series: List[str] = None
) -> List[Dict]:
    """
    Download historical daily price and volume data for a specific equity symbol.
    
    Args:
        symbol (str): Stock symbol (e.g., "HDFCBANK", "TCS", "RELIANCE")
        from_date (date, optional): Start date. Defaults to 30 days before to_date.
        to_date (date, optional): End date. Defaults to today.
        series (List[str], optional): Series to fetch (e.g., ["EQ"]). Defaults to ["EQ"].
        
    Returns:
        List[Dict]: List of historical data records with OHLCV data
        
    Raises:
        ValueError: If from_date > to_date or invalid parameters
        TypeError: If date parameters are not date objects
        Exception: If API request fails
    """
    if series is None:
        series = ["EQ"]
        
    # Validate date parameters
    if from_date and not isinstance(from_date, date):
        raise TypeError("from_date must be a datetime.date object")
    if to_date and not isinstance(to_date, date):
        raise TypeError("to_date must be a datetime.date object")
        
    # Set default dates
    if not to_date:
        to_date = date.today()
    if not from_date:
        from_date = to_date - timedelta(days=30)
        
    if from_date > to_date:
        raise ValueError("from_date cannot be greater than to_date")
    
    # Simple case - use basic endpoint for EQ series with recent data
    if series == ["EQ"] and (to_date - from_date).days <= 30:
        endpoint = "historical/cm/equity"
        params = {"symbol": symbol.upper()}
        try:
            data = fetch_data_from_nse(endpoint, params=params)
            if data and "data" in data:
                all_records = data["data"]
                # Filter by date range if specific dates were provided
                if from_date and to_date:
                    filtered_records = []
                    for record in all_records:
                        record_date = datetime.strptime(record["mTIMESTAMP"], "%d-%b-%Y").date()
                        if from_date <= record_date <= to_date:
                            filtered_records.append(record)
                    return filtered_records[::-1]  # Reverse for chronological order
                return all_records[::-1]
        except Exception as e:
            logger.warning(f"Simple endpoint failed for {symbol}: {e}")
    
    # For longer date ranges, split into chunks
    date_chunks = _split_date_range(from_date, to_date, max_chunk_size=100)
    all_data = []
    
    for chunk_start, chunk_end in date_chunks:
        endpoint = "historical/cm/equity"
        params = {
            "symbol": symbol.upper(),
            "series": json.dumps(series),
            "from": chunk_start.strftime("%d-%m-%Y"),
            "to": chunk_end.strftime("%d-%m-%Y")
        }
        
        try:
            logger.debug(f"Fetching data for {symbol} from {chunk_start} to {chunk_end}")
            response = fetch_data_from_nse(endpoint, params=params)
            
            if response and "data" in response:
                # Add data in reverse order to maintain chronological order
                chunk_data = list(reversed(response["data"]))
                all_data.extend(chunk_data)
            
        except Exception as e:
            logger.warning(f"Failed to fetch data chunk for {symbol}: {e}")
            continue
    
    if not all_data:
        raise Exception(f"No historical data found for symbol: {symbol}")
        
    return all_data


__all__ = [
    "get_market_status",
    "get_bhavcopy",
    "get_stock_quote",
    "get_option_chain",
    "get_all_indices",
    "get_corporate_actions",
    "get_announcements",
    "get_holidays",
    "bulk_deals",
    "get_fii_dii_data",
    "get_top_gainers",
    "get_top_losers",
    "get_regulatory_status",
    "get_most_active_equities",
    "get_most_active_sme",
    "get_most_active_etf",
    "get_volume_gainers",
    "get_all_indices_performance",
    "get_price_band_hitters",
    "get_52_week_high",
    "get_52_week_low",
    "get_52_week_data_by_symbol",
    "get_52_week_counts",
    "get_large_deals",
    "get_advance_data",
    "get_decline_data",
    "get_unchanged_data",
    "get_stocks_traded",
    "get_stocks_traded_by_symbol",
    "get_equity_metadata",
    "get_symbol_lookup",
    "get_historical_equity_data",
    "get_historical_index_data",
    "get_fno_lot_sizes",
]
