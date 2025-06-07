import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from user_store import add_user
from src.calendar_watcher import get_next_event_for_user  # создадим эту функцию отдельно

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()

        # Регистрируем команды и кнопки
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.handle_button))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            add_user(user.username, update.effective_chat.id)
            logger.info(f"Пользователь @{user.username} добавлен в user_store.")

            # Кнопка
            keyboard = [[InlineKeyboardButton("Следующая тренировка", callback_data="next_training")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Вы подписаны на уведомления.",
                reply_markup=reply_markup
            )
        else:
            logger.warning("Не удалось определить пользователя")

    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        username = query.from_user.username
        chat_id = query.message.chat_id

        logger.info(f"Нажата кнопка пользователем @{username}")

        # Получаем следующее событие из календаря
        event_text = await get_next_event_for_user(username)
        if event_text:
            await context.bot.send_message(chat_id=chat_id, text=event_text)
        else:
            await context.bot.send_message(chat_id=chat_id, text="🔍 Вы еще не записались.")

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        await self.application.updater.wait_for_stop()
