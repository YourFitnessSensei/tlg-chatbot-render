import asyncio
import os
import logging
from datetime import datetime, timedelta
import pytz
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build

from telegram import Bot
from user_map import user_map



# Telegram bot instance
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

# Переменные окружения
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
CALENDAR_IDS = os.getenv("GOOGLE_CALENDAR_IDS", "").split(",")

# Проверка переменных
if not GOOGLE_CREDENTIALS_JSON or not CALENDAR_IDS:
    raise ValueError("GOOGLE_CREDENTIALS_JSON и GOOGLE_CALENDAR_IDS должны быть заданы")

# Учётные данные Google
credentials = service_account.Credentials.from_service_account_info(
    json.loads(GOOGLE_CREDENTIALS_JSON),
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)

def extract_username(summary: str) -> str | None:
    if summary and "@" in summary:
        parts = summary.split("@")
        if len(parts) > 1:
            return parts[1].split()[0].strip()
    return None

async def watch_google_calendar():
    service = build("calendar", "v3", credentials=credentials)
    logging.info("Google Calendar Watcher запущен")

    while True:
        now = datetime.utcnow().isoformat() + "Z"
        time_max = (datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z"

        for calendar_id in CALENDAR_IDS:
            try:
                events_result = service.events().list(
                    calendarId=calendar_id.strip(),
                    timeMin=now,
                    timeMax=time_max,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()
                events = events_result.get("items", [])

                if not events:
                    logging.info(f"Нет событий в календаре {calendar_id}")
                else:
                    for event in events:
                        summary = event.get("summary", "")
                        start = event["start"].get("dateTime", event["start"].get("date"))
                        logging.info(f"[{calendar_id}] Событие: {summary} в {start}")

                        username = extract_username(summary)
                        if username:
                            chat_id = user_map.get(username)
                            if chat_id:
                                try:
                                    await bot.send_message(
                                        chat_id=chat_id,
                                        text=f"Напоминание: {summary} в {start}"
                                    )
                                    logging.info(f"Уведомление отправлено @{username}")
                                except Exception as e:
                                    logging.error(f"Ошибка при отправке уведомления @{username}: {e}")
                            else:
                                logging.warning(f"Пользователь @{username} не зарегистрирован в user_map")
                        else:
                            logging.warning(f"Не удалось извлечь username из summary: {summary}")

            except Exception as e:
                logging.error(f"Ошибка при обработке календаря {calendar_id}: {e}")

        await asyncio.sleep(60)
