import asyncio
from typing import Optional, Dict, Any

from hydrogram import Client, filters
from hydrogram.types import (
    Message,
    ChatPermissions,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from hydrogram.enums import ChatMemberStatus
from hydrogram.errors.exceptions.bad_request_400 import MessageNotModified
import time
from collections import defaultdict

user_message_timestamps = defaultdict(list)
from db import YnDB  # Asumsi ini sudah sesuai implementasinya

API_TOKEN = "7579188265:AAEELB662s1GrCrqCjvgxYzEJWHfkEsJ3TI"

bot = Client(
    name="not",
    api_hash="d3a6dbd3e466159f7170f6af7fb35ac1",
    api_id=6973446,
    bot_token=API_TOKEN
)

# Database
db = YnDB("ankesDB.sqlite3", "groups")
db_warnings = YnDB("ankesDB.sqlite3", "warnings")
db_freeusers = YnDB("ankesDB.sqlite3", "freeusers")
db_authorize = YnDB("ankesDB.sqlite3", "authorize")

# --- Database helpers ---

def get_group_settings(chat_id: int) -> Dict[str, Any]:
    docs = db.find({"chat_id": chat_id})
    if docs:
        return docs[0]
    default = {
        "chat_id": chat_id,
        "antiforward": True,
        "nolinks": True,
        "noevents": False,
        "nocontacts": False,
        "nolocations": False,
        "nocommands": False,
        "nohashtags": False,
        "novoice": False,
        "imagefilter": False,
        "antibot": False,
        "antiflood": False,
        "blacklist": False,
        "action_mode": "delete",  # delete, mute, ban
        "max_warnings": 3,
        "badwords": [],  # daftar kata terlarang
    }
    db.insert_one(default)
    return default

def update_group_setting(chat_id: int, key: str, value: Any) -> None:
    db.update_one({"chat_id": chat_id}, {"$set": {key: value}})

def is_free_user(chat_id: int, user_id: int) -> bool:
    docs = db_freeusers.find({"chat_id": chat_id, "user_id": user_id})
    return len(docs) > 0

def add_free_user(chat_id: int, user_id: int) -> None:
    if not is_free_user(chat_id, user_id):
        db_freeusers.insert_one({"chat_id": chat_id, "user_id": user_id})

def remove_free_user(chat_id: int, user_id: int) -> None:
    db_freeusers.delete_one({"chat_id": chat_id, "user_id": user_id})

def get_warnings(chat_id: int, user_id: int) -> int:
    docs = db_warnings.find({"chat_id": chat_id, "user_id": user_id})
    if docs:
        return docs[0].get("count", 0)
    return 0

def add_warning(chat_id: int, user_id: int) -> int:
    docs = db_warnings.find({"chat_id": chat_id, "user_id": user_id})
    if not docs:
        db_warnings.insert_one({"chat_id": chat_id, "user_id": user_id, "count": 1})
        return 1
    count = docs[0]["count"] + 1
    db_warnings.update_one({"chat_id": chat_id, "user_id": user_id}, {"$set": {"count": count}})
    return count

def reset_warnings(chat_id: int, user_id: int) -> None:
    db_warnings.delete_one({"chat_id": chat_id, "user_id": user_id})

# --- Admin check ---

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False

# --- UI: Settings keyboard ---

def settings_keyboard(settings: Dict[str, Any]) -> InlineKeyboardMarkup:
    def on_off_button(name: str, label: str) -> InlineKeyboardButton:
        val = settings.get(name, False)
        emoji = "✅" if val else "❌"
        return InlineKeyboardButton(f"{emoji} {label}", callback_data=f"toggle_{name}")

    action_mode = settings.get("action_mode", "delete")
    mode_buttons = [
        InlineKeyboardButton("🗑️ Delete", callback_data="setaction_delete"),
        InlineKeyboardButton("🔇 Mute", callback_data="setaction_mute"),
        InlineKeyboardButton("⛔ Ban", callback_data="setaction_ban"),
    ]

    keyboard = [
        [on_off_button("antiforward", "Anti Forward"), on_off_button("nolinks", "Filter Links")],
        [on_off_button("noevents", "Filter Join/Left"), on_off_button("nocontacts", "Filter Contacts")],
        [on_off_button("nolocations", "Filter Locations"), on_off_button("nocommands", "Filter Commands")],
        [on_off_button("nohashtags", "Filter Hashtags"), on_off_button("novoice", "Filter Voice")],
        [on_off_button("blacklist", "Blacklist Domains"), on_off_button("antibot", "Anti Bot Add")],
        [on_off_button("antiflood", "AntiFlood"), on_off_button("imagefilter", "Anti-Image")],
        mode_buttons,
    ]

    if action_mode in ("mute", "ban"):
        keyboard.append([
            InlineKeyboardButton("➖", callback_data="warnings_minus"),
            InlineKeyboardButton(f"Max Warnings: {settings.get('max_warnings', 3)}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="warnings_plus"),
        ])

    keyboard.append([InlineKeyboardButton("❌ Tutup", callback_data="close_settings")])

    return InlineKeyboardMarkup(keyboard)

# --- Handle violation ---

async def handle_violation(client: Client, msg: Message) -> None:
    chat_id = msg.chat.id
    user = msg.from_user
    user_id = user.id if user else None
    if not user_id:
        return

    if is_free_user(chat_id, user_id):
        return
    
    if await is_admin(chat_id, user_id):
        return

    settings = get_group_settings(chat_id)
    action_mode = settings.get("action_mode", "delete")
    max_warn = settings.get("max_warnings", 3)

    warning_count = add_warning(chat_id, user_id)

    try:
        if action_mode == "delete":
            ok = await client.send_message(chat_id, f"<blockquote><b>⚠️ Notifikasi Message\n{user.mention} Dilarang mengirim pesan seperti itu.</b></blockquote>")
            await msg.delete()
            await asyncio.sleep(3)
            await ok.delete()

        elif action_mode == "mute":
            oke = await client.send_message(chat_id, f"{user.mention} Dilarang mengirim pesan seperti itu.")
            await msg.delete()
            await asyncio.sleep(3)
            await oke.delete()
            if warning_count >= max_warn:
                await msg.reply("⚠️ Kesempatan habis, anda akan di-mute 10 menit.")
                await bot.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=int(msg.date.timestamp()) + 600,
                )
                reset_warnings(chat_id, user_id)
            else:
                await msg.reply(f"🚫 Anda melanggar aturan. Kesempatan {warning_count}/{max_warn}.")

        elif action_mode == "ban":
            okee = await client.send_message(chat_id, f"{user.mention} Dilarang mengirim pesan seperti itu.")
            await msg.delete()
            await asyncio.sleep(3)
            await okee.delete()
            if warning_count >= max_warn:
                await msg.reply("⚠️ Kesempatan habis, anda akan di-ban.")
                await bot.ban_chat_member(chat_id, user_id)
                reset_warnings(chat_id, user_id)
            else:
                await msg.reply(f"🚫 Anda melanggar aturan. Kesempatan {warning_count}/{max_warn}.")

    except Exception:
        # Jangan crash bot jika error
        pass


@bot.on_message(filters.command("settings") & filters.group)
async def cmd_settings(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang boleh mengakses pengaturan.")
        return

    settings = get_group_settings(chat_id)
    keyboard = settings_keyboard(settings)
    await msg.reply("⚙️ Pengaturan Bot:", reply_markup=keyboard)

# --- Main message handler ---

@bot.on_message(filters.group)
async def on_message(client: Client, msg: Message) -> None:
    chat_id = msg.chat.id
    user = msg.from_user
    user_id = user.id if user else None

#    authorized = db_authorize.find({"chat_id": chat_id})

#    if not authorized:
#        try:
#            await client.send_message(chat_id, "⚠️ Layanan bot dihentikan karena grup ini belum membayar. Bot akan keluar otomatis. Hubungi admin bot untuk informasi lebih lanjut.\n\nAdmin : @phobiakalian")
#        except:
#            pass  # Jika tidak bisa reply
#        await client.leave_chat(chat_id)
#        return

    if not user_id:
        return

    settings = get_group_settings(chat_id)

    if is_free_user(chat_id, user_id):
        return

    # Filter kata terlarang
    badwords = settings.get("badwords", [])
    text = (msg.text or msg.caption or "").lower()
    if any(word in text for word in badwords):
        await handle_violation(client, msg)
        return

    if settings.get("antiforward", False) and msg.forward_date:
        await handle_violation(client, msg)
        return

    if settings.get("nolinks", False):
        if any(x in text for x in ["http://", "https://", "t.me", ".com"]):
            await handle_violation(client, msg)
            return

    if settings.get("noevents", False):
        if msg.new_chat_members or msg.left_chat_member:
            try:
                await msg.delete()
            except Exception:
                pass
            return

    if settings.get("nocontacts", False) and msg.contact:
        await handle_violation(client, msg)
        return

    if settings.get("nolocations", False) and msg.location:
        await handle_violation(client, msg)
        return

    if settings.get("nocommands", False) and msg.text and msg.text.startswith("/"):
        await handle_violation(client, msg)
        return

    if settings.get("nohashtags", False):
        if "#" in text:
            await handle_violation(client, msg)
            return

    if settings.get("novoice", False) and msg.voice:
        await handle_violation(client, msg)
        return
    
 #   if settings.get("novoice", False) and msg.video_note:
 #       await handle_violation(client, msg)
 #       return
    
    # --- Anti Bot ---
    if settings.get("antibot", False) and user.is_bot:
        await handle_violation(client, msg)
        return

    # --- Image Filter ---
    if settings.get("imagefilter", False) and msg.photo:
        await handle_violation(client, msg)
        return

    # --- Anti Flood ---
    if settings.get("antiflood", False):
        now = time.time()
        user_message_timestamps[(chat_id, user_id)].append(now)
        # Hapus timestamp yang lebih dari 60 detik lalu
        user_message_timestamps[(chat_id, user_id)] = [
            t for t in user_message_timestamps[(chat_id, user_id)] if now - t < 60
        ]

        if len(user_message_timestamps[(chat_id, user_id)]) >= 5:
            async for old_msg in client.get_chat_history(chat_id, limit=100):
                if old_msg.from_user and old_msg.from_user.id == user_id:
                    try:
                        await old_msg.delete()
                    except:
                        pass
            user_message_timestamps[(chat_id, user_id)].clear()
            return


    # TODO: Implement filters for imagefilter, antibot, antiflood, blacklist

# --- /badwords command for admin ---

@bot.on_message(filters.command("badwords") & filters.group)
async def cmd_badwords(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang boleh mengatur kata terlarang.")
        return

    parts = msg.text.split(maxsplit=2)
    if len(parts) < 2:
        await msg.reply("Gunakan:\n/badwords add <kata>\n/badwords rem <kata>\n/badwords list")
        return

    action = parts[1].lower()
    settings = get_group_settings(chat_id)
    badwords = settings.get("badwords", [])

    if action == "list":
        if badwords:
            await msg.reply("📋 Daftar kata terlarang:\n" + "\n".join(f"- {w}" for w in badwords))
        else:
            await msg.reply("📋 Tidak ada kata terlarang saat ini.")
        return

    if len(parts) < 3:
        await msg.reply("Masukkan kata yang ingin ditambahkan atau dihapus.")
        return

    word = parts[2].strip().lower()

    if action == "add":
        if word in badwords:
            await msg.reply(f"⚠️ Kata '{word}' sudah ada di daftar.")
        else:
            badwords.append(word)
            update_group_setting(chat_id, "badwords", badwords)
            await msg.reply(f"✅ Kata '{word}' berhasil ditambahkan ke daftar kata terlarang.")
        return

    if action == "rem":
        if word not in badwords:
            await msg.reply(f"⚠️ Kata '{word}' tidak ditemukan di daftar.")
        else:
            badwords.remove(word)
            update_group_setting(chat_id, "badwords", badwords)
            await msg.reply(f"✅ Kata '{word}' berhasil dihapus dari daftar kata terlarang.")
        return

    await msg.reply("Gunakan action yang benar: add, rem, atau list.")

# --- Callback query handler ---

@bot.on_callback_query()
async def on_callback(client: Client, cb: CallbackQuery) -> None:
    chat = cb.message.chat
    if chat.type not in ("supergroup", "group"):
        return
    
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id

    data = cb.data
    settings = get_group_settings(chat_id)

    if not await is_admin(chat_id, user_id):
        await cb.answer("⚠️ Hanya admin yang bisa mengatur.")
        return

    if data.startswith("toggle_"):
        key = data.split("_", 1)[1]
        current = settings.get(key, False)
        update_group_setting(chat_id, key, not current)
        new_settings = get_group_settings(chat_id)
        keyboard = settings_keyboard(new_settings)
        try:
            await cb.message.edit_reply_markup(keyboard)
        except MessageNotModified:
            pass
        await cb.answer(f"{key} di {'aktifkan' if not current else 'dinonaktifkan'}.")
        return

    if data.startswith("setaction_"):
        mode = data.split("_", 1)[1]
        update_group_setting(chat_id, "action_mode", mode)
        new_settings = get_group_settings(chat_id)
        keyboard = settings_keyboard(new_settings)
        try:
            await cb.message.edit_reply_markup(keyboard)
        except MessageNotModified:
            pass
        await cb.answer(f"Mode tindakan diatur ke {mode}.")
        return

    if data == "warnings_plus":
        max_warn = settings.get("max_warnings", 3)
        if max_warn < 10:
            max_warn += 1
            update_group_setting(chat_id, "max_warnings", max_warn)
        new_settings = get_group_settings(chat_id)
        keyboard = settings_keyboard(new_settings)
        try:
            await cb.message.edit_reply_markup(keyboard)
        except MessageNotModified:
            pass
        await cb.answer(f"Batas kesempatan diubah menjadi {max_warn}.")
        return

    if data == "warnings_minus":
        max_warn = settings.get("max_warnings", 3)
        if max_warn > 1:
            max_warn -= 1
            update_group_setting(chat_id, "max_warnings", max_warn)
        new_settings = get_group_settings(chat_id)
        keyboard = settings_keyboard(new_settings)
        try:
            await cb.message.edit_reply_markup(keyboard)
        except MessageNotModified:
            pass
        await cb.answer(f"Batas kesempatan diubah menjadi {max_warn}.")
        return

    if data == "close_settings":
        try:
            await cb.message.delete()
        except Exception:
            pass
        await cb.answer("Menu pengaturan ditutup.")
        return

    if data == "noop":
        await cb.answer()
        return

# --- /freeuser command ---

@bot.on_message(filters.command("freeuser") & filters.group)
async def cmd_freeuser(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang bisa mengatur free user.")
        return

    parts = msg.text.split()
    if len(parts) < 2:
        await msg.reply("Gunakan:\n/reply ke pesan atau /freeuser add @username\n/freeuser remove @username")
        return

    action = parts[1].lower()

    # Coba ambil target user dari reply
    target_user = None
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif len(parts) >= 3:
        try:
            target_user = await client.get_users(parts[2])
        except Exception:
            await msg.reply("⚠️ Username atau user ID tidak valid.")
            return
    else:
        await msg.reply("⚠️ Kamu harus membalas pesan pengguna atau memberikan @username/user_id.")
        return

    target_id = target_user.id
    username_display = f"@{target_user.username}" if target_user.username else target_user.mention

    if action == "add":
        add_free_user(chat_id, target_id)
        await msg.reply(f"✅ Pengguna {username_display} dimasukkan ke daftar free user.")
    elif action == "remove":
        remove_free_user(chat_id, target_id)
        await msg.reply(f"✅ Pengguna {username_display} dihapus dari daftar free user.")
    else:
        await msg.reply("Gunakan action yang benar: `add` atau `remove`.")



@bot.on_message(filters.command("authorize") & filters.private)
async def authorize_group(client: Client, msg: Message) -> None:
    if msg.from_user.id != 6304696376:
        await msg.reply("❌ Kamu tidak memiliki izin untuk menjalankan perintah ini.")
        return

    if len(msg.command) < 2:
        await msg.reply("Gunakan:\n/authorize <chat_id>")
        return

    try:
        chat_id = int(msg.command[1])
        if db_authorize.find({"chat_id": chat_id}):
            await msg.reply("✅ Grup sudah terdaftar sebagai authorized.")
        else:
            db_authorize.insert_one({"chat_id": chat_id})
            await msg.reply("✅ Grup berhasil ditambahkan ke daftar perizinan.")
    except ValueError:
        await msg.reply("⚠️ Format chat_id tidak valid.")


@bot.on_message(filters.command("unauthorize") & filters.private)
async def unauthorize_group(client: Client, msg: Message) -> None:
    if msg.from_user.id != 6304696376:
        await msg.reply("❌ Kamu tidak memiliki izin untuk menjalankan perintah ini.")
        return

    if len(msg.command) < 2:
        await msg.reply("Gunakan:\n/unauthorize <chat_id>")
        return

    try:
        chat_id = int(msg.command[1])
        result = db_authorize.delete_one({"chat_id": chat_id})
        if result:
            await msg.reply("❌ Grup berhasil dihapus dari daftar perizinan.")
        else:
            await msg.reply("⚠️ Grup tidak ditemukan dalam daftar perizinan.")
    except ValueError:
        await msg.reply("⚠️ Format chat_id tidak valid.")

Start_text = (
            "👋 Halo, {0}!\n\n"
            "Selamat datang di <b>YNA Security Bot</b> — asisten moderasi otomatis untuk menjaga keamanan dan ketertiban dalam grup Telegram Anda.\n\n"
            "🔐 Bot ini dilengkapi dengan sistem filter, proteksi anti-bot, pemblokiran tautan, dan berbagai fitur lainnya yang dirancang untuk membantu admin dalam mengelola grup secara lebih efektif.\n\n"
            "Untuk memulai, Anda bisa:\n"
            "• Mengundang bot ke grup Anda\n"
            "• Melihat daftar fitur dan panduan penggunaannya\n\n"
            "Gunakan tombol di bawah ini untuk melanjutkan:"
        )

@bot.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, msg: Message):
    await msg.reply(Start_text.format(msg.from_user.mention), reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Tambahkan ke Grup", url="https://t.me/ynankesbot?startgroup=true")],
        [InlineKeyboardButton("📖 Bantuan & Perintah", callback_data="help_main")]
    ])
    )
        


HELP_PAGES = {
    "start": {
        "text": (
            "👋 Halo, {0}!\n\n"
            "Selamat datang di <b>YNA Security Bot</b> — asisten moderasi otomatis untuk menjaga keamanan dan ketertiban dalam grup Telegram Anda.\n\n"
            "🔐 Bot ini dilengkapi dengan sistem filter, proteksi anti-bot, pemblokiran tautan, dan berbagai fitur lainnya yang dirancang untuk membantu admin dalam mengelola grup secara lebih efektif.\n\n"
            "Untuk memulai, Anda bisa:\n"
            "• Mengundang bot ke grup Anda\n"
            "• Melihat daftar fitur dan panduan penggunaannya\n\n"
            "Gunakan tombol di bawah ini untuk melanjutkan:"
        ),
        "buttons": [
            [("➕ Tambahkan ke Grup", "url:https://t.me/ynankesbot?startgroup=true")],
            [("📖 Bantuan & Perintah", "callback:help_main")],
        ],
    },
    "main": {
        "text": (
            "**📚 Bantuan & Panduan Penggunaan Bot**\n\n"
            "Silakan pilih salah satu kategori bantuan di bawah ini untuk mempelajari fitur yang tersedia serta cara menggunakannya:"
        ),
        "buttons": [
            [("📌 Fitur Umum", "callback:help_features")],
            [("🛡 Panduan Admin", "callback:help_admin")],
            [("🔒 Kebijakan Privasi", "callback:help_privacy")],
            [("🔙 Kembali", "callback:help_start")],
        ],
    },    
    "features": {
        "text": (
            "**📌 Fitur Umum yang Tersedia**\n\n"
            "Berikut adalah daftar fitur umum yang dapat diaktifkan di grup Anda untuk menjaga kenyamanan serta mengatur konten:\n\n"
            "• <b>Anti-Link</b>: Blokir pesan yang mengandung tautan\n"
            "• <b>Anti-Bot</b>: Cegah anggota menambahkan bot tanpa izin\n"
            "• <b>Filter Kata Kasar</b>: Deteksi dan hapus kata-kata tidak pantas\n"
            "• <b>Auto-Mute</b>: Otomatis bungkam anggota baru untuk waktu tertentu\n"
            "• <b>Anti-Spam</b>: Deteksi pengiriman pesan beruntun\n"
            "• <b>Notifikasi Join/Leave</b>: Menyembunyikan atau menampilkan pemberitahuan anggota keluar/masuk\n\n"
            "Gunakan perintah <code>/settings</code> atau menu admin untuk menyesuaikan fitur-fitur ini."
        ),
        "buttons": [
            [("🔙 Kembali", "callback:help_main")]
        ],
    },
    "admin": {
        "text": (
            "**🛡 Panduan Admin Grup**\n\n"
            "<blockquote>__Bot ini menyediakan berbagai fitur keamanan yang dapat membantu admin dalam menjaga ketertiban grup, memfilter konten yang tidak diinginkan, serta mencegah spam dan penyalahgunaan oleh anggota tidak bertanggung jawab.__</blockquote>\n\n"
            "Berikut daftar fitur keamanan yang tersedia. Klik salah satu untuk melihat penjelasan dan cara penggunaannya secara detail:"
        ),
        "buttons": [
            [("🤖 Anti-Bot", "callback:help_antibot"), ("🔁 Anti-Forward", "callback:help_antiforward")],
            [("🏷 Anti-Hashtags", "callback:help_Nohashtags"), ("💬 Anti-Flood", "callback:help_Noflood")],
            [("⛔️ Anti-Commands", "callback:help_Nocommands"), ("🎙 Anti-Voice Note", "callback:help_Novoice")],
            [("🚫 Blacklist", "callback:help_Blacklist")],
            [("📍 Filter Lokasi", "callback:help_Nolocations"), ("🔗 Filter Tautan", "callback:help_nolinks")],
            [("📅 Filter Event", "callback:help_noevents"), ("🖼 Filter Gambar", "callback:help_Noimage")],
            [("🔙 Kembali", "callback:help_main")],
        ],
    },
    "antiforward": {
        "text": "**🛡 Anti Forward Message**\n\n<blockquote>__Fitur antiforward dirancang untuk mencegah anggota grup mengirimkan pesan yang diteruskan (forwarded messages) dari chat atau grup lain. Pesan yang diteruskan sering kali dapat mengandung informasi yang tidak relevan, spam, atau bahkan konten yang tidak sesuai dengan kebijakan grup. Dengan mengaktifkan fitur ini, bot akan secara otomatis menghapus pesan yang berupa forward dan, bila perlu, memberikan peringatan kepada pengirimnya. Ini membantu menjaga orisinalitas dan kualitas diskusi dalam grup serta mencegah penyebaran konten yang tidak diinginkan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "antibot": {
        "text": "**🛡 Anti Bot Add**\n\n<blockquote>__Fitur antibot mencegah anggota biasa menambahkan bot lain ke dalam grup tanpa izin admin. Hal ini sangat penting untuk mencegah masuknya bot spam, bot berbahaya, atau bot yang mengganggu aktivitas grup. Ketika fitur ini aktif, hanya admin yang memiliki hak khusus yang dapat menambahkan bot ke dalam grup.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "nolinks": {
        "text": "**🛡 Filter Links**\n\n<blockquote>__Fitur nolinks secara aktif memindai setiap pesan yang dikirimkan anggota dan memblokir pesan yang mengandung tautan URL, baik berupa HTTP, HTTPS, tautan domain, maupun tautan Telegram (seperti t.me). Hal ini bertujuan untuk mengurangi risiko penyebaran spam, iklan, malware, atau link berbahaya lainnya yang dapat merugikan anggota grup. Dengan pengaturan ini, hanya pesan yang tidak mengandung tautan yang dapat dikirim, sehingga grup tetap terjaga dari konten berbahaya dan iklan yang tidak diinginkan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "noevents": {
        "text": "**🛡 Filtes Events**\n\n<blockquote>__Fitur noevents bertujuan untuk menonaktifkan atau menghalangi pesan yang berisi jenis-jenis event tertentu seperti undangan grup, stiker event, atau update acara yang tidak diinginkan. Ini membantu menjaga fokus diskusi di grup dan menghindari gangguan akibat pesan event yang tidak relevan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Nolocations": {
        "text": "**🛡 Anti Location**\n\n<blockquote>__Dengan fitur nolocations aktif, pengiriman lokasi (geotag, live location) di dalam grup akan dicegah. Ini bermanfaat untuk menghindari penyebaran informasi lokasi pribadi yang bisa menimbulkan risiko keamanan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Nocommands": {
        "text": "**🛡 Anti Commands**\n\n<blockquote>__Fitur ini mencegah anggota mengirimkan pesan yang berupa perintah (commands) bot tertentu secara tidak sengaja atau berlebihan, yang bisa mengganggu jalannya bot atau menyebabkan spam. Biasanya digunakan untuk membatasi command dari bot yang tidak diizinkan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Nohashtags": {
        "text": "**🛡 Anti Hashtags**\n\n<blockquote>__Dengan fitur nohashtags, pesan yang berisi tanda pagar (#) atau hashtag akan diblokir. Ini menghindari penyalahgunaan hashtag untuk promosi atau spam yang tidak sesuai dengan aturan grup.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Noflood": {
        "text": "**🛡 Anti Flood**\n\n<blockquote>__Antiflood adalah mekanisme untuk mencegah spam berlebihan atau pengiriman pesan terlalu cepat secara berturut-turut oleh anggota. Jika seseorang mengirim pesan dalam jumlah besar dalam waktu singkat, bot akan memberikan peringatan atau mengeluarkan sementara dari grup untuk menjaga kenyamanan anggota lain.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Blacklist": {
        "text": (
            "**🛡 Kata Terlarang**\n\n"
            "<blockquote>__Blacklist adalah daftar kata, frasa, atau pengguna yang dilarang di grup. Jika ada anggota yang menggunakan kata-kata terlarang atau masuk dalam daftar blacklist, bot akan secara otomatis menindak seperti menghapus pesan atau memberikan peringatan.__</blockquote>\n\n"
            "📌 <b>Cara Menggunakan Blacklist:</b>\n\n"
            "🔹 <b>Lihat daftar blacklist</b>\n"
            "<code>/badwords list</code>\n\n"
            "🔹 <b>Tambah kata ke blacklist</b>\n"
            "<code>/badwords add <kata></code>\n"
            "Contoh: <code>/badwords add goblok</code>\n\n"
            "🔹 <b>Hapus kata dari blacklist</b>\n"
            "<code>/badwords rem <kata></code>\n"
            "Contoh: <code>/badwords rem goblok</code>\n\n"
            "💡 Gunakan dengan bijak untuk menjaga kenyamanan grup."
        ),
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Novoice": {
        "text": "**🛡 Anti Voice Note**\n\n<blockquote>__Fitur ini melarang pengiriman pesan suara atau voice notes dalam grup. Sangat cocok untuk grup yang mengutamakan komunikasi tertulis agar suasana diskusi tetap kondusif dan tidak berisik.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Noimage": {
        "text": "**🛡 Anti Image**\n\n<blockquote>__Fitur imagefilter bertujuan untuk memfilter atau memblokir pengiriman gambar, foto, atau media visual tertentu yang tidak sesuai aturan grup. Bisa juga dikonfigurasi untuk memblokir gambar berukuran besar, gambar dengan konten tidak pantas, atau gambar dari sumber yang tidak terpercaya.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "privacy": {
        "text": "**📜 Kebijakan Privasi**\n\n<blockquote>Kami menghargai privasi dan keamanan data Anda. Kebijakan Privasi ini menjelaskan bagaimana kami mengumpulkan, menggunakan, menyimpan, dan melindungi informasi pribadi pengguna saat menggunakan layanan kami.</blockquote>\n\n"
                "**1. Informasi yang Kami Kumpulkan**\n<blockquote>"
                "- ID pengguna Telegram atau data publik lainnya dari platform tempat layanan dijalankan.\n"
                "- Data interaksi Anda dengan bot, seperti perintah yang digunakan dan preferensi pengaturan.\n"
                "- Informasi tambahan yang diberikan secara sukarela, seperti saran atau masukan.</blockquote>\n\n"
                "**2. Penggunaan Informasi**\n<blockquote>"
                "- Menyediakan dan meningkatkan layanan.\n"
                "- Personalisasi pengalaman pengguna.\n"
                "- Memastikan keamanan dan pencegahan penyalahgunaan.</blockquote>\n\n"
                "**3. Penyimpanan dan Keamanan**\n<blockquote>"
                "- Data disimpan secara lokal atau di server yang aman.\n"
                "- Kami mengambil langkah-langkah teknis dan organisasi yang wajar untuk melindungi data dari akses, perubahan, atau pengungkapan yang tidak sah.</blockquote>\n\n"
                "**4. Pembagian Data**\n<blockquote>"
                "- Kami tidak menjual, menyewakan, atau membagikan informasi pribadi Anda kepada pihak ketiga, kecuali jika diwajibkan oleh hukum.</blockquote>\n\n"
                "**5. Hak Pengguna**\n<blockquote>"
                "- Anda berhak meminta penghapusan data Anda.\n"
                "- Anda dapat menghubungi kami untuk informasi lebih lanjut terkait data yang disimpan.</blockquote>\n\n"
                "**6. Perubahan Kebijakan**\n<blockquote>"
                "- Kami berhak memperbarui kebijakan privasi ini kapan saja.\n"
                "- Perubahan akan diumumkan melalui saluran resmi atau langsung dalam layanan.</blockquote>\n\n"
                "**7. Kontak**\n<blockquote>"
                "Jika Anda memiliki pertanyaan mengenai kebijakan privasi ini, silakan hubungi admin kami:\n📩 Telegram: @phobiakalian</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_main")]
        ],
    },
}

def make_keyboard(buttons):
    keyboard = []
    for row in buttons:
        button_row = []
        for text, action in row:
            if action.startswith("callback:"):
                button_row.append(InlineKeyboardButton(text, callback_data=action.replace("callback:", "", 1)))
            elif action.startswith("url:"):
                button_row.append(InlineKeyboardButton(text, url=action.replace("url:", "", 1)))
        keyboard.append(button_row)
    return InlineKeyboardMarkup(keyboard)


@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
        page = HELP_PAGES["main"]
        await message.reply(
            page["text"],
            reply_markup=make_keyboard(page["buttons"])
        )

@bot.on_callback_query(filters.regex("^help_"))
async def help_callback(client: Client, callback_query: CallbackQuery):
        data = callback_query.data.replace("help_", "")
        page_key = data if data in HELP_PAGES else "main"
        page = HELP_PAGES[page_key]
        if page_key == "start":
            await callback_query.message.edit_text(
                page["text"].format(callback_query.from_user.mention),
                reply_markup=make_keyboard(page["buttons"])
            )
            return await callback_query.answer()
        await callback_query.message.edit_text(
            page["text"],
            reply_markup=make_keyboard(page["buttons"])
        )
        await callback_query.answer()


# --- Bot start ---
if __name__ == "__main__":
    print("Bot started...")
    asyncio.run(bot.run())
