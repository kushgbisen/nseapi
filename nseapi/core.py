# nseapi/core.py

from .utils import fetch_data_from_nse

def get_market_status():
    """Fetch the current market status from NSE."""
    endpoint = "marketStatus"
    return fetch_data_from_nse(endpoint)
