"""Yn Security Bot - Admin Utilities."""

from hydrogram.enums import ChatMemberStatus


async def is_admin(bot, chat_id: int, user_id: int) -> bool:
    """Check if a user is an admin in the chat."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False