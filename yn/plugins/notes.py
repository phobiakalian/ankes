"""
Notes plugin for Yn Security Bot.
Allows admins to save and retrieve important messages (rules, FAQ, group info).
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional, Dict, Any, List
import logging
import json
import sqlite3
import threading

from yn.utils.db import db
from yn.plugins.i18n.translations import get_text, DEFAULT_LANGUAGE
from yn.utils.utils import admin_check

logger = logging.getLogger(__name__)

# Separate SQLite connection for notes (since YnDB doesn't support direct SQL)
NOTES_DB_FILE = "ankesnotes.sqlite3"
_notes_lock = threading.Lock()

def _get_notes_connection() -> sqlite3.Connection:
    """Get a notes database connection."""
    return sqlite3.connect(NOTES_DB_FILE, check_same_thread=False)

def init_notes_db():
    """Initialize notes database table."""
    with _notes_lock:
        conn = _get_notes_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                note_name TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, note_name)
            )
        """)
        conn.commit()
        conn.close()

def get_chat_language(chat_id: int) -> str:
    """Get language for a chat."""
    try:
        # Use the existing db instance for settings
        results = db.find({"chat_id": chat_id})
        if results:
            return results[0].get("language_code", DEFAULT_LANGUAGE)
        return DEFAULT_LANGUAGE
    except Exception:
        return DEFAULT_LANGUAGE


@Client.on_message(filters.command(["save", "addnote"]) & filters.group)
@admin_check
async def save_note(client: Client, message: Message):
    """
    Save a note.
    
    Usage: /save <note_name> or reply to a message with /save <note_name>
    """
    lang = get_chat_language(message.chat.id)
    
    # Check if there's a reply or the message has content
    if not message.reply_to_message and not (len(message.command) > 1 and message.text):
        await message.reply(
            get_text(lang, "error") + " " + 
            "Gunakan: /save <nama_catatan>\nAtau balas pesan dengan /save <nama_catatan>"
        )
        return
    
    # Get note name from command
    if len(message.command) < 2:
        await message.reply(
            get_text(lang, "error") + " " +
            "Nama catatan diperlukan!\nGunakan: /save <nama_catatan>"
        )
        return
    
    note_name = message.command[1].lower()
    
    # Validate note name (alphanumeric and underscores only)
    if not note_name.replace("_", "").replace("-", "").isalnum():
        await message.reply(
            get_text(lang, "error") + " " +
            "Nama catatan hanya boleh mengandung huruf, angka, underscore (_), dan tanda hubung (-)."
        )
        return
    
    # Get content to save
    if message.reply_to_message:
        # Save replied message content
        content = message.reply_to_message.text or message.reply_to_message.caption
        content_type = "text"
        
        if not content:
            # Check for media
            if message.reply_to_message.photo:
                content_type = "photo"
                content = message.reply_to_message.photo[-1].file_id
            elif message.reply_to_message.document:
                content_type = "document"
                content = message.reply_to_message.document.file_id
            elif message.reply_to_message.video:
                content_type = "video"
                content = message.reply_to_message.video.file_id
            elif message.reply_to_message.sticker:
                content_type = "sticker"
                content = message.reply_to_message.sticker.file_id
            else:
                await message.reply(get_text(lang, "error") + " Tidak ada konten yang bisa disimpan.")
                return
    else:
        # Save text from command (everything after the note name)
        content = message.text.split(None, 2)[2] if len(message.text.split()) > 2 else ""
        content_type = "text"
    
    if not content and content_type == "text":
        await message.reply(get_text(lang, "error") + " Konten catatan tidak boleh kosong.")
        return
    
    # Save to database
    try:
        with _notes_lock:
            conn = _get_notes_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO notes (chat_id, note_name, content, content_type, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (message.chat.id, note_name, content, content_type))
            conn.commit()
            conn.close()
        
        await message.reply(
            get_text(lang, "success") + " " +
            get_text(lang, "note_saved", name=note_name)
        )
    except Exception as e:
        logger.error(f"Error saving note: {e}")
        await message.reply(get_text(lang, "error") + " Gagal menyimpan catatan.")


@Client.on_message(filters.command(["get", "note"]) & filters.group)
async def get_note(client: Client, message: Message):
    """
    Get a note.
    
    Usage: /get <note_name> or #note_name
    """
    lang = get_chat_language(message.chat.id)
    
    # Get note name from command or hashtag
    if len(message.command) > 1:
        note_name = message.command[1].lower()
    elif message.text.startswith("#"):
        note_name = message.text.split()[0][1:].lower()
    else:
        await message.reply(
            get_text(lang, "error") + " " +
            "Nama catatan diperlukan!\nGunakan: /get <nama_catatan> atau #nama_catatan"
        )
        return
    
    # Retrieve note from database
    try:
        with _notes_lock:
            conn = _get_notes_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content, content_type FROM notes WHERE chat_id = ? AND note_name = ?",
                (message.chat.id, note_name)
            )
            result = cursor.fetchone()
            
            if not result:
                await message.reply(get_text(lang, "note_not_found", name=note_name))
                return
            
            content, content_type = result
            
            # Send the note based on content type
            if content_type == "photo":
                await message.reply_photo(photo=content)
            elif content_type == "document":
                await message.reply_document(document=content)
            elif content_type == "video":
                await message.reply_video(video=content)
            elif content_type == "sticker":
                await message.reply_sticker(sticker=content)
            else:
                await message.reply(content)
    except Exception as e:
        logger.error(f"Error getting note: {e}")
        await message.reply(get_text(lang, "error") + " Gagal mengambil catatan.")


@Client.on_message(filters.command(["notes", "allnotes"]) & filters.group)
async def list_notes(client: Client, message: Message):
    """
    List all saved notes.
    """
    lang = get_chat_language(message.chat.id)
    
    try:
        with _notes_lock:
            conn = _get_notes_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT note_name FROM notes WHERE chat_id = ? ORDER BY note_name",
                (message.chat.id,)
            )
            notes = cursor.fetchall()
        
        if not notes:
            await message.reply(get_text(lang, "note_list_empty"))
            return
        
        # Create formatted list
        notes_list = "\n".join([f"• #{note[0]}" for note in notes])
        
        await message.reply(
            get_text(lang, "note_list_title") + "\n\n" +
            notes_list + "\n\n" +
            get_text(lang, "note_usage")
        )
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        await message.reply(get_text(lang, "error") + " Gagal mengambil daftar catatan.")


@Client.on_message(filters.command(["delnote", "deletenote"]) & filters.group)
@admin_check
async def delete_note(client: Client, message: Message):
    """
    Delete a note.
    
    Usage: /delnote <note_name>
    """
    lang = get_chat_language(message.chat.id)
    
    if len(message.command) < 2:
        await message.reply(
            get_text(lang, "error") + " " +
            "Nama catatan diperlukan!\nGunakan: /delnote <nama_catatan>"
        )
        return
    
    note_name = message.command[1].lower()
    
    try:
        with _notes_lock:
            conn = _get_notes_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM notes WHERE chat_id = ? AND note_name = ?",
                (message.chat.id, note_name)
            )
            if cursor.fetchone()[0] == 0:
                await message.reply(get_text(lang, "note_not_found", name=note_name))
                conn.close()
                return
            
            cursor.execute(
                "DELETE FROM notes WHERE chat_id = ? AND note_name = ?",
                (message.chat.id, note_name)
            )
            conn.commit()
            conn.close()
        
        await message.reply(
            get_text(lang, "success") + " " +
            get_text(lang, "note_deleted", name=note_name)
        )
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        await message.reply(get_text(lang, "error") + " Gagal menghapus catatan.")


@Client.on_message(filters.regex(r"^#[a-zA-Z0-9_]+$") & filters.group)
async def hashtag_note(client: Client, message: Message):
    """
    Handle hashtag-style note retrieval (#note_name).
    """
    # Extract note name from hashtag
    note_name = message.text[1:].lower()
    
    try:
        with _notes_lock:
            conn = _get_notes_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content, content_type FROM notes WHERE chat_id = ? AND note_name = ?",
                (message.chat.id, note_name)
            )
            result = cursor.fetchone()
            
            if result:
                content, content_type = result
                
                # Send the note based on content type
                if content_type == "photo":
                    await message.reply_photo(photo=content)
                elif content_type == "document":
                    await message.reply_document(document=content)
                elif content_type == "video":
                    await message.reply_video(video=content)
                elif content_type == "sticker":
                    await message.reply_sticker(sticker=content)
                else:
                    await message.reply(content)
            conn.close()
    except Exception as e:
        logger.error(f"Error handling hashtag note: {e}")


def init_notes_db():
    """Initialize notes database table."""
    with _notes_lock:
        conn = _get_notes_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                note_name TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(chat_id, note_name)
            )
        """)
        conn.commit()
        conn.close()


# Initialize database on module load
init_notes_db()
