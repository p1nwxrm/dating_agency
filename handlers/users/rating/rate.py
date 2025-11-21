from aiogram import Router, types

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from database.db import get_connection
from database.queries import get_like_type_id, get_dislike_type_id
from database.queries import add_interaction, add_to_blacklist

from .viewing import viewing_profiles
from handlers.users.show_menus import show_user_main_menu, show_user_complaints_menu

router = Router()

# ---------------------------
# Оцінка анкет
# ---------------------------
@router.message(UserMenu.rate_menu)
async def handle_profile_reaction(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    current_profile_id = data.get("current_profile_id")

    if text == "⬅️ Меню":
        await show_user_main_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.main_menu)
        return

    if text == "🚨 Скарга":
        conn = get_connection()
        cursor = conn.cursor(dictionary = True)
        try:
            # Знаходимо користувача
            cursor.execute("SELECT id FROM users WHERE id = %s", (message.from_user.id,))
            user = cursor.fetchone()
            if not user:
                await message.answer("❌ Користувача не знайдено.")
                return
            user_id = user["id"]

            cursor.execute("SELECT are_complaints_allowed FROM profiles WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()
            if not profile:
                await message.answer("❌ Твоя анкета не знайдена. Створи її спочатку.")
                return

            # Перевіряємо, чи дозволено цьому користувачу скаржитись
            if not profile["are_complaints_allowed"]:
                await message.answer("🚫 Тобі тимчасово заборонено надсилати скарги.")
                return

        finally:
            cursor.close()
            conn.close()

        # Якщо дозволено — показуємо меню скарг
        await show_user_complaints_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.complaints_menu)
        return

    if text == "🚫 ЧС":
        if not current_profile_id:
            await message.answer("⚠️ Сталася помилка: не знайдено поточну анкету.")
            return

        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        try:
            # user_id користувача, чию анкету переглядаємо
            cursor.execute("SELECT user_id FROM profiles WHERE id = %s", (current_profile_id,))
            profile_owner = cursor.fetchone()

            if not profile_owner:
                await message.answer("❌ Анкету не знайдено.")
                return

            blocked_id = profile_owner["user_id"]

            # Поточний користувач
            cursor.execute("SELECT id FROM users WHERE id = %s", (message.from_user.id,))
            user = cursor.fetchone()

            if not user:
                await message.answer("❌ Твій обліковий запис не знайдено в системі.")
                return

            blocker_id = user["id"]

            # Перевірка: не можна додати себе
            if blocker_id == blocked_id:
                await message.answer("😅 Ви не можете додати себе до чорного списку.")
                return

            # Перевірка: чи вже є у ЧС
            cursor.execute("""
                SELECT 1 FROM blacklist
                WHERE blocker_id = %s AND blocked_id = %s
                LIMIT 1
            """, (blocker_id, blocked_id))
            if cursor.fetchone():
                await message.answer("⚠️ Цей користувач вже є у вашому чорному списку.")
                return
        finally:
            cursor.close()
            conn.close()

        # Додаємо в ЧС
        success = add_to_blacklist(blocker_id, blocked_id)

        if not success:
            await message.answer("⚠️ Помилка при додаванні до чорного списку.")
            return

        await message.answer("🚫 Користувача успішно додано до чорного списку.")

        # Ставимо дизлайк
        dislike_id = get_dislike_type_id()
        add_interaction(blocker_id, blocked_id, dislike_id)

        # Показуємо наступну анкету
        await viewing_profiles(message, state)
        return

    if text not in ["❤️ Лайк", "💔 Дизлайк"]:
        await message.answer("❌ Обери дію нижче.")
        return

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)
    try:
        # Знаходимо користувача
        cursor.execute("SELECT id FROM users WHERE tg_username = %s", (message.from_user.username,))
        user = cursor.fetchone()
        if not user:
            await message.answer("❌ Користувача не знайдено.")
            return
        user_id = user["id"]

        # Визначаємо interaction_type_id
        interaction_type_id = None
        if text == "❤️ Лайк":
            interaction_type_id = get_like_type_id()  # Лайк
        elif text == "💔 Дизлайк":
            interaction_type_id = get_dislike_type_id()  # Дизлайк

        # Отримуємо user_id анкети, яку оцінюємо
        cursor.execute("SELECT user_id FROM profiles WHERE id = %s", (current_profile_id,))
        evaluated = cursor.fetchone()
        if not evaluated:
            await message.answer("❌ Анкету не знайдено.")
            return
        evaluated_id = evaluated["user_id"]

        # Записуємо у interaction_history
        add_interaction(user_id, evaluated_id, interaction_type_id)

        # Відправляємо нову анкету
        await viewing_profiles(message, state)
    finally:
        cursor.close()
        conn.close()