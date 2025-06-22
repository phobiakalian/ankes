
from hydrogram import Client, filters
from hydrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from yn.utils.db import db_users 

Start_text = (
            "👋 Halo, {0}!\n\n"
            "Selamat datang di <b>YNA Security Bot</b> — asisten moderasi otomatis untuk menjaga keamanan dan ketertiban dalam grup Telegram Anda.\n\n"
            "🔐 Bot ini dilengkapi dengan sistem filter, proteksi anti-bot, pemblokiran tautan, dan berbagai fitur lainnya yang dirancang untuk membantu admin dalam mengelola grup secara lebih efektif.\n\n"
            "Untuk memulai, Anda bisa:\n"
            "• Mengundang bot ke grup Anda\n"
            "• Melihat daftar fitur dan panduan penggunaannya\n\n"
            "Gunakan tombol di bawah ini untuk melanjutkan:"
        )

@Client.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, msg: Message):
    try:
        if db_users.find({"user_id": msg.chat.id}):
            pass
        else:
            db_users.insert_one({"user_id": msg.chat.id})
    except:
        pass
    await msg.reply(Start_text.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Tambahkan ke Grup", url="https://t.me/ynankesbot?startgroup=true")],
        [InlineKeyboardButton("📖 Bantuan & Perintah", callback_data="help_main")]
    ])
    ) 
    return
        