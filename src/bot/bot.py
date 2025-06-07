import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from user_store import add_user
from scr.calendar_watcher import find_next_event_for_user

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CallbackQueryHandler(self.handle_button_click))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user:
            add_user(user.username, update.effective_chat.id)
            keyboard = [[InlineKeyboardButton("\u23E9 Следующая тренировка", callback_data="next_training")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Вы подписаны на уведомления.",
                reply_markup=reply_markup
            )
            logger.info(f"Пользователь @{user.username} добавлен в user_store.")
        else:
            logger.warning("Не удалось определить пользователя")

    async def handle_button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        await query.answer()

        if query.data == "next_training":
            username = query.from_user.username
            response = await find_next_event_for_user(username)
            if response:
                await context.bot.send_message(chat_id=query.message.chat_id, text=response)
            else:
                await context.bot.send_message(chat_id=query.message.chat_id, text="\u2639\ufe0f Нет запланированных тренировок.")

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        #await self.application.updater.start_polling()
        #await self.application.updater.wait_for_stop()
