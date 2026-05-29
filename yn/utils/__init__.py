"""Yn Security Bot - Utility Functions."""

from difflib import get_close_matches
from typing import Any, Optional

from yn.utils.db import db, db_stats, db_freeusers, db_warnings


def update_group_setting(chat_id: int, key: str, value: Any) -> None:
    """Update a group setting in the database."""
    db.update_one({"chat_id": chat_id}, {"$set": {key: value}})


# -- Stats --


def add_violation_stat(chat_id: int, user_id: int, username: str) -> None:
    """Add or increment violation statistics for a user."""
    doc = db_stats.find({"chat_id": chat_id, "user_id": user_id})
    if not doc:
        db_stats.insert_one(
            {
                "chat_id": chat_id,
                "user_id": user_id,
                "username": username,
                "violations": 1,
                "messages": 0,
            }
        )
    else:
        db_stats.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$inc": {"violations": 1}, "$set": {"username": username}},
        )


# -- Free Users --


def is_free_user(chat_id: int, user_id: int) -> bool:
    """Check if a user is in the free users list."""
    docs = db_freeusers.find({"chat_id": chat_id, "user_id": user_id})
    return len(docs) > 0


def add_free_user(chat_id: int, user_id: int) -> None:
    """Add a user to the free users list."""
    if not is_free_user(chat_id, user_id):
        db_freeusers.insert_one({"chat_id": chat_id, "user_id": user_id})


def remove_free_user(chat_id: int, user_id: int) -> None:
    """Remove a user from the free users list."""
    db_freeusers.delete_one({"chat_id": chat_id, "user_id": user_id})


def log_user_message(chat_id: int, user_id: int, username: str) -> None:
    """Log a user message for statistics."""
    doc = db_stats.find({"chat_id": chat_id, "user_id": user_id})
    if not doc:
        db_stats.insert_one(
            {
                "chat_id": chat_id,
                "user_id": user_id,
                "username": username,
                "violations": 0,
                "messages": 1,
            }
        )
    else:
        db_stats.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$inc": {"messages": 1}, "$set": {"username": username}},
        )


# -- Warnings --


def get_warnings(chat_id: int, user_id: int) -> int:
    """Get the number of warnings for a user."""
    docs = db_warnings.find({"chat_id": chat_id, "user_id": user_id})
    if docs:
        return docs[0].get("count", 0)
    return 0


def add_warning(chat_id: int, user_id: int) -> int:
    """Add a warning to a user and return the new count."""
    docs = db_warnings.find({"chat_id": chat_id, "user_id": user_id})
    if not docs:
        db_warnings.insert_one({"chat_id": chat_id, "user_id": user_id, "count": 1})
        return 1
    count = docs[0]["count"] + 1
    db_warnings.update_one(
        {"chat_id": chat_id, "user_id": user_id}, {"$set": {"count": count}}
    )
    return count


def reset_warnings(chat_id: int, user_id: int) -> None:
    """Reset warnings for a user."""
    db_warnings.delete_one({"chat_id": chat_id, "user_id": user_id})


# -- Get Feature Info --

FEATURE_DESCRIPTIONS = {
    "antiforward": "🔒 Blokir pesan yang diteruskan (forwarded) dari chat lain untuk mencegah spam dan promosi terselubung.",
    "nolinks": "🔗 Cegah pengguna mengirim tautan atau link (termasuk http/https) dalam pesan.",
    "noevents": "📅 Nonaktifkan pengiriman pesan berupa event seperti jadwal atau pengingat otomatis.",
    "nocontacts": "👤 Blokir pengiriman kontak oleh anggota, mencegah promosi nomor telepon.",
    "nolocations": "📍 Blokir pengiriman lokasi (location) untuk mencegah spam atau informasi lokasi yang tidak perlu.",
    "nocommands": "⌨️ Blokir penggunaan perintah bot oleh anggota non-admin.",
    "nohashtags": "#️⃣ Nonaktifkan penggunaan hashtag di grup untuk menjaga fokus pembicaraan.",
    "novoice": "🎙 Blokir pengiriman pesan suara (voice message), cocok untuk grup diskusi serius.",
    "imagefilter": "🖼 Blokir gambar (photo) agar tidak ada konten visual yang tidak relevan masuk.",
    "antibot": "🤖 Otomatis keluarkan bot yang masuk selain yang ada dalam whitelist admin.",
    "antiflood": "🌊 Batasi jumlah pesan yang dikirim dalam waktu singkat untuk mencegah spam massal.",
    "blacklist": "🚫 Blokir pesan yang mengandung kata-kata yang termasuk dalam daftar hitam (blacklist).",
}


def get_closest_feature_name(
    input_name: str, valid_features: set
) -> Optional[str]:
    """Get the closest matching feature name using fuzzy matching."""
    matches = get_close_matches(input_name, valid_features, n=1, cutoff=0.6)
    return matches[0] if matches else None