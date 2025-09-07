import asyncio
import string
import base64
import aiohttp
from io import BytesIO
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand, FSInputFile

# 🔑 токен
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"
STICKER_ID = "CAACAgIAAxkBAAEPRx9osv3fEm_YpnmF9di9yNREBJnjxwACuw0AAq9OeUiyCBJMdTHfNjYE"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message()
async def handler(message: Message):
    text = message.text
    if not text:
        return

    # команда /pic
    if text.startswith("/pic"):
        prompt = text.replace("/pic", "").strip()
        if not prompt:
            await message.reply("Напиши, что сгенерировать: /pic кот в космосе")
            return

        await message.reply("⏳ Генерирую картинку через Craiyon... (занимает 15–30 сек)")

        try:
            async with aiohttp.ClientSession() as session:
                # отправляем запрос на Craiyon API
                async with session.post(
                    "https://backend.craiyon.com/generate",
                    json={"prompt": prompt}
                ) as resp:
                    if resp.status != 200:
                        await message.reply(f"Ошибка Craiyon: {resp.status}")
                        return
                    data = await resp.json()

            # Craiyon отдаёт список base64 картинок
            images = data.get("images")
            if not images:
                await message.reply("⚠️ Craiyon не вернул изображения")
                return

            # Берём первую картинку
            img_b64 = images[0]
            img_bytes = base64.b64decode(img_b64)

            # Отправляем как файл (без сохранения на диск)
            bio = BytesIO(img_bytes)
            bio.name = "image.png"
            await bot.send_photo(message.chat.id, photo=bio, caption=f"✨ {prompt}")

        except Exception as e:
            await message.reply(f"⚠️ Ошибка: {e}")
        return

    # если не команда → проверка на "да" и "пизда"
    words = text.strip().lower().split()
    for word in words:
        clean = word.strip(string.punctuation)
        if clean in ("да", "пизда"):
            await message.reply_sticker(STICKER_ID)
            break


async def main():
    await bot.set_my_commands([
        BotCommand(command="pic", description="Generate image with Craiyon")
    ])
    print("Бот запущен…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
