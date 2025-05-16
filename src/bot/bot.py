import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен и готов к работе!")

# Функция запуска бота (используется в main.py)
async def run_bot():
    logging.info("Запуск Telegram-бота")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Инициализируем и запускаем бота вручную
    await application.initialize()
    await application.start()

    # Запускаем polling в фоне (без .idle())
    asyncio.create_task(application.updater.start_polling())

