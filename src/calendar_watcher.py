import asyncio
import logging
import os
import json
from datetime import datetime
from dateutil import parser
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from user_store import load_user_map

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

CALENDAR_IDS = [
    "feda623f7ff64223e61e023a56d72fb82c8741e7e58fea9696449c9d37073a90@group.calendar.google.com",
    "b8f68c9a9a6109f84e95071f4359e3d6afd261fcd3811fecaa0b81ba87ab0e3d@group.calendar.google.com"
]

NOTIFIED_EVENTS_FILE = "notified_events.json"

RUS_MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}


def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON не установлена")
    creds_info = json.loads(creds_json)
    credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return build('calendar', 'v3', credentials=credentials)


def load_notified_event_ids():
    if os.path.exists(NOTIFIED_EVENTS_FILE):
        with open(NOTIFIED_EVENTS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_notified_event_ids(event_ids):
    with open(NOTIFIED_EVENTS_FILE, "w") as f:
        json.dump(list(event_ids), f)


async def check_and_notify(bot):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'
    user_map = load_user_map()
    notified_event_ids = load_notified_event_ids()

    for calendar_id in CALENDAR_IDS:
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            for event in events:
                event_id = event.get('id')
                if not event_id or event_id in notified_event_ids:
                    continue  # Пропускаем, если уже отправляли

                summary = event.get("summary", "")
                matched_chat_id = None

                for username, chat_id in user_map.items():
                    if username in summary:
                        matched_chat_id = chat_id
                        break

                if not matched_chat_id:
                    continue  # Пропускаем, если не найден пользователь

                # Форматируем дату/время
                start_raw = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = parser.parse(start_raw)
                day = start_dt.day
                month = RUS_MONTHS[start_dt.month]
                year = start_dt.year
                time_str = start_dt.strftime("%H:%M")

                message = (
                    f"🏋️ Привет, {summary}\n"
                    f"🗓 У тебя тренировка {day} {month} {year}\n"
                    f"⏰ В {time_str} по Москве"
                )

                try:
                    await bot.application.bot.send_message(chat_id=matched_chat_id, text=message)
                    logger.info(f"Отправлено уведомление для {matched_chat_id}")
                    notified_event_ids.add(event_id)  # Запоминаем, чтобы не спамить
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения: {e}")

        except Exception as e:
            logger.error(f"Ошибка при проверке календаря {calendar_id}: {e}")

    save_notified_event_ids(notified_event_ids)


async def watch_calendar_loop(bot, interval_seconds=60):
    while True:
        await check_and_notify(bot)
        await asyncio.sleep(interval_seconds)
