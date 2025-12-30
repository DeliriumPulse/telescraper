Telegram Forwarder VPS (Headless)
=================================

A lightweight, command-line version of the Telegram Forwarder designed for running on servers (VPS) or in the background.

Features
--------
*   **Headless Operation**: Runs entirely in the terminal.
*   **Interactive CLI**: robust command menu for configuration.
*   **Scrape Mode**: Copies messages to bypass restrictions.
*   **Multi-Source**: Monitor multiple targets at once.
*   **Safety Delays**: Built-in rate limiting.

Installation
------------
1.  **Prerequisites**: Python 3.8+ installed.
2.  **Setup**:
    ```bash
    unzip TelegramForwarder_VPS.zip
    cd TelegramForwarder_VPS
    pip install -r requirements.txt
    ```

Usage
-----
1.  **Start the Bot**:
    ```bash
    python headless.py
    ```
2.  **First Run**:
    *   It will prompt for API ID, Hash, and Phone.
    *   Enter the login code sent to your Telegram.

3.  **Commands**:
    Once running, you can control the bot by typing commands into the terminal:

    *   `.menu`: Show the main interactive menu.
    *   `.status`: Show current monitoring status.
    *   `.add`: Add a new source group/channel to monitor.
    *   `.edit`: Edit an existing source configuration.
    *   `.remove`: Remove a source.
    *   `.list`: List all configured sources.
    *   `.search <query>`: Search for groups/channels.
    *   `.dest`: Configure destination channels.
    *   `.start`: **Start monitoring**.
    *   `.stop`: Stop monitoring.
    *   `.help`: Show all commands.

Configuration
-------------
*   **Credentials**: Stored in `.env`.
*   **Targets**: Stored in `targets.json`.
*   **Session**: Stored in `session_<phone>.session`.

Running in Background (Linux)
-----------------------------
To keep the bot running after you disconnect:

1.  Use `screen` or `tmux`:
    ```bash
    screen -S telegram_bot
    python headless.py
    # Press Ctrl+A, then D to detach
    ```
2.  To resume:
    ```bash
    screen -r telegram_bot
    ```

Credits
-------
Developed by Zack Whitson.

*   **Telegram**: [@definitezer0](https://t.me/definitezer0)
*   **X (Twitter)**: [Delirium_Pulse](https://x.com/Delirium_Pulse)
*   **Website**: [www.zackwhitson.com](http://www.zackwhitson.com)
*   **Upwork**: [Hire Me](https://www.upwork.com/freelancers/~01b74427823660e746)
