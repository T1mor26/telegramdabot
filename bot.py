import asyncio
import string
from aiogram import Bot, Dispatcher, types

# 🔑 токен от BotFather
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"

# 👇 file_id твоего стикера
STICKER_ID = "CAACAgIAAxkBAAEPRx9osv3fEm_YpnmF9di9yNREBJnjxwACuw0AAq9OeUiyCBJMdTHfNjYE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ========= ОБРАБОТЧИК СТИКЕРОВ =========
async def check_message(message: types.Message):
    if not message.text:
        return

    words = message.text.strip().lower().split()

    for word in words:
        clean_word = word.strip(string.punctuation)
        if clean_word in ("да", "пизда"):
            await message.reply_sticker(STICKER_ID)
            break

dp.message.register(check_message)

# ========= ОБРАБОТЧИК КАРТИНОК =========
async def send_image(message: types.Message):
    if not message.text.startswith("/картинка"):
        return

    prompt = message.text.replace("/картинка", "").strip()
    if not prompt:
        await message.reply("Напиши, что сгенерировать. Пример:\n/картинка кот в космосе")
        return

    await message.reply("⏳ Генерирую картинку...")

    try:
        # Pollinations.AI работает без ключа, можно сразу давать ссылку
        image_url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"
        await bot.send_photo(message.chat.id, photo=image_url, caption=f"✨ Вот твоя картинка: {prompt}")
    except Exception as e:
        await message.reply(f"⚠️ Ошибка генерации: {e}")

dp.message.register(send_image)

# ========= СТАРТ =========
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
