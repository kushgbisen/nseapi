import pytest
from pathlib import Path
import logging

# Adjust the import statement
from nseapi.helpers import logger


def test_logging_setup():
    """Test if logger is properly configured"""

    # Test log file creation
    logger.info("Test message")
    log_file = Path("nseapi.log")
    assert log_file.exists()

    # Close the logger handlers
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

    # Cleanup
    log_file.unlink()
