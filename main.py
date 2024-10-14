import asyncio
import argparse
from pathlib import Path
from downloader.client import TelegramClientManager
from downloader.downloader import MediaDownloader
from config.settings import Settings
from downloader.logger import setup_logger
from telethon import TelegramClient

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download media from a Telegram channel or group.')
    parser.add_argument('channel', type=str, help='The username or invite link of the Telegram channel or group')
    parser.add_argument('--ext', type=str, help='Comma-separated list of file extensions to download (e.g., pdf,jpg)')
    return parser.parse_args()

async def main():
    args = parse_arguments()
    channel_input = args.channel.replace('@', '').replace('https://t.me/', '')
    allowed_extensions = args.ext.lower().split(',') if args.ext else None

    # Initialize Telegram client
    client_manager = TelegramClientManager(Settings.TELEGRAM_API_KEY, Settings.TELEGRAM_API_HASH, Settings.PHONE_NUMBER)
    client = await client_manager.start_client()

    # Setup logger early to capture all logs
    logger = setup_logger()

    # Fetch entity
    try:
        entity = await client.get_entity(channel_input)
        logger.info(f"Fetching messages from {entity.title}")
    except Exception as e:
        logger.error(f"Failed to get entity {channel_input}: {e}")
        return

    download_folder = Path(Settings.DOWNLOADS_FOLDER) / channel_input
    try:
        download_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Download folder set to: {download_folder}")
    except Exception as e:
        logger.error(f"Failed to create download folder '{download_folder}': {e}")
        return

    # Initialize MediaDownloader
    downloader = MediaDownloader(client, download_folder, allowed_extensions, Settings.CONCURRENT_DOWNLOADS)

    # Iterate and download media
    async for message in client.iter_messages(entity):
        await downloader.download_media(message)

    logger.info("Download completed.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
