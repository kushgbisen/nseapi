from datetime import datetime
from pathlib import Path
import requests
import zipfile
import os
from typing import List, Dict, Literal, Optional

# Initialize a session for all requests
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
})

def get_market_status():
    """Fetch the current market status."""
    url = "https://www.nseindia.com/api/marketStatus"
    response = session.get(url)
    response.raise_for_status()
    return response.json()

def status() -> List[Dict]:
    """Returns market status of all NSE market segments.

    :return: Market status of all NSE market segments.
    :rtype: list[dict]
    """
    url = "https://www.nseindia.com/api/marketStatus"
    response = session.get(url)
    response.raise_for_status()
    return response.json()["marketState"]

def download_bhavcopy(date: datetime, download_dir: str = None) -> Path:
    """Download the equity bhavcopy for a specific date from NSE.
    
    Args:
        date (datetime): The date for which to download the bhavcopy
        download_dir (str, optional): Directory to save the downloaded file. 
                                    Defaults to current working directory.
    
    Returns:
        Path: Path to the downloaded CSV file
        
    Raises:
        requests.exceptions.RequestException: If download fails
        zipfile.BadZipFile: If the downloaded file is not a valid ZIP
        OSError: If there are file operation issues
    """
    # Set download directory
    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    # Determine URL based on year
    if date.year >= 2024:
        url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv.zip"
    else:
        url = f"https://nsearchives.nseindia.com/content/historical/EQUITIES/{date.strftime('%Y')}/{date.strftime('%b').upper()}/cm{date.strftime('%d%b%Y').upper()}bhav.csv.zip"

    try:
        response = session.get(url)
        response.raise_for_status()
        
        # Save and extract zip file
        zip_path = target_directory / f"bhav_copy_{date.strftime('%Y%m%d')}.zip"
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_directory)

        # Get the extracted CSV file name
        extracted_csv_name = zip_ref.namelist()[0]
        extracted_csv_path = target_directory / extracted_csv_name
        
        # Standardize the CSV file name to 2024 format
        new_csv_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        new_csv_path = target_directory / new_csv_name
        
        # Rename if needed
        if extracted_csv_path != new_csv_path:
            os.rename(extracted_csv_path, new_csv_path)
        
        # Cleanup zip file
        os.remove(zip_path)
        
        print(f"Downloaded bhavcopy for {date.strftime('%Y-%m-%d')} at {new_csv_path}")
        return new_csv_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download bhavcopy: {e}")
    except zipfile.BadZipFile as e:
        raise Exception(f"Invalid zip file received: {e}")
    except OSError as e:
        raise Exception(f"File operation failed: {e}")

def delivery_bhavcopy(date: datetime, download_dir: str = None) -> Path:
    """Download the daily Equity delivery report for specified date.
    
    Args:
        date (datetime): Date of delivery bhavcopy to download
        download_dir (str, optional): Directory to save the downloaded file. 
                                      Defaults to current working directory.
    
    Returns:
        Path: Path to the downloaded CSV file
        
    Raises:
        requests.exceptions.RequestException: If download fails
        OSError: If there are file operation issues
    """
    # Set download directory
    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    # URL for the delivery bhavcopy
    url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date.strftime('%d%m%Y')}.csv"

    try:
        response = session.get(url)
        response.raise_for_status()
        
        # Save the CSV file
        csv_path = target_directory / f"delivery_bhavcopy_{date.strftime('%Y%m%d')}.csv"
        with open(csv_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Downloaded delivery bhavcopy for {date.strftime('%Y-%m-%d')} at {csv_path}")
        return csv_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download delivery bhavcopy: {e}")
    except OSError as e:
        raise Exception(f"File operation failed: {e}")

def bhavcopy_index(date: datetime, download_dir: str = None) -> Path:
    """Download the daily Equity bhavcopy for Index data for a specified date.
    
    Args:
        date (datetime): Date of bhavcopy to download
        download_dir (str, optional): Directory to save the downloaded file. 
                                      Defaults to current working directory.
    
    Returns:
        Path: Path to the downloaded CSV file
        
    Raises:
        requests.exceptions.RequestException: If download fails
        OSError: If there are file operation issues
    """
    # Set download directory
    target_directory = Path(download_dir) if download_dir else Path.cwd()
    target_directory.mkdir(parents=True, exist_ok=True)

    # URL for the index bhavcopy
    url = f"https://www1.nseindia.com/content/indices/ind_close_all_{date.strftime('%d%m%Y')}.csv"

    try:
        response = session.get(url)
        response.raise_for_status()
        
        # Save the CSV file
        csv_path = target_directory / f"bhavcopy_index_{date.strftime('%Y%m%d')}.csv"
        with open(csv_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Downloaded bhavcopy index for {date.strftime('%Y-%m-%d')} at {csv_path}")
        return csv_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download bhavcopy index: {e}")
    except OSError as e:
        raise Exception(f"File operation failed: {e}")

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
        list[dict]: List of corporate actions.
    
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
        params.update({
            "from_date": from_date.strftime("%d-%m-%Y"),
            "to_date": to_date.strftime("%d-%m-%Y"),
        })

    response = session.get(url, params=params)
    response.raise_for_status()
    return response.json()

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
        list[dict]: List of corporate announcements.
    
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
        params.update({
            "from_date": from_date.strftime("%d-%m-%Y"),
            "to_date": to_date.strftime("%d-%m-%Y"),
        })

    response = session.get(url, params=params)
    response.raise_for_status()
    return response.json()
