from aiogram import Router, types, F

from aiogram.fsm.context import FSMContext
from states.user_states import UserMenu

from utils.show_user_stats import show_user_stats
from show_menus import show_user_main_menu

router = Router()

# ---------------------------
# Переглянути статистику про себе
# ---------------------------
@router.message(UserMenu.main_menu, F.text == "5")
async def show_profile_stat(message: types.Message, state: FSMContext):
    await show_user_stats(message.bot, message.chat.id, message.from_user.id)
    await show_user_main_menu(message.bot, message.chat.id)
    await state.set_state(UserMenu.main_menu)