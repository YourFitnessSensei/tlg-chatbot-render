import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Generator

import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import StreamingResponse

from __version__ import __version__
from calendar_watcher import watch_google_calendar
from src.bot.bot import run_bot  # функция запуска бота (НЕ объект Bot!)
from src.utils import (
    BOT_NAME,
    create_initial_folders,
    get_date_time,
    initialize_logging,
)

# --- Логгирование и инициализация ---
create_initial_folders()
console_out = initialize_logging()
time_str = get_date_time("Asia/Ho_Chi_Minh")

try:
    BOT_VERSION = __version__
except Exception:
    BOT_VERSION = "unknown"

# --- lifespan-функция и FastAPI app ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    background_tasks = set()

    task_bot = loop.create_task(run_bot())
    background_tasks.add(task_bot)
    task_bot.add_done_callback(background_tasks.discard)

    task_calendar = loop.create_task(watch_google_calendar())
    background_tasks.add(task_calendar)
    task_calendar.add_done_callback(background_tasks.discard)

    logging.info("App successfully started")

    # ✔️ НЕ БЛОКИРУЕМ запуск FastAPI!
    yield

    # 👇 Здесь отрабатывает shutdown
    logging.info("Lifespan shutting down")
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)


# --- Инициализация FastAPI только один раз ---
app = FastAPI(lifespan=lifespan, title=BOT_NAME)

# --- Роуты ---
@app.get("/")
async def root() -> str:
    return f"{BOT_NAME} {BOT_VERSION} is deployed!"

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> str:
    return f"{BOT_NAME} {BOT_VERSION} health check"

@app.get("/log")
async def log_check() -> StreamingResponse:
    async def generate_log() -> Generator[bytes, None, None]:
        console_log = console_out.getvalue()
        yield console_log.encode("utf-8")
    return StreamingResponse(generate_log())

# --- Запуск на Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
