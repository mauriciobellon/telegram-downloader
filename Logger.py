# logger.py
import logging
from rich.logging import RichHandler

def setup_logger(log_level='INFO'):
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(),
            logging.FileHandler("download.log", mode="w", encoding="utf-8")
        ]
    )
    return logging.getLogger(__name__)

# downloader.py
import asyncio

class TelegramDownloader:
    def __init__(self, client, download_folder, concurrent_downloads, logger):
        self.client = client
        self.download_folder = download_folder
        self.concurrent_downloads = concurrent_downloads
        self.logger = logger
        # Initialize other attributes as needed

    async def download_media(self, message):
        # Implementation
        pass

    async def run(self):
        # Implementation
        pass