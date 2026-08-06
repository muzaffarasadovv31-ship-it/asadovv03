import asyncio
import logging
import os
import re
import uuid

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")


DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

INSTAGRAM_URL_PATTERN = re.compile(
    r"(https?://(?:www\.)?instagram\.com/(?:reel|p|tv)/[A-Za-z0-9_\-]+/?\S*)"
)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Assalomu alaykum! 👋\n\n"
        "Menga Instagram video havolasini yuboring, men uni yuklab beraman.\n\n"
        "Masalan:\n"
        "<code>https://www.instagram.com/reel/XXXXXXXXXXX/</code>"
    )

@dp.message(F.text.regexp(INSTAGRAM_URL_PATTERN))
async def download_instagram_video(message: Message):
    match = INSTAGRAM_URL_PATTERN.search(message.text)
    url = match.group(1)

    status_msg = await message.answer("⏳ Video yuklab olinmoqda, biroz kuting...")

    file_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{file_id}.mp4")

    ydl_opts = {
        "outtmpl": output_path,
        "format": "mp4/best",
        "quiet": True,
        "no_warnings": True,
    }

    try:
        loop = asyncio.get_event_loop()

        def run_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, run_download)

        if os.path.exists(output_path):
            video_file = FSInputFile(output_path)
            await message.answer_video(video_file, caption="✅ Mana video!")
            os.remove(output_path)
        else:
            await status_msg.edit_text("❌ Video topilmadi.")

    except Exception as e:
        logging.error(f"Yuklashda xatolik: {e}")
        await status_msg.edit_text("❌ Video yuklab bo'lmadi.")
    finally:
        try:
            await status_msg.delete()
        except Exception:
            pass

@dp.message(F.text)
async def other_text(message: Message):
    await message.answer("Iltimos, to'g'ri Instagram havolasini yuboring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
