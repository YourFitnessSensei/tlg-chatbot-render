import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from user_store import add_user

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.application.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            add_user(user.username, update.effective_chat.id)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Вы подписаны на уведомления."
            )
            logger.info(f"Пользователь @{user.username} добавлен в user_store.")
        else:
            logger.warning("Не удалось определить пользователя")

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await self.application.updater.wait_for_stop()
