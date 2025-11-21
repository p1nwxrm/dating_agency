from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from .gender import ask_gender

router = Router()

# ---------------------------
# Обробка інформації про вік користувача
# ---------------------------
@router.message(Registration.set_age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.strip().isdigit() or not (11 <= int(message.text) <= 66):
        await message.answer("❌ Введи, будь ласка, справжній вік числом (11–66).")
        return
    await state.update_data(age = int(message.text))

    # --- Стать ---
    await ask_gender(message)
    await state.set_state(Registration.set_gender)