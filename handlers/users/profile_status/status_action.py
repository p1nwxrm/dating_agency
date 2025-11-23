from aiogram import Router, types

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from database.db import get_connection
from show_menus import show_user_main_menu

router = Router()

# ---------------------------
# Робота із статусом анкети
# ---------------------------
@router.message(UserMenu.status_menu)
async def handle_status_action(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Введи текст.")
        return

    text = message.text.strip()

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id FROM users WHERE tg_username = %s", (message.from_user.username,))
    user = cursor.fetchone()

    if not user:
        await message.answer("❌ Користувача не знайдено у базі даних.")
        cursor.close()
        conn.close()
        return

    user_id = user["id"]

    # --- Активувати профіль ---
    if text == "✅ Активувати":
        cursor.execute("UPDATE profiles SET is_active = TRUE WHERE user_id = %s", (user_id,))
        conn.commit()
        await message.answer("🌞 Анкету активовано! Тепер її видно іншим користувачам.")

    # --- Деактивувати профіль ---
    elif text == "😴 Деактивувати":
        cursor.execute("UPDATE profiles SET is_active = FALSE WHERE user_id = %s", (user_id,))
        conn.commit()
        await message.answer("😴 Анкету деактивовано. Вона не відображається іншим.")

    elif text != "⬅️ Назад":
        await message.answer("❌ Обери один із варіантів нижче.")
        cursor.close()
        conn.close()
        return

    cursor.close()
    conn.close()
    await show_user_main_menu(message.bot, message.chat.id)
    await state.set_state(UserMenu.main_menu)
