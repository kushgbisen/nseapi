from datetime import datetime
from pathlib import Path
import requests
import zipfile
import os

def get_market_status():
    """Fetch the current market status."""
    url = "https://www.nseindia.com/api/marketStatus"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def download_bhavcopy(date: datetime):
    """Download the equity bhavcopy for a specific date from NSE and save it in the current working directory."""
    current_directory = Path.cwd()

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
        
        zip_path = current_directory / f"bhav_copy_{date.strftime('%Y%m%d')}.zip"
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(current_directory)

        # Get the extracted CSV file name
        extracted_csv_name = zip_ref.namelist()[0]
        extracted_csv_path = current_directory / extracted_csv_name
        
        # Rename the CSV file to follow the 2024 naming convention
        new_csv_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        new_csv_path = current_directory / new_csv_name
        os.rename(extracted_csv_path, new_csv_path)
        
        # Delete the ZIP file
        os.remove(zip_path)
        
        # Print confirmation message
        print(f"Downloaded bhavcopy for {date.strftime('%Y-%m-%d')} at {new_csv_path}")
        
    except Exception as e:
        print(f"Error: {e}")
