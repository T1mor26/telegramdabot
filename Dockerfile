import asyncio
import string
from aiogram import Bot, Dispatcher, types

# 🔑 токен от BotFather
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"

# 👇 file_id своего стикера
STICKER_ID = "CAACAgIAAxkBAAEPRx9osv3fEm_YpnmF9di9yNREBJnjxwACuw0AAq9OeUiyCBJMdTHfNjYE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_message(message: types.Message):
    if not message.text:
        return

    words = message.text.strip().lower().split()

    for word in words:
        # убираем знаки пунктуации с конца слова
        clean_word = word.strip(string.punctuation)

        # реагируем на 'да' и 'пизда'
        if clean_word in ("да", "пизда"):
            await message.reply_sticker(STICKER_ID)
            break

# Регистрируем обработчик сообщений
dp.message.register(check_message)

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
