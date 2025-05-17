# main.py
import asyncio
import logging
import os
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import status

from calendar_watcher import watch_google_calendar
from src.bot.bot import run_bot  # run_bot запускает и держит бота живым

# Логгирование
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting lifespan")

    loop = asyncio.get_event_loop()
    background_tasks = set()

    task_bot = loop.create_task(run_bot())
    background_tasks.add(task_bot)
    task_bot.add_done_callback(background_tasks.discard)

    task_calendar = loop.create_task(watch_google_calendar())
    background_tasks.add(task_calendar)
    task_calendar.add_done_callback(background_tasks.discard)

    try:
        yield  # !!! Важно: yield до asyncio.Event().wait() = все завершится
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        for task in background_tasks:
            task.cancel()
        await asyncio.gather(*background_tasks, return_exceptions=True)
        raise
    finally:
        logging.info("Lifespan complete")


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return "Bot is running"

@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    return "OK"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
