"""
Logging configuration for ETL Engine
"""

import os
import logging
import time
from datetime import datetime
from typing import Tuple

def get_logger(run_id: str, logs_dir: str = "logs") -> Tuple[logging.Logger, str]:
    """
    Create and configure logger for ETL operations.
    
    Args:
        run_id: Unique identifier for this ETL run
        logs_dir: Directory to store log files
        
    Returns:
        Tuple of (logger, log_file_path)
    """
    # Ensure logs directory exists
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create log filename with timestamp and run ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"etl_{timestamp}_{run_id}.log"
    log_path = os.path.join(logs_dir, log_filename)
    
    # Create logger
    logger = logging.getLogger(f"etl_{run_id}")
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger, log_path
