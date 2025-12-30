# Telegram Forwarder & Scraper

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Build Status](https://img.shields.io/github/actions/workflow/status/DeliriumPulse/telescraper/build.yml)

A powerful, user-friendly tool to scrape and forward messages from multiple Telegram groups and channels to your own destinations.

## Key Features

*   **Scrape Mode**: Copies messages instead of forwarding them. This bypasses "Copy Restricted" content and removes the "Forwarded from" tag.
*   **Multi-Source Monitoring**: Monitor multiple groups/channels simultaneously.
*   **Smart Configuration**: 
    *   Select a group -> Configure (Monitor All or Specific Members) -> Auto-saves.
    *   Switch between groups to configure them independently.
*   **Search Functionality**: Easily find groups and destinations with the built-in search bars.
*   **Auto-Login**: Automatically connects on launch if you have a saved session.
*   **Safety Delays**: Random delays (0.5s - 1.5s) between messages to protect your account from spam bans.
*   **Secure Storage**: Credentials are stored securely in a local `.env` file.
*   **Cross-Platform**: Runs on Windows, macOS, and Linux.

## Installation

### Windows (GUI)
1.  Download the latest release from the [Releases](https://github.com/DeliriumPulse/telescraper/releases) page (or build from source).
2.  Run `TelegramForwarder.exe`.
3.  Login with your API ID and Hash.

### macOS (GUI)
1.  Go to the **Actions** tab in this repository.
2.  Click on the latest successful build.
3.  Download the `TelegramForwarder-Mac` artifact.
4.  Unzip and run the `.app`.

### Running from Source (Linux/Mac/Windows)
1.  Clone the repository:
    ```bash
    git clone https://github.com/DeliriumPulse/telescraper.git
    cd telescraper
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## VPS / Headless Mode
For server deployments, use the headless version:
```bash
python headless.py
```
Type `.help` in the console for a list of commands.

## Credits

**Developed by Zack Whitson**

*   **Telegram**: [@definitezer0](https://t.me/definitezer0)
*   **X (Twitter)**: [Delirium_Pulse](https://x.com/Delirium_Pulse)
*   **Website**: [www.zackwhitson.com](http://www.zackwhitson.com)
*   **Upwork**: [Hire Me](https://www.upwork.com/freelancers/~01b74427823660e746)
