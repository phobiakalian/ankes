"""
Detect Edit Pesan plugin for Yn Security Bot.
Monitors edited messages for violations that may have been introduced after initial check.
"""

from pyrogram import Client, filters
from pyrogram.types import Message
import logging
import re

from yn.utils.db import db
from yn.utils.loggers.activity_logger import ActivityLogger
from yn.plugins.i18n.translations import get_text, DEFAULT_LANGUAGE
from yn.utils.utils import admin_check

logger = logging.getLogger(__name__)

# Initialize activity logger
activity_logger = ActivityLogger(db)


def get_chat_language(chat_id: int) -> str:
    """Get language for a chat."""
    try:
        cursor = db.execute(
            "SELECT language_code FROM chat_languages WHERE chat_id = ?",
            (chat_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else DEFAULT_LANGUAGE
    except Exception:
        return DEFAULT_LANGUAGE


def contains_link(text: str) -> bool:
    """Check if text contains a link."""
    if not text:
        return False
    
    # URL patterns
    url_patterns = [
        r'https?://\S+',
        r'www\.\S+',
        r't\.me/\S+',
        r'telegram\.me/\S+',
        r'tg://\S+'
    ]
    
    for pattern in url_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def contains_command(text: str) -> bool:
    """Check if text contains a command."""
    if not text:
        return False
    
    return bool(re.search(r'/[a-zA-Z][a-zA-Z0-9_@]+', text))


def contains_hashtag(text: str) -> bool:
    """Check if text contains hashtags."""
    if not text:
        return False
    
    return bool(re.search(r'#[a-zA-Z][a-zA-Z0-9_]*', text))


def is_violation_type_enabled(chat_id: int, violation_type: str) -> bool:
    """Check if a specific violation type is enabled for a chat."""
    try:
        cursor = db.execute(
            "SELECT setting_value FROM group_settings WHERE chat_id = ? AND setting_name = ?",
            (chat_id, f"no_{violation_type}")
        )
        result = cursor.fetchone()
        
        if result:
            return result[0] == "1" or result[0].lower() == "true"
        
        # Default to enabled for security
        return True
    except Exception:
        return True


async def check_edited_message_violations(message: Message):
    """
    Check an edited message for violations.
    
    Args:
        message: The edited message
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = get_chat_language(chat_id)
    
    # Skip admins
    chat_member = await message.chat.get_member(user_id)
    if chat_member.status in ["administrator", "creator"]:
        return
    
    # Get message text
    text = message.text or message.caption
    
    if not text:
        return
    
    violations_found = []
    
    # Check for links
    if is_violation_type_enabled(chat_id, "links") and contains_link(text):
        violations_found.append("link")
    
    # Check for commands
    if is_violation_type_enabled(chat_id, "commands") and contains_command(text):
        violations_found.append("command")
    
    # Check for hashtags
    if is_violation_type_enabled(chat_id, "hashtags") and contains_hashtag(text):
        violations_found.append("hashtag")
    
    # Check for badwords
    if is_violation_type_enabled(chat_id, "badwords"):
        badwords = get_badwords(chat_id)
        if badwords:
            text_lower = text.lower()
            for badword in badwords:
                if badword.lower() in text_lower:
                    violations_found.append("badword")
                    break
    
    # Handle violations
    if violations_found:
        for violation in violations_found:
            await handle_violation(message, violation, lang)


async def handle_violation(message: Message, violation_type: str, lang: str):
    """
    Handle a violation detected in an edited message.
    
    Args:
        message: The message with violation
        violation_type: Type of violation
        lang: Language code
    """
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Delete the message
    try:
        await message.delete()
    except Exception as e:
        logger.error(f"Error deleting message: {e}")
    
    # Log violation
    activity_logger.log_violation(chat_id, user_id, f"edit_{violation_type}", "Detected in edited message")
    
    # Get warning count
    warning_count = get_user_warnings(chat_id, user_id)
    max_warnings = get_max_warnings(chat_id)
    
    # Increment warning
    add_warning(chat_id, user_id, violation_type)
    warning_count += 1
    
    # Notify user
    violation_messages = {
        "link": get_text(lang, "violation_link"),
        "command": get_text(lang, "violation_command"),
        "hashtag": get_text(lang, "violation_hashtag"),
        "badword": get_text(lang, "violation_badword"),
        "forward": get_text(lang, "violation_forward"),
        "voice": get_text(lang, "violation_voice"),
        "flood": get_text(lang, "violation_flood")
    }
    
    notification = violation_messages.get(violation_type, f"⚠️ Pelanggaran {violation_type} terdeteksi!")
    notification += f"\n{get_text(lang, 'violation_warning', current=warning_count, max=max_warnings)}"
    
    try:
        await message.reply(notification)
    except Exception:
        pass
    
    # Check if user should be kicked/banned
    if warning_count >= max_warnings:
        await handle_max_warnings(message, user_id, lang)


def get_badwords(chat_id: int) -> list:
    """Get list of badwords for a chat."""
    try:
        cursor = db.execute(
            "SELECT setting_value FROM group_settings WHERE chat_id = ? AND setting_name = 'badwords'",
            (chat_id,)
        )
        result = cursor.fetchone()
        
        if result and result[0]:
            return [word.strip() for word in result[0].split(',')]
        
        return []
    except Exception:
        return []


def get_user_warnings(chat_id: int, user_id: int) -> int:
    """Get current warning count for a user."""
    try:
        cursor = db.execute(
            "SELECT warning_count FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception:
        return 0


def get_max_warnings(chat_id: int) -> int:
    """Get max warnings before kick/ban."""
    try:
        cursor = db.execute(
            "SELECT setting_value FROM group_settings WHERE chat_id = ? AND setting_name = 'max_warnings'",
            (chat_id,)
        )
        result = cursor.fetchone()
        
        if result:
            try:
                return int(result[0])
            except ValueError:
                pass
        
        return 5  # Default max warnings
    except Exception:
        return 5


def add_warning(chat_id: int, user_id: int, violation_type: str):
    """Add a warning to a user."""
    try:
        db.execute("""
            INSERT INTO warnings (chat_id, user_id, violation_type, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(chat_id, user_id) DO UPDATE SET
                warning_count = warning_count + 1,
                last_warning = CURRENT_TIMESTAMP
        """, (chat_id, user_id, violation_type))
        db.commit()
        
        # Log warning
        activity_logger.log_warning(chat_id)
    except Exception as e:
        logger.error(f"Error adding warning: {e}")


async def handle_max_warnings(message: Message, user_id: int, lang: str):
    """
    Handle when a user reaches max warnings.
    
    Args:
        message: The message that triggered the max warnings
        user_id: User ID
        lang: Language code
    """
    chat_id = message.chat.id
    
    try:
        # Kick the user
        await message.chat.ban_member(user_id)
        
        # Unban immediately (so they can rejoin if it's not a permanent ban)
        await message.chat.unban_member(user_id)
        
        # Clear warnings
        db.execute(
            "DELETE FROM warnings WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        db.commit()
        
        # Log action
        activity_logger.log_action(chat_id, user_id, "kick", reason="Max warnings reached")
        
        # Notify
        try:
            await message.reply(get_text(lang, "violation_kicked"))
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error handling max warnings: {e}")


@Client.on_edited_message(filters.group & ~filters.service)
async def on_edited_message(client: Client, message: Message):
    """
    Handler for edited messages.
    """
    try:
        await check_edited_message_violations(message)
    except Exception as e:
        logger.error(f"Error in edited message handler: {e}")


@Client.on_message(filters.command(["toggleeditcheck"]) & filters.group)
@admin_check
async def toggle_edit_check(client: Client, message: Message):
    """
    Toggle edit message checking on/off.
    """
    chat_id = message.chat.id
    lang = get_chat_language(chat_id)
    
    try:
        # Get current setting
        cursor = db.execute(
            "SELECT setting_value FROM group_settings WHERE chat_id = ? AND setting_name = 'check_edited_messages'",
            (chat_id,)
        )
        result = cursor.fetchone()
        
        current_value = result[0] if result else "1"
        new_value = "0" if current_value == "1" else "1"
        
        # Update setting
        db.execute("""
            INSERT OR REPLACE INTO group_settings (chat_id, setting_name, setting_value)
            VALUES (?, ?, ?)
        """, (chat_id, "check_edited_messages", new_value))
        db.commit()
        
        status = "diaktifkan" if new_value == "1" else "dimatikan"
        await message.reply(f"✅ Cek pesan edit {status}.")
    except Exception as e:
        logger.error(f"Error toggling edit check: {e}")
        await message.reply(get_text(lang, "error") + " Gagal mengubah pengaturan.")


def is_edit_check_enabled(chat_id: int) -> bool:
    """Check if edit message checking is enabled."""
    try:
        cursor = db.execute(
            "SELECT setting_value FROM group_settings WHERE chat_id = ? AND setting_name = 'check_edited_messages'",
            (chat_id,)
        )
        result = cursor.fetchone()
        
        if result:
            return result[0] == "1" or result[0].lower() == "true"
        
        return True  # Default to enabled
    except Exception:
        return True
