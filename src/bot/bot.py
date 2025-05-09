import logging
import os
from telegram import Bot
from dotenv import load_dotenv

# Загрузка ключей
def load_keys():
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    return bot_token

# Инициализация бота
bot_token = load_keys()
telegram_bot = Bot(token=bot_token)

async def send_message(chat_id, message):
    try:
        await telegram_bot.send_message(chat_id=chat_id, text=message)
        logging.info(f"Message sent to {chat_id}: {message}")
    except Exception as e:
        logging.error(f"Error sending message: {e}")

# Запускаем бота
async def start_bot():
    chat_id = 'your_chat_id'  # ← заменишь позже на нужный ID или username
    message = "Пример события из календаря!"
    await send_message(chat_id, message)

