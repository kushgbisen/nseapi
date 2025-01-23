# backend/utils.py
import requests
from datetime import datetime
from typing import Dict, List, Optional

def fetch_data_from_nse(endpoint: str, params: Optional[Dict] = None) -> Dict:
    """Fetch data from a given NSE endpoint."""
    base_url = "https://www.nseindia.com/api"
    url = f"{base_url}/{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
