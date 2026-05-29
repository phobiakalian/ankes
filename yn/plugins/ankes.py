"""Yn Security Bot - Core Message Handler & Filters.

Module ini adalah inti dari sistem keamanan bot yang menangani semua filter dan proteksi grup.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message

from yn import user_message_timestamps, user_message_ids
from yn.utils.settings import get_group_settings
from yn.utils.utils import is_admin
from yn.utils import (
    add_violation_stat,
    is_free_user,
    log_user_message,
    add_warning,
    reset_warnings,
)


def contains_link(message: Message) -> bool:
    """Memeriksa apakah pesan mengandung tautan.
    
    Args:
        message: Objek pesan untuk diperiksa
    
    Returns:
        True jika pesan mengandung URL atau text_link, False sebaliknya.
    """
    entities = (message.entities or []) + (message.caption_entities or [])
    return any(ent.type in ("url", "text_link") for ent in entities)


async def handle_violation(client: Client, msg: Message, violation_type: str = "") -> None:
    """Menangani pelanggaran aturan grup.
    
    Fungsi ini memproses tindakan berdasarkan mode yang diatur (delete/mute/ban)
    dan mencatat statistik pelanggaran.
    
    Args:
        client: Instance klien Hydrogram
        msg: Pesan yang melanggar aturan
        violation_type: Jenis pelanggaran (opsional, untuk logging)
    """
    chat_id: int = msg.chat.id
    user = msg.from_user
    user_id: Optional[int] = user.id if user else None
    
    if not user_id:
        return
    
    # Abaikan free users dan admin
    if is_free_user(chat_id, user_id):
        return
    
    if await is_admin(client, chat_id, user_id):
        return
    
    # Dapatkan pengaturan grup
    settings = get_group_settings(chat_id)
    action_mode: str = settings.get("action_mode", "delete")
    max_warn: int = settings.get("max_warnings", 3)
    
    # Tambahkan warning
    warning_count: int = add_warning(chat_id, user_id)
    user_mention: str = user.mention if user else "Pengguna"
    
    try:
        if action_mode == "delete":
            # Hanya hapus pesan dan beri notifikasi
            notification = await client.send_message(
                chat_id,
                f"<blockquote><b>⚠️ Notifikasi Pelanggaran</b>\n"
                f"{user_mention} Dilarang mengirim {violation_type or 'pesan seperti itu'}.</blockquote>",
            )
            await msg.delete()
            await asyncio.sleep(3)
            await notification.delete()
        
        elif action_mode == "mute":
            # Hapus pesan, beri notifikasi, dan mute jika warning habis
            notification = await client.send_message(
                chat_id,
                f"<blockquote><b>⚠️ Notifikasi Pelanggaran</b>\n"
                f"{user_mention} Dilarang mengirim {violation_type or 'pesan seperti itu'}.</blockquote>",
            )
            await msg.delete()
            await asyncio.sleep(3)
            await notification.delete()
            
            if warning_count >= max_warn:
                await client.send_message(
                    chat_id,
                    f"⚠️ Kesempatan habis, {user_mention} akan di-mute selama 10 menit.",
                )
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=datetime.utcnow() + timedelta(seconds=600),
                )
                reset_warnings(chat_id, user_id)
            else:
                await client.send_message(
                    chat_id,
                    f"🚫 {user_mention} melanggar aturan. Peringatan: {warning_count}/{max_warn}.",
                )
        
        elif action_mode == "ban":
            # Hapus pesan, beri notifikasi, dan ban jika warning habis
            notification = await client.send_message(
                chat_id,
                f"{user_mention} Dilarang mengirim {violation_type or 'pesan seperti itu'}.",
            )
            await msg.delete()
            await asyncio.sleep(3)
            await notification.delete()
            
            if warning_count >= max_warn:
                await client.send_message(
                    chat_id,
                    f"⚠️ Kesempatan habis, {user_mention} akan di-ban dari grup.",
                )
                await client.ban_chat_member(chat_id, user_id)
                reset_warnings(chat_id, user_id)
            else:
                await client.send_message(
                    chat_id,
                    f"🚫 {user_mention} melanggar aturan. Peringatan: {warning_count}/{max_warn}.",
                )
        
        # Catat statistik pelanggaran
        add_violation_stat(chat_id, user_id, user_mention)
    
    except Exception as e:
        # Log error tapi jangan crash bot
        print(f"[ERROR] Gagal menangani pelanggaran: {e}")


@Client.on_message(filters.group & ~filters.service)
async def on_message(client: Client, msg: Message) -> None:
    """Handler utama untuk semua pesan di grup.
    
    Fungsi ini memeriksa setiap pesan terhadap semua filter yang aktif
    dan mengambil tindakan sesuai pengaturan grup.
    
    Args:
        client: Instance klien Hydrogram
        msg: Pesan yang diterima
    """
    chat_id: int = msg.chat.id
    user = msg.from_user
    user_id: Optional[int] = user.id if user else None
    user_mention: str = user.mention if user else "Pengguna"
    
    # Log pesan untuk statistik
    if user_id:
        log_user_message(chat_id, user_id, user_mention)
    else:
        return
    
    # Dapatkan pengaturan grup
    settings = get_group_settings(chat_id)
    
    # Abaikan free users
    if user_id and is_free_user(chat_id, user_id):
        return
    
    # Ekstrak teks pesan (dari text atau caption)
    text: str = (msg.text or msg.caption or "").lower()
    
    # === FILTER KATA TERLARANG ===
    badwords = settings.get("badwords", [])
    if badwords and any(word in text for word in badwords):
        await handle_violation(client, msg, "kata terlarang")
        return
    
    # === ANTI FORWARD ===
    if settings.get("antiforward", False) and msg.forward_date:
        await handle_violation(client, msg, "pesan forward")
        return
    
    # === ANTI LINKS ===
    if settings.get("nolinks", False) and contains_link(msg):
        await handle_violation(client, msg, "tautan/link")
        return
    
    # === NO EVENTS (Join/Leave messages) ===
    if settings.get("noevents", False):
        if msg.new_chat_members or msg.left_chat_member:
            try:
                await msg.delete()
            except Exception:
                pass
            return
    
    # === NO CONTACTS ===
    if settings.get("nocontacts", False) and msg.contact:
        await handle_violation(client, msg, "kontak")
        return
    
    # === NO LOCATIONS ===
    if settings.get("nolocations", False) and msg.location:
        await handle_violation(client, msg, "lokasi")
        return
    
    # === NO COMMANDS ===
    if settings.get("nocommands", False) and msg.text and msg.text.startswith("/"):
        await handle_violation(client, msg, "perintah/command")
        return
    
    # === NO HASHTAGS ===
    if settings.get("nohashtags", False) and "#" in text:
        await handle_violation(client, msg, "hashtag")
        return
    
    # === NO VOICE NOTES ===
    if settings.get("novoice", False) and (msg.voice or msg.video_note):
        await handle_violation(client, msg, "voice note")
        return
    
    # === ANTI BOT ===
    if settings.get("antibot", False) and user and user.is_bot:
        await handle_violation(client, msg, "bot")
        return
    
    # === IMAGE FILTER ===
    if settings.get("imagefilter", False) and msg.photo:
        await handle_violation(client, msg, "gambar/foto")
        return
    
    # === ANTI FLOOD ===
    if settings.get("antiflood", False) and user_id:
        now: float = time.time()
        key: tuple[int, int] = (chat_id, user_id)
        
        # Tambahkan timestamp dan message ID
        user_message_timestamps[key].append(now)
        user_message_ids[key].append(msg.id)
        
        # Bersihkan timestamp lama (> 60 detik)
        user_message_timestamps[key] = [t for t in user_message_timestamps[key] if now - t < 60]
        
        # Batasi penyimpanan message ID (maksimal 5)
        user_message_ids[key] = user_message_ids[key][-5:]
        
        # Deteksi flood (>= 5 pesan dalam 60 detik)
        if len(user_message_timestamps[key]) >= 5:
            # Hapus semua pesan spam
            for mid in user_message_ids[key]:
                try:
                    await client.delete_messages(chat_id, mid)
                except Exception:
                    pass
            
            user_message_timestamps[key].clear()
            user_message_ids[key].clear()
            
            # Catat pelanggaran
            add_violation_stat(chat_id, user_id, user_mention)
            
            # Notifikasi anti-flood
            notification = await client.send_message(
                chat_id,
                f"<blockquote><b>⚠️ Notifikasi Anti-Flood</b>\n"
                f"{user_mention} mengirim terlalu banyak pesan dalam waktu singkat.</blockquote>",
            )
            await asyncio.sleep(3)
            await notification.delete()
            
            # Dapatkan action mode untuk tindakan lanjutan
            action = settings.get("action_mode", "delete")
            
            if action == "delete":
                return
            
            # Tambahkan warning dan ambil tindakan
            warning_count = add_warning(chat_id, user_id)
            max_warn = settings.get("max_warnings", 3)
            
            if warning_count >= max_warn:
                if action == "mute":
                    await client.send_message(
                        chat_id,
                        f"<blockquote>🔇 {user_mention} telah dimute selama 10 menit karena spam.</blockquote>",
                    )
                    await client.restrict_chat_member(
                        chat_id,
                        user_id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=datetime.utcnow() + timedelta(seconds=600),
                    )
                
                elif action == "ban":
                    await client.send_message(
                        chat_id,
                        f"<blockquote>🚫 {user_mention} dilarang dari grup karena spam berlebihan.</blockquote>",
                    )
                    await client.ban_chat_member(chat_id, user_id)
                
                reset_warnings(chat_id, user_id)
            else:
                await client.send_message(
                    chat_id,
                    f"<blockquote>🚫 {user_mention}, kamu melanggar batas pengiriman pesan (flooding).\n"
                    f"Peringatan: {warning_count} dari {max_warn}.</blockquote>",
                )
            return
        
        return
