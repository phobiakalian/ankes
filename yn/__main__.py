import asyncio
import logging
import platform
import sys
import os
from hydrogram import idle

from yn.bot import Yn, userbot, call

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

try:
    import uvloop

    uvloop.install()
except ImportError:
    if platform.system() != "Windows":
        logger.warning("uvloop is not installed and therefore will be disabled.")


async def main():
    ynankes = Yn()

    try:
        await ynankes.start()
        await userbot.start()
        await call.start()
        if "test" not in sys.argv:
            await idle()
    except KeyboardInterrupt:
        # exit gracefully
        logger.warning("Forced stop… Bye!")
    finally:
        await ynankes.stop()


if __name__ == "__main__":
    # open new asyncio event loop
    event_policy = asyncio.get_event_loop_policy()
    event_loop = event_policy.new_event_loop()
    asyncio.set_event_loop(event_loop)

    # start the bot
    event_loop.run_until_complete(main())

    # close asyncio event loop
    event_loop.close()