"""Yn Security Bot - Blacklist/Badwords Handler.

Module ini menyediakan manajemen daftar kata terlarang (blacklist) untuk grup.
"""

from __future__ import annotations

from typing import List, Set

from hydrogram import Client, filters
from hydrogram.types import Message

from yn.utils.settings import get_group_settings
from yn.utils.utils import is_admin
from yn.utils import update_group_setting


@Client.on_message(filters.command("badwords") & filters.group)
async def cmd_badwords(client: Client, msg: Message) -> None:
    """Mengelola daftar kata terlarang (blacklist).
    
    Perintah yang didukung:
        /badwords list - Menampilkan semua kata terlarang
        /badwords add <kata1> [kata2] [...] - Menambahkan kata ke blacklist
        /badwords rem <kata1> [kata2] [...] - Menghapus kata dari blacklist
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    user_id: int = msg.from_user.id if msg.from_user else 0
    chat_id: int = msg.chat.id
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, user_id):
        await msg.reply("<blockquote>⚠️ Hanya admin yang boleh mengatur kata terlarang.</blockquote>")
        return
    
    parts: List[str] = msg.text.split(maxsplit=2)
    if len(parts) < 2:
        await msg.reply(
            "Gunakan:\n"
            "/badwords add <kata1> [kata2] [...]\n"
            "/badwords rem <kata1> [kata2] [...]\n"
            "/badwords list"
        )
        return
    
    action: str = parts[1].lower()
    settings = get_group_settings(chat_id)
    badwords: List[str] = settings.get("badwords", [])
    
    # === LIST BADWORDS ===
    if action == "list":
        if badwords:
            word_list = "\n".join(f"- {w}" for w in badwords)
            await msg.reply(f"📋 Daftar kata terlarang:\n\n<blockquote>{word_list}</blockquote>")
        else:
            await msg.reply("📋 Tidak ada kata terlarang saat ini.")
        return
    
    # === VALIDASI JUMLAH ARGUMEN ===
    if len(parts) < 3:
        await msg.reply("Masukkan kata yang ingin ditambahkan atau dihapus.")
        return
    
    # Parse kata-kata (pisah dengan spasi atau koma, hapus duplikat)
    words_input: str = parts[2].lower().replace(",", " ")
    words: List[str] = list(set(words_input.split()))
    
    if not words:
        await msg.reply("❗ Tidak ada kata valid untuk diproses.")
        return
    
    # === ADD BADWORDS ===
    if action == "add":
        added: List[str] = []
        for word in words:
            if word not in badwords:
                badwords.append(word)
                added.append(word)
        
        update_group_setting(chat_id, "badwords", badwords)
        
        if added:
            await msg.reply(f"✅ Kata berhasil ditambahkan:\n" + ", ".join(added))
        else:
            await msg.reply("⚠️ Tidak ada kata baru yang ditambahkan.")
        return
    
    # === REMOVE BADWORDS ===
    if action in {"rem", "remove", "del"}:
        removed: List[str] = []
        for word in words:
            if word in badwords:
                badwords.remove(word)
                removed.append(word)
        
        update_group_setting(chat_id, "badwords", badwords)
        
        if removed:
            await msg.reply(f"✅ Kata berhasil dihapus:\n" + ", ".join(removed))
        else:
            await msg.reply("⚠️ Tidak ada kata yang ditemukan dalam daftar.")
        return
    
    # === ACTION TIDAK VALID ===
    await msg.reply("Gunakan action yang benar: `add`, `rem`, atau `list`.")


@Client.on_message(filters.command("clearbadwords") & filters.group)
async def cmd_clear_badwords(client: Client, msg: Message) -> None:
    """Menghapus semua kata terlarang dari daftar blacklist.
    
    Perintah ini memerlukan konfirmasi untuk mencegah penghapusan tidak sengaja.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    user_id: int = msg.from_user.id if msg.from_user else 0
    chat_id: int = msg.chat.id
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, user_id):
        await msg.reply("<blockquote>⚠️ Hanya admin yang boleh mengatur kata terlarang.</blockquote>")
        return
    
    settings = get_group_settings(chat_id)
    badwords: List[str] = settings.get("badwords", [])
    
    if not badwords:
        await msg.reply("📋 Tidak ada kata terlarang untuk dihapus.")
        return
    
    # Cek konfirmasi
    args = msg.text.split()
    if len(args) < 2 or args[1].lower() != "confirm":
        await msg.reply(
            f"⚠️ Anda akan menghapus {len(badwords)} kata terlarang.\n\n"
            "Ketik <code>/clearbadwords confirm</code> untuk mengonfirmasi.",
            quote=True,
        )
        return
    
    # Hapus semua badwords
    update_group_setting(chat_id, "badwords", [])
    await msg.reply(
        f"✅ Semua {len(badwords)} kata terlarang telah dihapus dari daftar.",
        quote=True,
    )


@Client.on_message(filters.command("checkbadwords") & filters.group)
async def cmd_check_badwords(client: Client, msg: Message) -> None:
    """Memeriksa apakah sebuah teks mengandung kata terlarang.
    
    Gunakan dengan me-reply pesan atau menyertakan teks setelah perintah.
    
    Args:
        client: Instance klien Hydrogram
        msg: Objek pesan perintah
    """
    user_id: int = msg.from_user.id if msg.from_user else 0
    chat_id: int = msg.chat.id
    
    # Verifikasi admin
    if not await is_admin(client, chat_id, user_id):
        await msg.reply("<blockquote>⚠️ Hanya admin yang boleh menggunakan perintah ini.</blockquote>")
        return
    
    settings = get_group_settings(chat_id)
    badwords: List[str] = settings.get("badwords", [])
    
    if not badwords:
        await msg.reply("📋 Tidak ada kata terlarang dalam daftar.")
        return
    
    # Dapatkan teks untuk diperiksa
    text_to_check: str = ""
    if msg.reply_to_message:
        text_to_check = (msg.reply_to_message.text or msg.reply_to_message.caption or "").lower()
    elif len(msg.text.split()) > 1:
        text_to_check = msg.text.split(maxsplit=1)[1].lower()
    else:
        await msg.reply(
            "Balas pesan atau sertakan teks untuk diperiksa.\n"
            "Contoh: <code>/checkbadwords teks yang ingin diperiksa</code>"
        )
        return
    
    # Periksa kata terlarang
    found_words: List[str] = [word for word in badwords if word in text_to_check]
    
    if found_words:
        await msg.reply(
            f"⚠️ Ditemukan {len(found_words)} kata terlarang:\n"
            f"<blockquote>{', '.join(found_words)}</blockquote>\n\n"
            "Pesan ini akan dihapus jika filter aktif."
        )
    else:
        await msg.reply("✅ Tidak ada kata terlarang yang ditemukan dalam teks tersebut.")
