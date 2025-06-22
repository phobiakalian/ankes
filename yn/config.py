from typing import List

# This is a template configuration file for EduuRobot.
# You can use this file as a base for your own config file by
# copying this file to `eduu/config.py` and filling in the values.
#


# API keys

# Bot token from Bot Father
TOKEN: str = "7579188265:AAEELB662s1GrCrqCjvgxYzEJWHfkEsJ3TI"

# Telegram API ID and API hash
# Get it from https://my.telegram.org/apps
API_ID: int = 6973446
API_HASH: str = "d3a6dbd3e466159f7170f6af7fb35ac1"

# Number of updates that can be processed in parallel
WORKERS = 24

# Chat used for logging
LOG_CHAT: int = -1002468368175


# List of disabled plugins
DISABLED_PLUGINS: List[str] = []