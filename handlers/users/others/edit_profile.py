from aiogram import Router, types, F

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu, Registration
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

#---------------------------
# Редагування анкети
# ---------------------------
@router.message(UserMenu.main_menu, F.text == "4")
async def edit_profile(message: types.Message, state: FSMContext):
    button = KeyboardButton(text = message.from_user.first_name or "???")
    kb = ReplyKeyboardMarkup(keyboard = [[button]], resize_keyboard = True)
    await message.answer("🔁 Почнемо редагування.\nЯк тебе звати? 👇", reply_markup = kb)

    await state.clear()
    await state.set_state(Registration.set_name)
