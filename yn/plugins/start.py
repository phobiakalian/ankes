"""Yn Security Bot - Start Command Handler.

Module ini menangani perintah /start untuk pengguna privat dan mencatat statistik pengguna.
"""

from __future__ import annotations

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from yn.utils.db import db_users

# Template pesan sambutan
START_MESSAGE_TEMPLATE: str = (
    "👋 Halo, {0}!\n\n"
    "Selamat datang di <b>YNA Security Bot</b> — asisten moderasi otomatis untuk menjaga "
    "keamanan dan ketertiban dalam grup Telegram Anda.\n\n"
    "🔐 Bot ini dilengkapi dengan sistem filter, proteksi anti-bot, pemblokiran tautan, "
    "dan berbagai fitur lainnya yang dirancang untuk membantu admin dalam mengelola grup "
    "secara lebih efektif.\n\n"
    "Untuk memulai, Anda bisa:\n"
    "• Mengundang bot ke grup Anda\n"
    "• Melihat daftar fitur dan panduan penggunaannya\n\n"
    "Gunakan tombol di bawah ini untuk melanjutkan:"
)


def _register_user(user_id: int) -> None:
    """Mendaftarkan pengguna baru ke database.
    
    Args:
        user_id: ID Telegram pengguna yang akan didaftarkan.
    """
    try:
        # db_users adalah instance YnDB, bukan MongoDB Collection
        existing_user = db_users.find({"user_id": user_id})
        if not existing_user:
            from datetime import datetime
            db_users.insert_one({"user_id": user_id, "registered_at": datetime.utcnow().isoformat()})
    except Exception as e:
        # Log error tapi jangan crash bot
        print(f"[WARNING] Gagal mendaftarkan user {user_id}: {e}")


@Client.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, msg: Message) -> None:
    """Menangani perintah /start untuk chat privat.
    
    Fungsi ini akan:
    1. Mendaftarkan pengguna ke database jika belum terdaftar
    2. Mengirim pesan sambutan dengan keyboard inline
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan yang diterima
    """
    # Registrasi pengguna
    if msg.from_user:
        _register_user(msg.from_user.id)
    
    # Buat keyboard inline
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Tambahkan ke Grup",
                    url="https://t.me/ynankesbot?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton(
                    "📖 Bantuan & Perintah",
                    callback_data="help_main",
                )
            ],
        ]
    )
    
    # Kirim pesan sambutan
    await msg.reply(
        text=START_MESSAGE_TEMPLATE.format(msg.from_user.mention if msg.from_user else "Pengguna"),
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
