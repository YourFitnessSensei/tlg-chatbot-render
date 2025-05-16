import os
import logging
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

# Простейшее извлечение username из summary (если формат: "Тренировка @username")
def extract_username(summary: str) -> str | None:
    if "@" in summary:
        parts = summary.split("@")
        if len(parts) > 1:
            return parts[1].split()[0]
    return None

async def send_notification(summary: str, start_time: str):
    username = extract_username(summary)
    if not username:
        logging.warning(f"Не удалось извлечь username из summary: {summary}")
        return

    try:
        message = f"Привет, @{username}! У тебя тренировка {start_time}"
        await bot.send_message(chat_id=f"@{username}", text=message)
        logging.info(f"Отправлено уведомление @{username}")
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления @{username}: {e}")
