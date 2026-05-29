"""Yn Security Bot - Admin Commands Handler.

Module ini menyediakan perintah admin untuk moderasi grup seperti mute, unmute, dan ban.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from yn.utils.utils import is_admin

# Regex untuk parsing durasi (contoh: 1d, 2h, 30m, 45s)
DURATION_REGEX: re.Pattern[str] = re.compile(r"(\d+)([dhms])", re.IGNORECASE)


def parse_duration(text: str) -> int:
    """Mengonversi string durasi menjadi detik.
    
    Args:
        text: String durasi (contoh: "1d2h30m" atau "60s")
    
    Returns:
        Total durasi dalam detik.
    """
    total: int = 0
    for value, unit in DURATION_REGEX.findall(text):
        value_int = int(value)
        if unit.lower() == "d":
            total += value_int * 86400
        elif unit.lower() == "h":
            total += value_int * 3600
        elif unit.lower() == "m":
            total += value_int * 60
        elif unit.lower() == "s":
            total += value_int
    return total


def parse_mute_args(
    args_text: str,
    reply_message: Optional[Message],
) -> Tuple[Optional[int], int, str]:
    """Menganalisis argumen perintah mute/unmute.
    
    Args:
        args_text: Teks argumen dari perintah
        reply_message: Pesan yang dibalas (jika ada)
    
    Returns:
        Tuple berisi (target_user_id, duration_seconds, reason)
    """
    target_user_id: Optional[int] = None
    duration_seconds: int = 0
    reason: str = ""
    
    # Target dari reply message
    if reply_message and reply_message.from_user:
        target_user_id = reply_message.from_user.id
        duration_seconds = parse_duration(args_text)
        reason = DURATION_REGEX.sub("", args_text).strip() if duration_seconds else args_text.strip()
    
    # Target dari mention/ID
    elif args_text:
        parts = args_text.split()
        user_ref = parts[0]
        
        # Coba parse sebagai ID numerik
        try:
            target_user_id = int(user_ref)
        except ValueError:
            # Bukan ID numerik, bisa jadi username atau mention
            if user_ref.startswith("@"):
                # Username, perlu di-resolve oleh caller
                pass
            elif user_ref.startswith("tg://user?id="):
                # Mention link
                try:
                    target_user_id = int(user_ref.split("=")[1])
                except (ValueError, IndexError):
                    pass
        
        rest_text = " ".join(parts[1:]) if len(parts) > 1 else ""
        duration_seconds = parse_duration(rest_text)
        reason = DURATION_REGEX.sub("", rest_text).strip() if duration_seconds else rest_text.strip()
    
    return target_user_id, duration_seconds, reason


@Client.on_message(filters.command("mute") & filters.group)
async def mute_user(client: Client, msg: Message) -> None:
    """Membungkam pengguna di grup.
    
    Perintah ini hanya dapat digunakan oleh admin grup.
    Mendukung durasi custom (contoh: /mute @user 10m spam) dan alasan opsional.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    chat_id: int = msg.chat.id
    admin_id: int = msg.from_user.id if msg.from_user else 0
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, admin_id):
        await msg.reply("❌ Hanya admin yang bisa melakukan mute.")
        return
    
    # Parse argumen
    args_text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    target_user_id, duration_seconds, reason = parse_mute_args(args_text, msg.reply_to_message)
    
    # Jika target dari mention/username, resolve user
    if target_user_id is None and args_text:
        parts = args_text.split()
        user_ref = parts[0]
        try:
            user = await client.get_users(user_ref)
            target_user_id = user.id
        except Exception as e:
            await msg.reply(f"❌ Gagal menemukan user `{user_ref}`: {e}")
            return
    
    if target_user_id is None:
        await msg.reply("❗ Balas pesan user atau sebut username/ID setelah perintah.")
        return
    
    # Hitung waktu hingga mute berakhir
    until_date: Optional[datetime] = None
    if duration_seconds > 0:
        until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
    
    try:
        # Restrict permissions (mute)
        await client.restrict_chat_member(
            chat_id=chat_id,
            user_id=target_user_id,
            permissions=ChatPermissions(),
            until_date=until_date,
        )
        
        # Format pesan konfirmasi
        duration_str = f" selama {timedelta(seconds=duration_seconds)}" if until_date else " secara permanen"
        reason_str = f"\n📌 Alasan: {reason}" if reason else ""
        
        await msg.reply(
            f"🔇 <a href='tg://user?id={target_user_id}'>Pengguna</a> telah dimute{duration_str}.{reason_str}",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await msg.reply(f"⚠️ Gagal mute: {e}")


@Client.on_message(filters.command("unmute") & filters.group)
async def unmute_user(client: Client, msg: Message) -> None:
    """Membuka bungkam pengguna di grup.
    
    Perintah ini hanya dapat digunakan oleh admin grup.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    chat_id: int = msg.chat.id
    admin_id: int = msg.from_user.id if msg.from_user else 0
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, admin_id):
        await msg.reply("❌ Hanya admin yang bisa melakukan unmute.")
        return
    
    # Parse argumen
    args_text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    target_user_id: Optional[int] = None
    
    # Target dari reply message
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target_user_id = msg.reply_to_message.from_user.id
    
    # Target dari mention/ID
    elif args_text:
        try:
            user = await client.get_users(args_text)
            target_user_id = user.id
        except Exception as e:
            await msg.reply(f"❌ Gagal menemukan user: {e}")
            return
    
    if target_user_id is None:
        await msg.reply("❗ Balas pesan user atau sebut username/ID setelah perintah.")
        return
    
    try:
        # Restore permissions (unmute)
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
            user_id=target_user_id,
            permissions=permissions,
        )
        
        await msg.reply(
            f"🔈 <a href='tg://user?id={target_user_id}'>Pengguna</a> telah di-unmute.",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await msg.reply(f"⚠️ Gagal unmute: {e}")


@Client.on_message(filters.command("ban") & filters.group)
async def ban_user(client: Client, msg: Message) -> None:
    """Melarang pengguna dari grup.
    
    Perintah ini hanya dapat digunakan oleh admin grup.
    Mendukung durasi ban temporer dan alasan opsional.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    chat_id: int = msg.chat.id
    admin_id: int = msg.from_user.id if msg.from_user else 0
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, admin_id):
        await msg.reply("❌ Hanya admin yang bisa melakukan ban.")
        return
    
    # Parse argumen
    args_text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    target_user_id, duration_seconds, reason = parse_mute_args(args_text, msg.reply_to_message)
    
    # Jika target dari mention/username, resolve user
    if target_user_id is None and args_text:
        parts = args_text.split()
        user_ref = parts[0]
        try:
            user = await client.get_users(user_ref)
            target_user_id = user.id
        except Exception as e:
            await msg.reply(f"❌ Gagal menemukan user `{user_ref}`: {e}")
            return
    
    if target_user_id is None:
        await msg.reply("❗ Balas pesan user atau sebut username/ID setelah perintah.")
        return
    
    # Hitung waktu hingga ban berakhir (jika temporer)
    until_date: Optional[datetime] = None
    if duration_seconds > 0:
        until_date = datetime.utcnow() + timedelta(seconds=duration_seconds)
    
    try:
        # Ban user
        await client.ban_chat_member(
            chat_id=chat_id,
            user_id=target_user_id,
            until_date=until_date,
        )
        
        # Format pesan konfirmasi
        ban_type = "temporer" if until_date else "permanen"
        duration_str = f" ({timedelta(seconds=duration_seconds)})" if until_date else ""
        reason_str = f"\n📌 Alasan: {reason}" if reason else ""
        
        await msg.reply(
            f"🚫 <a href='tg://user?id={target_user_id}'>Pengguna</a> telah di-ban {ban_type}{duration_str}.{reason_str}",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await msg.reply(f"⚠️ Gagal ban: {e}")


@Client.on_message(filters.command("unban") & filters.group)
async def unban_user(client: Client, msg: Message) -> None:
    """Mencabut larangan pengguna dari grup.
    
    Perintah ini hanya dapat digunakan oleh admin grup.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    chat_id: int = msg.chat.id
    admin_id: int = msg.from_user.id if msg.from_user else 0
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, admin_id):
        await msg.reply("❌ Hanya admin yang bisa melakukan unban.")
        return
    
    # Parse argumen
    args_text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    target_user_id: Optional[int] = None
    
    # Target dari reply message
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target_user_id = msg.reply_to_message.from_user.id
    
    # Target dari mention/ID
    elif args_text:
        try:
            user = await client.get_users(args_text)
            target_user_id = user.id
        except Exception as e:
            await msg.reply(f"❌ Gagal menemukan user: {e}")
            return
    
    if target_user_id is None:
        await msg.reply("❗ Balas pesan user atau sebut username/ID setelah perintah.")
        return
    
    try:
        # Unban user
        await client.unban_chat_member(
            chat_id=chat_id,
            user_id=target_user_id,
        )
        
        await msg.reply(
            f"✅ <a href='tg://user?id={target_user_id}'>Pengguna</a> telah di-unban.",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await msg.reply(f"⚠️ Gagal unban: {e}")
