# src/bot/bot.py

import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()

        self.application.add_handler(CommandHandler("start", self.start_handler))

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        logger.info("✅ Telegram-бот готов к работе")

    async def shutdown(self):
        await self.application.stop()
        await self.application.shutdown()
        logger.info("🛑 Telegram-бот остановлен")

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_text(f"Привет, {user.first_name}!")
