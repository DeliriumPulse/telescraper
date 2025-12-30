"""
Telegram Forwarder
Developed by Zack Whitson
Telegram: @definitezer0
X (Twitter): @Delirium_Pulse
Website: www.zackwhitson.com
Upwork: https://www.upwork.com/freelancers/~01b74427823660e746
"""
import os
from dotenv import load_dotenv, set_key

CONFIG_FILE = ".env"

def load_config():
    load_dotenv(CONFIG_FILE)
    return {
        "api_id": os.getenv("API_ID"),
        "api_hash": os.getenv("API_HASH"),
        "phone": os.getenv("PHONE")
    }

def save_config(api_id, api_hash, phone):
    # Create file if not exists
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            f.write("")
            
    set_key(CONFIG_FILE, "API_ID", str(api_id))
    set_key(CONFIG_FILE, "API_HASH", str(api_hash))
    set_key(CONFIG_FILE, "PHONE", str(phone))
