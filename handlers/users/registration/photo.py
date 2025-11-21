from aiogram import Router, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states.user_states import Registration
from handlers.users.registration.about import ask_about_yourself
from database.queries import get_existing_photos
from config import MAX_PHOTO_AMOUNT

router = Router()

# ---------------------------
# Запит фото у користувача
# ---------------------------
async def ask_photo(message: types.Message, existing_photos: list):
    # Формуємо клавіатуру
    if existing_photos:
        kb = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "📸 Залишити поточні фото")],], resize_keyboard = True)
        extra_text = "\n\nЯкщо хочеш залишити поточні фото — натисни кнопку нижче."
    else:
        kb = ReplyKeyboardRemove()
        extra_text = ""

    # Відправляємо повідомлення
    await message.answer(f"Надішли до 2 своїх фото 📸{extra_text}", reply_markup = kb)

# ---------------------------
# Обробка фото користувача (не альбомом)
# ---------------------------
@router.message(Registration.set_photos, F.photo)
async def process_single_photo(message: types.Message, state: FSMContext):
    if message.media_group_id:
        await message.answer("📸 Надсилай фото по одному, будь ласка 🙂")
        return

    data = await state.get_data()
    photos = data.get("photos", [])

    # Беремо найякісніше фото з одного повідомлення
    file_id = message.photo[-1].file_id
    if not photos or photos[-1] != file_id:
        photos.append(file_id)

    # Обмежуємо кількість
    photos = photos[-MAX_PHOTO_AMOUNT:]
    await state.update_data(photos = photos)

    if len(photos) < MAX_PHOTO_AMOUNT:
        kb = ReplyKeyboardMarkup(
            keyboard = [[KeyboardButton(text="Далі")]],
            resize_keyboard = True
        )
        await message.answer("Фото збережено ✅. Надішли ще або натисни «Далі».", reply_markup = kb)
    else:
        await ask_about_yourself(message, state, prefix_text = "Фото збережено ✅.")

# ---------------------------
# Кнопка “Далі” → Про себе
# ---------------------------
@router.message(Registration.set_photos, F.text.lower() == "далі")
async def next_to_about(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    # Якщо жодного фото — не дозволяємо переходити
    if not photos:
        await message.answer("❌ Спочатку надішли хоча б одне фото 📸")
        return

    await ask_about_yourself(message, state, prefix_text = "Фото збережено ✅.")

# ---------------------------
# Кнопка "Залишити поточні фото"
# ---------------------------
@router.message(Registration.set_photos, F.text.lower() == "📸 залишити поточні фото")
async def keep_existing_photos(message: types.Message, state: FSMContext):
    existing_photos = get_existing_photos(message.from_user.username)
    if not existing_photos:
        await message.answer("❌ У тебе немає поточних фото в анкеті.")
        return

    await state.update_data(photos=[p["photo_url"] for p in existing_photos])
    await ask_about_yourself(message, state, prefix_text = "📸 Поточні фото залишено без змін.")