from datetime import datetime
from pathlib import Path
import requests
import zipfile

import os
import zlib
import gzip
import shutil

from typing import List, Dict, Literal, Optional, Union
from functools import lru_cache
from rich import print as rprint
from rich.table import Table
from rich.console import Console
from .helpers import fetch_data_from_nse

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


def get_market_status(pretty: bool = False) -> Dict:
    """Fetch the current market status.


    Args:
        pretty (bool, optional): Whether to print the output in a prettified format. Defaults to False.

    Returns:
        Dict: A dictionary containing the market status.

    """
    url = "https://www.nseindia.com/api/marketStatus"
    try:
        response = session.get(url, cookies=_fetch_cookies())
        response.raise_for_status()
        data = response.json()

        if pretty:
            console = Console()
            table = Table(title="Market Status", border_style="#555555")
            table.add_column("Market", style="bold white")
            table.add_column("Status", style="bold white")
            table.add_column("Trade Date", style="bold white")
            table.add_column("Index", style="bold white")
            table.add_column("Last Price", style="bold white")
            table.add_column("Change", style="bold white")

            table.add_column("Percent Change", style="bold white")

            for market in data["marketState"]:
                table.add_row(
                    market["market"],
                    market["marketStatus"],
                    market.get("tradeDate", "N/A"),
                    market.get("index", "N/A"),
                    str(market.get("last", "N/A")),
                    str(market.get("variation", "N/A")),
                    str(market.get("percentChange", "N/A")),
                )
            console.print(table)
        return data
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
        bhavcopy_type: Type of bhavcopy to download. Options: "equity", "delivery", "indices", "fno", "priceband", "pr", "cm_mii".
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
            url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv.zip"
        else:
            url = f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{date.strftime('%Y')}/{date.strftime('%b').upper()}/cm{date.strftime('%d%b%Y').upper()}bhav.csv.zip"
    elif bhavcopy_type == "delivery":

        url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date.strftime('%d%m%Y')}.csv"
    elif bhavcopy_type == "indices":
        url = f"https://www1.nseindia.com/content/indices/ind_close_all_{date.strftime('%d%m%Y')}.csv"
    elif bhavcopy_type == "fno":
        url = f"https://nsearchives.nseindia.com/content/fo/BhavCopy_NSE_FO_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv.zip"
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


def get_stock_quote(symbol: str, pretty: bool = False) -> Dict:
    """Fetch the stock quote for a specific symbol.

    Args:
        symbol (str): The stock symbol (e.g., "INFY", "RELIANCE").
        pretty (bool, optional): Whether to print the output in a prettified format. Defaults to False.

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

        if pretty:
            console = Console()
            table = Table(title=f"Stock Quote for {symbol}", border_style="#555555")
            table.add_column("Field", style="bold white")
            table.add_column("Value", style="bold white")

            for key, value in quote_data.items():
                table.add_row(key, str(value))

            console.print(table)

        return quote_data
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ValueError(f"Invalid symbol: {symbol}")
        raise Exception(f"Failed to fetch stock quote: {e}")
    except requests.exceptions.RequestException as e:

        raise Exception(f"API request failed: {e}")


def get_option_chain(symbol: str, is_index: bool = False, pretty: bool = False) -> Dict:
    """Fetch the option chain for a specific stock or index.

    Args:
        symbol (str): The stock or index symbol (e.g., "NIFTY", "BANKNIFTY", "RELIANCE").
        is_index (bool): Whether the symbol is an index. Defaults to False.
        pretty (bool, optional): Whether to print the output in a prettified format. Defaults to False.

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

        if pretty:
            console = Console()
            table = Table(title=f"Option Chain for {symbol}", border_style="#555555")
            table.add_column("Strike Price", style="bold white")
            table.add_column("Expiry Date", style="bold white")

            table.add_column("Call/Put", style="bold white")

            table.add_column("Last Price", style="bold white")
            table.add_column("Open Interest", style="bold white")

            for record in data["records"]["data"]:
                strike_price = record["strikePrice"]
                expiry_date = record["expiryDate"]

                if "CE" in record:
                    ce = record["CE"]
                    table.add_row(
                        str(strike_price),
                        expiry_date,
                        "Call",
                        str(ce["lastPrice"]),
                        str(ce["openInterest"]),
                    )

                if "PE" in record:
                    pe = record["PE"]
                    table.add_row(
                        str(strike_price),
                        expiry_date,
                        "Put",
                        str(pe["lastPrice"]),
                        str(pe["openInterest"]),
                    )

            console.print(table)

        return data

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            raise ValueError(f"Invalid symbol: {symbol}")
        raise Exception(f"Failed to fetch option chain: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {e}")


def get_all_indices(pretty: bool = False) -> List[Dict]:
    """Fetch data for all NSE indices.

    Args:
        pretty (bool, optional): Whether to print the output in a prettified format. Defaults to False.

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

        if pretty:

            console = Console()
            table = Table(title="All Indices", border_style="#555555")
            table.add_column("Name", style="bold white")
            table.add_column("Last Price", style="bold white")
            table.add_column("Change", style="bold white")
            table.add_column("Percent Change", style="bold white")
            table.add_column("High", style="bold white")
            table.add_column("Low", style="bold white")
            table.add_column("Open", style="bold white")
            table.add_column("Previous Close", style="bold white")

            for index in indices:
                table.add_row(
                    index["name"],
                    str(index["last_price"]),
                    str(index["change"]),
                    str(index["percent_change"]),
                    str(index["high"]),
                    str(index["low"]),
                    str(index["open"]),
                    str(index["previous_close"]),
                )
            console.print(table)

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

    url = f"https://www.nseindia.com/api/historical/bulk-deals?from={from_date.strftime('%d-%m-%Y')}&to={to_date.strftime('%d-%m-%Y')}"

    try:
        response = session.get(url, cookies=_fetch_cookies())

        response.raise_for_status()
        data = response.json()

        if not data.get("data"):

            raise RuntimeError(
                "No bulk deals data available for the specified date range."
            )

        return data["data"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download bulk deals: {e}")


__version__ = "0.1.0"

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
]
