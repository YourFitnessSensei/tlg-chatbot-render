import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from user_map import user_map, save_user_map

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.effective_user.username or str(chat_id)
        user_map[username] = chat_id
        save_user_map()
        await context.bot.send_message(chat_id=chat_id, text="✅ Ты успешно подписан на уведомления!")

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        # idle не нужен — FastAPI управляет циклом
