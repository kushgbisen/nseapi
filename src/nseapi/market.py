from datetime import datetime
from pathlib import Path
import requests
import zipfile
import os
from typing import List, Dict

def get_market_status():
    """Fetch the current market status."""
    url = "https://www.nseindia.com/api/marketStatus"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def status() -> List[Dict]:
    """Returns market status of all NSE market segments.

    :return: Market status of all NSE market segments.
    :rtype: list[dict]
    """
    url = "https://www.nseindia.com/api/marketStatus"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["marketState"]

def download_bhavcopy(date: datetime, download_dir: str = None):
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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
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
