import asyncio
import string
from io import BytesIO
from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from craiyon import Craiyon  # из пакета craiyon.py

# 🔑 Твой токен
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"

# 👇 file_id стикера
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

        await message.reply("⏳ Генерация через Craiyon, подожди 20–40 секунд...")

        try:
            generator = Craiyon()  # клиент
            result = await asyncio.to_thread(generator.async_generate, prompt)

            # берём первые 3 картинки
            for img in result.images[:3]:
                bio = BytesIO(img)
                bio.name = "craiyon.png"
                await bot.send_photo(message.chat.id, photo=bio)

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
