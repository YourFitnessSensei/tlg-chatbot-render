import os
import asyncio
import logging
from fastapi import FastAPI
from src.bot.bot import TelegramBot
from src.calendar_watcher import start_calendar_watcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
bot = None

@app.on_event("startup")
async def on_startup():
    global bot
    logger.info("🚀 Запуск приложения")

    # Запуск Telegram-бота
    bot = TelegramBot(token=os.environ["TELEGRAM_BOT_TOKEN"])
    asyncio.create_task(bot.run())  # не блокирует event loop

    # Запуск фонового календарного watcher
    start_calendar_watcher()
    logger.info("✅ Календарный watcher и бот запущены")

@app.get("/")
async def root():
    return {"status": "working"}
