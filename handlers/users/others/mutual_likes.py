from aiogram import Router, types, F

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from database.db import get_connection

from utils.show_profile import show_profile
from show_menus import show_user_main_menu

from database.queries import get_like_type_id

router = Router()

# ---------------------------
# Взаємні симпатії
# ---------------------------
@router.message(UserMenu.main_menu, F.text == "2")
async def show_mutual_likes(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    # Перевіряємо, чи користувач є у БД
    cursor.execute("""
            SELECT u.id AS user_id, p.subscription_type_id, st.name AS subscription_name
            FROM users u
            JOIN profiles p ON u.id = p.user_id
            JOIN subscription_types st ON p.subscription_type_id = st.id
            WHERE user_id = %s
        """, (user_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer("⚠️ Ваш профіль не знайдено у базі. Будь ласка, створіть спочатку анкету.")
        cursor.close()
        conn.close()
        return

    # Визначаємо ліміт анкет залежно від типу підписки
    subscription_name = user["subscription_name"]

    if subscription_name == "Базова":
        max_profiles = 5
    else:
        max_profiles = 50  # запасний варіант для майбутніх підписок

    like_id = get_like_type_id()

    # Знаходимо взаємні лайки (останній взаємодій обох сторін має бути 'Лайк')
    cursor.execute("""
        SELECT ih2.evaluator_id AS matched_user_id, MAX(ih1.datetime) AS last_interaction
        FROM interaction_history ih1
        JOIN interaction_history ih2
            ON ih1.evaluated_id = ih2.evaluator_id
            AND ih2.evaluated_id = ih1.evaluator_id
        WHERE ih1.evaluator_id = %s
            AND ih1.interaction_type_id = %s
            AND ih2.interaction_type_id = %s
        GROUP BY ih2.evaluator_id
        ORDER BY last_interaction DESC
        LIMIT %s
    """, (user_id, like_id, like_id, max_profiles))

    matches = cursor.fetchall()
    cursor.close()
    conn.close()

    if not matches:
        await message.answer("💔 Наразі у вас немає взаємних симпатій.")

        await show_user_main_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.main_menu)

        return

    count = len(matches)
    text = f"💞 Знайдено {count} "
    if count == 1:
        text += "взаємну симпатію!"
    elif 2 <= count <= 4:
        text += "взаємні симпатії!"
    else:
        text += "взаємних симпатій!"
    await message.answer(text)

    # Виводимо кожну анкету з юзернеймом
    for match in matches:
        await show_profile(message.bot, message.chat.id, match["matched_user_id"], show_username = True)

    await show_user_main_menu(message.bot, message.chat.id)
    await state.set_state(UserMenu.main_menu)