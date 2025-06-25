from hydrogram import Client, filters
from hydrogram.types import Message

from yn.utils.utils import is_admin
from yn.utils.settings import get_group_settings
from yn.plugins.settings import update_group_setting

# --- /badwords command for admin ---
@Client.on_message(filters.command("badwords") & filters.group)
async def cmd_badwords(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        await msg.reply("<blockquote>⚠️ Hanya admin yang boleh mengatur kata terlarang.</blockquote>")
        return

    parts = msg.text.split(maxsplit=2)
    if len(parts) < 2:
        await msg.reply("Gunakan:\n/badwords add <kata1> [kata2] [...]\n/badwords rem <kata1> [kata2] [...]\n/badwords list")
        return

    action = parts[1].lower()
    settings = get_group_settings(chat_id)
    badwords = settings.get("badwords", [])

    if action == "list":
        if badwords:
            await msg.reply("📋 Daftar kata terlarang:\n\n<blockquote>" + "\n".join(f"- {w}" for w in badwords) + "</blockquote>")
        else:
            await msg.reply("📋 Tidak ada kata terlarang saat ini.")
        return

    if len(parts) < 3:
        await msg.reply("Masukkan kata yang ingin ditambahkan atau dihapus.")
        return

    # Pecah kata per spasi, buang duplikat dengan set
    words = list(set(parts[2].lower().replace(",", " ").split()))
    if not words:
        await msg.reply("❗ Tidak ada kata valid untuk diproses.")
        return

    if action == "add":
        added = []
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

    if action in ["rem", "remove", "del"]:
        removed = []
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

    await msg.reply("Gunakan action yang benar: `add`, `rem`, atau `list`.")
