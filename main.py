import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi import status
from src.bot.bot import TelegramBot

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
async def root():
    return "Bot is running"

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return "OK"

if __name__ == "__main__":
    import asyncio

    async def main():
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logging.error("TELEGRAM_BOT_TOKEN не задан!")
            return
        bot = TelegramBot(token)
        await bot.run()  # Запускаем бот, внутри него запустим watcher

    asyncio.run(main())
