"""Yn core package."""

from subprocess import run
from yn.utils.db import YnDB 


db_users = YnDB("users.sqlite3", "users")

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