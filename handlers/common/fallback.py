from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from .start import cmd_start

router = Router()

# ---------------------------
# Catch-all handler (message)
# ---------------------------
@router.message()
async def handle_unrecognized_message(message: types.Message, state: FSMContext):
    await message.answer("🤔 Хмм… не можу зараз обробити цю дію. Повертаємося в головне меню ⬅️🏠", show_alert = False)
    await cmd_start(message, state)

# ---------------------------
# Catch-all handler (callback)
# ---------------------------
@router.callback_query()
async def handle_unrecognized_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("🤔 Хмм… не можу зараз обробити цю дію. Повертаємося в головне меню ⬅️🏠", show_alert = False)
    await cmd_start(callback.message, state)