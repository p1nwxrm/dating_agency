import logging
from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.queries import get_all_reasons

# ---------------------------
# Меню вибору причини скарги
# ---------------------------
async def show_complaints_menu(bot: Bot, chat_id: int):
    try:
        reasons = get_all_reasons()

        if not reasons:
            await bot.send_message(chat_id, "⚠️ Немає доступних причин для скарг.")
            return

        reasons_text = "Обери, будь ласка, причину скарги:\n\n"
        for r in reasons:
            reasons_text += f"{r["id"]}. {r["name"]}\n"

        buttons = [
            [KeyboardButton(text = str(r["id"])) for r in reasons],
            [KeyboardButton(text = "⬅️ Назад")]
        ]
        reasons_kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
        await bot.send_message(chat_id, reasons_text, reply_markup = reasons_kb)
    except Exception as e:
        logging.exception(e)