# nseapi/core.py

from datetime import datetime
from pathlib import Path
import requests
import zipfile
from .utils import fetch_data_from_nse

def get_market_status():
    """Fetch the current market status from NSE."""
    endpoint = "marketStatus"
    return fetch_data_from_nse(endpoint)

def download_bhavcopy(date: datetime, download_folder: str = 'downloads'):
    """Download the equity bhavcopy for a specific date from NSE."""
    Path(download_folder).mkdir(exist_ok=True)
    
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
        
        zip_path = Path(download_folder) / f"bhav_copy_{date.strftime('%Y%m%d')}.zip"
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_folder)
            
    except Exception as e:
        print(f"Error: {e}")
