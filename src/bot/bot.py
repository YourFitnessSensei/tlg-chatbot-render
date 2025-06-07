import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from user_store import add_user
#from src.calendar_watcher import find_next_event_for_user

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()

        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.handle_button))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            add_user(user.username, update.effective_chat.id)

            keyboard = [
                [InlineKeyboardButton("📅 Следующая тренировка", callback_data="next_training")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Вы подписаны на уведомления.",
                reply_markup=reply_markup
            )
            logger.info(f"Пользователь @{user.username} добавлен в user_store.")
        else:
            logger.warning("Не удалось определить пользователя")

    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "next_training":
            username = query.from_user.username
            event_message = find_next_event_for_user(username)
            if event_message:
                await context.bot.send_message(chat_id=query.message.chat_id, text=event_message)
            else:
                await context.bot.send_message(chat_id=query.message.chat_id, text="❌ Тренировка не найдена.")

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        # НЕ используем start_polling/wait_for_stop чтобы не конфликтовало с FastAPI
