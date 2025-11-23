from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states.moderator_states import ModeratorPanel, ModeratorBan
from show_menus import show_moderator_main_menu, show_complaints_menu

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from database.queries import (
    get_user,
    get_profile,
    is_user_banned,
    get_ban_info,
    ban_user,
    unban_user,
    get_all_reasons,
    get_reason_by_id,
)

from config import MIN_USERNAME_SYMBOLS
from utils.show_profile import show_profile

router = Router()

# ---------------------------
# Обробник кнопки "🚫 Керування банами"
# ---------------------------
@router.message(ModeratorPanel.main_menu, F.text == "🚫 Керування банами")
async def moderator_ban_menu(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "⬅️ Вийти в головне меню")]],resize_keyboard = True)
    await message.answer("🔎 Введіть юзернейм користувача у форматі @username:", reply_markup = kb)
    await state.set_state(ModeratorBan.enter_username)


# ---------------------------
# Обробка введеного юзернейму
# ---------------------------
@router.message(ModeratorBan.enter_username)
async def moderator_check_user(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Вийти в головне меню":
        await show_moderator_main_menu(message.bot, message.chat.id)
        await state.set_state(ModeratorPanel.main_menu)
        return

    text = message.text.strip()

    # Перевірка формату юзернейма
    if not text.startswith("@") or len(text) < MIN_USERNAME_SYMBOLS:
        await message.answer("❗️ Формат невірний. Введіть у вигляді @username.")
        return

    username = text[1:]
    user = get_user(username)

    # Перевірка користувача
    if not user:
        await message.answer("❌ Користувача з таким юзернеймом не знайдено.")
        return

    user_id = user["id"]
    role_name = user["role_name"]

    # Перевірка профілю
    profile = get_profile(user_id)

    if profile:
        # Надсилаємо анкету
        await show_profile(bot = message.bot, chat_id = message.chat.id, user_id = user_id, show_username = False)
    else:
        await message.answer("📝 Анкета відсутня.")

    # Статус бану
    is_banned = is_user_banned(user_id)
    ban_status = "🚫 Заблокований" if is_banned else "✅ Не заблокований"

    # Формуємо службове повідомлення
    info_text = (
        f"👤 Юзернейм: @{username}\n"
        f"🔰 Роль: {role_name}\n"
        f"🔒 Статус акаунту: {ban_status}"
    )

    # Отримуємо причину бану, якщо користувач заблокований
    ban_reason_text = ""
    if is_banned:
        ban_info = get_ban_info(user_id)
        if ban_info:
            reason_name = ban_info["reason_name"]
            extra_info = ban_info.get("extra_info")
            ban_reason_text = f"\nПричина бану: {reason_name}"
            if reason_name == "Інше" and extra_info:
                ban_reason_text += f" ({extra_info})"

    info_text += ban_reason_text

    # Кнопка бану (лише для звичайних юзерів)
    if role_name == "Користувач":
        btn_text = "🔓 Розблокувати" if is_banned else "🚫 Заблокувати"
        kb = InlineKeyboardMarkup(
            inline_keyboard = [
                [InlineKeyboardButton(
                    text = btn_text,
                    callback_data = f"toggle_ban:{user_id}"
                )]
            ]
        )
    else:
        info_text += "\n\n⚠️ Ви не можете змінювати статус акаунту для модераторів та адміністраторів."
        kb = None
    await message.answer(info_text, reply_markup = kb)


# ---------------------------
# Callback для перемикання бан/розбан
# ---------------------------
@router.callback_query(F.data.startswith("toggle_ban:"))
async def toggle_ban_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])

    currently_banned = is_user_banned(user_id)

    if currently_banned:
        # Розбан одразу
        success = unban_user(callback.from_user.id, user_id)

        if success:
            await callback.message.answer("Користувача розбанено ✅")

        await show_moderator_main_menu(callback.message.bot, callback.message.chat.id)
        await state.set_state(ModeratorPanel.main_menu)
        return

    # Якщо користувач НЕ забанений → показуємо меню вибору причини бану
    await state.update_data(ban_user_id = user_id)

    await show_complaints_menu(callback.bot, callback.message.chat.id)
    await state.set_state(ModeratorBan.choose_reason)

    await callback.answer()


# ---------------------------
# Обробка вибору причини бану
# ---------------------------
@router.message(ModeratorBan.choose_reason)
async def moderator_choose_ban_reason(message: types.Message, state: FSMContext):
    text = message.text.strip()

    if text == "⬅️ Назад":
        await message.answer("❌ Бан скасовано.", reply_markup = types.ReplyKeyboardRemove())
        await state.clear()

        await show_moderator_main_menu(message.bot, message.chat.id)
        await state.set_state(ModeratorPanel.main_menu)

        return

    reasons = get_all_reasons()
    reason_ids = [str(r["id"]) for r in reasons]

    if text not in reason_ids:
        await message.answer("❌ Оберіть номер причини зі списку або натисніть «⬅️ Назад».")
        return

    # Чи це “інше”?
    reason_id = int(text)
    reason = get_reason_by_id(reason_id)

    if reason and "інше" in reason.lower():
        await state.update_data(reason_id = reason_id)

        kb = ReplyKeyboardMarkup(keyboard = [[KeyboardButton(text = "⬅️ Назад")]], resize_keyboard = True)
        await message.answer("📝 Вкажіть додаткове пояснення причини бану:", reply_markup = kb)
        await state.set_state(ModeratorBan.other_reason)
        return

    # Стандартна причина → банимо без додаткового тексту
    data = await state.get_data()
    banned_user_id = data.get("ban_user_id")

    success = ban_user(message.from_user.id, banned_user_id, reason_id = reason_id)

    if success:
        await message.answer("🚫 Користувача заблоковано.", reply_markup = types.ReplyKeyboardRemove())
    else:
        await message.answer("❌ Не вдалося забанити користувача.", reply_markup=types.ReplyKeyboardRemove())

    await state.clear()
    await show_moderator_main_menu(message.bot, message.chat.id)
    await state.set_state(ModeratorPanel.main_menu)


# ---------------------------
# Обробка тексту при “Інше”
# ---------------------------
@router.message(ModeratorBan.other_reason)
async def moderator_other_ban_reason(message: types.Message, state: FSMContext):
    if message.text == "⬅️ Назад":
        await message.answer("❌ Бан скасовано.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()

        await show_moderator_main_menu(message.bot, message.chat.id)
        await state.set_state(ModeratorPanel.main_menu)

        return

    extra_text = message.text.strip()
    data = await state.get_data()

    reason_id = data.get("reason_id")
    banned_user_id = data.get("ban_user_id")

    success = ban_user(
        reviewer_id = message.from_user.id,
        user_id = banned_user_id,
        reason_id = reason_id,
        extra_info = extra_text
    )

    if success:
        await message.answer("🚫 Користувача заблоковано.\nДодаткова причина збережена.", reply_markup = types.ReplyKeyboardRemove())
    else:
        await message.answer("❌ Не вдалося забанити користувача.", reply_markup = types.ReplyKeyboardRemove())

    await state.clear()
    await show_moderator_main_menu(message.bot, message.chat.id)
    await state.set_state(ModeratorPanel.main_menu)