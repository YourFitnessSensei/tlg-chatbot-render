import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from user_map import user_map

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.application = ApplicationBuilder().token(token).build()
        self.user_map = user_map

        self.application.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("📥 Получена команда /start")  # Для проверки, что handler сработал
        chat_id = update.effective_chat.id
        self.user_map[chat_id] = True  # подписываем пользователя
        await context.bot.send_message(chat_id=chat_id, text="👋 Бот запущен. Вы подписаны на уведомления.")

    async def run(self):
        logger.info("🚀 Старт Telegram бота")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def shutdown(self):
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
