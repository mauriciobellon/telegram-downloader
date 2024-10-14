# downloader/client.py
import os
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from downloader.logger import setup_logger
from downloader.utils import prompt_user

logger = setup_logger()

class TelegramClientManager:
    def __init__(self, api_id: str, api_hash: str, phone_number: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_name = self.phone_number.replace('+', '')
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

    async def start_client(self):
        await self.client.start(phone=self.phone_number)
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            code = await prompt_user("Enter the code you received: ")
            if not code:
                logger.error("No code entered. Exiting.")
                exit(1)
            try:
                await self.client.sign_in(self.phone_number, code)
            except SessionPasswordNeededError:
                password = await prompt_user("Two-Step Verification enabled. Enter your password: ")
                await self.client.sign_in(password=password)
        logger.info("Telegram client started and authorized.")
        return self.client

