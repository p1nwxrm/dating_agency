from aiogram import Router, types, F

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from show_menus import show_user_status_menu

router = Router()

# ---------------------------
# Меню для статусу анкети
# ---------------------------
@router.message(UserMenu.main_menu, F.text == "6")
async def profile_status(message: types.Message, state: FSMContext):
    await show_user_status_menu(message.bot, message.chat.id)
    await state.set_state(UserMenu.status_menu)