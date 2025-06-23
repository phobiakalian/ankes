
import os, asyncio
from hydrogram import Client, filters
from hydrogram.types import Message
from pytgcalls import PyTgCalls, filters as fl
from pytgcalls.types import ChatUpdate
from pytgcalls.types.stream import StreamEnded
from pytgcalls.filters import stream_end
from yn.utils.downloader import download_audio
from yn.utils.mqueue import add_to_mqueue, get_next, skip_current, clear_mqueue, get_mqueue_list
from yn.bot import call

@Client.on_message(filters.command("play") & filters.group)
async def play_handler(bot : Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.reply("❗ Berikan judul lagu untuk diputar.")
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Mencari lagu...")

    try:
        title, filepath, thumbnail, duration = download_audio(query)
    except Exception as e:
        return await msg.edit(f"⚠️ Gagal unduh lagu: {e}")

    add_to_mqueue(chat_id, title, filepath)
    await msg.delete()
    await bot.send_photo(
        chat_id,
        photo=thumbnail if thumbnail else None,
        caption=f"🎵 Ditambahkan ke antrean: **{title}**"
    )

    if len(get_mqueue_list(chat_id)) == 1:
        await play_next(chat_id, message)

async def play_next(chat_id, message):
    song = get_next(chat_id)
    if not song:
        return await message.reply("📭 Tidak ada lagu berikutnya.")
    try:
        await call.play(chat_id, song['file'])
    except Exception as e:
        await message.reply(f"⚠️ Gagal memutar lagu: {e}")
        skip_current(chat_id)

@Client.on_message(filters.command("skip") & filters.group)
async def skip_handler(_, message: Message):
    chat_id = message.chat.id
    skip_current(chat_id)
    await play_next(chat_id, message)

@Client.on_message(filters.command("end") & filters.group)
async def end_handler(_, message: Message):
    chat_id = message.chat.id
    clear_mqueue(chat_id)
    try:
        await call.leave_call(chat_id)
        await message.reply("🚑 Pemutaran dihentikan.")
    except:
        await message.reply("❗️ Tidak sedang dalam voice chat.")

@Client.on_message(filters.command("queue") & filters.group)
async def mqueue_handler(_, message: Message):
    chat_id = message.chat.id
    q = get_mqueue_list(chat_id)
    if not q:
        return await message.reply("📜 Antrean kosong.")
    text = "**🎶 Antrean Saat Ini:**\n"
    for i, song in enumerate(q):
        text += f"{i+1}. {song['title']}\n"
    await message.reply(text)

@call.on_update(stream_end())
async def on_stream_ended(client: PyTgCalls, update: StreamEnded):
    if update.stream_type == StreamEnded.Type.AUDIO:
        chat_id = update.chat_id
        skip_current(chat_id)
        next_song = get_next(chat_id)
        if next_song:
            try:
                await client.play(chat_id, next_song["file"])
            except Exception as e:
                print(f"Gagal memutar lagu berikutnya: {e}")
        else:
            try:
                await client.leave_call(chat_id)
                print(f"Keluar VC karena antrean habis: {chat_id}")
            except Exception:
                pass