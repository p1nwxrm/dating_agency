from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from config import MAX_SEARCH_RADIUS

from database.queries import get_existing_photos
from .photo import ask_photo

router = Router()

# ---------------------------
# Обробка інформації про радіус пошуку
# ---------------------------
@router.message(Registration.set_search_radius)
async def process_radius(message: types.Message, state: FSMContext):
    if message.text is None:
        await message.answer("❌ Введи число (наприклад, 10 або 5.5)")
        return

    text = message.text.strip()

    if text == "🌍 Шукати по всьому світу":
        radius = MAX_SEARCH_RADIUS
    elif text.replace('.', '', 1).isdigit():
        radius = float(text)
    else:
        await message.answer("❌ Введи число (наприклад, 10 або 5.5)")
        return

    if radius > MAX_SEARCH_RADIUS:
        radius = MAX_SEARCH_RADIUS

    await state.update_data(search_radius_km = radius, photos = [])

    existing_photos = get_existing_photos(message.from_user.username)
    await ask_photo(message, existing_photos)
    await state.set_state(Registration.set_photos)