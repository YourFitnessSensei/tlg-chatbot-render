import asyncio
import logging
import os
import json
from datetime import datetime, timedelta, timezone
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


def save_notified_event_ids(data):
    with open(NOTIFIED_EVENTS_FILE, "w") as f:
        json.dump(data, f)


async def check_and_notify(bot):
    service = get_calendar_service()
    now = datetime.now(timezone.utc)
    user_map = load_user_map()
    notified_events = load_notified_event_ids()

    for calendar_id in CALENDAR_IDS:
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now.isoformat(),
                maxResults=20,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            for event in events:
                event_id = event.get('id')
                if not event_id:
                    continue

                summary = event.get("summary", "")
                matched_chat_id = None

                for username, chat_id in user_map.items():
                    if username in summary:
                        matched_chat_id = chat_id
                        break

                if not matched_chat_id:
                    continue

                # Время события
                start_raw = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = parser.parse(start_raw)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)

                time_diff = start_dt - now

                # Форматируем дату/время
                day = start_dt.day
                month = RUS_MONTHS[start_dt.month]
                year = start_dt.year
                time_str = start_dt.strftime("%H:%M")

                message = (
                    f"🏋️ Привет, {summary}\n"
                    f"🗓 У тебя тренировка {day} {month} {year}\n"
                    f"⏰ В {time_str} по Москве"
                )

                # Отправка уведомлений
                if timedelta(hours=0) < time_diff <= timedelta(hours=1) and event_id not in notified_events["1h"]:
                    try:
                        await bot.application.bot.send_message(chat_id=matched_chat_id, text="⏰ Напоминание за 1 час!\n" + message)
                        logger.info(f"[1h] Уведомление отправлено: {event_id}")
                        notified_events["1h"].append(event_id)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке [1h]: {e}")

                elif timedelta(hours=1) < time_diff <= timedelta(hours=24) and event_id not in notified_events["24h"]:
                    try:
                        await bot.application.bot.send_message(chat_id=matched_chat_id, text="📅 Напоминание за 24 часа!\n" + message)
                        logger.info(f"[24h] Уведомление отправлено: {event_id}")
                        notified_events["24h"].append(event_id)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке [24h]: {e}")

        except Exception as e:
            logger.error(f"Ошибка при проверке календаря {calendar_id}: {e}")

    save_notified_event_ids(notified_events)


async def watch_calendar_loop(bot, interval_seconds=60):
    while True:
        await check_and_notify(bot)
        await asyncio.sleep(interval_seconds)
