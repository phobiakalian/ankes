"""Yn Security Bot - Admin Utilities."""

from functools import wraps
from typing import Callable, Any
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message


async def is_admin(bot, chat_id: int, user_id: int) -> bool:
    """Check if a user is an admin in the chat."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


def admin_check(func: Callable) -> Callable:
    """Decorator to check if the user is an admin before executing the command."""
    @wraps(func)
    async def wrapper(client, message: Message, *args, **kwargs) -> Any:
        if not message.from_user:
            return None
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        if not await is_admin(client, chat_id, user_id):
            await message.reply("⚠️ Hanya admin yang boleh menggunakan perintah ini.")
            return None
        
        return await func(client, message, *args, **kwargs)
    
    return wrapper