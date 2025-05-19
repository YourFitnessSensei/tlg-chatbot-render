# src/calendar_watcher.py

import threading
import logging
import time

logger = logging.getLogger(__name__)

def watch_calendar():
    while True:
        logger.info("🔍 Проверка событий календаря...")
        # Здесь должна быть ваша логика работы с Google Calendar API
        time.sleep(60)  # интервал проверки, например, каждую минуту

def start_calendar_watcher():
    watcher_thread = threading.Thread(target=watch_calendar, daemon=True)
    watcher_thread.start()
    logger.info("📡 Календарный вотчер запущен в отдельном потоке")
