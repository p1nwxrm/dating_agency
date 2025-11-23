from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from database.db import get_connection

from utils.show_profile import show_profile
from show_menus import show_user_main_menu

router = Router()

# ---------------------------
# Перегляд ЧС
# ---------------------------
@router.message(UserMenu.main_menu, F.text == "3")
async def view_blacklist(message: types.Message, state: FSMContext):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        # Знаходимо поточного користувача
        cursor.execute("SELECT id FROM users WHERE tg_username = %s", (message.from_user.username,))
        user = cursor.fetchone()
        if not user:
            await message.answer("❌ Користувача не знайдено в системі.")
            return
        blocker_id = user["id"]

        # Беремо всіх, кого цей користувач заблокував
        cursor.execute("""
            SELECT b.blocked_id AS blocked_id, u.tg_username AS blocked_username
            FROM blacklist b
            JOIN users u ON b.blocked_id = u.id
            WHERE b.blocker_id = %s
            ORDER BY b.datetime DESC
        """, (blocker_id,))
        blocked_rows = cursor.fetchall()

        if not blocked_rows:
            await message.answer("✅ Твій чорний список порожній.", reply_markup = ReplyKeyboardRemove())
            await show_user_main_menu(message.bot, message.chat.id)
            await state.set_state(UserMenu.main_menu)
            return

        # Для кожного заблокованого користувача — показуємо його анкету і кнопку розблокування
        for row in blocked_rows:
            blocked_id = row["blocked_id"]
            blocked_username = row.get("blocked_username")

            try:
                await show_profile(bot = message.bot, chat_id = message.chat.id, user_id = blocked_id)
            except Exception:
                # У разі помилки з показом профілю — виведемо хоча б ім'я/username
                if blocked_username:
                    await message.answer(f"Профіль @{blocked_username} (ID: {blocked_id})")

            # Кнопка розблокування з callback_data = "unblock:<blocked_id>:<profile_id>"
            kb = InlineKeyboardMarkup(
                inline_keyboard = [
                    [InlineKeyboardButton(text = "🔓 Розблокувати", callback_data = f"toggle_block:{blocked_id}")]
                ]
            )
            # коротке пояснення під анкетою
            await message.bot.send_message(message.chat.id, "Натисни «Розблокувати», щоб прибрати користувача зверху з ЧС.", reply_markup = kb)

        # Після показу всіх записів повертаємо юзера в головне меню (UserMenu.main_menu)
        await show_user_main_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.main_menu)

    finally:
        cursor.close()
        conn.close()