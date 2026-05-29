"""
Language settings plugin for Yn Security Bot.
Allows admins to change bot language and manage i18n settings.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging

from yn.utils.db import db
from yn.plugins.i18n.translations import (
    get_text, 
    get_available_languages, 
    is_language_supported,
    DEFAULT_LANGUAGE,
    LanguageManager
)
from yn.utils.utils import admin_check

logger = logging.getLogger(__name__)

# Initialize language manager
lang_manager = LanguageManager(db)


def get_chat_language(chat_id: int) -> str:
    """Get language for a chat."""
    return lang_manager.get_chat_language(chat_id)


@Client.on_message(filters.command(["language", "lang", "setlang"]) & filters.group)
@admin_check
async def set_language(client: Client, message: Message):
    """
    Set language for the group.
    
    Usage: /language <code> or /language (shows keyboard)
    """
    chat_id = message.chat.id
    current_lang = get_chat_language(chat_id)
    lang = current_lang  # Use current language for messages
    
    # If language code provided
    if len(message.command) > 1:
        new_lang = message.command[1].lower()
        
        if not is_language_supported(new_lang):
            await message.reply(
                get_text(lang, "error") + " Bahasa tidak didukung.\n\n"
                f"Bahasa yang tersedia: {', '.join(get_available_languages().values())}"
            )
            return
        
        if lang_manager.set_chat_language(chat_id, new_lang):
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
    auto_detect = lang_manager.is_auto_detect_enabled(chat_id)
    auto_flag = "✅ " if auto_detect else ""
    buttons.append([InlineKeyboardButton(f"{auto_flag}Auto Detect", callback_data="lang_auto_toggle")])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        f"{get_text(lang, 'settings_title')}\n\n"
        f"{get_text(lang, 'settings_language', lang=get_available_languages()[current_lang])}\n\n"
        "Pilih bahasa yang diinginkan:",
        reply_markup=keyboard
    )


@Client.on_callback_query(filters.regex(r"^lang_"))
async def language_callback(client: Client, callback_query: CallbackQuery):
    """
    Handle language selection callbacks.
    """
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    current_lang = get_chat_language(chat_id)
    
    try:
        if data.startswith("lang_") and data != "lang_auto_toggle":
            # Language selection
            new_lang = data.replace("lang_", "")
            
            if is_language_supported(new_lang):
                if lang_manager.set_chat_language(chat_id, new_lang):
                    # Update the message with new language
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
                    
                    auto_detect = lang_manager.is_auto_detect_enabled(chat_id)
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
            auto_detect = lang_manager.is_auto_detect_enabled(chat_id)
            
            if auto_detect:
                lang_manager.disable_auto_detect(chat_id)
                action_text = "dimatikan"
            else:
                lang_manager.enable_auto_detect(chat_id)
                action_text = "diaktifkan"
            
            # Refresh the keyboard
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
            
            auto_detect = lang_manager.is_auto_detect_enabled(chat_id)
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
            await callback_query.answer(get_text(current_lang, "error"), show_alert=True)
        except Exception:
            pass


@Client.on_message(filters.command(["mylang"]) & filters.group)
async def my_language(client: Client, message: Message):
    """
    Show current language setting.
    """
    chat_id = message.chat.id
    current_lang = get_chat_language(chat_id)
    languages = get_available_languages()
    auto_detect = lang_manager.is_auto_detect_enabled(chat_id)
    
    text = (
        f"🌐 **Bahasa Saat Ini:** {languages.get(current_lang, current_lang)}\n\n"
        f"🔍 **Auto Detect:** {'Aktif' if auto_detect else 'Mati'}\n\n"
        f"Gunakan /language untuk mengubah bahasa."
    )
    
    await message.reply(text)


def init_language_db():
    """Initialize language database tables."""
    # This is handled by LanguageManager class
    pass


# Initialize on module load
init_language_db()
