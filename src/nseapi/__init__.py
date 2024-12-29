from datetime import datetime
from pathlib import Path
import requests
import zipfile
import os
from typing import List, Dict, Literal, Optional
from functools import lru_cache

# Initialize a session for all requests
session = requests.Session()
session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/",
        "Origin": "https://www.nseindia.com",
    }
)


# Fetch cookies required for API access
def _fetch_cookies():
    session.get("https://www.nseindia.com/")
    return session.cookies


def get_market_status() -> Dict:
    """Fetch the current market status.

    Returns:
        Dict: A dictionary containing the market status.
    """
    url = "https://www.nseindia.com/api/marketStatus"
    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch market status: {e}")


def download_bhavcopy(date: datetime, download_dir: str = None) -> Path:
    """Download the equity bhavcopy for a specific date.

    Args:
        date (datetime): The date for which to download the bhavcopy.
        download_dir (str, optional): Directory to save the file. Defaults to the current directory.

    Returns:
        Path: Path to the downloaded CSV file.

    Raises:
        ValueError: If the date is in the future.
    """
    if date > datetime.now():
        raise ValueError("Cannot download bhavcopy for a future date.")

    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    if date.year >= 2024:
        url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv.zip"
    else:
        url = f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{date.strftime('%Y')}/{date.strftime('%b').upper()}/cm{date.strftime('%d%b%Y').upper()}bhav.csv.zip"

    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()

        zip_path = target_directory / f"bhav_copy_{date.strftime('%Y%m%d')}.zip"
        with open(zip_path, "wb") as file:
            file.write(response.content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(target_directory)

        extracted_csv_name = zip_ref.namelist()[0]
        extracted_csv_path = target_directory / extracted_csv_name

        new_csv_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        new_csv_path = target_directory / new_csv_name

        if extracted_csv_path != new_csv_path:
            os.rename(extracted_csv_path, new_csv_path)

        os.remove(zip_path)
        return new_csv_path

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download bhavcopy: {e}")
    except zipfile.BadZipFile as e:
        raise Exception(f"Invalid zip file received: {e}")
    except OSError as e:
        raise Exception(f"File operation failed: {e}")


def delivery_bhavcopy(date: datetime, download_dir: str = None) -> Path:
    """Download the daily Equity delivery report for a specific date.

    Args:
        date (datetime): The date for which to download the delivery report.
        download_dir (str, optional): Directory to save the file. Defaults to the current directory.

    Returns:
        Path: Path to the downloaded CSV file.
    """
    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date.strftime('%d%m%Y')}.csv"

    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()

        csv_path = target_directory / f"delivery_bhavcopy_{date.strftime('%Y%m%d')}.csv"
        with open(csv_path, "wb") as file:
            file.write(response.content)

        return csv_path

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download delivery bhavcopy: {e}")
    except OSError as e:
        raise Exception(f"File operation failed: {e}")


def bhavcopy_index(date: datetime, download_dir: str = None) -> Path:
    """Download the daily Equity bhavcopy for Index data for a specific date.

    Args:
        date (datetime): The date for which to download the bhavcopy.
        download_dir (str, optional): Directory to save the file. Defaults to the current directory.

    Returns:
        Path: Path to the downloaded CSV file.
    """
    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    url = f"https://www1.nseindia.com/content/indices/ind_close_all_{date.strftime('%d%m%Y')}.csv"

    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()

        csv_path = target_directory / f"bhavcopy_index_{date.strftime('%Y%m%d')}.csv"
        with open(csv_path, "wb") as file:
            file.write(response.content)

        return csv_path

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download bhavcopy index: {e}")
    except OSError as e:
        raise Exception(f"File operation failed: {e}")


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
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()
        data = response.json()

        if not data.get("info", {}).get("symbol"):
            raise ValueError(f"Invalid symbol: {symbol}")

        quote_data = {
            "symbol": data["info"]["symbol"],
            "company_name": data["info"]["companyName"],
            "current_price": data["priceInfo"]["lastPrice"],
            "open": data["priceInfo"]["open"],
            "high": data["priceInfo"]["intraDayHighLow"]["max"],
            "low": data["priceInfo"]["intraDayHighLow"]["min"],
            "close": data["priceInfo"]["close"],
            "volume": data["preOpenMarket"]["totalTradedVolume"],
            "52_week_high": data["priceInfo"]["weekHighLow"]["max"],
            "52_week_low": data["priceInfo"]["weekHighLow"]["min"],
            "market_cap": data["securityInfo"].get("issuedSize", "N/A"),
        }
        return quote_data
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
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
    url = f"https://www.nseindia.com/api/{endpoint}?symbol={symbol}"
    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()
        data = response.json()

        if not data.get("records"):
            raise ValueError(f"Invalid symbol: {symbol}")

        return data
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
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
    url = "https://www.nseindia.com/api/allIndices"
    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()
        data = response.json()

        indices = []
        for index in data.get("data", []):
            indices.append(
                {
                    "name": index.get("index"),  # Use the "index" key for the name
                    "last_price": index.get("last"),
                    "change": index.get("variation"),  # Use "variation" for change
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
    url = "https://www.nseindia.com/api/corporates-corporateActions"
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
        response = session.get(url, params=params, cookies=_fetch_cookies())
        response.raise_for_status()
        return response.json()
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
    url = "https://www.nseindia.com/api/corporate-announcements"
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
        response = session.get(url, params=params, cookies=_fetch_cookies())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch corporate announcements: {e}")


__version__ = "0.1.0"
__all__ = [
    "get_market_status",
    "download_bhavcopy",
    "delivery_bhavcopy",
    "bhavcopy_index",
    "get_stock_quote",
    "get_option_chain",
    "get_all_indices",
    "get_corporate_actions",
    "get_announcements",
]
