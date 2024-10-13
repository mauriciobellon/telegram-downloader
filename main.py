import asyncio
import os
import argparse

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from asyncio import Semaphore

# Load environment variables from .env file
load_dotenv()

# Set up Telegram API credentials
api_id = os.getenv('TELEGRAM_API_KEY')  #put you telegram API key here
api_hash = os.getenv('TELEGRAM_API_HASH') #put yout telegram API hash here
phone_number = os.getenv('PHONE_NUMBER')
master_download_folder = os.getenv('DOWNLOADS_FOLDER')
concurrent_downloads = os.getenv('CONCURRENT_DOWNLOADS')

client = TelegramClient('session_name', api_id, api_hash)

# Set up argument parser
parser = argparse.ArgumentParser(description='Download media from a Telegram channel or group.')
parser.add_argument('channel', type=str, help='The username or invite link of the Telegram channel or group')
args = parser.parse_args()
channel = args.channel

# Define a function to download media files
async def download_media(message, channel_name, semaphore):
    async with semaphore:
        try:
            if message.media:
                print(f"Found media in message: {message.id}")
                print(f"Media type: {type(message.media)}")

                # add a master download folder
                os.makedirs(master_download_folder, exist_ok=True)
                # Remove @ if present
                folder_name = channel_name.replace('@', '') 
                # append channel name to master download folder
                download_folder = os.path.join(master_download_folder, folder_name)
                # Create folder with channel name if it doesn't exist
                os.makedirs(download_folder, exist_ok=True)
            
                # Get the file name
                file_name = message.file.name if hasattr(message.file, 'name') else f"file_{message.id}"
                file_path = os.path.join(folder_name, file_name)
                
                # Check if file already exists
                if os.path.exists(file_path):
                    print(f"File already exists: {file_path}")
                    return
                
                # Download the file
                print(f"Downloading media to: {file_path}")
                file = await client.download_media(message.media, file=file_path)
                
                if file:
                    print(f"Downloaded media: {file}")
                else:
                    print(f"Failed to download media from message: {message.id}")
            else:
                print(f"No media found in message: {message.id}")
        except Exception as e:
            print(f"Error downloading media from message {message.id}: {e}")

# Define an async function to iterate over messages and download media files
async def download_all_media():
    try:
        # Log in to the Telegram API
        await client.start(phone=phone_number)
        
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            code = input("Enter the code you received: ")
            await client.sign_in(phone_number, code)

        # Get the group or channel entity
        entity = await client.get_entity(channel)
        print(f"Found entity: {entity.id} - {entity.title}")

        # Use the entity's username or title as the folder name
        channel_name = entity.username or entity.title

        # Create a semaphore to limit concurrent downloads
        semaphore = Semaphore(concurrent_downloads)


        message_count = 0
        download_tasks = []
        async for message in client.iter_messages(entity):
            message_count += 1
            print(f"Processing message {message_count}: {message.id}")
            task = asyncio.create_task(download_media(message, channel_name, semaphore))
            download_tasks.append(task)

        # Wait for all download tasks to complete
        await asyncio.gather(*download_tasks)

        print(f"Processed {message_count} messages in total")

    except Exception as e:
        print(f"Error in download_all_media: {e}")

    finally:
        # Log out of the Telegram API
        await client.disconnect()

# Define and call an async function to run the script
def main():
    asyncio.run(download_all_media())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download media from a Telegram channel or group.')
    parser.add_argument('channel', type=str, help='The username or invite link of the Telegram channel or group')
    args = parser.parse_args()
    channel = args.channel
    main()