import logging

import requests

from time import sleep

from functools import lru_cache

from pathlib import Path


# Configure logger

logger = logging.getLogger("NSEIndia")

logger.setLevel(logging.INFO)


# Create logs directory if it doesn't exist

logs_dir = Path("logs")

logs_dir.mkdir(exist_ok=True)


# Create handlers if not already present

if not logger.handlers:

    handler = logging.FileHandler(logs_dir / "nseapi.log")

    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logger.addHandler(handler)


def fetch_data_from_nse(endpoint, params=None, retries=3, delay=2, timeout=10):
    """Fetch data from a given NSE endpoint with retry logic and caching.



    Args:

        endpoint (str): The API endpoint to fetch data from.

        params (dict, optional): Query parameters for the request. Defaults to None.

        retries (int, optional): Number of retry attempts. Defaults to 3.

        delay (int, optional): Delay between retries in seconds. Defaults to 2.

        timeout (int, optional): Timeout for the request in seconds. Defaults to 10.



    Returns:

        dict: JSON response from the API.



    Raises:

        requests.RequestException: If the request fails after all retries.

    """

    from . import (
        session,
        _fetch_cookies,
    )  # Import session and cookie function from __init__.py

    base_url = "https://www.nseindia.com/api"

    url = f"{base_url}/{endpoint}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/118.0"
    }

    for attempt in range(retries):

        try:

            logger.debug(f"Attempt {attempt + 1}: Making request to: {url}")

            response = session.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout,
                cookies=_fetch_cookies(),
            )

            response.raise_for_status()

            logger.info(f"Successfully fetched data from {endpoint}")

            return response.json()

        except requests.RequestException as e:

            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

            if attempt < retries - 1:

                sleep(delay)  # Wait before retrying

            else:

                logger.error(
                    f"Failed to fetch data from {endpoint} after {retries} attempts: {str(e)}"
                )

                raise
