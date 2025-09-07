import asyncio
import string
import urllib.parse
import aiohttp
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

        await message.reply("⏳ Генерирую картинку...")

        encoded = urllib.parse.quote_plus(prompt)
        # ⚠️ Это пример — возьмём API Craiyon (демо)
        url = f"https://image.pollinations.ai/prompt/{encoded}"

        try:
            # качаем картинку
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await message.reply(f"Ошибка генерации: {resp.status}")
                        return
                    data = await resp.read()
                    file_path = f"temp.png"
                    with open(file_path, "wb") as f:
                        f.write(data)

            # отправляем как файл
            photo = FSInputFile(file_path)
            await bot.send_photo(message.chat.id, photo=photo, caption=f"✨ {prompt}")

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
        BotCommand(command="pic", description="Generate image")
    ])
    print("Бот запущен…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
