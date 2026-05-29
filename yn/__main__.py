"""Yn Security Bot - Main Entry Point."""

import asyncio
import logging
import os
import sys

from hydrogram import idle
from uvloop import install

from yn import LOOP
from yn.bot import Yn

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s.%(funcName)s | %(levelname)s | %(message)s",
    datefmt="[%X]",
)

# To avoid some annoying log
logging.getLogger("hydrogram.syncer").setLevel(logging.WARNING)
logging.getLogger("hydrogram.client").setLevel(logging.WARNING)

os.makedirs("downloads", exist_ok=True)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    ynankes = Yn()

    try:
        await ynankes.start()
        if "test" not in sys.argv:
            await idle()
    except KeyboardInterrupt:
        logger.warning("Forced stop… Bye!")
    finally:
        await ynankes.stop()


if __name__ == "__main__":
    install()
    LOOP.run_until_complete(main())