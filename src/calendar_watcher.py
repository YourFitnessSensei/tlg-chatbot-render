import asyncio
import logging
from datetime import datetime, timedelta
from src.calendar.google_calendar import get_upcoming_events
from src.bot.user_map import user_map  # ключ: username, значение: chat_id

logger = logging.getLogger(__name__)

async def watch_calendar_loop(bot_instance):
    while True:
        try:
            await check_and_notify(bot_instance)
        except Exception as e:
            logger.exception(f"❌ Ошибка при проверке календаря: {e}")
        await asyncio.sleep(60)  # Проверка раз в 60 секунд

async def check_and_notify(bot_instance):
    calendars = [
        "feda623f7ff64223e61e023a56d72fb82c8741e7e58fea9696449c9d37073a90@group.calendar.google.com",
        "b8f68c9a9a6109f84e95071f4359e3d6afd261fcd3811fecaa0b81ba87ab0e3d@group.calendar.google.com",
    ]

    now = datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + timedelta(minutes=1)).isoformat() + "Z"

    for calendar_id in calendars:
        events = get_upcoming_events(calendar_id, time_min, time_max)

        if not events:
            logger.info(f"Нет событий в календаре {calendar_id}")
            continue

        for event in events:
            summary = event.get("summary", "")
            logger.info(f"[{calendar_id}] Событие: {summary} в {event['start']['dateTime']}")

            username = extract_username_from_summary(summary)
            if username in user_map:
                chat_id = user_map[username]
                message = f"Напоминание: {summary} начнётся в {event['start']['dateTime']}"
                await bot_instance.send_message(chat_id, message)
            else:
                logger.warning(f"Пользователь {username} не зарегистрирован в user_map")

def extract_username_from_summary(summary):
    # Пример: "Тренировка с @username" → "@username"
    words = summary.split()
    for word in words:
        if word.startswith("@"):
            return word
    return ""
