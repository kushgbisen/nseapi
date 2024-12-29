import pytest
from pathlib import Path
import logging
from unittest.mock import patch
import requests
from nseapi.helpers import fetch_data_from_nse, logger
from nseapi import session  # Import the session object from nseapi


def test_logging_setup():
    """Test if logger is properly configured."""
    # Test log file creation
    logger.info("Test message")
    log_file = Path("logs/nseapi.log")
    assert log_file.exists()

    # Close the logger handlers
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

    # Cleanup
    log_file.unlink()


def test_fetch_data_from_nse_success():
    """Test successful API request."""
    with patch("nseapi.session.get") as mock_get:  # Mock the session.get method
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"key": "value"}

        data = fetch_data_from_nse("test-endpoint")
        assert data == {"key": "value"}


def test_fetch_data_from_nse_retry():
    """Test retry logic on failed API request."""
    with patch(
        "nseapi.session.get", side_effect=requests.exceptions.RequestException("Failed")
    ) as mock_get:
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            fetch_data_from_nse("test-endpoint", retries=3, delay=1)
        assert str(exc_info.value) == "Failed"
        assert mock_get.call_count == 3


def test_fetch_data_from_nse_timeout():
    """Test timeout handling."""
    with patch(
        "nseapi.session.get", side_effect=requests.exceptions.Timeout("Timeout")
    ) as mock_get:
        with pytest.raises(requests.exceptions.Timeout) as exc_info:
            fetch_data_from_nse("test-endpoint", timeout=5)
        assert str(exc_info.value) == "Timeout"
