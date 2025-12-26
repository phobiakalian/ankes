from typing import List

# This is a template configuration file for EduuRobot.
# You can use this file as a base for your own config file by
# copying this file to `eduu/config.py` and filling in the values.
#


# API keys

# Bot token from Bot Father
TOKEN: str = ""

# Telegram API ID and API hash
# Get it from https://my.telegram.org/apps
API_ID: int = 12345
API_HASH: str = ""

# Number of updates that can be processed in parallel
WORKERS = 24

# Chat used for logging
LOG_CHAT: int = -100000000000


# List of disabled plugins
DISABLED_PLUGINS: List[str] = []
