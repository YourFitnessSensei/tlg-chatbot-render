import asyncio
import logging
import os
import json
from datetime import datetime

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from telegram import Bot

from user_map import user_map

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

CALENDAR_IDS = [
    "feda623f7ff64223e61e023a56d72fb82c8741e7e58fea9696449c9d37073a90@group.calendar.google.com",
    "b8f68c9a9a6109f84e95071f4359e3d6afd261fcd3811fecaa0b81ba87ab0e3d@group.calendar.google.com"
]

def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON не установлена")
    creds_info = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return build('calendar', 'v3', credentials=credentials)

async def check_and_notify(bot: Bot):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'

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

            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                message = f"🗓 Новое событие: {event.get('summary', 'Без названия')}\n⏰ Начало: {start}"

                logger.info(f"Отправка события из календаря {calendar_id}")

                for chat_id in user_map.values():
                    try:
                        await bot.send_message(chat_id=chat_id, text=message)
                    except Exception as e:
                        logger.error(f"Ошибка отправки в чат {chat_id}: {e}")
        except Exception as e:
            logger.error(f"Ошибка при работе с календарем {calendar_id}: {e}")

async def watch_calendar_loop(telegram_bot, interval_seconds=60):
    while True:
        try:
            await check_and_notify(telegram_bot.application.bot)
        except Exception as e:
            logger.error(f"Ошибка в вотчере календаря: {e}")
        await asyncio.sleep(interval_seconds)
