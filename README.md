# Telegram Downloader

![Telegram Downloader](https://img.shields.io/badge/Telegram-Downloader-green)
![Python Version](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Table of Contents

- [About](#about)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## About

**Telegram Downloader** is a powerful and efficient tool designed to download media from Telegram channels or groups. Leveraging asynchronous programming and concurrent downloads, this script ensures rapid retrieval of media files, significantly reducing download time.

## Features

- **Concurrent Downloads:** Utilize multiple threads to download files in parallel.
- **Selective Downloading:** Filter downloads based on file extensions.
- **Progress Tracking:** Monitor download progress with an interactive progress bar.
- **Resumable Downloads:** Skip already downloaded files to save time.
- **Configurable Settings:** Customize behavior via environment variables.
- **Easy Setup:** Simple installation using Poetry.

## Prerequisites

Before installing Telegram Downloader, ensure you have the following:

- **Python 3.7 or higher:** [Download Python](https://www.python.org/downloads/)
- **Poetry:** Dependency management and packaging tool.

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

  After installation, ensure Poetry is added to your PATH:

  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

- **Telegram API Credentials:**
  - **API ID**
  - **API Hash**

  Obtain these by logging into [Telegram's API Development Tools](https://my.telegram.org/apps).

## Installation

Follow these steps to set up Telegram Downloader on your machine:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/telegram-downloader.git
   cd telegram-downloader
   ```

2. **Create and Configure the `.env` File:**

   Create a `.env` file in the project root to store environment variables.

   ```bash
   touch .env
   ```

3. **Set Up Environment Variables:**

   Open the `.env` file in your favorite text editor and add the following:

   ```env
   TELEGRAM_API_KEY=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   PHONE_NUMBER=your_phone_number
   DOWNLOADS_FOLDER=path/to/downloads
   CONCURRENT_DOWNLOADS=5
   ```

   - **TELEGRAM_API_KEY:** Your Telegram API ID.
   - **TELEGRAM_API_HASH:** Your Telegram API Hash.
   - **PHONE_NUMBER:** Your Telegram account's phone number (include country code, e.g., +123456789).
   - **DOWNLOADS_FOLDER:** Directory where downloaded files will be saved.
   - **CONCURRENT_DOWNLOADS:** Number of parallel downloads (default is 5).

4. **Install Dependencies with Poetry:**

   ```bash
   poetry install
   ```

   This command installs all necessary packages as specified in the `pyproject.toml` file.

## Configuration

Ensure the `.env` file is correctly set up with your Telegram credentials and desired settings. Here's a breakdown of each environment variable:

- **TELEGRAM_API_KEY:** *(Required)* Your unique Telegram API ID.
- **TELEGRAM_API_HASH:** *(Required)* Your unique Telegram API Hash.
- **PHONE_NUMBER:** *(Required)* The phone number associated with your Telegram account.
- **DOWNLOADS_FOLDER:** *(Required)* Absolute or relative path where media files will be saved.
- **CONCURRENT_DOWNLOADS:** *(Optional)* Number of files to download simultaneously. Default is `5`.

**Example `.env` File:**

```env
TELEGRAM_API_KEY=123456
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+123456789
DOWNLOADS_FOLDER=./downloads
CONCURRENT_DOWNLOADS=10
```

## Usage

Run the downloader using Poetry with the following command structure:

````bash
poetry run python main.py <channel_username> [--ext ext1,ext2,...]
````

### Arguments

- `<channel_username>`: *(Required)* The username or invite link of the Telegram channel or group from which you want to download media.

### Options

- `--ext`: *(Optional)* Comma-separated list of file extensions to download. If not specified, all media types will be downloaded.

## Examples

1. **Download All Media from a Channel:**

   ```bash
   poetry run python main.py my_telegram_channel
   ```

2. **Download Only Specific File Types (e.g., PDFs and JPGs):**

   ```bash
   poetry run python main.py my_telegram_channel --ext pdf,jpg
   ```

3. **Using an Invite Link:**

   ```bash
   poetry run python main.py https://t.me/joinchat/XXXXXX
   ```

## Troubleshooting

### Common Issues

1. **Authentication Errors:**

   - **Symptom:** Prompted for a code repeatedly or unable to log in.
   - **Solution:** Ensure that the `PHONE_NUMBER` in your `.env` file is correct and that you have access to the device to receive the authentication code.

2. **Invalid API Credentials:**

   - **Symptom:** Errors related to invalid API ID or Hash.
   - **Solution:** Double-check your `TELEGRAM_API_KEY` and `TELEGRAM_API_HASH` in the `.env` file.

3. **Network Issues:**

   - **Symptom:** Download failures or timeouts.
   - **Solution:** Verify your internet connection. If problems persist, check for firewall restrictions or try a different network.

4. **Rate Limiting:**

   - **Symptom:** Errors indicating too many requests.
   - **Solution:** Reduce the `CONCURRENT_DOWNLOADS` value in the `.env` file to minimize the number of simultaneous requests.

5. **Missing Dependencies:**

   - **Symptom:** Import errors or missing module exceptions.
   - **Solution:** Ensure all dependencies are installed by running `poetry install`.

### Logging and Debugging

Consider enhancing the script with more robust logging mechanisms using Python's `logging` module for better insight into operations and errors.

## Contributing

Contributions are welcome! To contribute:

1. **Fork the Repository**

2. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Commit Your Changes:**

   ```bash
   git commit -m "Add some feature"
   ```

4. **Push to the Branch:**

   ```bash
   git push origin feature/YourFeatureName
   ```

5. **Open a Pull Request**

Please ensure your code follows the project's coding standards and includes appropriate documentation and tests.

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer:** Use this tool responsibly and in compliance with Telegram's [Terms of Service](https://telegram.org/tos). Ensure you have permission to download and redistribute any media from channels or groups.
