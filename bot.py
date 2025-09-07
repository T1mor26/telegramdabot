import re
import asyncio
import string
import urllib.parse
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, Message

# Вставь свой токен и sticker_id
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"
STICKER_ID = "CAACAgIAAxkBAAEPRx9osv3fEm_YpnmF9di9yNREBJnjxwACuw0AAq9OeUiyCBJMdTHfNjYE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Регулярка для команды /pic с возможным упоминанием @BotUsername
CMD_RE = re.compile(r'^/pic(@\w+)?(?:\s|$)', re.IGNORECASE)

@dp.message()
async def unified_handler(message: Message):
    text = message.text
    if not text:
        return

    # 1) Если это команда /pic (включая /pic@BotName) — обрабатываем её
    if CMD_RE.match(text):
        prompt = re.sub(r'^/pic(@\w+)?\s*', '', text, flags=re.IGNORECASE).strip()
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
        return  # обработали команду — выходим

    # 2) Если сообщение — любая другая команда (/something) — игнорируем
    if text.startswith("/"):
        return

    # 3) Иначе — проверяем слова и реагируем стикером на "да" / "пизда"
    words = text.strip().lower().split()
    for word in words:
        clean = word.strip(string.punctuation)
        if clean in ("да", "пизда"):
            await message.reply_sticker(STICKER_ID)
            break

async def main():
    # Регистрируем команду в меню (опционально)
    await bot.set_my_commands([
        BotCommand(command="pic", description="Generate an image from text"),
    ])

    print("Бот запущен…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
