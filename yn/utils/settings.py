"""Yn Security Bot - Settings Module."""

from typing import Any, Dict

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from yn.utils.db import db


def settings_keyboard(settings: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Generate the settings inline keyboard."""

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
        [on_off_button("antiforward", "antiforward"), on_off_button("nolinks", "nolinks")],
        [on_off_button("noevents", "noevents"), on_off_button("nocontacts", "nocontacts")],
        [on_off_button("nolocations", "nolocations"), on_off_button("nocommands", "nocommands")],
        [on_off_button("nohashtags", "nohashtags"), on_off_button("novoice", "novoice")],
        [on_off_button("blacklist", "blacklist"), on_off_button("antibot", "antibot")],
        [on_off_button("antiflood", "antiflood"), on_off_button("imagefilter", "imagefilter")],
        mode_buttons,
    ]

    if action_mode in ("mute", "ban"):
        keyboard.append(
            [
                InlineKeyboardButton("➖", callback_data="warnings_minus"),
                InlineKeyboardButton(
                    f"Max Warnings: {settings.get('max_warnings', 3)}",
                    callback_data="noop",
                ),
                InlineKeyboardButton("➕", callback_data="warnings_plus"),
            ]
        )

    keyboard.append([InlineKeyboardButton("❌ Tutup", callback_data="close_settings")])

    return InlineKeyboardMarkup(keyboard)


def get_group_settings(chat_id: int) -> Dict[str, Any]:
    """Get group settings from database or create default settings."""
    try:
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
            "free_users": [],  # daftar user bebas aturan
        }
        db.insert_one(default)
        return default
    except Exception as e:
        # Return default settings if database error
        return {
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
            "action_mode": "delete",
            "max_warnings": 3,
            "badwords": [],
            "free_users": [],
        }