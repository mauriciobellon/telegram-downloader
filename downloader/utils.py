# downloader/utils.py
import asyncio
from pathlib import Path
import re

async def prompt_user(prompt: str, timeout: int = 30) -> str:
    """
    Prompts the user for input asynchronously with a timeout.

    Args:
        prompt (str): The prompt message.
        timeout (int): Timeout in seconds.

    Returns:
        str: User input or an empty string if timed out.
    """
    try:
        return await asyncio.wait_for(asyncio.to_thread(input, prompt), timeout)
    except asyncio.TimeoutError:
        print("Input timed out.")
        return ""

def generate_unique_filepath(file_path: Path) -> Path:
    """
    Generates a unique file path by appending a suffix to the file name if it already exists.

    Args:
        file_path (Path): The original file path.

    Returns:
        Path: A unique file path.
    """
    if file_path.exists():
        suffix = 1
        while True:
            new_file_path = file_path.with_name(f"{file_path.stem}_{suffix}{file_path.suffix}")
            if not new_file_path.exists():
                return new_file_path
            suffix += 1
    return file_path 

def sanitize_folder_name(name: str) -> str:
    """
    Sanitizes a string to be safe for use as a folder name.

    Args:
        name (str): The original folder name.

    Returns:
        str: A sanitized folder name.
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # Optionally, replace spaces with underscores
    sanitized = sanitized.strip().replace(' ', '_')
    return sanitized
