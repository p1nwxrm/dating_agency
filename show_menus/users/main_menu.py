from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ---------------------------
# Головне меню
# ---------------------------
async def show_user_main_menu(bot: Bot, chat_id: int):
    text = (
        "Оберіть дію нижче 👇\n\n"
        "1️⃣ Переглянути інші анкети 💫\n"
        "2️⃣ Взаємні симпатії ❤️\n"
        "3️⃣ Чорний список 🚫\n"
        "4️⃣ Редагувати анкету ✏️\n"
        "5️⃣ Власна статистика 📊\n"
        "6️⃣ Керувати статусом 🟢🔴"
    )

    buttons = [
        [KeyboardButton(text = "1"), KeyboardButton(text = "2")],
        [KeyboardButton(text = "3"), KeyboardButton(text = "4")],
        [KeyboardButton(text = "5"), KeyboardButton(text = "6")]
    ]

    menu_kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
    await bot.send_message(chat_id, text, reply_markup = menu_kb)