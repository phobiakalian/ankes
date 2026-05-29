# 🛡️ Yn Security Bot - Panduan Lengkap

Bot keamanan grup Telegram profesional dengan fitur lengkap dan dukungan multi-bahasa.

## ✨ Fitur Utama

### 🔐 Keamanan
- **Anti-Forward**: Mencegah forward pesan dari chat lain
- **No-Links**: Blokir semua jenis link (HTTP, HTTPS, Telegram, dll)
- **No-Events**: Blokir pesan event (user joined via invite link)
- **No-Contacts**: Blokir pengiriman contact
- **No-Locations**: Blokir pengiriman location
- **No-Commands**: Blokir command di grup
- **No-Hashtags**: Blokir hashtag
- **No-Voice**: Blokir voice note dan video note
- **Image Filter**: Filter gambar berdasarkan konten
- **Anti-Bot**: Deteksi dan kick bot otomatis
- **Anti-Flood**: Proteksi spam pesan
- **Detect Edit Pesan**: Deteksi pelanggaran pada pesan yang diedit

### 👥 Manajemen User
- **Warning System**: Sistem peringatan otomatis
- **Free User Management**: Kelola user gratis
- **Ban/Unban**: Ban permanen atau temporer
- **Mute/Unmute**: Mute user dengan durasi custom
- **Tagall**: Tag semua member grup

### 📝 Notes & Saved Messages
- **Simpan Catatan**: `/save <nama>` untuk menyimpan aturan, FAQ, info grup
- **Panggil Catatan**: `#nama` atau `/get nama` untuk memanggil
- **List Notes**: `/notes` untuk melihat semua catatan
- **Hapus Notes**: `/delnote <nama>` untuk menghapus
- **Support Media**: Text, photo, document, video, sticker

### 📊 Dashboard & Statistik
- **Dashboard Grup**: `/dashboard` untuk melihat statistik real-time
  - Member baru hari ini
  - Pesan dihapus
  - Pelanggaran terdeteksi
  - Total mute/ban
- **Activity Report**: `/report [hari]` untuk laporan aktivitas user
  - User paling aktif
  - User paling sering di-mute
  - User paling sering di-kick
  - Violations per tipe

### 🌐 Multi-Language Support
- **10 Bahasa**: Indonesian, English, Arabic, Spanish, French, German, Russian, Chinese, Japanese, Korean
- **Auto-Detect**: Deteksi bahasa dari judul grup
- **Manual Setting**: `/language` untuk mengatur bahasa manual

### ⚙️ Admin Commands
- `/save <nama>` - Simpan catatan
- `/delnote <nama>` - Hapus catatan
- `/notes` - List semua catatan
- `/dashboard` - Tampilkan statistik grup
- `/report [hari]` - Laporan aktivitas (default: 7 hari)
- `/language` - Atur bahasa bot
- `/mylang` - Lihat bahasa saat ini
- `/toggleeditcheck` - Toggle deteksi edit pesan
- `/ban [durasi] [alasan]` - Ban user
- `/unban` - Unban user
- `/mute [durasi] [alasan]` - Mute user
- `/unmute` - Unmute user
- `/addbadwords` - Tambah kata terlarang
- `/clearbadwords confirm` - Hapus semua badwords
- `/checkbadwords <teks>` - Cek teks mengandung badwords

## 🚀 Cara Menjalankan

### 1. Persiapan Environment

```bash
# Buat virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\Activate.ps1  # Windows

# Upgrade pip
pip install --upgrade pip
```

### 2. Instalasi Dependensi

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Bot

**Opsi A: Menggunakan Environment Variables (Recommended)**

Buat file `.env`:
```bash
cp .env.example .env
nano .env
```

Isi dengan credentials Anda:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
LOG_CHAT=-1001234567890
```

**Opsi B: Edit File Config**

Edit `yn/config.py` langsung (tidak recommended untuk production).

### 4. Mendapatkan API Credentials

1. Kunjungi https://my.telegram.org/apps
2. Login dengan nomor Telegram Anda
3. Buat aplikasi baru
4. Salin **API ID** dan **API Hash**

### 5. Mendapatkan Bot Token

1. Buka @BotFather di Telegram
2. Ketik `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Salin token yang diberikan

### 6. Menjalankan Bot

**Mode Testing (Foreground):**
```bash
python -m yn
```

**Mode Production (Background):**
```bash
nohup python -m yn > bot.log 2>&1 &

# Lihat log
tail -f bot.log

# Stop bot
pkill -f "python -m yn"
```

## 📁 Struktur Database

Bot menggunakan SQLite dengan file berikut:
- `ankesDB.sqlite3` - Settings grup
- `ankeswarn.sqlite3` - Warning system
- `ankesfree.sqlite3` - Free users
- `ankesauth.sqlite3` - Authorized users
- `ankesstats.sqlite3` - Statistics
- `ankesusers.sqlite3` - User data
- `ankesnotes.sqlite3` - Notes/saved messages

## 🔧 Troubleshooting

### Error: "API key is required"
- Pastikan `API_ID` dan `API_HASH` sudah diisi dengan benar
- Cek file `.env` atau `yn/config.py`

### Error: "No module named 'uvloop'"
```bash
pip install uvloop
```

### Bot tidak merespon command
- Pastikan bot sudah diinvite ke grup sebagai admin
- Cek apakah plugin tidak di-disable di `config.py`
- Lihat log untuk error detail

### Database error
```bash
# Hapus database corrupt dan restart
rm *.sqlite3
python -m yn
```

## 📞 Support

Jika mengalami masalah:
1. Cek log file (`bot.log`)
2. Pastikan semua dependencies terinstall
3. Verifikasi credentials di `.env`
4. Test dengan command sederhana seperti `/start`

## 📝 License

Gunakan dengan bijak dan bertanggung jawab.

---

**Dibuat dengan ❤️ untuk komunitas Telegram Indonesia**
