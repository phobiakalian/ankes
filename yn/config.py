"""Yn Security Bot - Configuration Module.

This module contains all configuration variables for the bot.
Copy this file to `config_local.py` and fill in your actual values.
"""

import os
from typing import List, Optional

# API keys

# Bot token from Bot Father
TOKEN: str = os.getenv("BOT_TOKEN", "")

# Telegram API ID and API hash
# Get it from https://my.telegram.org/apps
API_ID: int = int(os.getenv("API_ID", "0"))
API_HASH: str = os.getenv("API_HASH", "")

# Number of updates that can be processed in parallel
WORKERS: int = int(os.getenv("WORKERS", "24"))

# Chat used for logging (use your channel/group ID)
LOG_CHAT: Optional[int] = int(os.getenv("LOG_CHAT", "0")) or None

# List of disabled plugins
DISABLED_PLUGINS: List[str] = []

# Owner IDs (users who can access owner commands)
OWNER_IDS: List[int] = []

# Default settings
DEFAULT_MAX_WARNINGS: int = 3
DEFAULT_ACTION_MODE: str = "delete"  # delete, mute, ban

# Flood control settings
FLOOD_TIME_WINDOW: int = 60  # seconds
FLOOD_MESSAGE_LIMIT: int = 5  # messages per time window

# Tagall settings
TAGALL_CHUNK_SIZE: int = 10
TAGALL_DELAY: float = 2.0  # seconds between chunks
