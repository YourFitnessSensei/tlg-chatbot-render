import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_service():
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
    credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    service = build("calendar", "v3", credentials=credentials)
    return service

async def check_and_notify(client: TelegramClient):
    service = get_calendar_service()
    calendar_ids = os.environ["GOOGLE_CALENDAR_ID"].split(",")

    while True:
        now = datetime.utcnow()
        time_max = now + timedelta(hours=24)
        notified = set()

        for calendar_id in calendar_ids:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now.isoformat() + "Z",
                timeMax=time_max.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])
            for event in events:
                description = event.get("description", "")
                start = event["start"].get("dateTime")
                if not start or "@" not in description:
                    continue

                username = [word for word in description.split() if word.startswith("@")]
                if not username:
                    continue
                username = username[0]

                event_time = datetime.fromisoformat(start[:-1])  # remove trailing 'Z'
                diff = event_time - now

                event_id = event["id"]
                if (event_id, username) in notified:
                    continue

                # отправка сразу после создания
                created = event.get("created")
                if created and (now - datetime.fromisoformat(created[:-1])) < timedelta(minutes=5):
                    await client.send_message(username, f"Вы записаны на тренировку в {event_time.strftime('%H:%M %d.%m')}")
                    notified.add((event_id, username))

                # напоминание за 2 часа
                if timedelta(hours=1, minutes=55) < diff < timedelta(hours=2, minutes=5):
                    await client.send_message(username, f"Напоминаем о тренировке через 2 часа — в {event_time.strftime('%H:%M %d.%m')}")
                    notified.add((event_id, username))

        await asyncio.sleep(300)  # ждать 5 минут
