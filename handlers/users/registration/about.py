from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from database.db import get_connection
from database.queries import get_about_info
from .save_profile import save_profile_to_db

router = Router()

# ---------------------------
# Допоміжна функція: перехід до розділу "Про себе"
# ---------------------------
async def ask_about_yourself(message: types.Message, state: FSMContext, prefix_text: str = ""):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("""
        SELECT p.description
        FROM profiles p
        JOIN users u ON p.user_id = u.id
        WHERE u.tg_username = %s
    """, (message.from_user.username,))
    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    # Формуємо клавіатуру
    buttons = [[KeyboardButton(text = "Пропустити")]]
    extra_text = ""

    if profile and profile["description"]:
        buttons.insert(0, [KeyboardButton(text = "📝 Залишити поточний опис")])
        extra_text = "\n\nЯкщо хочеш залишити поточний опис — натисни кнопку нижче."

    kb = ReplyKeyboardMarkup(keyboard = buttons, resize_keyboard = True)

    prefix = f"{prefix_text}\n\n" if prefix_text else ""
    await message.answer(
        f"{prefix}📝 Розкажи трохи про себе.{extra_text}",
        reply_markup = kb
    )

    await state.set_state(Registration.set_about_info)

# ---------------------------
# Про себе
# ---------------------------
@router.message(Registration.set_about_info)
async def process_about(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Введи текст або натисни «Пропустити».")
        return

    text = message.text.strip().lower()

    if text == "📝 залишити поточний опис":
        about = get_about_info(message.from_user.username)
    elif text == "пропустити":
        about = None
    else:
        about = message.text.strip()

    await state.update_data(about = about)
    await state.set_state(Registration.save_to_db)
    await save_profile_to_db(message, state)