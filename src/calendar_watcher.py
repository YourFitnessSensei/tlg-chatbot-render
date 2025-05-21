import asyncio
import datetime
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

from telegram import Bot
from user_map import user_map  # user_map в корне проекта

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SERVICE_ACCOUNT_FILE = 'creds.json'

# Список ID календарей
CALENDAR_IDS = [
    "feda623f7ff64223e61e023a56d72fb82c8741e7e58fea9696449c9d37073a90@group.calendar.google.com",
    "b8f68c9a9a6109f84e95071f4359e3d6afd261fcd3811fecaa0b81ba87ab0e3d@group.calendar.google.com"
]

def get_upcoming_events(calendar_id, time_min, time_max):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=credentials)

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

async def watch_calendar_loop(bot: Bot):
    logging.info("🔁 Цикл наблюдения за календарём запущен")
    while True:
        now = datetime.datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + datetime.timedelta(hours=1)).isoformat() + 'Z'

        for calendar_id in CALENDAR_IDS:
            try:
                events = get_upcoming_events(calendar_id, time_min, time_max)

                if not events:
                    logging.info(f"Нет событий в календаре {calendar_id}")
                    continue

                for event in events:
                    summary = event.get("summary", "")
                    start = event["start"].get("dateTime", event["start"].get("date"))

                    for username, chat_id in user_map.items():
                        if f"@{username}" in summary:
                            msg = f"📅 Напоминание: {summary} в {start}"
                            await bot.send_message(chat_id=chat_id, text=msg)
                            logging.info(f"✅ Отправлено: {msg} -> @{username}")
                        else:
                            logging.warning(f"⛔ Пользователь @{username} не найден в событии {summary}")
            except Exception as e:
                logging.error(f"Ошибка при проверке календаря {calendar_id}: {e}")

        await asyncio.sleep(60)  # Ждём 60 секунд перед следующей проверкой
