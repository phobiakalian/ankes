import logging
import time

import hydrogram
from hydrogram import Client
from hydrogram.enums import ParseMode
from hydrogram.errors import BadRequest
from hydrogram.raw.all import layer
from pytgcalls import PyTgCalls
from yn.config import API_HASH, API_ID, DISABLED_PLUGINS, LOG_CHAT, TOKEN, WORKERS

from . import __commit__, __version_number__

logger = logging.getLogger(__name__)

userbot = Client("user", api_id=API_ID, api_hash=API_HASH)
call = PyTgCalls(userbot)

class Yn(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            name=name,
            app_version=f"EduuRobot r{__version_number__} ({__commit__})",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token="7579188265:AAF0SA0wk1GWwRPF4ukm8caK9Z3TtIJF4L4",
            parse_mode=ParseMode.HTML,
            workers=WORKERS,
            plugins={"root": "yn.plugins", "exclude": DISABLED_PLUGINS},
            sleep_threshold=180,
        )

    async def start(self):
        await super().start()

        self.start_time = time.time()

        logger.info(
            "Yn running with Hydrogram v%s (Layer %s) started on @%s. Hi!",
            hydrogram.__version__,
            layer,
            self.me.username,
        )
        start_message = (
            "<b>Yn | Ankes started!</b>\n\n"
            f"<b>Version number:</b> <code>r{__version_number__} ({__commit__})</code>\n"
            f"<b>Hydrogram:</b> <code>v{hydrogram.__version__}</code>"
        )

        try:
            await self.send_message(chat_id=LOG_CHAT, text=start_message)
        except BadRequest:
            logger.warning("Unable to send message to LOG_CHAT.")

    async def stop(self):
        await super().stop()
        logger.warning("Yn stopped. Bye!")