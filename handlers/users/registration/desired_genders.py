from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from database.queries import get_genders

router = Router()

# ---------------------------
# Вибір бажаних статей
# ---------------------------
@router.callback_query(Registration.set_desired_genders, F.data.startswith("desired_"))
async def choose_desired_gender(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = list(data.get("desired_genders", []))

    gender_id = int(callback.data.split("_")[1])

    if gender_id in selected:
        selected.remove(gender_id)
    else:
        selected.append(gender_id)

    await state.update_data(desired_genders = selected)

    # Показуємо оновлений список
    genders = get_genders()

    buttons = []
    for g in genders:
        prefix = "✅ " if g["id"] in selected else "☑️ "
        buttons.append([InlineKeyboardButton(text = prefix + g["name"], callback_data = f"desired_{g['id']}")])
    if selected:
        buttons.append([InlineKeyboardButton(text = "➡️ Далі", callback_data = "goto_location")])
    await callback.message.edit_text("Оберіть, співрозмовники якої статі вас цікавлять 👇", reply_markup = InlineKeyboardMarkup(inline_keyboard = buttons))

# ---------------------------
# Кнопка “Далі” → Геолокація
# ---------------------------
@router.callback_query(Registration.set_desired_genders, F.data == "goto_location")
async def ask_location(callback: types.CallbackQuery, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "📍 Надіслати геолокацію", request_location = True)]], resize_keyboard = True)
    await callback.message.answer("Будь ласка, надішли свою геолокацію 🌍", reply_markup = kb)
    await state.set_state(Registration.set_location)