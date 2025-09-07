import os
import re
import asyncio
import string
import base64
from io import BytesIO

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand, Message

# === Настройки (твой токен уже вставлен) ===
TOKEN = "5754410446:AAEGkNkTL5gB0Bo8w5qwmh5ZfxGyHOeyX4I"
STICKER_ID = "CAACAgIAAxkBAAEPRx9osv3fEm_YpnmF9di9yNREBJnjxwACuw0AAq9OeUiyCBJMdTHfNjYE"

# Hugging Face (опционально). Если хочешь использовать HF, добавь HF_TOKEN в env:
HF_TOKEN = os.getenv("HF_TOKEN")  # пример: "hf_xxx..."
HF_MODEL = os.getenv("HF_MODEL", "stabilityai/stable-diffusion-2")  # можно менять

bot = Bot(token=TOKEN)
dp = Dispatcher()

CMD_RE = re.compile(r'^/pic(@\w+)?(?:\s|$)', re.IGNORECASE)


async def fetch_from_huggingface(prompt: str) -> BytesIO:
    """Попытка сгенерировать через Hugging Face Inference API.
    Возвращает BytesIO с изображением или возбуждает Exception."""
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            text = await resp.text()
            ct = resp.headers.get("content-type", "")
            if resp.status != 200:
                raise Exception(f"HuggingFace API {resp.status}: {text[:500]}")

            # Если вернулось изображение (image/png or octet-stream)
            if "image" in ct or "octet-stream" in ct:
                data = await resp.read()
                bio = BytesIO(data)
                bio.name = "image.png"
                bio.seek(0)
                return bio

            # Если JSON — попробуем добыть base64
            try:
                data_json = await resp.json()
            except Exception:
                raise Exception(f"HuggingFace returned non-image non-json response: {text[:500]}")

            # Варианты ключей с base64-строками
            if isinstance(data_json, dict):
                # common keys: 'images', 'generated_images', maybe list of dicts
                for key in ("images", "generated_images", "image", "data"):
                    if key in data_json:
                        val = data_json[key]
                        if isinstance(val, list) and len(val) > 0:
                            b64 = val[0]
                            if isinstance(b64, str):
                                raw = base64.b64decode(b64)
                                bio = BytesIO(raw)
                                bio.name = "image.png"
                                bio.seek(0)
                                return bio
                # maybe it's list of dicts at top level
            if isinstance(data_json, list) and len(data_json) > 0:
                first = data_json[0]
                if isinstance(first, dict) and "image_base64" in first:
                    raw = base64.b64decode(first["image_base64"])
                    bio = BytesIO(raw)
                    bio.name = "image.png"
                    bio.seek(0)
                    return bio

            raise Exception("HuggingFace returned JSON but no recognizable image data found.")


async def fetch_from_craiyon(prompt: str) -> BytesIO:
    """Запрос через библиотеку craiyon.py (fallback)."""
    # импорт здесь, чтобы не требовать craiyon.py если HF используется и craiyon.py не установлен
    try:
        from craiyon import Craiyon
    except Exception as e:
        raise Exception("craiyon.py не установлен или недоступен: " + str(e))

    generator = Craiyon()
    # use blocking generate in a thread
    result = await asyncio.to_thread(generator.generate, prompt)
    # result.images — список байтов (в зависимости от реализации)
    if not getattr(result, "images", None):
        raise Exception("Craiyon вернул пустой ответ.")
    first = result.images[0]
    # если элемент — строка base64
    if isinstance(first, str):
        raw = base64.b64decode(first)
    else:
        raw = first  # bytes
    bio = BytesIO(raw)
    bio.name = "image.png"
    bio.seek(0)
    return bio


async def generate_image_with_fallback(prompt: str) -> BytesIO:
    """Пытаемся HF (если задан), иначе Craiyon. Делает 3 попытки с backoff."""
    last_exc = None
    attempts = 3
    for attempt in range(attempts):
        try:
            if HF_TOKEN:
                return await fetch_from_huggingface(prompt)
            else:
                return await fetch_from_craiyon(prompt)
        except Exception as e:
            last_exc = e
            # backoff
            await asyncio.sleep(1 + attempt * 2)
            continue
    raise last_exc or Exception("Неизвестная ошибка генерации")


@dp.message()
async def unified_handler(message: Message):
    text = message.text
    if not text:
        return

    # 1) Команда /pic или /pic@Bot
    if CMD_RE.match(text):
        prompt = re.sub(r'^/pic(@\w+)?\s*', '', text, flags=re.IGNORECASE).strip()
        if not prompt:
            await message.reply("Напиши, что сгенерировать. Пример:\n/pic cat in space")
            return

        await message.reply("⏳ Генерирую картинку... (может занять 10–60 с)")

        try:
            img_bio = await generate_image_with_fallback(prompt)
            img_bio.seek(0)
            await bot.send_photo(message.chat.id, photo=img_bio, caption=f"✨ {prompt}")
        except Exception as e:
            await message.reply(f"⚠️ Ошибка генерации: {e}")
        return

    # 2) Игнорируем другие команды
    if text.startswith("/"):
        return

    # 3) Стикер-триггер: слова "да" и "пизда"
    words = text.strip().lower().split()
    for word in words:
        clean = word.strip(string.punctuation)
        if clean in ("да", "пизда"):
            await message.reply_sticker(STICKER_ID)
            break


async def main():
    # регистрируем команду в меню (опционально)
    try:
        await bot.set_my_commands([BotCommand(command="pic", description="Generate image")])
    except Exception:
        pass
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
