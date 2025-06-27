#!/usr/bin/env python3
"""
Test script to verify logging configuration is working correctly.
"""

from logging_config import setup_logging

def test_logging():
    """Test different logging levels to ensure they work correctly."""
    logger = setup_logging()
    
    logger.info("This is an info message - should appear in both console and error.log")
    logger.warning("This is a warning message - should appear in both console and error.log")
    logger.error("This is an error message - should appear in both console and error.log")
    logger.debug("This is a debug message - should only appear if debug level is enabled")
    
    print("Test completed. Check the logs/error.log file to verify logging is working.")

if __name__ == "__main__":
    test_logging() 