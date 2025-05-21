import logging
import asyncio

logger = logging.getLogger(__name__)

def start_calendar_watcher():
    async def watcher():
        while True:
            logger.info("📅 Проверка календаря...")
            await asyncio.sleep(30)  # Примерная задержка

    asyncio.create_task(watcher())
