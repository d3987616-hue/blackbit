import os
import logging
import requests
import time
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROUP_CHAT_ID = -1004446670922
WEB_APP_URL = "https://d3987616-hue.github.io/blackbit/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlackBitBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.app.add_handler(CommandHandler("start", self.start))

    async def start(self, update: Update, context):
        user = update.effective_user
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        await self.app.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"🟢 НОВЫЙ ВХОД В БОТА!\n\n"
                 f"👤 ID: `{user.id}`\n"
                 f"👤 Имя: {user.first_name or 'без имени'}\n"
                 f"👤 Username: @{user.username or 'нет'}\n"
                 f"🕐 Время: {current_time}",
            parse_mode="Markdown"
        )

        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"Нажмите кнопку ВНИЗУ, чтобы открыть приложение BlackBit.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("🔑 Войти", web_app=WebAppInfo(url=WEB_APP_URL))]],
                resize_keyboard=True
            )
        )

    def run(self):
        try:
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True')
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1&timeout=1')
            time.sleep(1)
        except:
            pass

        print("=" * 50)
        print("🚀 БОТ BLACKBIT ЗАПУЩЕН")
        print("=" * 50)
        self.app.run_polling()


if __name__ == "__main__":
    bot = BlackBitBot()
    bot.run()
