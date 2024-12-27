"""
NSEAPI - National Stock Exchange India API wrapper
"""

from nseapi.market import get_market_status, download_bhavcopy

__version__ = "0.1.0"
__all__ = ["get_market_status", "download_bhavcopy"]
