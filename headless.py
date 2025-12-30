"""
Telescraper
Developed by Zack Whitson
Telegram: @definitezer0
X (Twitter): @Delirium_Pulse
Website: www.zackwhitson.com
Upwork: https://www.upwork.com/freelancers/~01b74427823660e746
"""
import asyncio
import json
import os
import sys
from client_manager import ClientManager

# File paths
CONFIG_FILE = "config.json"
TARGETS_FILE = "targets.json"

def load_json(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return None
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

async def main():
    print("Starting Headless Telescraper...")

    # Load Config
    config = load_json(CONFIG_FILE)
    if not config:
        print("Please upload config.json from your local machine.")
        return

    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    phone = config.get("phone")

    if not api_id or not api_hash or not phone:
        print("Invalid config.json.")
        return

    try:
        api_id = int(api_id)
    except ValueError:
        print("Error: api_id in config.json must be a number.")
        return

    # Initialize ClientManager
    manager = ClientManager()

    # Connect signals to print (since we have no GUI)
    manager.log_signal.connect(lambda msg: print(f"[LOG] {msg}"))
    manager.login_failed_signal.connect(lambda err: print(f"[ERROR] Login Failed: {err}"))
    
    # Connect
    print("Connecting...")
    await manager.connect_client(api_id, api_hash, phone)

    # Wait for connection/authorization
    # Since connect_client is async but returns before full auth in some cases (if code needed),
    # we need to check status. But for headless, we assume session file is valid.
    
    if not await manager.client.is_user_authorized():
        print("Error: Session not authorized.")
        print("Please make sure you upload the 'session_...' file from your local machine.")
        return

    print(f"Logged in as: {(await manager.client.get_me()).first_name}")

    # Start monitoring
    if manager.sources:
        print(f"Starting monitoring for {len(manager.sources)} sources...")
        manager.start_monitoring()
    else:
        print("No sources configured in targets.json. Please configure via GUI or Telegram commands.")

    print("Headless mode running. Send commands to 'Saved Messages' to control.")
    print("Press Ctrl+C to stop.")
    
    await manager.client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
