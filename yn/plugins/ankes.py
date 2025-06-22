import asyncio, time
from datetime import datetime, timedelta
from hydrogram import Client, filters
from hydrogram.types import (
    Message,
    ChatPermissions,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from yn import user_message_timestamps, user_message_ids
from yn.utils.utils import is_admin
from yn.utils.settings import get_group_settings
from yn.utils import add_violation_stat, is_free_user, log_user_message, add_warning, reset_warnings

def contains_link(message) -> bool:
    entities = (message.entities or []) + (message.caption_entities or [])
    return any(ent.type in ("url", "text_link") for ent in entities)

# --- Handle violation ---

async def handle_violation(client: Client, msg: Message) -> None:
    chat_id = msg.chat.id
    user = msg.from_user
    user_id = user.id if user else None
    if not user_id:
        return

    if is_free_user(chat_id, user_id):
        return
    
    if await is_admin(client, chat_id, user_id):
        return

    settings = get_group_settings(chat_id)
    action_mode = settings.get("action_mode", "delete")
    max_warn = settings.get("max_warnings", 3)

    warning_count = add_warning(chat_id, user_id)

    try:
        if action_mode == "delete":
            ok = await client.send_message(chat_id, f"<blockquote><b>⚠️ Notifikasi Message\n{user.mention} Dilarang mengirim pesan seperti itu.</b></blockquote>")
            await msg.delete()
            await asyncio.sleep(3)
            await ok.delete()

        elif action_mode == "mute":
            oke = await client.send_message(chat_id, f"<blockquote><b>⚠️ Notifikasi Message\n{user.mention} Dilarang mengirim pesan seperti itu.</b></blockquote>")
            await msg.delete()
            await asyncio.sleep(3)
            await oke.delete()
            if warning_count >= max_warn:
                await msg.reply("⚠️ Kesempatan habis, anda akan di-mute 10 menit.")
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=int(msg.date.timestamp()) + 600,
                )
                reset_warnings(chat_id, user_id)
            else:
                await msg.reply(f"🚫 Anda melanggar aturan. Kesempatan {warning_count}/{max_warn}.")

        elif action_mode == "ban":
            okee = await client.send_message(chat_id, f"{user.mention} Dilarang mengirim pesan seperti itu.")
            await msg.delete()
            await asyncio.sleep(3)
            await okee.delete()
            if warning_count >= max_warn:
                await msg.reply("⚠️ Kesempatan habis, anda akan di-ban.")
                await client.ban_chat_member(chat_id, user_id)
                reset_warnings(chat_id, user_id)
            else:
                await msg.reply(f"🚫 Anda melanggar aturan. Kesempatan {warning_count}/{max_warn}.")

        add_violation_stat(chat_id, user_id, user.mention)

    except Exception:
        # Jangan crash bot jika error
        pass

# --- Main message handler ---

@Client.on_message(filters.group)
async def on_message(client: Client, msg: Message) -> None:
    chat_id = msg.chat.id
    user = msg.from_user
    user_id = user.id if user else None
    log_user_message(chat_id, user_id, user.mention)
    if not user_id:
        return

    settings = get_group_settings(chat_id)

    if is_free_user(chat_id, user_id):
        return

    # Filter kata terlarang
    badwords = settings.get("badwords", [])
    text = (msg.text or msg.caption or "").lower()
    if any(word in text for word in badwords):
        await handle_violation(client, msg)
        return

    if settings.get("antiforward", False) and msg.forward_date:
        await handle_violation(client, msg)
        return

    if settings.get("nolinks", False) and contains_link(msg):
        #if any(x in text for x in ["http://", "https://", "t.me", ".com", "www"]):
        await handle_violation(client, msg)
        return

    if settings.get("noevents", False):
        if msg.new_chat_members or msg.left_chat_member:
            try:
                await msg.delete()
            except Exception:
                pass
            return

    if settings.get("nocontacts", False) and msg.contact:
        await handle_violation(client, msg)
        return

    if settings.get("nolocations", False) and msg.location:
        await handle_violation(client, msg)
        return

    if settings.get("nocommands", False) and msg.text and msg.text.startswith("/"):
        await handle_violation(client, msg)
        return

    if settings.get("nohashtags", False):
        if "#" in text:
            await handle_violation(client, msg)
            return

    if settings.get("novoice", False) and msg.voice:
        await handle_violation(client, msg)
        return
    
 #   if settings.get("novoice", False) and msg.video_note:
 #       await handle_violation(client, msg)
 #       return
    
    # --- Anti Bot ---
    if settings.get("antibot", False) and user.is_bot:
        await handle_violation(client, msg)
        return

    # --- Image Filter ---
    if settings.get("imagefilter", False) and msg.photo:
        await handle_violation(client, msg)
        return

    # --- Anti Flood ---
    if settings.get("antiflood", False):
        now = time.time()
        key = (chat_id, user_id)

        user_message_timestamps[key].append(now)
        user_message_ids[key].append(msg.id)

        # Buang timestamp lebih dari 60 detik
        user_message_timestamps[key] = [t for t in user_message_timestamps[key] if now - t < 60]
        user_message_ids[key] = user_message_ids[key][-5:]  # jaga-jaga, simpan maksimal 5 msg

        if len(user_message_timestamps[key]) >= 5:
            # Hapus semua pesan yang terdeteksi spam
            for mid in user_message_ids[key]:
                try:
                    await client.delete_messages(chat_id, mid)
                except:
                    pass
            user_message_timestamps[key].clear()
            user_message_ids[key].clear()
            add_violation_stat(chat_id, user_id, user.mention)

            oke = await client.send_message(chat_id, f"<blockquote><b>⚠️ Notifikasi Anti-Flood\n{user.mention} mengirim terlalu banyak pesan dalam waktu singkat.</b></blockquote>")
            await asyncio.sleep(3)
            await oke.delete()
            action = get_group_settings(chat_id).get("action_mode", "delete")
            if action == "delete":
                return
            warning_count = add_warning(chat_id, user_id)
            max_warn = get_group_settings(chat_id).get("max_warnings", 3)
            if warning_count >= max_warn:
                if action == "mute":
                    await client.send_message(
                        chat_id,
                        f"<blockquote>🔇 {user.mention} telah dimute selama 10 menit karena mengirim pesan secara berlebihan (spam).</blockquote>"
                    )

                    await client.restrict_chat_member(
                        chat_id,
                        user_id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=datetime.utcnow() + timedelta(seconds=600), 
                    )
                elif action == "ban":
                    await client.send_message(chat_id, f"<blockquote><b>{user.mention} dilarang dari grup karena melebihi batas spam yang diizinkan.</b>\n\n📌 Pelanggaran ini tercatat sebagai tindakan spam otomatis oleh sistem.</blockquote>")
                    await client.ban_chat_member(chat_id, user_id)

                reset_warnings(chat_id, user_id)
            else:
                await client.send_message(
                    chat_id,
                    f"<blockquote>🚫 {user.mention}, kamu telah melanggar batas pengiriman pesan dalam waktu singkat (flooding).\n"
                    f"Peringatan: {warning_count} dari {max_warn}.</blockquote>"
                )
            return
        return



    # TODO: Implement filters for imagefilter, antibot, antiflood, blacklist
