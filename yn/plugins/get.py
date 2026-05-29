from pyrogram import Client, filters
from pyrogram.types import Message

from yn.utils.utils import is_admin
from yn.utils import FEATURE_DESCRIPTIONS, get_closest_feature_name
from difflib import get_close_matches
from yn.utils.settings import get_group_settings

@Client.on_message(filters.command("get") & filters.group)
async def cmd_get_feature(client: Client, msg: Message) -> None:
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not await is_admin(client, chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang boleh melihat pengaturan ini.")
        return

    parts = msg.text.strip().split()
    if len(parts) != 2:
        await msg.reply("📋 Format salah.\nGunakan:\n<code>/get &lt;fitur&gt;</code>", quote=True)
        return

    _, feature = parts
    feature = feature.lower()
    original_feature = feature

    if feature not in FEATURE_DESCRIPTIONS:
        closest = get_closest_feature_name(feature, FEATURE_DESCRIPTIONS.keys())
        if closest:
            feature = closest
            await msg.reply(f"⚠️ Fitur <b>{original_feature}</b> tidak ditemukan. Menggunakan <b>{feature}</b> sebagai pengganti.", quote=True)
        else:
            feature_list = "\n".join(
                [f"• <b>{name}</b>: {desc}" for name, desc in FEATURE_DESCRIPTIONS.items()]
            )
            await msg.reply(
                f"<b>❌ Fitur <b>{original_feature}</b> tidak dikenal.</b>\n\n"
                "<b>Berikut daftar fitur yang tersedia:</b>\n"
                f"<blockquote>{feature_list}</blockquote>\n\n"
                "Gunakan perintah:\n"
                "<code>/get &lt;fitur&gt;</code> untuk melihat status\n"
                "<code>/set &lt;fitur&gt; on/off</code> untuk mengubahnya.",
                quote=True
            )
            return

    settings = get_group_settings(chat_id)
    value = settings.get(feature, False)
    emoji = "✅ Aktif" if value else "❌ Nonaktif"
    desc = FEATURE_DESCRIPTIONS.get(feature, "Tidak ada deskripsi tersedia.")
    await msg.reply(
        f"<b>ℹ️ Status Fitur</b>\n"
        f"<blockquote>{feature}: {emoji}\n\n{desc}</blockquote>",
        quote=True
    )
