from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ---------------------------
# Головне меню для модераторів
# ---------------------------
async def show_moderator_main_menu(bot: Bot, chat_id: int):
    text = (
        "🛠 Панель модератора 🛠\n"
        "Оберіть потрібну дію 👇\n\n"
        "1️⃣ Керування банами 🚫\n"
        "2️⃣ Перегляд скарг 🚨\n"
        "3️⃣ Моя статистика 📈"
    )

    buttons = [
        [KeyboardButton(text = "🚫 Керування банами")],
        [KeyboardButton(text = "🚨 Скарги")],
        [KeyboardButton(text = "📈 Моя статистика")]
    ]

    kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
    await bot.send_message(chat_id, text, reply_markup = kb)