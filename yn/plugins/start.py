
from hydrogram import Client, filters
from hydrogram.types import Message


@Client.on_message(filters.command("start") & filters.group)
async def cmd_stats(client: Client, msg: Message):
    await client.send_messahe(msg.chat.id, "ppk")
