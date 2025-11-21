from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.user_states import Registration

router = Router()

# ---------------------------
# Ім'я
# ---------------------------
@router.message(Registration.set_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name = name)

    # --- Вік ---
    await message.answer("Скільки тобі років? 🔢", reply_markup = types.ReplyKeyboardRemove())
    await state.set_state(Registration.set_age)
