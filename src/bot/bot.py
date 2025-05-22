import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

from calendar_watcher import watch_calendar_loop
from user_map import user_map  # глобальный словарь

logger = logging.getLogger(__name__)

TOKEN = "7655995093:AAFXF6tJ-DAAp36IJmJUuP0qCW6VvMlvJFc"  # замени на свой токен

class TelegramBot:
    def __init__(self):
        self.application = ApplicationBuilder().token(TOKEN).build()
        self.application.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user_map[chat_id] = True  # сохраняем chat_id
        await context.bot.send_message(chat_id=chat_id, text="👋 Бот запущен. Вы подписаны на уведомления.")
        logger.info(f"Добавлен chat_id: {chat_id} в user_map")

    async def run(self):
        await self.application.initialize()
        await self.application.start()

        watcher_task = asyncio.create_task(watch_calendar_loop(self.application.bot))

        logger.info("Бот и календарный воркер запущены")

        await self.application.updater.idle()

        watcher_task.cancel()
        try:
            await watcher_task
        except asyncio.CancelledError:
            pass

        await self.application.stop()
        await self.application.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = TelegramBot()
    asyncio.run(bot.run())
