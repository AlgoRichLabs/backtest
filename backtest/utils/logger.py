import logging
from datetime import datetime


# Set up the logger once in the logger module
def setup_logger():
    logger = logging.getLogger("")
    if not logger.hasHandlers():  # Avoid duplicate handlers
        logger.setLevel(logging.DEBUG)

        # Create handlers (console and file)
        console_handler = logging.StreamHandler()
        timestamp = datetime.now().strftime("%Y-%m-%d")
        file_handler = logging.FileHandler(f"logs/{timestamp}.log")

        # Set level for handlers
        console_handler.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.INFO)

        # Create formatter and add it to handlers
        formatter = logging.Formatter('%(levelname)s -  %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Create a global instance of the logger
logger = setup_logger()