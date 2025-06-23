import time
import os
import requests
from yt_dlp import YoutubeDL
from io import BytesIO
from thumb import create_player_card

def download_audio(query: str) -> tuple[str, str, str, int]:
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "quiet": True,
        "cookiefile": "cookies.txt",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        title = info["title"]
        artist = info.get("uploader", "Unknown Artist")
        
        # Durasi dalam detik
        duration_seconds = int(info.get("duration", 0))
        
        # Format durasi (mm:ss) untuk ditampilkan
        duration_display = str(duration_seconds // 60) + ":" + str(duration_seconds % 60).zfill(2)
        
        thumbnail_url = info.get("thumbnail", "")
        filename = ydl.prepare_filename(info).replace(".webm", ".opus").replace(".m4a", ".opus")
        thumbnail_path = f"downloads/thumbnails/{title}.jpg"

        if thumbnail_url:
            create_player_card(thumbnail_url, title, artist, duration_display, thumbnail_path)

        return title, filename, thumbnail_path, duration_seconds
