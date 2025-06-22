
from hydrogram import Client, filters
from hydrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

HELP_PAGES = {
    "start": {
        "text": (
            "👋 Halo, {0}!\n\n"
            "Selamat datang di <b>YNA Security Bot</b> — asisten moderasi otomatis untuk menjaga keamanan dan ketertiban dalam grup Telegram Anda.\n\n"
            "🔐 Bot ini dilengkapi dengan sistem filter, proteksi anti-bot, pemblokiran tautan, dan berbagai fitur lainnya yang dirancang untuk membantu admin dalam mengelola grup secara lebih efektif.\n\n"
            "Untuk memulai, Anda bisa:\n"
            "• Mengundang bot ke grup Anda\n"
            "• Melihat daftar fitur dan panduan penggunaannya\n\n"
            "Gunakan tombol di bawah ini untuk melanjutkan:"
        ),
        "buttons": [
            [("➕ Tambahkan ke Grup", "url:https://t.me/ynankesbot?startgroup=true")],
            [("📖 Bantuan & Perintah", "callback:help_main")],
        ],
    },
    "main": {
        "text": (
            "**📚 Bantuan & Panduan Penggunaan Bot**\n\n"
            "Silakan pilih salah satu kategori bantuan di bawah ini untuk mempelajari fitur yang tersedia serta cara menggunakannya:"
        ),
        "buttons": [
            [("📌 Fitur Umum", "callback:help_features")],
            [("🛡 Panduan Admin", "callback:help_admin")],
            [("🔒 Kebijakan Privasi", "callback:help_privacy")],
            [("🔙 Kembali", "callback:help_start")],
        ],
    },    
    "features": {
        "text": (
            "**📌 Fitur Umum yang Tersedia**\n\n"
            "Berikut adalah daftar fitur umum yang dapat diaktifkan di grup Anda untuk menjaga kenyamanan serta mengatur konten:\n\n"
            "• <b>Anti-Link</b>: Blokir pesan yang mengandung tautan\n"
            "• <b>Anti-Bot</b>: Cegah anggota menambahkan bot tanpa izin\n"
            "• <b>Filter Kata Kasar</b>: Deteksi dan hapus kata-kata tidak pantas\n"
            "• <b>Auto-Mute</b>: Otomatis bungkam anggota baru untuk waktu tertentu\n"
            "• <b>Anti-Spam</b>: Deteksi pengiriman pesan beruntun\n"
            "• <b>Notifikasi Join/Leave</b>: Menyembunyikan atau menampilkan pemberitahuan anggota keluar/masuk\n\n"
            "Gunakan perintah <code>/settings</code> atau menu admin untuk menyesuaikan fitur-fitur ini."
        ),
        "buttons": [
            [("🔙 Kembali", "callback:help_main")]
        ],
    },
    "admin": {
        "text": (
            "**🛡 Panduan Admin Grup**\n\n"
            "<blockquote>__Bot ini menyediakan berbagai fitur keamanan yang dapat membantu admin dalam menjaga ketertiban grup, memfilter konten yang tidak diinginkan, serta mencegah spam dan penyalahgunaan oleh anggota tidak bertanggung jawab.__</blockquote>\n\n"
            "Berikut daftar fitur keamanan yang tersedia. Klik salah satu untuk melihat penjelasan dan cara penggunaannya secara detail:"
        ),
        "buttons": [
            [("🤖 Anti-Bot", "callback:help_antibot"), ("🔁 Anti-Forward", "callback:help_antiforward")],
            [("🏷 Anti-Hashtags", "callback:help_Nohashtags"), ("💬 Anti-Flood", "callback:help_Noflood")],
            [("⛔️ Anti-Commands", "callback:help_Nocommands"), ("🎙 Anti-Voice Note", "callback:help_Novoice")],
            [("🚫 Blacklist", "callback:help_Blacklist")],
            [("📍 Filter Lokasi", "callback:help_Nolocations"), ("🔗 Filter Tautan", "callback:help_nolinks")],
            [("📅 Filter Event", "callback:help_noevents"), ("🖼 Filter Gambar", "callback:help_Noimage")],
            [("🔙 Kembali", "callback:help_main")],
        ],
    },
    "antiforward": {
        "text": "**🛡 Anti Forward Message**\n\n<blockquote>__Fitur antiforward dirancang untuk mencegah anggota grup mengirimkan pesan yang diteruskan (forwarded messages) dari chat atau grup lain. Pesan yang diteruskan sering kali dapat mengandung informasi yang tidak relevan, spam, atau bahkan konten yang tidak sesuai dengan kebijakan grup. Dengan mengaktifkan fitur ini, bot akan secara otomatis menghapus pesan yang berupa forward dan, bila perlu, memberikan peringatan kepada pengirimnya. Ini membantu menjaga orisinalitas dan kualitas diskusi dalam grup serta mencegah penyebaran konten yang tidak diinginkan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "antibot": {
        "text": "**🛡 Anti Bot Add**\n\n<blockquote>__Fitur antibot mencegah anggota biasa menambahkan bot lain ke dalam grup tanpa izin admin. Hal ini sangat penting untuk mencegah masuknya bot spam, bot berbahaya, atau bot yang mengganggu aktivitas grup. Ketika fitur ini aktif, hanya admin yang memiliki hak khusus yang dapat menambahkan bot ke dalam grup.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "nolinks": {
        "text": "**🛡 Filter Links**\n\n<blockquote>__Fitur nolinks secara aktif memindai setiap pesan yang dikirimkan anggota dan memblokir pesan yang mengandung tautan URL, baik berupa HTTP, HTTPS, tautan domain, maupun tautan Telegram (seperti t.me). Hal ini bertujuan untuk mengurangi risiko penyebaran spam, iklan, malware, atau link berbahaya lainnya yang dapat merugikan anggota grup. Dengan pengaturan ini, hanya pesan yang tidak mengandung tautan yang dapat dikirim, sehingga grup tetap terjaga dari konten berbahaya dan iklan yang tidak diinginkan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "noevents": {
        "text": "**🛡 Filtes Events**\n\n<blockquote>__Fitur noevents bertujuan untuk menonaktifkan atau menghalangi pesan yang berisi jenis-jenis event tertentu seperti undangan grup, stiker event, atau update acara yang tidak diinginkan. Ini membantu menjaga fokus diskusi di grup dan menghindari gangguan akibat pesan event yang tidak relevan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Nolocations": {
        "text": "**🛡 Anti Location**\n\n<blockquote>__Dengan fitur nolocations aktif, pengiriman lokasi (geotag, live location) di dalam grup akan dicegah. Ini bermanfaat untuk menghindari penyebaran informasi lokasi pribadi yang bisa menimbulkan risiko keamanan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Nocommands": {
        "text": "**🛡 Anti Commands**\n\n<blockquote>__Fitur ini mencegah anggota mengirimkan pesan yang berupa perintah (commands) bot tertentu secara tidak sengaja atau berlebihan, yang bisa mengganggu jalannya bot atau menyebabkan spam. Biasanya digunakan untuk membatasi command dari bot yang tidak diizinkan.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Nohashtags": {
        "text": "**🛡 Anti Hashtags**\n\n<blockquote>__Dengan fitur nohashtags, pesan yang berisi tanda pagar (#) atau hashtag akan diblokir. Ini menghindari penyalahgunaan hashtag untuk promosi atau spam yang tidak sesuai dengan aturan grup.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Noflood": {
        "text": "**🛡 Anti Flood**\n\n<blockquote>__Antiflood adalah mekanisme untuk mencegah spam berlebihan atau pengiriman pesan terlalu cepat secara berturut-turut oleh anggota. Jika seseorang mengirim pesan dalam jumlah besar dalam waktu singkat, bot akan memberikan peringatan atau mengeluarkan sementara dari grup untuk menjaga kenyamanan anggota lain.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Blacklist": {
        "text": (
            "**🛡 Kata Terlarang**\n\n"
            "<blockquote>__Blacklist adalah daftar kata, frasa, atau pengguna yang dilarang di grup. Jika ada anggota yang menggunakan kata-kata terlarang atau masuk dalam daftar blacklist, bot akan secara otomatis menindak seperti menghapus pesan atau memberikan peringatan.__</blockquote>\n\n"
            "📌 <b>Cara Menggunakan Blacklist:</b>\n\n"
            "🔹 <b>Lihat daftar blacklist</b>\n"
            "<code>/badwords list</code>\n\n"
            "🔹 <b>Tambah kata ke blacklist</b>\n"
            "<code>/badwords add <kata></code>\n"
            "Contoh: <code>/badwords add goblok</code>\n\n"
            "🔹 <b>Hapus kata dari blacklist</b>\n"
            "<code>/badwords rem <kata></code>\n"
            "Contoh: <code>/badwords rem goblok</code>\n\n"
            "💡 Gunakan dengan bijak untuk menjaga kenyamanan grup."
        ),
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Novoice": {
        "text": "**🛡 Anti Voice Note**\n\n<blockquote>__Fitur ini melarang pengiriman pesan suara atau voice notes dalam grup. Sangat cocok untuk grup yang mengutamakan komunikasi tertulis agar suasana diskusi tetap kondusif dan tidak berisik.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "Noimage": {
        "text": "**🛡 Anti Image**\n\n<blockquote>__Fitur imagefilter bertujuan untuk memfilter atau memblokir pengiriman gambar, foto, atau media visual tertentu yang tidak sesuai aturan grup. Bisa juga dikonfigurasi untuk memblokir gambar berukuran besar, gambar dengan konten tidak pantas, atau gambar dari sumber yang tidak terpercaya.__</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_admin")]
        ],
    },
    "privacy": {
        "text": "**📜 Kebijakan Privasi**\n\n<blockquote>Kami menghargai privasi dan keamanan data Anda. Kebijakan Privasi ini menjelaskan bagaimana kami mengumpulkan, menggunakan, menyimpan, dan melindungi informasi pribadi pengguna saat menggunakan layanan kami.</blockquote>\n\n"
                "**1. Informasi yang Kami Kumpulkan**\n<blockquote>"
                "- ID pengguna Telegram atau data publik lainnya dari platform tempat layanan dijalankan.\n"
                "- Data interaksi Anda dengan bot, seperti perintah yang digunakan dan preferensi pengaturan.\n"
                "- Informasi tambahan yang diberikan secara sukarela, seperti saran atau masukan.</blockquote>\n\n"
                "**2. Penggunaan Informasi**\n<blockquote>"
                "- Menyediakan dan meningkatkan layanan.\n"
                "- Personalisasi pengalaman pengguna.\n"
                "- Memastikan keamanan dan pencegahan penyalahgunaan.</blockquote>\n\n"
                "**3. Penyimpanan dan Keamanan**\n<blockquote>"
                "- Data disimpan secara lokal atau di server yang aman.\n"
                "- Kami mengambil langkah-langkah teknis dan organisasi yang wajar untuk melindungi data dari akses, perubahan, atau pengungkapan yang tidak sah.</blockquote>\n\n"
                "**4. Pembagian Data**\n<blockquote>"
                "- Kami tidak menjual, menyewakan, atau membagikan informasi pribadi Anda kepada pihak ketiga, kecuali jika diwajibkan oleh hukum.</blockquote>\n\n"
                "**5. Hak Pengguna**\n<blockquote>"
                "- Anda berhak meminta penghapusan data Anda.\n"
                "- Anda dapat menghubungi kami untuk informasi lebih lanjut terkait data yang disimpan.</blockquote>\n\n"
                "**6. Perubahan Kebijakan**\n<blockquote>"
                "- Kami berhak memperbarui kebijakan privasi ini kapan saja.\n"
                "- Perubahan akan diumumkan melalui saluran resmi atau langsung dalam layanan.</blockquote>\n\n"
                "**7. Kontak**\n<blockquote>"
                "Jika Anda memiliki pertanyaan mengenai kebijakan privasi ini, silakan hubungi admin kami:\n📩 Telegram: @phobiakalian</blockquote>",
        "buttons": [
            [("🔙 Kembali", "callback:help_main")]
        ],
    },
}

def make_keyboard(buttons):
    keyboard = []
    for row in buttons:
        button_row = []
        for text, action in row:
            if action.startswith("callback:"):
                button_row.append(InlineKeyboardButton(text, callback_data=action.replace("callback:", "", 1)))
            elif action.startswith("url:"):
                button_row.append(InlineKeyboardButton(text, url=action.replace("url:", "", 1)))
        keyboard.append(button_row)
    return InlineKeyboardMarkup(keyboard)


@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
        page = HELP_PAGES["main"]
        await message.reply(
            page["text"],
            reply_markup=make_keyboard(page["buttons"])
        )

@Client.on_callback_query(filters.regex("^help_"))
async def help_callback(client: Client, callback_query: CallbackQuery):
        data = callback_query.data.replace("help_", "")
        page_key = data if data in HELP_PAGES else "main"
        page = HELP_PAGES[page_key]
        if page_key == "start":
            await callback_query.message.edit_text(
                page["text"].format(callback_query.from_user.mention),
                reply_markup=make_keyboard(page["buttons"])
            )
            return await callback_query.answer()
        await callback_query.message.edit_text(
            page["text"],
            reply_markup=make_keyboard(page["buttons"])
        )
        await callback_query.answer()

