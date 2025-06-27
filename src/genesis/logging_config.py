import logging
import os
from datetime import datetime

def setup_logging():
    """
    Set up logging configuration to output to both console and error.log file.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler for error.log
            logging.FileHandler(
                os.path.join(logs_dir, 'error.log'),
                mode='a',
                encoding='utf-8'
            )
        ]
    )
    
    # Get the logger
    logger = logging.getLogger(__name__)
    return logger

def get_logger():
    """
    Get the configured logger instance.
    """
    return logging.getLogger(__name__) 