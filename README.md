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

## Telegram Commands (Headless Mode)

When running in VPS/Headless mode, you control the bot entirely via Telegram messages (Saved Messages).

### General
*   `.menu` / `.status`: Show the main dashboard with active sources and status.
*   `.start`: Start monitoring all configured sources.
*   `.stop`: Stop monitoring.

### Source Management
*   `.list [page]`: List all available groups and channels you can monitor.
*   `.search <text>`: Search for a specific group or channel by name.
*   `.add <id>`: Add a source to the monitoring list.
*   `.remove <id>`: Remove a source from monitoring.
*   `.edit <id>`: Select a source to modify its settings.

### Configuration (While Editing a Source)
*   `.mode`: Toggle between **Monitor All Messages** and **Monitor Specific Members**.
*   `.members [page]`: List members in the group (for selecting specific people).
*   `.select <id>`: Monitor this user's messages.
*   `.unselect <id>`: Stop monitoring this user.
*   `.done`: Save changes and exit edit mode.

### Destination Management
*   `.dest`: List current destination channels.
*   `.dest add <id>`: Add a destination (Channel ID or 'me' for Saved Messages).
*   `.dest del <id>`: Remove a destination.

## Configuration

The application uses two main files for configuration:
1.  **`.env`**: Stores your sensitive API credentials (API ID, Hash, Phone). This is created automatically on first login.
2.  **`targets.json`**: Stores your monitoring rules (Source Channels -> Destination Channels).

**Example `targets.json`**:
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

## Troubleshooting

*   **"Session Revoked"**: If you log out from another device, delete the `session_*.session` file and login again.
*   **Messages Not Arriving**:
    *   Check if the bot has permission to send messages in the Destination channel.
    *   Verify "Monitor All" is checked or the correct members are selected.
*   **Login Code Not Sending**: Check your Telegram app on your phone; the code is sent via Telegram, not SMS.

## Disclaimer

This tool is for educational and personal use only. The developers are not responsible for any misuse of this software or any bans resulting from excessive use. Please respect Telegram's Terms of Service and API usage limits.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

**Developed by Zack Whitson**

*   **Telegram**: [@definitezer0](https://t.me/definitezer0)
*   **X (Twitter)**: [Delirium_Pulse](https://x.com/Delirium_Pulse)
*   **Website**: [www.zackwhitson.com](http://www.zackwhitson.com)
*   **Upwork**: [Hire Me](https://www.upwork.com/freelancers/~01b74427823660e746)
