"""Yn Security Bot - Core Package."""

import asyncio
from collections import defaultdict
from subprocess import run

from yn.utils.db import (
    db,
    db_warnings,
    db_freeusers,
    db_authorize,
    db_stats,
    db_users,
)

LOOP = asyncio.get_event_loop()

EMOJI_LIST = [
    "🙎🏿‍♀️",
    "🤤",
    "👨🏾‍🦯",
    "🥍",
    "💁🏽‍♀️",
    "🛎",
    "🫴🏿",
    "🧞",
    "🫅",
    "🦸",
    "🧙",
    "🧝",
    "🧛",
    "🧟",
]

tagall_tasks: dict = {}
user_message_timestamps: defaultdict = defaultdict(list)
user_message_ids: defaultdict = defaultdict(list)


def _get_git_commit() -> str:
    """Get the current git commit hash."""
    try:
        return (
            run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, check=False)
            .stdout.decode()
            .strip()
            or "None"
        )
    except Exception:
        return "None"


def _get_version_number() -> str:
    """Get the current version number from git."""
    try:
        return (
            run(["git", "rev-list", "--count", "HEAD"], capture_output=True, check=False)
            .stdout.decode()
            .strip()
            or "0"
        )
    except Exception:
        return "0"


__commit__ = _get_git_commit()
__version_number__ = _get_version_number()
__version__ = f"r{__version_number__} ({__commit__})"