"""
Language settings plugin for Yn Security Bot.
Allows admins to change bot language and manage i18n settings.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
import sqlite3

from yn.utils.db import db
from yn.plugins.i18n.translations import (
    get_text, 
    get_available_languages, 
    is_language_supported,
    DEFAULT_LANGUAGE,
)
from yn.utils.utils import is_admin

logger = logging.getLogger(__name__)

# Database connection for language settings
_lang_db_conn = sqlite3.connect("language_settings.sqlite3", check_same_thread=False)

def _init_lang_db():
    """Initialize language database tables."""
    cursor = _lang_db_conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_languages (
            chat_id INTEGER PRIMARY KEY,
            language_code TEXT DEFAULT 'id',
            auto_detect BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _lang_db_conn.commit()

_init_lang_db()


def get_chat_language(chat_id: int) -> str:
    """Get language for a chat."""
    cursor = _lang_db_conn.cursor()
    cursor.execute(
        "SELECT language_code FROM chat_languages WHERE chat_id = ?",
        (chat_id,)
    )
    result = cursor.fetchone()
    return result[0] if result else DEFAULT_LANGUAGE


def set_chat_language(chat_id: int, lang_code: str) -> bool:
    """Set language for a chat."""
    if not is_language_supported(lang_code):
        return False
    
    cursor = _lang_db_conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO chat_languages 
        (chat_id, language_code, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (chat_id, lang_code))
    _lang_db_conn.commit()
    return True


def is_auto_detect_enabled(chat_id: int) -> bool:
    """Check if auto-detect is enabled for a chat."""
    cursor = _lang_db_conn.cursor()
    cursor.execute(
        "SELECT auto_detect FROM chat_languages WHERE chat_id = ?",
        (chat_id,)
    )
    result = cursor.fetchone()
    return bool(result and result[0])


def enable_auto_detect(chat_id: int):
    """Enable automatic language detection for a chat."""
    cursor = _lang_db_conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO chat_languages 
        (chat_id, auto_detect, updated_at) 
        VALUES (?, 1, CURRENT_TIMESTAMP)
    """, (chat_id,))
    _lang_db_conn.commit()


def disable_auto_detect(chat_id: int):
    """Disable automatic language detection for a chat."""
    cursor = _lang_db_conn.cursor()
    cursor.execute("""
        UPDATE chat_languages 
        SET auto_detect = 0, updated_at = CURRENT_TIMESTAMP 
        WHERE chat_id = ?
    """, (chat_id,))
    _lang_db_conn.commit()


@Client.on_message(filters.command(["language", "lang", "setlang"]) & filters.group)
async def set_language(client: Client, message: Message):
    """
    Set language for the group.
    
    Usage: /language <code> or /language (shows keyboard)
    """
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else 0
        
        # Check admin
        if not await is_admin(client, chat_id, user_id):
            await message.reply("⚠️ Hanya admin yang boleh mengubah bahasa.")
            return
        
        current_lang = get_chat_language(chat_id)
        lang = current_lang
        
        # If language code provided
        if len(message.command) > 1:
            new_lang = message.command[1].lower()
            
            if not is_language_supported(new_lang):
                await message.reply(
                    get_text(lang, "error") + " Bahasa tidak didukung.\n\n"
                    f"Bahasa yang tersedia: {', '.join(get_available_languages().values())}"
                )
                return
            
            if set_chat_language(chat_id, new_lang):
                await message.reply(
                    get_text(lang, "success") + " " +
                    get_text(lang, "settings_language_changed", lang=get_available_languages()[new_lang])
                )
            else:
                await message.reply(get_text(lang, "error") + " Gagal mengubah bahasa.")
            return
        
        # Show language selection keyboard
        languages = get_available_languages()
        buttons = []
        
        # Create button grid (2 columns)
        lang_items = list(languages.items())
        for i in range(0, len(lang_items), 2):
            row = []
            for j in range(2):
                if i + j < len(lang_items):
                    code, name = lang_items[i + j]
                    flag = "✅ " if code == current_lang else ""
                    row.append(InlineKeyboardButton(f"{flag}{name}", callback_data=f"lang_{code}"))
            buttons.append(row)
        
        # Add auto-detect button
        auto_detect = is_auto_detect_enabled(chat_id)
        auto_flag = "✅ " if auto_detect else ""
        buttons.append([InlineKeyboardButton(f"{auto_flag}Auto Detect", callback_data="lang_auto_toggle")])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        await message.reply(
            f"{get_text(lang, 'settings_title')}\n\n"
            f"{get_text(lang, 'settings_language', lang=get_available_languages()[current_lang])}\n\n"
            "Pilih bahasa yang diinginkan:",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error in set_language: {e}")
        await message.reply(f"⚠️ Terjadi kesalahan: {e}")


@Client.on_callback_query(filters.regex(r"^lang_"))
async def language_callback(client: Client, callback_query: CallbackQuery):
    """Handle language selection callbacks."""
    try:
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        
        # Check admin
        if not await is_admin(client, chat_id, user_id):
            await callback_query.answer("⚠️ Hanya admin yang bisa mengubah bahasa.", show_alert=True)
            return
        
        current_lang = get_chat_language(chat_id)
        
        if data.startswith("lang_") and data != "lang_auto_toggle":
            # Language selection
            new_lang = data.replace("lang_", "")
            
            if is_language_supported(new_lang):
                if set_chat_language(chat_id, new_lang):
                    lang = new_lang
                    languages = get_available_languages()
                    
                    buttons = []
                    lang_items = list(languages.items())
                    for i in range(0, len(lang_items), 2):
                        row = []
                        for j in range(2):
                            if i + j < len(lang_items):
                                code, name = lang_items[i + j]
                                flag = "✅ " if code == new_lang else ""
                                row.append(InlineKeyboardButton(f"{flag}{name}", callback_data=f"lang_{code}"))
                        buttons.append(row)
                    
                    auto_detect = is_auto_detect_enabled(chat_id)
                    auto_flag = "✅ " if auto_detect else ""
                    buttons.append([InlineKeyboardButton(f"{auto_flag}Auto Detect", callback_data="lang_auto_toggle")])
                    
                    keyboard = InlineKeyboardMarkup(buttons)
                    
                    await callback_query.message.edit_text(
                        f"{get_text(lang, 'settings_title')}\n\n"
                        f"{get_text(lang, 'settings_language', lang=languages[new_lang])}\n\n"
                        f"{get_text(lang, 'settings_language_changed', lang=languages[new_lang])}\n\n"
                        "Pilih bahasa yang diinginkan:",
                        reply_markup=keyboard
                    )
                    await callback_query.answer(f"Bahasa diubah ke {languages[new_lang]}!")
                else:
                    await callback_query.answer(get_text(current_lang, "error"), show_alert=True)
            else:
                await callback_query.answer(get_text(current_lang, "error"), show_alert=True)
        
        elif data == "lang_auto_toggle":
            # Toggle auto-detect
            auto_detect = is_auto_detect_enabled(chat_id)
            
            if auto_detect:
                disable_auto_detect(chat_id)
                action_text = "dimatikan"
            else:
                enable_auto_detect(chat_id)
                action_text = "diaktifkan"
            
            lang = current_lang
            languages = get_available_languages()
            
            buttons = []
            lang_items = list(languages.items())
            for i in range(0, len(lang_items), 2):
                row = []
                for j in range(2):
                    if i + j < len(lang_items):
                        code, name = lang_items[i + j]
                        flag = "✅ " if code == lang else ""
                        row.append(InlineKeyboardButton(f"{flag}{name}", callback_data=f"lang_{code}"))
                buttons.append(row)
            
            auto_detect = is_auto_detect_enabled(chat_id)
            auto_flag = "✅ " if auto_detect else ""
            buttons.append([InlineKeyboardButton(f"{auto_flag}Auto Detect", callback_data="lang_auto_toggle")])
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            await callback_query.message.edit_text(
                f"{get_text(lang, 'settings_title')}\n\n"
                f"{get_text(lang, 'settings_language', lang=languages[lang])}\n\n"
                f"Auto Detect {action_text}.\n\n"
                "Pilih bahasa yang diinginkan:",
                reply_markup=keyboard
            )
            await callback_query.answer(f"Auto Detect {action_text}!")
    except Exception as e:
        logger.error(f"Error handling language callback: {e}")
        try:
            current_lang = get_chat_language(callback_query.message.chat.id)
            await callback_query.answer(get_text(current_lang, "error"), show_alert=True)
        except Exception:
            pass


@Client.on_message(filters.command(["mylang"]) & filters.group)
async def my_language(client: Client, message: Message):
    """Show current language setting."""
    try:
        chat_id = message.chat.id
        current_lang = get_chat_language(chat_id)
        languages = get_available_languages()
        auto_detect = is_auto_detect_enabled(chat_id)
        
        text = (
            f"🌐 **Bahasa Saat Ini:** {languages.get(current_lang, current_lang)}\n\n"
            f"🔍 **Auto Detect:** {'Aktif' if auto_detect else 'Mati'}\n\n"
            f"Gunakan /language untuk mengubah bahasa."
        )
        
        await message.reply(text)
    except Exception as e:
        logger.error(f"Error in my_language: {e}")
        await message.reply(f"⚠️ Terjadi kesalahan: {e}")
