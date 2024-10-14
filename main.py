import asyncio
import os
import argparse
import sys
from tqdm import tqdm  # {{ edit_1 }}
from tqdm.asyncio import tqdm_asyncio

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from asyncio import Semaphore, Queue
from functools import partial
import threading
import logging
from rich.logging import RichHandler
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(),
        logging.FileHandler("download.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up Telegram API credentials
api_id = os.getenv('TELEGRAM_API_KEY')  # Put your Telegram API key here
api_hash = os.getenv('TELEGRAM_API_HASH')  # Put your Telegram API hash here
phone_number = os.getenv('PHONE_NUMBER')
master_download_folder = os.getenv('DOWNLOADS_FOLDER')
concurrent_downloads = int(os.getenv('CONCURRENT_DOWNLOADS', 5))

# Session name is the phone number
session_name = phone_number.replace('+', '')

client = TelegramClient(session_name, api_id, api_hash)

# Set up argument parser
parser = argparse.ArgumentParser(description='Download media from a Telegram channel or group.')
parser.add_argument('channel', type=str, help='The username or invite link of the Telegram channel or group')
parser.add_argument('--ext', type=str, help='Comma-separated list of file extensions to download (e.g., pdf,jpg)')

args = parser.parse_args()
channel = args.channel
allowed_extensions = args.ext.lower().split(',') if args.ext else None

# Strip @ from channel name if present
channel = channel.replace('@', '')

# Strip https://t.me/ if present
channel = channel.replace('https://t.me/', '')

# Define a function to prepare the download folder
def prepare_download_folder(channel_name):
    # Add a master download folder
    os.makedirs(master_download_folder, exist_ok=True)
    # Append channel name to master download folder
    download_folder = Path(master_download_folder) / channel_name
    # Create folder with channel name if it doesn't exist
    download_folder.mkdir(parents=True, exist_ok=True)
    return download_folder

# Define a function to download a file
async def download_file(message, file_path, retries=3):
    for attempt in range(retries):
        try:
            logger.info(f"Downloading {file_path}")
            file = await client.download_media(message.media, file=file_path)
            if file:
                logger.info(f"Downloaded media: {file}")
                return
            else:
                logger.warning(f"Failed to download media from message: {message.id}")
        except Exception as e:
            logger.error(f"Error downloading media from message {message.id}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    logger.error(f"Failed to download message {message.id} after {retries} attempts")

# Define a function to download media files
async def download_media(message, channel_name, pbar, lock):
    try:
        if message.media:
            print(f"Found media in message: {message.id}")
            print(f"Media type: {type(message.media)}")

            # Prepare download folder
            download_folder = prepare_download_folder(channel_name)
        
            # Get the file name and extension
            file_name = message.file.name if hasattr(message.file, 'name') else f"file_{message.id}"
            _, file_extension = os.path.splitext(file_name)
            file_extension = file_extension[1:].lower()  # Remove the dot and convert to lowercase

            # Check if the file extension is allowed
            if allowed_extensions and file_extension not in allowed_extensions:
                print(f"Skipping file with extension {file_extension}: {file_name}")
                with lock:
                    pbar.update(1)
                return
            
            file_path = os.path.join(download_folder, file_name)
            # Check if file already exists
            if os.path.exists(file_path):
                # Check if the file has the same size as the original file
                if os.path.getsize(file_path) == message.file.size:
                    logger.warning(f"File already exists: {file_path}")
                    with lock:
                        pbar.update(1)
                    return
            
            # Download the file
            try:
                await download_file(message, file_path)
            except FileNotFoundError:
                logger.error(f"File not found: {file_path}")
            except PermissionError:
                logger.error(f"Permission denied: {file_path}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
            with lock:
                pbar.update(1)
        else:
            print(f"No media found in message: {message.id}")
            with lock:
                pbar.update(1)
    except Exception as e:
        print(f"Error processing message {message.id}: {e}")
        with lock:
            pbar.update(1)

# Worker coroutine
async def worker(name, queue, channel_name, pbar, lock):
    while True:
        message = await queue.get()
        if message is None:
            queue.task_done()
            break
        await download_media(message, channel_name, pbar, lock)
        queue.task_done()

# Define a function to handle the login logic
async def login():
    await client.start(phone=phone_number)
    
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = await prompt_user("Enter the code you received: ")
        if not code:
            logger.error("No code entered. Exiting.")
            sys.exit(1)
        await client.sign_in(phone_number, code)

async def prompt_user(prompt, timeout=30):
    try:
        return await asyncio.wait_for(asyncio.to_thread(input, prompt), timeout)
    except asyncio.TimeoutError:
        logger.error("Input timed out.")
        return None

# Define an async function to iterate over messages and download media files
async def download_all_media():
    try:
        # Log in to the Telegram API
        await login()

        # Get the group or channel entity
        entity = await client.get_entity(channel)
        print(f"Found entity: {entity.id} - {entity.title}")

        # Use the entity's username or title as the folder name
        channel_name = entity.username or entity.title

        # Create a queue and populate it with messages
        queue = Queue()

        # Initialize a lock for thread-safe updates to pbar
        lock = threading.Lock()

        # Initialize tqdm
        pbar = tqdm(total=0, desc="Downloading", unit='file')

        # Start worker coroutines
        workers = []
        for i in range(concurrent_downloads):
            worker_task = asyncio.create_task(worker(f'worker-{i+1}', queue, channel_name, pbar, lock))
            workers.append(worker_task)

        message_count = 0

        # Iterate over messages and add them to the queue
        async for message in client.iter_messages(entity):
            message_count += 1
            queue.put_nowait(message)
            # Update the total for tqdm
            with lock:
                pbar.total = message_count
                pbar.refresh()

        # Add sentinel values to stop workers
        for _ in workers:
            queue.put_nowait(None)

        # Wait until the queue is fully processed
        await queue.join()

        print(f"Processed {message_count} messages in total")

    except Exception as e:
        print(f"Error in download_all_media: {e}")

    finally:
        # Cancel worker tasks
        for w in workers:
            w.cancel()
        # Log out of the Telegram API
        await client.disconnect()

# Define and call an async function to run the script
async def main():
    await download_all_media()

if __name__ == "__main__":
    asyncio.run(main())