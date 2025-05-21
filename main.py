import logging
import os
from fastapi import FastAPI
from src.bot.bot import TelegramBot
from src.calendar_watcher import start_calendar_watcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot: TelegramBot | None = None

@app.on_event("startup")
async def on_startup():
    global bot
    logger.info("🔄 Startup: Инициализация")

    bot = TelegramBot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    await bot.run()
    logger.info("✅ Telegram бот запущен")

    start_calendar_watcher()
    logger.info("📅 Google Calendar Watcher запущен")

@app.on_event("shutdown")
async def on_shutdown():
    global bot
    if bot:
        await bot.shutdown()
        logger.info("🛑 Telegram бот остановлен")
