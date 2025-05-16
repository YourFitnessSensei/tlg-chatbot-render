import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

user_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if user.username:
        user_map[user.username] = chat_id
        logging.info(f"Пользователь @{user.username} зарегистрирован с chat_id={chat_id}")
    else:
        logging.warning(f"Пользователь без username: chat_id={chat_id}")

    await update.message.reply_text("Бот запущен и готов к работе!")

class TelegramBot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.application.add_handler(CommandHandler("start", start))

    async def start(self):
        # Инициализация и старт бота (без run_polling)
        await self.application.initialize()
        await self.application.start()
        logging.info("Telegram Bot started")

    async def stop(self):
        # Корректная остановка бота
        await self.application.stop()
        await self.application.shutdown()
        logging.info("Telegram Bot stopped")

    async def idle(self):
        # Задержка чтобы бот работал
        await self.application.updater.idle()

async def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = TelegramBot(token)
    await bot.start()
    try:
        # Вместо run_polling просто держим таску живой
        while True:
            await asyncio.sleep(60)
    finally:
        await bot.stop()
