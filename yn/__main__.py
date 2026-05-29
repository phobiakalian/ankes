"""Yn Security Bot - Main Entry Point."""

import asyncio
import logging
import os
import sys
from signal import SIGINT, SIGTERM, signal

from pyrogram import idle
from uvloop import install

from yn import LOOP
from yn.bot import Yn

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s.%(funcName)s | %(levelname)s | %(message)s",
    datefmt="[%X]",
)

# To avoid some annoying log
logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
logging.getLogger("pyrogram.client").setLevel(logging.WARNING)

os.makedirs("downloads", exist_ok=True)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    ynankes = Yn()

    try:
        await ynankes.start()
        if "test" not in sys.argv:
            await idle()
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Forced stop… Bye!")
    finally:
        await ynankes.stop()


def handle_signal(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    raise SystemExit


if __name__ == "__main__":
    install()
    signal(SIGINT, handle_signal)
    signal(SIGTERM, handle_signal)
    LOOP.run_until_complete(main())