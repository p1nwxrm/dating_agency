from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ---------------------------
# Головне меню для адміна
# ---------------------------
async def show_admin_main_menu(bot: Bot, chat_id: int):
    text = (
        "⚙️⚙️️ Адмін-панель ⚙️⚙️\n"
        "Оберіть потрібну дію 👇\n\n"
        "1️⃣ Статистика користувачів 📊\n"
        "2️⃣ Адміни та модератори 👑\n"
        "3️⃣ Змінити роль користувача 🔄\n"
        "4️⃣ Керування банами 🚫"
    )

    buttons = [
        [KeyboardButton(text = "📊 Статистика")],
        [KeyboardButton(text = "👑 Адміни та модератори")],
        [KeyboardButton(text = "🔄 Змінити роль")],
        [KeyboardButton(text = "🚫 Керування банами")]
    ]

    kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
    await bot.send_message(chat_id, text, reply_markup = kb)