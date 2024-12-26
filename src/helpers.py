# nseapi/utils.py

import requests

def fetch_data_from_nse(endpoint):
    """Fetch data from a given NSE endpoint."""
    base_url = "https://www.nseindia.com/api"
    url = f"{base_url}/{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/118.0"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
