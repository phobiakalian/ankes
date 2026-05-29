"""Yn Security Bot - Telegram Client Module."""

import logging
import time
from typing import Final

import hydrogram
from hydrogram import Client
from hydrogram.enums import ParseMode
from hydrogram.errors import BadRequest
from hydrogram.raw.all import layer

from yn.config import API_HASH, API_ID, DISABLED_PLUGINS, LOG_CHAT, TOKEN, WORKERS
from yn import __commit__, __version_number__

logger: Final = logging.getLogger(__name__)


class Yn(Client):
    """Yn Security Bot - Telegram Group Management Bot."""

    def __init__(self) -> None:
        """Initialize the Yn bot client."""
        name: str = self.__class__.__name__.lower()

        super().__init__(
            name=name,
            app_version=f"Yn | Ankes r{__version_number__} ({__commit__})",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=TOKEN,
            parse_mode=ParseMode.HTML,
            workers=WORKERS,
            plugins={"root": "yn.plugins", "exclude": DISABLED_PLUGINS},
            sleep_threshold=180,
        )

    async def start(self) -> None:
        """Start the bot client."""
        await super().start()

        self.start_time: float = time.time()

        logger.info(
            "Yn running with Hydrogram v%s (Layer %s) started on @%s. Hi!",
            hydrogram.__version__,
            layer,
            self.me.username,
        )
        start_message: str = (
            "<b>Yn | Ankes started!</b>\n\n"
            f"<b>Version number:</b> <code>r{__version_number__} ({__commit__})</code>\n"
            f"<b>Hydrogram:</b> <code>v{hydrogram.__version__}</code>"
        )

        if LOG_CHAT:
            try:
                await self.send_message(chat_id=LOG_CHAT, text=start_message)
            except BadRequest:
                logger.warning("Unable to send message to LOG_CHAT.")

    async def stop(self) -> None:
        """Stop the bot client."""
        await super().stop()
        logger.warning("Yn stopped. Bye!")