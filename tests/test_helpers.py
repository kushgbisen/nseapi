import pytest
from pathlib import Path

def test_logging_setup():
    """Test if logger is properly configured"""
    from src.helpers import logger
    
    # Test log file creation
    logger.info("Test message")
    log_file = Path("nseapi.log")
    assert log_file.exists()
    
    # Cleanup
    log_file.unlink()
