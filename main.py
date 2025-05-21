import asyncio
import logging
from fastapi import FastAPI
import os
from src.bot.bot import TelegramBot
from src.calendar_watcher import watch_calendar_loop

logging.basicConfig(level=logging.INFO)

bot = TelegramBot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    logging.info("🚀 FastAPI запущен")

    # Запускаем Telegram бота
    asyncio.create_task(bot.run())

    # Запускаем проверку календаря в фоне
    asyncio.create_task(watch_calendar_loop(bot))
