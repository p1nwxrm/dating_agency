from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from utils.show_moderator_stats import show_moderator_stats
from states.moderator_states import ModeratorPanel
from show_menus import show_moderator_main_menu

router = Router()

# ---------------------------
# Обробник натискання кнопки "📈 Моя статистика"
# ---------------------------
@router.message(ModeratorPanel.main_menu, F.text == "📈 Моя статистика")
async def show_stats(message: types.Message, state: FSMContext):
    # Отримуємо ID користувача (модератора)
    user_id = message.from_user.id

    # Викликаємо універсальну функцію для відображення статистики
    await show_moderator_stats(bot = message.bot, chat_id = message.chat.id, user_id = user_id)
    await show_moderator_main_menu(message.bot, message.chat.id)