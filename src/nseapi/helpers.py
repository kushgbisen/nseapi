import logging
import requests

# Configure logger
logger = logging.getLogger('NSEIndia')
logger.setLevel(logging.INFO)

# Create handlers if not already present
if not logger.handlers:
    handler = logging.FileHandler('nseapi.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def fetch_data_from_nse(endpoint):
    """Fetch data from a given NSE endpoint."""
    base_url = "https://www.nseindia.com/api"
    url = f"{base_url}/{endpoint}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/118.0"
    }
    
    logger.debug(f"Making request to: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f"Successfully fetched data from {endpoint}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from {endpoint}: {str(e)}")
        raise
