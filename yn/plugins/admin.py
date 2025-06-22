import re
from datetime import datetime, timedelta
from hydrogram import Client, filters
from hydrogram.types import Message, ChatPermissions
from yn.utils.utils import is_admin

# Regex untuk parsing durasi
DURATION_REGEX = re.compile(r"(\d+)([dhms])", re.IGNORECASE)

def parse_duration(text: str) -> int:
    total = 0
    for value, unit in DURATION_REGEX.findall(text):
        value = int(value)
        if unit.lower() == "d":
            total += value * 86400
        elif unit.lower() == "h":
            total += value * 3600
        elif unit.lower() == "m":
            total += value * 60
        elif unit.lower() == "s":
            total += value
    return total

# --- /mute command ---
@Client.on_message(filters.command("mute") & filters.group)
async def mute_user(client: Client, msg: Message):
    chat_id = msg.chat.id
    admin_id = msg.from_user.id

    if not await is_admin(client, chat_id, admin_id):
        await msg.reply("❌ Hanya admin yang bisa melakukan mute.")
        return

    args_text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    target_user = None
    reason = ""
    duration_seconds = 0

    # --- TARGET: REPLY ---
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
        duration_seconds = parse_duration(args_text)
        reason = DURATION_REGEX.sub("", args_text).strip() if duration_seconds else args_text.strip()

    # --- TARGET: MENTION/ID ---
    elif args_text:
        parts = args_text.split()
        user_ref = parts[0]
        try:
            target_user = await client.get_users(user_ref)
        except Exception as e:
            await msg.reply(f"❌ Gagal menemukan user `{user_ref}`: {e}")
            return

        rest_text = " ".join(parts[1:]) if len(parts) > 1 else ""
        duration_seconds = parse_duration(rest_text)
        reason = DURATION_REGEX.sub("", rest_text).strip() if duration_seconds else rest_text.strip()
    else:
        await msg.reply("❗ Balas pesan user atau sebut username/ID setelah perintah.")
        return

    until_date = datetime.utcnow() + timedelta(seconds=duration_seconds) if duration_seconds else None

    try:
        await client.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=ChatPermissions(),
            until_date=until_date,
        )

        duration_str = f" selama {timedelta(seconds=duration_seconds)}" if until_date else " secara permanen"
        reason_str = f"\n📌 Alasan: {reason}" if reason else ""
        await msg.reply(
            f"🔇 <a href='tg://user?id={target_user.id}'>Pengguna</a> telah dimute{duration_str}.{reason_str}",
            disable_web_page_preview=True
        )
    except Exception as e:
        await msg.reply(f"⚠️ Gagal mute: {e}")

# --- /unmute command ---
@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client: Client, msg: Message):
    chat_id = msg.chat.id
    admin_id = msg.from_user.id

    if not await is_admin(client, chat_id, admin_id):
        await msg.reply("❌ Hanya admin yang bisa melakukan unmute.")
        return

    args_text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    target_user = None

    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif args_text:
        try:
            target_user = await client.get_users(args_text)
        except Exception as e:
            await msg.reply(f"❌ Gagal menemukan user: {e}")
            return
    else:
        await msg.reply("❗ Balas pesan user atau sebut username/ID setelah perintah.")
        return

    try:
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False,
        )

        await client.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user.id,
            permissions=permissions,
        )

        await msg.reply(
            f"🔈 <a href='tg://user?id={target_user.id}'>Pengguna</a> telah di-unmute.",
            disable_web_page_preview=True
        )
    except Exception as e:
        await msg.reply(f"⚠️ Gagal unmute: {e}")
