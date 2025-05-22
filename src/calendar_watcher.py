import asyncio
import logging
import os
import json
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from telegram import Bot

from user_map import user_map  # Глобальный словарь пользователей

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# ID календарей
CALENDAR_IDS = [
    "feda623f7ff64223e61e023a56d72fb82c8741e7e58fea9696449c9d37073a90@group.calendar.google.com",
    "b8f68c9a9a6109f84e95071f4359e3d6afd261fcd3811fecaa0b81ba87ab0e3d@group.calendar.google.com"
]

def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("Переменная окружения GOOGLE_CREDENTIALS_JSON не установлена")
    
    try:
        creds_info = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        return service
    except Exception as e:
        logger.error(f"Ошибка при создании клиента календаря: {e}")
        raise

async def check_and_notify(bot):  # Не указываем тип Bot, он не telegram.Bot
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'  # UTC время

    for calendar_id in CALENDAR_IDS:
        try:
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

                for chat_id in user_map.values():
                    try:
                        await bot.application.bot.send_message(chat_id=chat_id, text=message)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке сообщения: {e}")
        except Exception as e:
            logger.error(f"Ошибка при проверке календаря {calendar_id}: {e}")


async def watch_calendar_loop(bot: Bot, interval_seconds: int = 60):
    while True:
        try:
            await check_and_notify(bot)
        except Exception as e:
            logger.error(f"Ошибка в календарном вотчере: {e}")
        await asyncio.sleep(interval_seconds)
