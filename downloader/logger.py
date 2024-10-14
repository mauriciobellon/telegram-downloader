# downloader/logger.py
import logging
from rich.logging import RichHandler

def setup_logger(log_file: str = "download.log", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up the logger with RichHandler and FileHandler.

    Args:
        log_file (str): Path to the log file.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(),
            logging.FileHandler(log_file, mode="w", encoding="utf-8")
        ]
    )
    logger = logging.getLogger("telegram_downloader")
    return logger

