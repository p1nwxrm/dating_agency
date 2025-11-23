from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from states.user_states import Registration
from database.queries import get_genders
from .goal import ask_goal

router = Router()

# ---------------------------
# Запит статі у користувача
# ---------------------------
async def ask_gender(message: types.Message):
    genders = get_genders()
    kb = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text = g["name"], callback_data = f"gender_{g['id']}")] for g in genders
    ])

    await message.answer("Оберіть свою стать 👇", reply_markup = kb)

# ---------------------------
# Обробка інформації про стать
# ---------------------------
@router.callback_query(Registration.set_gender, F.data.startswith("gender_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender_id = int(callback.data.split("_")[1])
    await state.update_data(gender_id = gender_id)

    # --- Ціль знайомства ---
    await ask_goal(callback.message)
    await state.set_state(Registration.set_goal)

    await callback.answer()