# config/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
    TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')
    DOWNLOADS_FOLDER = os.getenv('DOWNLOADS_FOLDER', 'downloads')
    CONCURRENT_DOWNLOADS = int(os.getenv('CONCURRENT_DOWNLOADS', 5))

