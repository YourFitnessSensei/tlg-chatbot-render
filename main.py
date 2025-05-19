import asyncio
import logging
import os
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI, status

from calendar_watcher import watch_google_calendar
from src.bot.bot import TelegramBot

logging.basicConfig(level=logging.INFO)

bot_instance = None

def run_bot_in_thread():
    global bot_instance
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logging.error("TELEGRAM_BOT_TOKEN не задан!")
        return
    bot_instance = TelegramBot(token)
    asyncio.run(bot_instance.run())  # запускаем polling

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🔄 Starting lifespan")

    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot_in_thread, name="BotThread", daemon=True)
    bot_thread.start()

    # Запускаем Google Calendar Watcher
    asyncio.create_task(watch_google_calendar())

    yield
    logging.info("🌙 Lifespan завершён")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return "Bot is running"

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return "OK"

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
