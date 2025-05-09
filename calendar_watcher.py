import asyncio
import os
import logging
from datetime import datetime, timedelta
import pytz
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Получаем переменные окружения
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
CALENDAR_IDS = os.getenv("GOOGLE_CALENDAR_IDS", "").split(",")

# Проверка
if not GOOGLE_CREDENTIALS_JSON or not CALENDAR_IDS:
    raise ValueError("GOOGLE_CREDENTIALS_JSON и GOOGLE_CALENDAR_IDS должны быть заданы в переменных окружения")

# Загружаем учётные данные
credentials = service_account.Credentials.from_service_account_info(
    json.loads(GOOGLE_CREDENTIALS_JSON),
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)

# Асинхронная функция для отслеживания событий
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
                        start = event["start"].get("dateTime", event["start"].get("date"))
                        logging.info(f"[{calendar_id}] Событие: {event['summary']} в {start}")
                        # Здесь можно вызывать бота / отправку сообщений

            except Exception as e:
                logging.error(f"Ошибка при получении событий из {calendar_id}: {e}")

        await asyncio.sleep(60) 

