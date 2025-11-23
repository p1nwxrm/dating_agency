import random
from aiogram import Router, types, F

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from database.db import get_connection
from utils.geolocation import calculate_distance
from config import DAILY_VIEW_LIMIT

from utils.show_profile import show_profile
from show_menus import show_user_main_menu, show_user_rating_menu

router = Router()

# ---------------------------
# Перегляд анкет
# ---------------------------
@router.message(UserMenu.main_menu, F.text == "1")
async def viewing_profiles(message: types.Message, state: FSMContext):
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

        # --- Перевірка бана ---
        cursor.execute("""
            SELECT 
                b.*,
                r.name AS reason_name,
                r.description AS reason_description
            FROM bans b
            JOIN reasons r ON b.reason_id = r.id
            WHERE b.user_id = %s
        """, (user_id,))
        ban = cursor.fetchone()

        if ban:
            await message.answer(
                f"🚫 Твій акаунт заблокований.\n\n"
                f"🔹 Причина: {ban['reason_name']}\n"
                f"📄 Деталі: {ban['reason_description'] or 'Без додаткового опису.'}\n\n"
                f"Якщо ти вважаєш, що це помилка — звернись до підтримки."
            )
            await show_user_main_menu(message.bot, message.chat.id)
            await state.set_state(UserMenu.main_menu)
            return

        # Завантажуємо профіль користувача
        cursor.execute("SELECT * FROM profiles WHERE user_id = %s", (user_id,))
        profile = cursor.fetchone()
        if not profile:
            await message.answer("❌ Спочатку створи анкету.")
            await show_user_main_menu(message.bot, message.chat.id)
            await state.set_state(UserMenu.main_menu)
            return

        # --- Перевірка статусу анкети ---
        if not profile["is_active"]:
            cursor.execute("UPDATE profiles SET is_active = TRUE WHERE user_id = %s", (user_id,))
            conn.commit()
            await message.answer(
                "🌞 Твоя анкета була неактивною, тому я автоматично зробив її активною.\n"
                "✅ Тепер ти можеш переглядати інші профілі!"
            )

        # Отримуємо бажані статі користувача
        cursor.execute("SELECT gender_id FROM desired_genders WHERE profile_id = %s", (profile["id"],))
        desired_genders = [r["gender_id"] for r in cursor.fetchall()]

        # Визначаємо допустиму різницю у віці
        age = profile["age"]
        if 11 <= age < 14: diff = 1
        elif 14 <= age < 18: diff = 2
        elif 18 <= age < 25: diff = 3
        elif 25 <= age < 40: diff = 5
        else: diff = 10
        min_age, max_age = age - diff, age + diff

        # Отримуємо чорний список (з обох боків)
        cursor.execute("""
            SELECT blocked_id FROM blacklist WHERE blocker_id = %s
            UNION
            SELECT blocker_id FROM blacklist WHERE blocked_id = %s
        """, (user_id, user_id))
        blacklisted = {r["blocked_id"] for r in cursor.fetchall()}

        # Отримуємо потенційні анкети
        cursor.execute("""
            SELECT p.*, u.id AS user_id
            FROM profiles p
            JOIN users u ON p.user_id = u.id
            WHERE p.is_active = TRUE
              AND p.goal_id = %s
              AND p.user_id != %s
              AND p.age BETWEEN %s AND %s
              AND p.is_active = TRUE
        """, (profile["goal_id"], user_id, min_age, max_age))
        candidates = cursor.fetchall()

        filtered = []
        for c in candidates:
            # Пропускаємо, якщо користувач у чорному списку
            if c["user_id"] in blacklisted:
                continue

            # Пропускаємо, якщо цей користувач у бані
            cursor.execute("SELECT 1 FROM bans WHERE user_id = %s LIMIT 1", (c["user_id"],))
            if cursor.fetchone():
                continue

            # Їхні бажані статі
            cursor.execute("SELECT gender_id FROM desired_genders WHERE profile_id = %s", (c["id"],))
            c_desired = [r["gender_id"] for r in cursor.fetchall()]

            # Перевірка взаємного підходження статей
            if (c["gender_id"] not in desired_genders) or (profile["gender_id"] not in c_desired):
                continue

            # Перевірка відстані
            distance = calculate_distance(profile["latitude"], profile["longitude"], c["latitude"], c["longitude"])
            if not (distance <= profile["search_radius_km"] and distance <= c["search_radius_km"]):
                continue

            # Перевірка, чи цю анкету вже показували цьому користувачу сьогодні N раз
            cursor.execute("""
                            SELECT COUNT(*) AS views_today
                            FROM interaction_history
                            WHERE evaluator_id = %s
                              AND evaluated_id = %s
                              AND DATE(datetime) = CURDATE()
                        """, (user_id, c["user_id"]))
            views_today = cursor.fetchone()["views_today"]

            if views_today < DAILY_VIEW_LIMIT:
                filtered.append(c)

        if not filtered:
            await message.answer("😕 Поки що немає відповідних анкет.")
            await show_user_main_menu(message.bot, message.chat.id)
            await state.set_state(UserMenu.main_menu)
            return

        # Випадковий вибір
        chosen = random.choice(filtered)

        await state.update_data(current_profile_id = chosen["id"])
        await show_profile(message.bot, message.chat.id, user_id = chosen["user_id"])
        await show_user_rating_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.rate_menu)
    finally:
        cursor.close()
        conn.close()