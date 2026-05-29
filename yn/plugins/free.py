from pyrogram import Client, filters
from pyrogram.types import Message
from yn.utils.utils import is_admin
from yn.utils.settings import get_group_settings
from yn.utils import add_free_user, remove_free_user


# --- /freeuser command ---

@Client.on_message(filters.command("freeuser") & filters.group)
async def cmd_add_freeuser(client: Client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        return await msg.reply("⚠️ Hanya admin yang bisa menambahkan free user.")

    target_user = None
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif len(msg.command) >= 2:
        try:
            target_user = await client.get_users(msg.command[1])
        except Exception:
            return await msg.reply("⚠️ Username atau user ID tidak valid.")
    else:
        return await msg.reply("⚠️ Balas pesan pengguna atau beri username/user_id.")

    add_free_user(chat_id, target_user.id)
    name = f"@{target_user.username}" if target_user.username else target_user.mention
    await msg.reply(f"✅ Pengguna {name} telah dimasukkan ke daftar free user.")

# --- /unfreeuser: Hapus user dari daftar free ---
@Client.on_message(filters.command("unfreeuser") & filters.group)
async def cmd_remove_freeuser(client: Client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        return await msg.reply("⚠️ Hanya admin yang bisa menghapus free user.")

    target_user = None
    if msg.reply_to_message:
        target_user = msg.reply_to_message.from_user
    elif len(msg.command) >= 2:
        try:
            target_user = await client.get_users(msg.command[1])
        except Exception:
            return await msg.reply("⚠️ Username atau user ID tidak valid.")
    else:
        return await msg.reply("⚠️ Balas pesan pengguna atau beri username/user_id.")

    remove_free_user(chat_id, target_user.id)
    name = f"@{target_user.username}" if target_user.username else target_user.mention
    await msg.reply(f"✅ Pengguna {name} telah dihapus dari daftar free user.")


# --- /listfree: Lihat daftar free user ---
@Client.on_message(filters.command("listfree") & filters.group)
async def cmd_list_freeuser(client: Client, msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        return await msg.reply("⚠️ Hanya admin yang bisa melihat daftar free user.")

    settings = get_group_settings(chat_id)
    free_users = settings.get("free_users", [])

    if not free_users:
        return await msg.reply("📋 Tidak ada pengguna dalam daftar free user.")

    text = "📋 <b>Daftar Free User</b>:\n\n"
    for uid in free_users:
        try:
            user = await client.get_users(uid)
            display = f"@{user.username}" if user.username else user.mention
        except Exception:
            display = f"<code>{uid}</code>"
        text += f"• {display}\n"

    await msg.reply(text)
