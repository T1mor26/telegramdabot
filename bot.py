import asyncio
import string
import urllib.parse
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BotCommand, Message

# 🔑 токен твоего бота
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"

# 👇 file_id стикера
STICKER_ID = "CAACAgIAAxkBAAEPRx9osv3fEm_YpnmF9di9yNREBJnjxwACuw0AAq9OeUiyCBJMdTHfNjYE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Стикер-триггер: реагируем на слова "да" и "пизда"
async def sticker_trigger(message: Message):
    if not message.text:
        return
    # Не реагируем на команды вида "/..."
    if message.text.startswith("/"):
        return

    words = message.text.strip().lower().split()
    for word in words:
        clean = word.strip(string.punctuation)
        if clean in ("да", "пизда"):
            await message.reply_sticker(STICKER_ID)
            break

dp.message.register(sticker_trigger)

# --- Команда /pic <prompt> (Pollinations.AI)
async def cmd_pic(message: Message):
    prompt = message.text[len("/pic"):].strip()
    if not prompt:
        await message.reply("Напиши, что сгенерировать. Пример:\n/pic cat in space")
        return

    await message.reply("⏳ Генерирую картинку...")
    encoded = urllib.parse.quote_plus(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}"

    try:
        await bot.send_photo(message.chat.id, photo=image_url, caption=f"✨ {prompt}")
    except Exception as e:
        await message.reply(f"⚠️ Не удалось отправить изображение: {e}")

# Регистрируем как TG-команду
dp.message.register(cmd_pic, Command("pic"))

async def main():
    # Настроим список команд в меню бота
    await bot.set_my_commands([
        BotCommand(command="pic", description="Generate an image from text"),
    ])
    print("Бот запущен…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
