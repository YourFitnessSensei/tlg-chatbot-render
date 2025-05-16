import asyncio
import logging

from fastapi import FastAPI
import uvicorn

from bot.bot import run_bot  # твой Telegram-бот
from calendar_watcher import watch_google_calendar  # фоновая задача

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Bot is alive"}

@app.on_event("startup")
async def startup_event():
    logging.info("🎯 Запускаю фоновые задачи: бот и календарь")
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    loop.create_task(watch_google_calendar())

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("📴 Завершение работы")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
