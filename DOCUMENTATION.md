# Telegram Forwarder Project Documentation

## Overview
The **Telegram Forwarder** is a sophisticated tool designed to automate the process of monitoring Telegram groups and channels and forwarding (scraping) their messages to specified destinations. It supports both a Graphical User Interface (GUI) for desktop use and a Headless mode for server/VPS deployment.

## Key Features
*   **Scrape Technology**: Instead of using the native "Forward" feature, the bot copies the message content (text, media, captions) and sends it as a new message.
    *   **Benefits**: Bypasses "Copy Restricted" (DRM) channels, hides the original sender ("Forwarded from" tag), and allows for cleaner message logs.
*   **Multi-Source Architecture**: Capable of monitoring an unlimited number of source groups simultaneously, each with its own unique configuration (e.g., Source A monitors ALL messages, Source B monitors only User X).
*   **Safety First**: Implements random delays (0.5s - 1.5s) between actions to mimic human behavior and prevent Telegram API flood bans.
*   **Secure Authentication**: Uses `python-dotenv` to store sensitive API credentials in a local `.env` file. Supports 2FA and auto-login on startup.

## Project Structure

### Core Files
*   **`client_manager.py`**: The brain of the operation.
    *   Manages the `Telethon` client connection.
    *   Handles login/authentication flows.
    *   Manages the `targets.json` configuration database.
    *   Contains the event listeners that detect new messages.
    *   Implements the "Scrape & Send" logic with safety delays.
*   **`config.py`**: Helper module to securely load and save credentials using `.env`.
*   **`targets.json`**: JSON database storing your monitoring configurations.
    *   *Structure*:
        ```json
        {
            "sources": {
                "123456789": {
                    "name": "Crypto Signals",
                    "type": "channel",
                    "monitor_all": true,
                    "user_ids": []
                }
            },
            "destination_ids": ["987654321", "me"]
        }
        ```

### Interfaces
*   **`gui.py` (Client)**:
    *   Built with **PyQt6**.
    *   Provides a modern, tabbed interface for Login and Dashboard.
    *   Features async event handling to keep the UI responsive during network operations.
    *   Implements "Live Config": Changes to checkboxes/selections are saved immediately.
*   **`headless.py` (VPS)**:
    *   Command-line interface for servers.
    *   Runs an interactive loop accepting commands like `.add`, `.list`, `.start`.
    *   Designed to be lightweight and robust for 24/7 operation.
## Setup & Deployment

### Desktop (GUI)
1.  **Windows**: Run `TelegramForwarder.exe`.
2.  **macOS**:
    *   **Option A (Easy)**: Download the Mac build from the GitHub Actions artifacts (if you set up the repo).
    *   **Option B (Manual)**: Run from source (see below).

### Running from Source (Mac/Linux)
1.  Install Python 3.8+ from [python.org](https://www.python.org/downloads/).
2.  Open Terminal and navigate to the folder.
3.  Install dependencies: `pip3 install -r requirements.txt`
4.  Run the app: `python3 main.py`

## Building for Mac (No Mac Required)
Since you cannot build a Mac app directly on Windows, we have included a **GitHub Actions** workflow.

1.  **Upload to GitHub**: Create a new repository and push this code.
2.  **Auto-Build**: Go to the "Actions" tab in your repository.
3.  **Download**: Click on the latest workflow run. You will see artifacts for `TelegramForwarder-Windows` and `TelegramForwarder-Mac`.
4.  **Run**: Download the Mac zip, extract it, and run the `.app`.

### Server (VPS)
1.  Upload the VPS package.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Run `python headless.py`.
4.  Use `.menu` to configure sources.
5.  Use `.start` to begin the background monitoring process.

## API Safety
To ensure the longevity of your Telegram account:
1.  **Delays**: The bot sleeps for a random interval (0.5s - 1.5s) after every message sent.
2.  **Error Handling**: If a flood wait error occurs, the bot logs it and pauses.
3.  **Rate Limits**: Avoid monitoring extremely high-traffic supergroups (10+ messages/second) with a single account.

## Troubleshooting
*   **Login Code Not Sending**: Check if you are logged in on your mobile device. Telegram sends the code there, not via SMS.
*   **"Session Revoked"**: If you log out from another device, delete the `.session` file and login again.
*   **Messages Not Arriving**:
    *   Check if the bot has permission to send messages in the Destination channel.
    *   Verify "Monitor All" is checked or the correct members are selected.

## Credits
Developed by **Zack Whitson**.

*   **Telegram**: [@definitezer0](https://t.me/definitezer0)
*   **X (Twitter)**: [Delirium_Pulse](https://x.com/Delirium_Pulse)
*   **Website**: [www.zackwhitson.com](http://www.zackwhitson.com)
*   **Upwork**: [Hire Me](https://www.upwork.com/freelancers/~01b74427823660e746)
