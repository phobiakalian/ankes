"""Yn core package."""

from subprocess import run
from collections import defaultdict


from yn.utils.db import db, db_warnings, db_freeusers, db_authorize, db_stats, db_users 

EMOJI_LIST = ["🙎🏿‍♀️", "🤤", "👨🏾‍🦯", "🥍", "💁🏽‍♀️", "🛎", "🫴🏿", "🧞", "🫅", "🦸", "🧙", "🧝", "🧛", "🧟"]
tagall_tasks = {}

user_message_timestamps = defaultdict(list)
user_message_ids = defaultdict(list)

__commit__ = (
    run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, check=False)
    .stdout.decode()
    .strip()
    or "None"
)

__version_number__ = (
    run(["git", "rev-list", "--count", "HEAD"], capture_output=True, check=False)
    .stdout.decode()
    .strip()
    or "0"
)