from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from utils.geolocation import get_city

router = Router()

# ---------------------------
# Геолокація
# ---------------------------
@router.message(Registration.set_location, F.location)
async def process_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    city = get_city(lat, lon, "uk")
    if city is None:
        city = "???"

    await state.update_data(latitude = lat, longitude = lon, city = city)

    # --- Радіус пошуку ---
    kb = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "🌍 Шукати по всьому світу")]], resize_keyboard = True)
    await message.answer("На яку відстань шукати співрозмовників (у км)? 📏", reply_markup = kb)
    await state.set_state(Registration.set_search_radius)