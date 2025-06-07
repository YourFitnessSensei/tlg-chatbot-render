import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
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
            return json.load(f)
    return {"1h": [], "24h": []}


def save_notified_event_ids(notified_dict):
    with open(NOTIFIED_EVENTS_FILE, "w") as f:
        json.dump(notified_dict, f)


def format_event_time(dt: datetime) -> str:
    day = dt.day
    month = RUS_MONTHS[dt.month]
    year = dt.year
    time_str = dt.strftime("%H:%M")
    return f"{day} {month} {year} в {time_str} по Москве"


async def check_and_notify(bot):
    service = get_calendar_service()
    now = datetime.utcnow()
    user_map = load_user_map()
    notified_event_ids = load_notified_event_ids()

    for calendar_id in CALENDAR_IDS:
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now.isoformat() + 'Z',
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            for event in events:
                event_id = event.get('id')
                summary = event.get("summary", "")
                start_raw = event['start'].get('dateTime', event['start'].get('date'))

                if not event_id or not start_raw:
                    continue

                start_dt = parser.parse(start_raw)
                time_diff = start_dt - now

                matched_chat_id = None
                matched_username = None

                for username, chat_id in user_map.items():
                    if username and username in summary:
                        matched_chat_id = chat_id
                        matched_username = username
                        break

                if not matched_chat_id:
                    continue

                notify_type = None
                if timedelta(minutes=59) < time_diff <= timedelta(hours=1, minutes=1):
                    notify_type = "1h"
                elif timedelta(hours=23) < time_diff <= timedelta(hours=25):
                    notify_type = "24h"

                if notify_type and event_id not in notified_event_ids[notify_type]:
                    message = (
                        f"🏋️ Привет, @{matched_username}!\n"
                        f"Напоминание: у тебя тренировка {format_event_time(start_dt)}"
                    )
                    try:
                        await bot.application.bot.send_message(chat_id=matched_chat_id, text=message)
                        logger.info(f"Уведомление {notify_type} отправлено @{matched_username} (chat_id: {matched_chat_id})")
                        notified_event_ids[notify_type].append(event_id)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке сообщения: {e}")

        except Exception as e:
            logger.error(f"Ошибка при проверке календаря {calendar_id}: {e}")

    save_notified_event_ids(notified_event_ids)


async def watch_calendar_loop(bot, interval_seconds=60):
    while True:
        await check_and_notify(bot)
        await asyncio.sleep(interval_seconds)
