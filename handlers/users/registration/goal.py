from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from database.db import get_connection
from database.queries import get_dating_goals

router = Router()

# ---------------------------
# Запит цілей знайомства
# ---------------------------
async def ask_goal(message: types.Message):
    goals = get_dating_goals()
    kb = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text = g["name"], callback_data = f"goal_{g['id']}")] for g in goals
    ])

    await message.answer("Яка твоя ціль знайомства? ❤️", reply_markup = kb)

# ---------------------------
# Обробка цілей знайомства
# ---------------------------
@router.callback_query(Registration.set_goal, F.data.startswith("goal_"))
async def process_goal(callback: types.CallbackQuery, state: FSMContext):
    goal_id = int(callback.data.split("_")[1])
    await state.update_data(goal_id = goal_id)

    # --- Стать партнера ---
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id, name FROM genders ORDER BY id")
    genders = cursor.fetchall()

    cursor.close()
    conn.close()

    kb = InlineKeyboardMarkup(inline_keyboard = [
        [InlineKeyboardButton(text = f"☑️ {g["name"]}", callback_data = f"desired_{g['id']}")] for g in genders
    ])

    await callback.message.answer("Оберіть, співрозмовники якої статі вас цікавлять 👇", reply_markup = kb)
    await state.update_data(desired_genders = [])
    await state.set_state(Registration.set_desired_genders)

    await callback.answer()