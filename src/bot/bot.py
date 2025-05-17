# bot.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from user_map import user_map  # предполагается, что user_map — это глобальный словарь в отдельном файле

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Первое сообщение — сразу подтверждаем получение команды
    await update.message.reply_text("Команда /start получена, бот запускается...")

    user = update.effective_user
    chat_id = update.effective_chat.id

    if user.username:
        user_map[user.username] = chat_id
        logging.info(f"Пользователь @{user.username} зарегистрирован с chat_id={chat_id}")
        await update.message.reply_text("Пользователь зарегистрирован, бот запущен и готов к работе!")
    else:
        logging.warning(f"Пользователь без username: chat_id={chat_id}")
        await update.message.reply_text("Пользователь без username, регистрация невозможна.")

class TelegramBot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.application.add_handler(CommandHandler("start", start))

    async def run(self):
        logging.info("Telegram Bot started")
        await self.application.run_polling()
