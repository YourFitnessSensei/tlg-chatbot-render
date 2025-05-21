import asyncio
import logging
from datetime import datetime, timezone

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from telegram import Bot

from user_map import user_map  # Глобальный словарь пользователей

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = 'C:\Users\Екатерина\Desktop\bot\yourfitnesssenseibot-1b0a46d0accf.json'

# ID календарей
CALENDAR_IDS = [
    "feda623f7ff64223e61e023a56d72fb82c8741e7e58fea9696449c9d37073a90@group.calendar.google.com",
    "b8f68c9a9a6109f84e95071f4359e3d6afd261fcd3811fecaa0b81ba87ab0e3d@group.calendar.google.com"
]

def get_calendar_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    service = build('calendar', 'v3', credentials=credentials)
    return service

async def check_and_notify(bot: Bot):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' означает UTC время

    for calendar_id in CALENDAR_IDS:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=5,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            logger.info(f"Нет событий в календаре {calendar_id}")
            continue

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            message = f"Новое событие в календаре:\n{event.get('summary', 'Без названия')}\nНачало: {start}"

            logger.info(f"Отправляем уведомление о событии в календаре {calendar_id}")

            # Рассылаем всем пользователям
            for user_id in user_map.keys():
                try:
                    await bot.send_message(chat_id=user_id, text=message)
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

async def calendar_watcher_loop(bot: Bot, interval_seconds: int = 60):
    while True:
        try:
            await check_and_notify(bot)
        except Exception as e:
            logger.error(f"Ошибка в календарном вотчере: {e}")
        await asyncio.sleep(interval_seconds)
