from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext
from states.admin_states import AdminPanel
from states.moderator_states import ModeratorPanel
from states.user_states import Registration, UserMenu

from utils.show_profile import show_profile
from handlers.users.show_menus.main_menu import show_user_main_menu
from handlers.admins.show_menus.main_menu import show_admin_main_menu
from handlers.moderators.show_menus.main_menu import show_moderator_main_menu

from database.db import get_connection
from database.queries import get_user_role, user_exists, profile_exists

router = Router()

# ---------------------------
# /start
# ---------------------------
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    # Якщо користувач у БД не існує — додаємо
    exists = user_exists(user_id)

    if not exists:
        cursor.execute(
            "INSERT INTO users (id, tg_username, role_id) VALUES (%s, %s, %s)",
            (user_id, username, 3)
        )
        conn.commit()

        # Вітання тільки для нових користувачів
        await message.answer(
	        f"👋 Привіт, {message.from_user.first_name or 'користувачу'}!\n\n"
	        "💫 Ласкаво просимо у RIZZEM — твій новий простір для знайомств, цікавих людей і яскравих вражень!\n\n"
	        "💬 Тут ти можеш не просто знайти друзів або нові знайомства — а й ділитися своїми інтересами, "
	        "спілкуватися з тими, хто тебе справді зрозуміє, і відкривати для себе нові можливості.\n\n"
	        "📸 Додай свої фото, розкажи трохи про себе і обери людей, які тобі цікаві.\n\n"
	        "❤️ Не бійся показати себе таким, який ти є — тут цінують щирість і відкритість.\n\n"
	        "✨ Починай знайомства вже зараз!"
        )

    # Отримуємо роль користувача
    role = get_user_role(user_id)

    # Якщо роль — адмін
    if role == 1:
        await show_admin_main_menu(message.bot, message.chat.id)
        await state.set_state(AdminPanel.main_menu)

        cursor.close()
        conn.close()
        return

    # Якщо роль — МОДЕРАТОР
    if role == 2:
        await show_moderator_main_menu(message.bot, message.chat.id)
        await state.set_state(ModeratorPanel.main_menu)

        cursor.close()
        conn.close()
        return

    # Якщо роль — користувач
    if not profile_exists(user_id):
        # Починаємо реєстрацію
        button = KeyboardButton(text = message.from_user.first_name or "???")
        kb = ReplyKeyboardMarkup(keyboard = [[button]], resize_keyboard = True)

        await message.answer("Як тебе звати? 👇", reply_markup = kb)
        await state.set_state(Registration.set_name)
    else:
        # Якщо анкета є — показуємо її й відкриваємо меню
        await message.answer("Ось так виглядає твоя анкета:")
        await show_profile(bot = message.bot, chat_id = message.chat.id, user_id = user_id)

        await show_user_main_menu(message.bot, message.chat.id)
        await state.set_state(UserMenu.main_menu)

    cursor.close()
    conn.close()