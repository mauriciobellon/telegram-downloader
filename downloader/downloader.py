# downloader/downloader.py
import os
from pathlib import Path
import asyncio
import logging
from telethon.tl.types import DocumentAttributeVideo
from downloader.logger import setup_logger
from downloader.utils import generate_unique_filepath
from collections import deque

logger = setup_logger()

class MediaDownloader:
    def __init__(self, client, download_folder: Path, allowed_extensions: list = None, concurrency: int = 5):
        self.client = client
        self.download_folder = download_folder
        self.allowed_extensions = allowed_extensions
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)
        self.download_queue = asyncio.Queue()
        self.download_tasks = set()

    async def download_media(self, message):
        await self.download_queue.put(message)

    async def process_downloads(self):
        while True:
            message = await self.download_queue.get()
            task = asyncio.create_task(self._download_single_media(message))
            self.download_tasks.add(task)
            task.add_done_callback(self.download_tasks.discard)

    async def _download_single_media(self, message):
        async with self.semaphore:
            try:
                if message.media:
                    file_name = message.file.name or f"file_{message.id}"
                    file_extension = Path(file_name).suffix.lower().strip('.')
                    
                    if self.allowed_extensions and file_extension not in self.allowed_extensions:
                        logger.info(f"Skipping {file_name}, unsupported extension.")
                        return

                    file_path = self.download_folder / file_name

                    if file_path.exists() and file_path.stat().st_size == message.file.size:
                        logger.warning(f"File already exists and is complete: {file_path}")
                        return

                    await self.client.download_media(message, file=str(file_path))
                    logger.info(f"Downloaded: {file_path}")
                else:
                    logger.info(f"No media found in message {message.id}.")
            except Exception as e:
                logger.error(f"Failed to download media from message {message.id}: {e}")
            finally:
                self.download_queue.task_done()

    async def wait_for_downloads(self):
        await self.download_queue.join()
        await asyncio.gather(*self.download_tasks)
