# src/bot/bot.py
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

user_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if user.username:
        user_map[user.username] = chat_id
        logging.info(f"Пользователь @{user.username} зарегистрирован с chat_id={chat_id}")
    else:
        logging.warning(f"Пользователь без username: chat_id={chat_id}")

    await update.message.reply_text("Бот запущен и готов к работе!")

async def run_bot():
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))

    await application.initialize()
    await application.start()
    logging.info("Telegram bot started")
    try:
        await asyncio.Event().wait()  # держим бота в фоне
    finally:
        await application.stop()
        await application.shutdown()
