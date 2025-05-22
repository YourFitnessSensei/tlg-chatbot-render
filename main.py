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

    # Запускаем проверку календаря
    asyncio.create_task(watch_calendar_loop(bot))

    # Запускаем бота (это должен быть последний шаг, т.к. run_polling — бесконечный)
    await bot.run()
