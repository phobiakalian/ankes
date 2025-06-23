from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests, os
from io import BytesIO

def create_player_card(thumbnail_url: str, title: str, artist: str, duration: str, output_path: str) -> str:
    try:
        response = requests.get(thumbnail_url)
        cover = Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        raise Exception(f"Gagal unduh thumbnail: {e}")

    # Ukuran canvas: landscape HD
    canvas_size = (1024, 576)
    canvas = Image.new("RGBA", canvas_size, (0, 0, 0))
    bg_blur = cover.resize(canvas_size).filter(ImageFilter.GaussianBlur(15))
    canvas.paste(bg_blur, (0, 0))

    # Player card
    card = Image.new("RGBA", (900, 400), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)

    # Rounded background
    card_draw.rounded_rectangle((0, 0, 900, 400), radius=40, fill=(40, 40, 40, 230))

    # Area thumbnail (dalam kartu)
    cover_resized = cover.resize((300, 300))
    card.paste(cover_resized, (40, 50))

    # Font
    try:
        font_title = ImageFont.truetype("font/DejaVuSans-Bold.ttf", 36)
        font_artist = ImageFont.truetype("font/DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("font/DejaVuSans.ttf", 18)
    except:
        font_title = font_artist = font_small = ImageFont.load_default()

    # Batasi panjang judul max 36 karakter
    short_title = title if len(title) <= 36 else title[:33] + "..."

    # Teks judul & artis
    card_draw.text((370, 60), short_title, font=font_title, fill="white")
    card_draw.text((370, 110), artist, font=font_artist, fill="lightgray")

    # Bar waktu
    card_draw.rounded_rectangle((370, 180, 820, 200), radius=8, fill="#888")  # total bar
    card_draw.rounded_rectangle((370, 180, 500, 200), radius=8, fill="white") # progress
    card_draw.text((370, 210), "1:08", font=font_small, fill="white")
    card_draw.text((770, 210), duration, font=font_small, fill="white")

    # Tombol media
    symbols = ["⏮", "⏸", "⏭"]
    for i, symbol in enumerate(symbols):
        card_draw.text((420 + i*80, 260), symbol, font=font_title, fill="white")

    # Volume bar
    card_draw.rounded_rectangle((370, 330, 770, 345), radius=6, fill="#666")
    card_draw.rounded_rectangle((370, 330, 600, 345), radius=6, fill="white")

    # Logo YN × MUSIC di pojok kanan bawah kartu
    card_draw.text((680, 360), "YN × MUSIC", font=font_artist, fill="white")

    # Gabungkan ke background
    canvas.paste(card, (62, 88), card)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG")
    return output_path
