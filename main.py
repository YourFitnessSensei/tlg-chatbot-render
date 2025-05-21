import logging
import os
import asyncio
from fastapi import FastAPI
from src.bot.bot import TelegramBot
from src.calendar_watcher import start_calendar_watcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot = None

@app.on_event("startup")
async def startup_event():
    global bot
    logger.info("🔄 Инициализация приложения")

    bot = TelegramBot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    asyncio.create_task(bot.run())
    logger.info("✅ Telegram-бот запущен")

    start_calendar_watcher()
    logger.info("📅 Обработчик календаря запущен")

@app.get("/")
async def root():
    return {"message": "Приложение работает"}

@app.on_event("shutdown")
async def shutdown_event():
    global bot
    if bot:
        await bot.shutdown()
        logger.info("🛑 Telegram-бот остановлен")
