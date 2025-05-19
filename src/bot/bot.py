from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from user_map import user_map
import logging
import asyncio
from calendar_watcher import watch_google_calendar  # импортируем тут

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("Команда /start получена от пользователя %s", update.effective_user.username)
    await update.message.reply_text("Привет! Ты успешно запустил бота.")
    
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

    async def run(self):
        logging.info("Запуск Telegram бота и watcher-а календаря")

        # запускаем watch_google_calendar параллельно
        task = asyncio.create_task(watch_google_calendar())
        await self.application.run_polling()
        await task  # этот await никогда не выполнится, но он тут чтобы не потерять task
