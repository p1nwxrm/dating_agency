from aiogram import Router, types

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from database.db import get_connection
from database.queries import send_complaint, add_interaction, get_dislike_type_id

from .viewing import viewing_profiles
from handlers.users.show_menus import show_user_rating_menu

router = Router()

# ---------------------------
# Обробка вибору причини скарги
# ---------------------------
@router.message(UserMenu.complaints_menu)
async def handle_complaint_reason(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if text == "⬅️ Назад":
        await show_user_rating_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.rate_menu)
        return

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        # Отримуємо користувача, що подає скаргу
        cursor.execute("SELECT id FROM users WHERE tg_username = %s", (message.from_user.username,))
        user = cursor.fetchone()
        if not user:
            await message.answer("❌ Користувача не знайдено.")
            return
        applicant_id = user["id"]

        data = await state.get_data()
        current_profile_id = data.get("current_profile_id")

        cursor.execute("SELECT user_id FROM profiles WHERE id = %s", (current_profile_id,))
        evaluated = cursor.fetchone()
        if not evaluated:
            await message.answer("❌ Анкету не знайдено.")
            return
        violator_id = evaluated["user_id"]

        # Отримуємо всі причини з БД
        cursor.execute("SELECT id, name FROM reasons ORDER BY id")
        reasons = cursor.fetchall()
        reason_ids = [str(r["id"]) for r in reasons]

        if text not in reason_ids:
            await message.answer("❌ Обери номер причини зі списку або натисни '⬅️ Назад'.")
            return

        reason_id = int(text)

        # Якщо вибрана причина “Інше”
        cursor.execute("SELECT name FROM reasons WHERE id = %s", (reason_id,))
        reason = cursor.fetchone()
        if reason and "інше" in reason["name"].lower():
            await state.update_data(reason_id = reason_id, applicant_id = applicant_id, violator_id = violator_id)
            await message.answer("📝 Опиши детальніше причину:")
            await state.set_state(UserMenu.other_complaints)
            return

        # Якщо звичайна причина
        success = send_complaint(applicant_id, violator_id, reason_id)

        if success:
            # Додаємо взаємодію «Дизлайк»
            dislike_id = get_dislike_type_id()
            add_interaction(applicant_id, violator_id, dislike_id)
            await message.answer("✅ Скаргу відправлено. Дякуємо за повідомлення!")

        await viewing_profiles(message, state)
    finally:
        cursor.close()
        conn.close()

# ---------------------------
# Обробка текстового опису "інше"
# ---------------------------
@router.message(UserMenu.other_complaints)
async def handle_other_reason_description(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()

    applicant_id = data.get("applicant_id")
    violator_id = data.get("violator_id")
    reason_id = data.get("reason_id")

    # Додаємо скаргу
    success = send_complaint(applicant_id, violator_id, reason_id, text)

    if success:
        # Додаємо взаємодію «Дизлайк»
        dislike_id = get_dislike_type_id()
        add_interaction(applicant_id, violator_id, dislike_id)
        await message.answer("✅ Скаргу відправлено. Дякуємо за деталі!")

    await viewing_profiles(message, state)