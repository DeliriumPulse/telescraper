Telescraper Client (GUI)
===============================

A powerful, user-friendly tool to scrape and forward messages from multiple Telegram groups and channels to your own destinations.

Features
--------
*   **Scrape Mode**: Copies messages instead of forwarding them. This bypasses "Copy Restricted" content and removes the "Forwarded from" tag.
*   **Multi-Source Monitoring**: Monitor multiple groups/channels simultaneously.
*   **Smart Configuration**: 
    *   Select a group -> Configure (Monitor All or Specific Members) -> Auto-saves.
    *   Switch between groups to configure them independently.
*   **Search Functionality**: Easily find groups and destinations with the built-in search bars.
*   **Auto-Login**: Automatically connects on launch if you have a saved session.
*   **Safety Delays**: Random delays (0.5s - 1.5s) between messages to protect your account from spam bans.
*   **Secure Storage**: Credentials are stored securely in a local `.env` file.

Installation & Setup
--------------------
**Windows:**
1.  **Download**: Extract `TelegramForwarder_Client.zip`.
2.  **Run**: Double-click `TelegramForwarder.exe`.

**macOS / Linux:**
1.  **Download**: Extract `TelegramForwarder_Source.zip`.
2.  **Install Python**: Make sure you have Python 3.8+ installed.
3.  **Install Deps**: Open Terminal, go to the folder, run `pip3 install -r requirements.txt`.
4.  **Run**: Execute `python3 main.py`.

3.  **Login**:
    *   Enter your API ID, API Hash, and Phone Number.
    *   (Get these from https://my.telegram.org/apps)
    *   Enter the code sent to your Telegram app.
    *   *Note: If you have 2FA enabled, enter your password.*

Usage Guide
-----------
1.  **Select Sources**:
    *   Use the "Target Selection" dropdown to pick a group/channel.
    *   **Monitor All**: Check "Monitor All Messages" to scrape everything from this source.
    *   **Specific Members**: Uncheck "Monitor All" and select specific users from the list.
    *   *Repeat this process for as many groups as you want. Your settings are saved automatically for each group.*

2.  **Select Destinations**:
    *   In the "Destination Selection" box, check the places you want messages to go.
    *   "Saved Messages" is your personal cloud storage.
    *   You can select multiple destinations.

3.  **Start**:
    *   Click **Start Monitor**.
    *   The bot is now running! It will scrape messages from ALL configured sources and send them to ALL selected destinations.

4.  **Stop**:
    *   Click **Stop Monitor** to pause. You can change settings and restart.

Troubleshooting
---------------
*   **"No running event loop"**: This has been fixed in the latest version.
*   **Login Issues**: Ensure your phone number includes the country code (e.g., +1...).
*   **Not Forwarding?**: Check the "Log Console" for errors. Ensure the source isn't empty.

Files
-----
*   `TelegramForwarder.exe`: The main application.
*   `.env`: Stores your API credentials (created after first login).
*   `targets.json`: Stores your monitoring configurations.
*   `session_*.session`: Your login session file. DO NOT SHARE THIS.

Credits
-------
Developed by Zack Whitson.

*   **Telegram**: [@definitezer0](https://t.me/definitezer0)
*   **X (Twitter)**: [Delirium_Pulse](https://x.com/Delirium_Pulse)
*   **Website**: [www.zackwhitson.com](http://www.zackwhitson.com)
*   **Upwork**: [Hire Me](https://www.upwork.com/freelancers/~01b74427823660e746)
