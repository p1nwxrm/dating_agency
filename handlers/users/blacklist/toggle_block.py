from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import get_connection
from database.queries import add_to_blacklist, remove_from_blacklist

router = Router()

# ---------------------------
# Блокування / розблокування користувача
# ---------------------------
@router.callback_query(F.data.startswith("toggle_block:"))
async def toggle_block(callback: types.CallbackQuery):
    blocker_id = callback.from_user.id
    blocked_id = int(callback.data.split(":")[1])

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        # Перевіряємо, чи є користувач у ЧС
        cursor.execute("""
            SELECT 1 FROM blacklist
            WHERE blocker_id = %s AND blocked_id = %s
            LIMIT 1
        """, (blocker_id, blocked_id))
        in_blacklist = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    new_text = None
    new_button = None

    # Якщо користувача немає у ЧС → додаємо
    if not in_blacklist:
        success = add_to_blacklist(blocker_id, blocked_id)

        if success:
            new_text = "Користувача додано до чорного списку 🚫"
            new_button = InlineKeyboardButton(
                text = "🔓 Розблокувати",
                callback_data = f"toggle_block:{blocked_id}"
            )

    # Якщо користувач є у ЧС → розблоковуємо
    else:
        success = remove_from_blacklist(blocker_id, blocked_id)

        if success:
            new_text = "Користувача розблоковано 🔓"
            new_button = InlineKeyboardButton(
                text = "🚫 Заблокувати",
                callback_data = f"toggle_block:{blocked_id}"
            )

    if new_text is not None and new_button is not None:
        # Оновлюємо інлайн-клавіатуру і текст в повідомленні
        new_kb = InlineKeyboardMarkup(inline_keyboard = [[new_button]])
        await callback.message.edit_text(new_text, reply_markup = new_kb)