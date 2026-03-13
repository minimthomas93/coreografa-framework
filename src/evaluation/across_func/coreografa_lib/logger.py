import os
import logging
from datetime import datetime

# Base directory: evaluation/across_func
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "eval_results"))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Single log file for the entire workflow
LOG_FILE = os.path.join(LOG_DIR, f"coreografa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

print(f"Logger initialized. Logs will be saved in: {LOG_FILE}")

# Formatter for all loggers
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# File handler (shared by all loggers)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Optional console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

def get_logger(module_name: str):
    """
    Return a logger for a specific module. All loggers share the same file and console output.
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    # Add handlers only once
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
