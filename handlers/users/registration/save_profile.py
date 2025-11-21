from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.user_states import Registration, UserMenu
from database.db import get_connection
from utils.show_profile import show_profile
from handlers.users.show_menus import show_user_main_menu

router = Router()

# ---------------------------
# Збереження анкети до БД
# ---------------------------
@router.message(Registration.save_to_db)
async def save_profile_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE tg_username = %s",
        (message.from_user.username,)
    )
    user_id = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM profiles WHERE user_id = %s", (user_id,))
    profile_row = cursor.fetchone()

    if profile_row:
        profile_id = profile_row[0]

        cursor.execute("""
            UPDATE profiles
            SET name = %s, age = %s, gender_id = %s, goal_id = %s,
                latitude = %s, longitude = %s, city = %s,
                search_radius_km = %s, description = %s
            WHERE id = %s
        """, (
            data["name"], data["age"], data["gender_id"], data["goal_id"],
            data["latitude"], data["longitude"], data["city"],
            data["search_radius_km"], data["about"], profile_id
        ))

        # Видаляємо старі фото та бажані статі перед додаванням нових
        cursor.execute("DELETE FROM profile_photos WHERE profile_id = %s", (profile_id,))
        cursor.execute("DELETE FROM desired_genders WHERE profile_id = %s", (profile_id,))

    else:
        # Створюємо профіль
        cursor.execute("""
            INSERT INTO profiles
                (user_id, name, age, gender_id, goal_id,
                 latitude, longitude, city, search_radius_km, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data["name"], data["age"], data["gender_id"], data["goal_id"],
            data["latitude"], data["longitude"], data["city"],
            data["search_radius_km"], data["about"]
        ))

        profile_id = cursor.lastrowid

    # --- Зберігаємо фото ---
    for url in data.get("photos", []):
        cursor.execute(
            "INSERT INTO profile_photos (profile_id, photo_url) VALUES (%s, %s)",
            (profile_id, url)
        )

    # --- Зберігаємо бажані статі ---
    for g_id in data["desired_genders"]:
        cursor.execute(
            "INSERT INTO desired_genders (profile_id, gender_id) VALUES (%s, %s)",
            (profile_id, g_id)
        )

    conn.commit()
    cursor.close()
    conn.close()

    # --- Надсилаємо анкету ---
    await message.answer("✅ Анкету створено! Ось так вона виглядає:", reply_markup = types.ReplyKeyboardRemove())
    await show_profile(bot = message.bot, chat_id = message.chat.id, user_id = message.from_user.id)

    await show_user_main_menu(bot = message.bot, chat_id = message.chat.id)
    await state.set_state(UserMenu.main_menu)