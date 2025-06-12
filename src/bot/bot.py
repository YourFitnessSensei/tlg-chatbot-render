import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from user_store import add_user
from src.calendar_watcher import find_next_event_for_user

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.button_handler))

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

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "next_training":
            user = update.effective_user
            if not user:
                await query.edit_message_text("Пользователь не определён.")
                return

            event_text = await find_next_event_for_user(user.username)
            await query.edit_message_text(event_text)

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("🤖 Бот запущен")

    #async def run(self):
        #await self.application.run_polling()
        #await self.application.initialize()
        #await self.application.start()
        #await self.application.updater.start_polling()
        #await self.application.updater.wait_for_stop()
