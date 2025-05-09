import logging
import os
import telegram
from telegram import Bot
from dotenv import load_dotenv

# Загрузка ключей
def load_keys():
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    return bot_token

# Инициализация бота
bot_token = load_keys()
bot = Bot(token=bot_token)

async def send_message(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logging.info(f"Message sent to {chat_id}: {message}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# Пример использования
async def watch_google_calendar():
    # Пример с событиями из календаря
    chat_id = 'your_chat_id'  # Укажите ID вашего чата
    message = "Пример события из календаря!"
    await send_message(chat_id, message)
