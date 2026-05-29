"""Yn Security Bot - Settings Handler.

Module ini menyediakan sistem pengaturan grup dengan GUI inline keyboard dan perintah teks.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from hydrogram import Client, filters
from hydrogram.errors.exceptions.bad_request_400 import MessageNotModified
from hydrogram.types import CallbackQuery, Message

from yn.utils import get_closest_feature_name, update_group_setting
from yn.utils.settings import get_group_settings, settings_keyboard
from yn.utils.utils import is_admin


@Client.on_message(filters.command("settings") & filters.group)
async def cmd_settings(client: Client, msg: Message) -> None:
    """Menampilkan menu pengaturan grup dengan inline keyboard.
    
    Hanya admin grup yang dapat mengakses menu ini.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    user_id: int = msg.from_user.id if msg.from_user else 0
    chat_id: int = msg.chat.id
    
    if not await is_admin(client, chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang boleh mengakses pengaturan.")
        return
    
    settings: Dict[str, Any] = get_group_settings(chat_id)
    keyboard = settings_keyboard(settings)
    await msg.reply("⚙️ Pengaturan Bot:", reply_markup=keyboard)


@Client.on_callback_query()
async def on_callback(client: Client, cb: CallbackQuery) -> None:
    """Menangani callback query untuk pengaturan grup.
    
    Handler ini mengelola:
    - Toggle fitur (toggle_*)
    - Set action mode (setaction_*)
    - Adjust max warnings (warnings_plus/minus)
    - Close settings (close_settings)
    
    Args:
        client: Instance klien Hydrogram
        cb: Objek callback query
    """
    chat_id: int = cb.message.chat.id
    user_id: int = cb.from_user.id
    data: str = cb.data
    
    # Abaikan callback help (ditangani oleh help.py)
    if data.startswith("help_"):
        return
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, user_id):
        await cb.answer("⚠️ Hanya admin yang bisa mengatur.")
        return
    
    settings: Dict[str, Any] = get_group_settings(chat_id)
    
    # === TOGGLE FITUR ===
    if data.startswith("toggle_"):
        key: str = data.split("_", 1)[1]
        current: bool = settings.get(key, False)
        update_group_setting(chat_id, key, not current)
        
        new_settings = get_group_settings(chat_id)
        keyboard = settings_keyboard(new_settings)
        
        try:
            await cb.message.edit_reply_markup(keyboard)
        except MessageNotModified:
            pass
        
        status = "aktifkan" if not current else "dinonaktifkan"
        await cb.answer(f"{key} di{status}.")
        return
    
    # === SET ACTION MODE ===
    if data.startswith("setaction_"):
        mode: str = data.split("_", 1)[1]
        update_group_setting(chat_id, "action_mode", mode)
        
        new_settings = get_group_settings(chat_id)
        keyboard = settings_keyboard(new_settings)
        
        try:
            await cb.message.edit_reply_markup(keyboard)
        except MessageNotModified:
            pass
        
        await cb.answer(f"Mode tindakan diatur ke {mode}.")
        return
    
    # === INCREASE MAX WARNINGS ===
    if data == "warnings_plus":
        max_warn: int = settings.get("max_warnings", 3)
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
    
    # === DECREASE MAX WARNINGS ===
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
    
    # === CLOSE SETTINGS ===
    if data == "close_settings":
        try:
            await cb.message.delete()
        except Exception:
            pass
        await cb.answer("Menu pengaturan ditutup.")
        return
    
    # === NOOP (untuk tombol disabled) ===
    if data == "noop":
        await cb.answer()
        return


@Client.on_message(filters.command("set") & filters.group)
async def cmd_set_feature(client: Client, msg: Message) -> None:
    """Perintah teks untuk mengatur fitur grup.
    
    Format: /set <fitur> <nilai>
    Contoh:
        /set action mute
        /set maxwarning 5
        /set antiflood on
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    user_id: int = msg.from_user.id if msg.from_user else 0
    chat_id: int = msg.chat.id
    
    if not await is_admin(client, chat_id, user_id):
        await msg.reply(
            "<blockquote>🚫 Akses ditolak.\nHanya admin yang dapat menggunakan perintah ini.</blockquote>"
        )
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
            quote=True,
        )
        return
    
    _, feature, value = parts
    feature = feature.lower()
    value = value.lower()
    original_feature: str = feature
    
    # Daftar fitur valid
    valid_features = {
        "action",
        "maxwarning",
        "antiforward",
        "nolinks",
        "noevents",
        "nocontacts",
        "nolocations",
        "nocommands",
        "nohashtags",
        "novoice",
        "imagefilter",
        "antibot",
        "antiflood",
        "blacklist",
    }
    
    # Auto-correct typo pada fitur
    if feature not in valid_features:
        closest: Optional[str] = get_closest_feature_name(feature, valid_features)
        if closest:
            feature = closest
            await msg.reply(
                f"⚠️ Fitur <b>{original_feature}</b> tidak ditemukan. Menggunakan <b>{feature}</b> sebagai pengganti.",
                quote=True,
            )
        else:
            fitur_list = "\n".join(f"• <code>{f}</code>" for f in sorted(valid_features))
            await msg.reply(
                f"<blockquote>❌ Fitur <b>{original_feature}</b> tidak dikenal.\n\n"
                f"Berikut fitur yang tersedia:\n{fitur_list}</blockquote>",
                quote=True,
            )
            return
    
    # === HANDLE ACTION MODE ===
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
            quote=True,
        )
        return
    
    # === HANDLE MAX WARNING ===
    if feature == "maxwarning":
        settings = get_group_settings(chat_id)
        if settings.get("action_mode", "delete") == "delete":
            await msg.reply(
                "❌ <b>maxwarning</b> hanya berlaku jika <b>action</b> adalah <code>mute</code> atau <code>ban</code>."
            )
            return
        
        if not value.isdigit():
            await msg.reply("❌ Nilai harus berupa angka. Contoh: <code>/set maxwarning 5</code>")
            return
        
        num: int = int(value)
        if not (1 <= num <= 10):
            await msg.reply("❌ Nilai harus antara <code>1</code> sampai <code>10</code>.")
            return
        
        update_group_setting(chat_id, "max_warnings", num)
        await msg.reply(f"✅ Batas peringatan diatur menjadi <b>{num}</b>.", quote=True)
        return
    
    # === HANDLE BOOLEAN FEATURES ===
    if value not in {"on", "off"}:
        await msg.reply(
            "<blockquote>❌ Nilai hanya bisa <code>on</code> atau <code>off</code>.\n"
            "Contoh: <code>/set antibot on</code></blockquote>",
            quote=True,
        )
        return
    
    update_group_setting(chat_id, feature, value == "on")
    emoji = "✅" if value == "on" else "❌"
    status = "diaktifkan" if value == "on" else "dinonaktifkan"
    await msg.reply(
        f"<blockquote>{emoji} Fitur <b>{feature}</b> telah {status}.</blockquote>",
        quote=True,
    )
