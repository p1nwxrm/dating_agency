from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.db import get_connection

# ---------------------------
# Меню вибору причини скарги
# ---------------------------
async def show_user_complaints_menu(bot: Bot, chat_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute("SELECT id, name FROM reasons ORDER BY id")
        reasons = cursor.fetchall()

        if not reasons:
            await bot.send_message(chat_id, "⚠️ Немає доступних причин для скарг.")
            return

        reasons_text = "Обери, будь ласка,  причину скарги:\n\n"
        for r in reasons:
            reasons_text += f"{r['id']}. {r['name']}\n"

        buttons = [
            [KeyboardButton(text = str(r["id"])) for r in reasons],
            [KeyboardButton(text = "⬅️ Назад")]
        ]
        reasons_kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)
        await bot.send_message(chat_id, reasons_text, reply_markup = reasons_kb)
    finally:
        cursor.close()