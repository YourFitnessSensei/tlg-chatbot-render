import asyncio
import logging
import os
import json
from datetime import datetime
from dateutil import parser
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone

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

def find_next_event_for_user(username: str):
    service = get_calendar_service()
    now = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    
    for calendar_id in CALENDAR_IDS:
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get("items", [])
            for event in events:
                summary = event.get("summary", "")
                if username.lower() in summary.lower():
                    start_raw = event["start"].get("dateTime", event["start"].get("date"))
                    start_dt = parser.parse(start_raw)
                    day = start_dt.day
                    month = RUS_MONTHS[start_dt.month]
                    year = start_dt.year
                    time_str = start_dt.strftime("%H:%M")

                    return (
                        f"🏋️ Следующая тренировка, {summary}\n"
                        f"🗓 {day} {month} {year}\n"
                        f"⏰ В {time_str} по Москве"
                    )

        except Exception as e:
            logger.error(f"Ошибка при поиске тренировки в календаре {calendar_id}: {e}")
    
    return "🔍 Тренировок не найдено."

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
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    now_iso = now.isoformat()

    user_map = load_user_map()
    notified_event_ids = load_notified_event_ids()

    for calendar_id in CALENDAR_IDS:
        try:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now_iso,
                maxResults=10,
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
                    if username.lower() in summary.lower():
                        matched_chat_id = chat_id
                        break

                if not matched_chat_id:
                    continue

                start_raw = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = parser.parse(start_raw).astimezone(timezone.utc)
                time_until_event = start_dt - now

                # Напоминание за 24 часа
                if 23.5 * 3600 < time_until_event.total_seconds() < 24.5 * 3600:
                    reminder_id_24h = f"{event_id}_24h"
                    if reminder_id_24h not in notified_event_ids:
                        message = (
                            f"⏰ Напоминание! Завтра тренировка: {summary}\n"
                            f"🗓 {start_dt.strftime('%d')} {RUS_MONTHS[start_dt.month]} {start_dt.year}\n"
                            f"⏰ В {start_dt.strftime('%H:%M')} по Москве"
                        )
                        try:
                            await bot.application.bot.send_message(chat_id=matched_chat_id, text=message)
                            logger.info(f"Отправлено напоминание за 24ч для {matched_chat_id}")
                            notified_event_ids.add(reminder_id_24h)
                        except Exception as e:
                            logger.error(f"Ошибка при отправке напоминания (24ч): {e}")

                # Напоминание за 1 час
                elif 0.5 * 3600 < time_until_event.total_seconds() < 1.5 * 3600:
                    reminder_id_1h = f"{event_id}_1h"
                    if reminder_id_1h not in notified_event_ids:
                        message = (
                            f"⏰ Скоро тренировка: {summary}\n"
                            f"🕐 Через час — в {start_dt.strftime('%H:%M')} по Москве!"
                        )
                        try:
                            await bot.application.bot.send_message(chat_id=matched_chat_id, text=message)
                            logger.info(f"Отправлено напоминание за 1ч для {matched_chat_id}")
                            notified_event_ids.add(reminder_id_1h)
                        except Exception as e:
                            logger.error(f"Ошибка при отправке напоминания (1ч): {e}")

                # Основное уведомление (если не было)
                if event_id not in notified_event_ids:
                    message = (
                        f"🏋️ Привет, {summary}\n"
                        f"🗓 У тебя тренировка {start_dt.strftime('%d')} {RUS_MONTHS[start_dt.month]} {start_dt.year}\n"
                        f"⏰ В {start_dt.strftime('%H:%M')} по Москве"
                    )
                    try:
                        await bot.application.bot.send_message(chat_id=matched_chat_id, text=message)
                        logger.info(f"Отправлено основное уведомление для {matched_chat_id}")
                        notified_event_ids.add(event_id)
                    except Exception as e:
                        logger.error(f"Ошибка при отправке основного сообщения: {e}")

        except Exception as e:
            logger.error(f"Ошибка при проверке календаря {calendar_id}: {e}")

    save_notified_event_ids(notified_event_ids)


async def watch_calendar_loop(bot, interval_seconds=60):
    while True:
        await check_and_notify(bot)
        await asyncio.sleep(interval_seconds)

