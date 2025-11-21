from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ---------------------------
# Меню для роботи із статусом акаунта
# ---------------------------
async def show_user_status_menu(bot: Bot, chat_id: int):
    text = (
        "🔧 Керування статусом анкети\n\n"
        "Виберіть, що хочете зробити:\n"
        "✅ Активувати — анкета знову з’явиться в пошуку\n"
        "😴 Деактивувати — анкета стане невидимою для інших"
    )

    buttons = [
        [KeyboardButton(text = "✅ Активувати")],
        [KeyboardButton(text = "😴 Деактивувати")],
        [KeyboardButton(text = "⬅️ Назад")]
    ]

    kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
    await bot.send_message(chat_id, text, reply_markup = kb)