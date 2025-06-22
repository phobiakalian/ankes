from hydrogram import Client, filters
from hydrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from typing import Optional, Dict, Any

from hydrogram.errors.exceptions.bad_request_400 import MessageNotModified
from difflib import get_close_matches

from yn.utils.db import db 
from yn.utils.settings import get_group_settings, settings_keyboard
from yn.utils.utils import is_admin

def get_closest_feature_name(input_name: str, valid_features: set) -> str | None:
    matches = get_close_matches(input_name, valid_features, n=1, cutoff=0.6)
    return matches[0] if matches else None

def update_group_setting(chat_id: int, key: str, value: Any) -> None:
    db.update_one({"chat_id": chat_id}, {"$set": {key: value}})

@Client.on_message(filters.command("settings") & filters.group)
async def cmd_settings(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang boleh mengakses pengaturan.")
        return

    settings = get_group_settings(chat_id)
    keyboard = settings_keyboard(settings)
    await msg.reply("⚙️ Pengaturan Bot:", reply_markup=keyboard)


# --- Callback query handler ---

@Client.on_callback_query()
async def on_callback(client: Client, cb: CallbackQuery) -> None:
    chat = cb.message.chat
    
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id

    data = cb.data
    settings = get_group_settings(chat_id)

    if data.startswith("help_"):
        return

    if not await is_admin(client, chat_id, user_id):
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


@Client.on_message(filters.command("set") & filters.group)
async def cmd_set_feature(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        await msg.reply("<blockquote>🚫 Akses ditolak.\nHanya admin yang dapat menggunakan perintah ini.</blockquote>")
        return

    parts = msg.text.strip().split()
    if len(parts) != 3:
        await msg.reply(
            "<b>🔧 Format Salah!</b>\n\n"
            "<blockquote>"
            "Gunakan format:\n"
            "<code>/set &lt;fitur&gt; &lt;nilai&gt;</code>\n\n"
            "<b>Contoh:</b>\n"
            "<code>/set action mute</code>\n"
            "<code>/set maxwarning 5</code>\n"
            "<code>/set antiflood on</code>\n\n"
            "<b>Daftar Fitur:</b>\n"
            "• action: <i>delete | mute | ban</i>\n"
            "• maxwarning: <i>1 - 10</i> (khusus untuk <code>mute</code> / <code>ban</code>)\n"
            "• antiforward, nolinks, noevents, nocontacts, nolocations, nocommands, nohashtags, novoice,\n"
            "• imagefilter, antibot, antiflood, blacklist\n"
            "</blockquote>",
            quote=True
        )
        return

    _, feature, value = parts
    feature = feature.lower()
    value = value.lower()

    original_feature = feature

    # Tangani typo pada fitur
    valid_features = {
        "action", "maxwarning", "antiforward", "nolinks", "noevents", "nocontacts",
        "nolocations", "nocommands", "nohashtags", "novoice",
        "imagefilter", "antibot", "antiflood", "blacklist"
    }

    if feature not in valid_features:
        closest = get_closest_feature_name(feature, valid_features)
        if closest:
            feature = closest
            await msg.reply(f"⚠️ Fitur <b>{original_feature}</b> tidak ditemukan. Menggunakan <b>{feature}</b> sebagai pengganti.", quote=True)
        else:
            fitur_list = "\n".join(f"• <code>{f}</code>" for f in sorted(valid_features))
            await msg.reply(
                f"<blockquote>❌ Fitur <b>{original_feature}</b> tidak dikenal.\n\n"
                "Berikut fitur yang tersedia:\n"
                f"{fitur_list}</blockquote>",
                quote=True
            )
            return

    if feature == "action":
        if value not in {"delete", "mute", "ban"}:
            await msg.reply(
                "<blockquote>❌ Nilai <b>action</b> tidak valid.\n"
                "Hanya bisa menggunakan:\n"
                "• <code>delete</code>\n"
                "• <code>mute</code>\n"
                "• <code>ban</code></blockquote>"
            )
            return
        update_group_setting(chat_id, "action_mode", value)
        await msg.reply(
            f"<blockquote>✅ Mode tindakan berhasil diatur ke <b>{value}</b>.</blockquote>",
            quote=True
        )
        return

    if feature == "maxwarning":
        settings = get_group_settings(chat_id)
        if settings.get("action_mode", "delete") == "delete":
            await msg.reply("❌ <b>maxwarning</b> hanya berlaku jika <b>action</b> adalah <code>mute</code> atau <code>ban</code>.")
            return

        if not value.isdigit():
            await msg.reply("❌ Nilai harus berupa angka. Contoh: <code>/set maxwarning 5</code>")
            return
        num = int(value)
        if not (1 <= num <= 10):
            await msg.reply("❌ Nilai harus antara <code>1</code> sampai <code>10</code>.")
            return
        update_group_setting(chat_id, "max_warnings", num)
        await msg.reply(f"✅ Batas peringatan diatur menjadi <b>{num}</b>.", quote=True)
        return

    if value not in {"on", "off"}:
        await msg.reply(
            "<blockquote>❌ Nilai hanya bisa <code>on</code> atau <code>off</code>.\n"
            "Contoh: <code>/set antibot on</code></blockquote>",
            quote=True
        )
        return

    update_group_setting(chat_id, feature, value == "on")
    emoji = "✅" if value == "on" else "❌"
    status = "diaktifkan" if value == "on" else "dinonaktifkan"
    await msg.reply(
        f"<blockquote>{emoji} Fitur <b>{feature}</b> telah {status}.</blockquote>",
        quote=True
    )
