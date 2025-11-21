from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ---------------------------
# Меню оцінки (лайк/дизлайк/скарга)
# ---------------------------
async def show_user_rating_menu(bot: Bot, chat_id: int):
    rating_text = "Оціни анкету 👇"

    buttons = [
        [KeyboardButton(text = "❤️ Лайк"), KeyboardButton(text = "💔 Дизлайк")],
        [KeyboardButton(text = "🚨 Скарга"), KeyboardButton(text = "🚫 ЧС")],
        [KeyboardButton(text = "⬅️ Меню")]
    ]
    rating_kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
    await bot.send_message(chat_id, rating_text, reply_markup = rating_kb)