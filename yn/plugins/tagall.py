import random, asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from yn.utils.utils import is_admin
from yn import tagall_tasks, EMOJI_LIST

# --- tagall --

@Client.on_message(filters.command("tagall") & filters.group)
async def tagall_emoji_hidden_mentions(client: Client, msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await msg.reply("❌ Hanya admin yang bisa menggunakan perintah ini.")
        return

    if chat_id in tagall_tasks and not tagall_tasks[chat_id].done():
        await msg.reply("⚠️ Tagall sedang berlangsung. Gunakan /stoptagall untuk menghentikan.")
        return

    text_split = msg.text.split(None, 1)
    additional_text = text_split[1] if len(text_split) > 1 else ""

    async def run_tagall():
        try:
            total_members = await client.get_chat_members_count(chat_id)
            limit = max(5, int(total_members * 0.4))

            members = []
            async for member in client.get_chat_members(chat_id):
                if member.user and not member.user.is_bot:
                    members.append(member.user)

            random.shuffle(members)
            members = members[:limit]

            emoji_tag_lines = [
                f"[{random.choice(EMOJI_LIST)}](tg://user?id={user.id})"
                for user in members
            ]

            chunks = [emoji_tag_lines[i:i + 10] for i in range(0, len(emoji_tag_lines), 10)]

            for chunk in chunks:
                try:
                    text = f"{additional_text}\n\n" if additional_text else ""
                    text += " ".join(chunk)
                    await client.send_message(chat_id, text, disable_web_page_preview=True)
                    await asyncio.sleep(2)
                except asyncio.CancelledError:
                    await client.send_message(chat_id, "⛔ Tagall dihentikan.\n\nPanggilan berakhir.\n@siniunivers")
                    break
                except Exception:
                    continue

            else:
                await client.send_message(chat_id, "✅ Tagall selesai.\n\nPanggilan berakhir.\n@siniunivers")

        except Exception as e:
            await msg.reply(f"❌ Terjadi kesalahan: {e}")
        finally:
            tagall_tasks.pop(chat_id, None)

    task = asyncio.create_task(run_tagall())
    tagall_tasks[chat_id] = task


@Client.on_message(filters.command("stoptagall") & filters.group)
async def cmd_stoptagall(client: Client, msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    if not await is_admin(client, chat_id, user_id):
        await msg.reply("⚠️ Hanya admin yang bisa menghentikan tagall.")
        return

    task = tagall_tasks.get(chat_id)
    if task and not task.done():
        task.cancel()
        await msg.reply("✅ Proses tagall dihentikan.")
    else:
        await msg.reply("ℹ️ Tidak ada proses tagall yang sedang berlangsung.")

